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

        Args:
            text: search query string
            extra_conditions_fn: optional callable(term, index) -> list of extra
                SQLAlchemy conditions to include in all-words and word-match levels

        """
        terms = text.split()
        ilike_fields = cls.search_ilike_fields
        sim_fields = cls.search_similarity_fields
        threshold = cls.search_similarity_threshold

        all_words_conditions = []
        for col in ilike_fields:
            all_words_conditions.append(
                and_(*[col.ilike(f"%{t}%") for t in terms]),
            )
        if extra_conditions_fn:
            for term in terms:
                all_words_conditions.extend(extra_conditions_fn(term, None))
        all_words_match = or_(*all_words_conditions)

        word_cases = []
        for i, term in enumerate(terms):
            term_conditions = [col.ilike(f"%{term}%") for col in ilike_fields]
            if extra_conditions_fn:
                term_conditions.extend(extra_conditions_fn(term, i))
            word_cases.append((or_(*term_conditions), literal(20 + i)))
        word_rank = case(*word_cases, else_=literal(30))

        sim_conditions = []
        for term in terms:
            for col in sim_fields:
                sim_conditions.append(func.similarity(col, term) >= threshold)
        similarity_match = or_(*sim_conditions) if sim_conditions else literal(False)

        wsim_conditions = []
        for term in terms:
            for col in sim_fields:
                wsim_conditions.append(func.word_similarity(term, col) >= threshold)
        word_similarity_match = or_(*wsim_conditions) if wsim_conditions else literal(False)

        main_rank = case(
            (all_words_match, literal(10)),
            (similarity_match, literal(40)),
            (word_similarity_match, literal(50)),
            else_=literal(99),
        )

        return main_rank, word_rank

    def _apply_relevance_filter(self, query, text: str, extra_conditions_fn=None):
        """Filter query to only matching rows and store text for ordering."""
        main_rank, word_rank = self._build_relevance_score(text, extra_conditions_fn)
        query = query.where(or_(main_rank < 99, word_rank < 30))
        self._search_text = text
        return query

    def _apply_relevance_ordering(self, query, extra_conditions_fn=None):
        """Prepend relevance ordering if text search is active."""
        text = getattr(self, "_search_text", None)
        if text:
            main_rank, word_rank = self._build_relevance_score(text, extra_conditions_fn)
            query = query.order_by(main_rank.asc(), word_rank.asc())
            self._search_text = None
        return query
