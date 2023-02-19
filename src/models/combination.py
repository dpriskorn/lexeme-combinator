from typing import List

from pydantic import BaseModel
from wikibaseintegrator.datatypes import Lexeme, String
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.models import Senses, Sense

import config
from src.models.exceptions import MissingInformationError


class Combination(BaseModel):
    parts: List[LexemeEntity] = []
    lang: str

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @property
    def claims(self):
        claims: List[Lexeme] = []
        count = 0
        for part in self.parts:
            count += 1
            claims.append(
                Lexeme(
                    prop_nr=config.combines_property,
                    value=part.id,
                    qualifiers=[
                        String(prop_nr=config.series_ordinal_property, value=str(count))
                    ],
                )
            )
        return claims

    def localized_lemma(self, lexeme: LexemeEntity) -> str:
        return str(lexeme.lemmas.get(language=self.lang))

    def localized_gloss(self, sense: Sense) -> str:
        if not self.lang:
            raise MissingInformationError()
        return str(sense.glosses.get(language=self.lang))

    def localized_glosses_from_all_senses(self, lexeme: LexemeEntity) -> str:
        glosses = []
        for sense in lexeme.senses.senses:
            glosses.append(self.localized_gloss(sense=sense))
        if glosses:
            return ", ".join(glosses)
        else:
            return f"No sense (please add it, see {self.lexeme_uri(lexeme=lexeme)})"

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
        glosses = []
        for part in self.parts:
            lemmas.append(self.localized_lemma(lexeme=part))
            lexical_categories.append(self.localized_lexical_category(lexeme=part))
            glosses.append(self.localized_glosses_from_all_senses(lexeme=part))
        return (
            f"{' + '.join(lemmas)}\n"
            f"{' + '.join(lexical_categories)}\n"
            f"{' + '.join(glosses)}"
        )

    def lexeme_uri(self, lexeme) -> str:
        return f"{config.wikibase_lexeme_base_uri}{lexeme.id}"
