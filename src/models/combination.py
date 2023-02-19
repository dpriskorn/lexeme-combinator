from typing import List, Any

from pydantic import BaseModel
from rich.table import Table
from wikibaseintegrator.datatypes import Lexeme, String
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.models import Senses, Sense

import config
from src.models.exceptions import MissingInformationError


class Combination(BaseModel):
    lexeme: Any  # circular type LexemeMissingCombines
    parts: List[LexemeEntity]
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
            return table
        else:
            raise NotImplementedError()

    @property
    def localized_lexical_categories(self) -> (str, str):
        return ()

    @property
    def localized_lemmas(self) -> (str, str):
        return ()

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

    @property
    def number_of_parts(self) -> int:
        return len(self.parts)

    def lexeme_uri(self, lexeme) -> str:
        return f"{config.wikibase_lexeme_base_uri}{lexeme.id}"
