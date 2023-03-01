from pydantic import BaseModel, validate_arguments
from wikibaseintegrator.entities import LexemeEntity

import config


class CombinatorBaseModel(BaseModel):
    @staticmethod
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def lexeme_uri(lexeme: LexemeEntity) -> str:
        return f"{config.wikibase_lexeme_base_uri}{lexeme.id}"

    @staticmethod
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __get_cleaned_localized_lemma__(lexeme: LexemeEntity) -> str:
        """We shave of the "-" here"""
        return str(lexeme.lemmas.get(language=config.language_code)).replace("-", "")
