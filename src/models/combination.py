from typing import List

from pydantic import BaseModel
from wikibaseintegrator.entities import LexemeEntity, ItemEntity

from src.exceptions import MissingInformationError


class Combination(BaseModel):
    parts: List[LexemeEntity] = []
    lang: str

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    def localized_lemma(self, lexeme: LexemeEntity) -> str:
        return str(lexeme.lemmas.get(language=self.lang))

    def localized_lexical_category(self, lexeme: LexemeEntity) -> str:
        if not self.lang:
            raise MissingInformationError()
        return str(
            ItemEntity()
            .get(entity_id=lexeme.lexical_category)
            .labels.get(language=self.lang)
        )

    def __str__(self):
        lemmas = []
        lexical_categories = []
        for part in self.parts:
            lemmas.append(self.localized_lemma(lexeme=part))
            lexical_categories.append(self.localized_lexical_category(lexeme=part))
        return f"{' + '.join(lemmas)}\n{' + '.join(lexical_categories)}"
