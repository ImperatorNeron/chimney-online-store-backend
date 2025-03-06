class FieldNotFoundError(Exception):
    """Custom exception for handling non-existent fields in the model."""

    def __init__(self, field_name: str, model_name: str):
        super().__init__(
            f"Field '{field_name}' does not exist in the model '{model_name}'.",
        )
