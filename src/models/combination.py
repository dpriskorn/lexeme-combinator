from typing import List, Any

from pydantic import BaseModel
from rich.table import Table
from wikibaseintegrator.datatypes import Lexeme, String
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.models import Sense

import config
from src.models.exceptions import MissingInformationError


class Combination(BaseModel):
    lexeme: Any  # circular type LexemeMissingCombines
    parts: List[LexemeEntity]

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

    @property
    def table(self) -> Table:
        if self.number_of_parts == 2:
            table = Table(title=self.lexeme.localized_lemma)
            table.add_column("First", style="cyan", justify="right")
            table.add_column("Second", style="magenta")
            table.add_row(
                self.localized_lemma(lexeme=self.parts[0]),
                self.localized_lemma(lexeme=self.parts[1]),
            )
            table.add_row(
                self.localized_lexical_category(lexeme=self.parts[0]),
                self.localized_lexical_category(lexeme=self.parts[1]),
            )
            table.add_row(
                self.localized_glosses_from_all_senses(lexeme=self.parts[0]),
                self.localized_glosses_from_all_senses(lexeme=self.parts[1]),
            )
            table.add_row(
                self.lexeme_uri(lexeme=self.parts[0]),
                self.lexeme_uri(lexeme=self.parts[0]),
            )
            return table
        else:
            raise NotImplementedError()

    @staticmethod
    def localized_lemma(lexeme: LexemeEntity) -> str:
        if not config.language_code:
            raise MissingInformationError()
        language_value = lexeme.lemmas.get(language=config.language_code)
        if language_value:
            return str(language_value)
        else:
            raise MissingInformationError()

    @staticmethod
    def localized_gloss(sense: Sense) -> str:
        if not config.language_code:
            raise MissingInformationError()
        language_value = sense.glosses.get(language=config.language_code)
        if language_value:
            return str(language_value)
        else:
            return (
                f"No gloss for '{config.language_code}' "
                f"language for this sense, please add one"
            )

    def localized_glosses_from_all_senses(self, lexeme: LexemeEntity) -> str:
        glosses = []
        for sense in lexeme.senses.senses:
            glosses.append(self.localized_gloss(sense=sense))
        if glosses:
            return ", ".join(glosses)
        else:
            return f"No senses (please add)"

    @staticmethod
    def localized_lexical_category(lexeme: LexemeEntity) -> str:
        if not config.language_code:
            raise MissingInformationError()
        return str(
            ItemEntity()
            .get(entity_id=lexeme.lexical_category)
            .labels.get(language=config.language_code)
        )

    @property
    def number_of_parts(self) -> int:
        return len(self.parts)

    @staticmethod
    def lexeme_uri(lexeme) -> str:
        return f"{config.wikibase_lexeme_base_uri}{lexeme.id}"
