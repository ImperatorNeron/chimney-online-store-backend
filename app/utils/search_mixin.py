from sqlalchemy import and_, case, func, literal, or_


class RelevanceSearchMixin:
    """Mixin for 4-level relevance text search.

    Subclasses must define:
        search_ilike_fields: list of columns for ilike matching
        search_similarity_fields: list of columns for pg_trgm similarity
        search_similarity_threshold: float (default 0.1)

    """

    search_ilike_fields: list = []
    search_similarity_fields: list = []
    search_similarity_threshold: float = 0.1

    @classmethod
    def _build_relevance_score(cls, text: str, extra_conditions_fn=None):
        """Build (main_rank, word_rank) expressions.

        Ranking model (lower = more relevant), matching user intent:
          1  exact  : the whole name equals the query
          2  prefix : the name starts with the query
          3  phrase : the name contains the whole query as a substring
          4  all-terms cross-field : every term found in SOME field
          5  all-terms single-field: every term found in ONE ilike field
          20 partial: at least one term matched (ranked by HOW MANY matched)
          60 fuzzy  : nothing matched literally, but pg_trgm is close enough
          99 no match: filtered out entirely

        Within the same main_rank, `word_rank` orders by number of matched
        terms (more matched -> higher), then by trigram similarity so the
        closest name wins ties.

        Args:
            text: search query string
            extra_conditions_fn: optional callable(term, index) -> list of extra
                SQLAlchemy conditions to include in all-words and word-match levels

        """
        terms = text.split()
        ilike_fields = cls.search_ilike_fields
        sim_fields = cls.search_similarity_fields
        threshold = cls.search_similarity_threshold

        # Per-term "found anywhere" condition: the term matches ANY ilike field
        # OR any extra (attribute) condition. This lets a query span several
        # columns, e.g. "труба 800 нерж" → name~труба, diameter~800, metal~нерж.
        def term_found_anywhere(term, index):
            conds = [col.ilike(f"%{term}%") for col in ilike_fields]
            if extra_conditions_fn:
                conds.extend(extra_conditions_fn(term, index))
            return or_(*conds)

        # --- Exact / prefix / phrase matches on the primary (first) field. ---
        # These are the strongest signals: the user typed (almost) the name.
        primary = ilike_fields[0] if ilike_fields else None
        exact_match = primary.ilike(text) if primary is not None else literal(False)
        prefix_match = primary.ilike(f"{text}%") if primary is not None else literal(False)
        phrase_match = primary.ilike(f"%{text}%") if primary is not None else literal(False)

        # Level 4: every term is found in SOME field (cross-field match).
        all_terms_found = and_(
            *[term_found_anywhere(t, i) for i, t in enumerate(terms)],
        )

        # Level 5: all terms present in a SINGLE ilike field.
        all_words_conditions = []
        for col in ilike_fields:
            all_words_conditions.append(
                and_(*[col.ilike(f"%{t}%") for t in terms]),
            )
        all_words_match = or_(*all_words_conditions)

        # How many DISTINCT terms matched somewhere. Drives partial ranking:
        # more matched terms => lower word_rank => higher in the list.
        match_count = None
        for i, term in enumerate(terms):
            hit = case((term_found_anywhere(term, i), literal(1)), else_=literal(0))
            match_count = hit if match_count is None else (match_count + hit)
        if match_count is None:
            match_count = literal(0)

        # At least one term matched literally.
        any_word_match = or_(
            *[term_found_anywhere(t, i) for i, t in enumerate(terms)],
        ) if terms else literal(False)

        # Fuzzy safety net (typos): pg_trgm similarity / word_similarity.
        sim_conditions = []
        wsim_conditions = []
        for term in terms:
            for col in sim_fields:
                sim_conditions.append(func.similarity(col, term) >= threshold)
                wsim_conditions.append(func.word_similarity(term, col) >= threshold)
        fuzzy_match = or_(*(sim_conditions + wsim_conditions)) if sim_conditions else literal(False)

        main_rank = case(
            (exact_match, literal(1)),
            (prefix_match, literal(2)),
            (phrase_match, literal(3)),
            (all_terms_found, literal(4)),
            (all_words_match, literal(5)),
            (any_word_match, literal(20)),
            (fuzzy_match, literal(60)),
            else_=literal(99),
        )

        # Secondary ordering: more matched terms first. (30 - matched) keeps it
        # small-is-better, consistent with main_rank. Ties broken by similarity
        # to the whole query on the primary field (closer name = higher).
        word_rank = literal(30) - match_count

        return main_rank, word_rank

    def _relevance_similarity(self, text: str):
        """Trigram similarity of the primary field to the whole query, as a
        DESC tie-breaker (higher similarity = more relevant).

        Returns None when there is no similarity field configured.

        """
        sim_fields = self.search_similarity_fields
        if not sim_fields:
            return None
        return func.similarity(sim_fields[0], text)

    def _apply_relevance_filter(self, query, text: str, extra_conditions_fn=None):
        """Filter query to only matching rows and store text for ordering."""
        main_rank, word_rank = self._build_relevance_score(text, extra_conditions_fn)
        # Keep anything that matched at all (literal OR fuzzy). Rank 99 rows
        # (no match, not even close) are dropped entirely.
        query = query.where(main_rank < 99)
        self._search_text = text
        return query

    def _apply_relevance_ordering(self, query, extra_conditions_fn=None):
        """Prepend relevance ordering if text search is active."""
        text = getattr(self, "_search_text", None)
        if text:
            main_rank, word_rank = self._build_relevance_score(text, extra_conditions_fn)
            order = [main_rank.asc(), word_rank.asc()]
            sim = self._relevance_similarity(text)
            if sim is not None:
                order.append(sim.desc())
            query = query.order_by(*order)
            self._search_text = None
        return query
