import logging
from typing import List, Any

from pydantic import validate_arguments
from rich.table import Table
from wikibaseintegrator.datatypes import Lexeme, String
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.models import Sense

import config
from src.console import console
from src.models.combinator_base_model import CombinatorBaseModel
from src.models.exceptions import MissingInformationError, WbiWriteError

logger = logging.getLogger(__name__)


class Combination(CombinatorBaseModel):
    lexeme: LexemeEntity
    parts: List[LexemeEntity]

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @property
    def ask_user_to_validate(self) -> bool:
        logger.debug("ask_user_to_validate: running")
        console.print(self.table)
        question = f"Do you want to upload this combination to Wikidata?(Y/n)"
        answer = console.input(question)
        if answer == "" or answer.lower() == "y":
            # we got enter/yes
            return True
        else:
            return False

    @property
    def the_parts_cover_the_whole_lemma(self) -> bool:
        part_lemmas = []
        for part in self.parts:
            part_lemmas.append(self.__get_cleaned_localized_lemma__(lexeme=part))
        logger.info(f"checking if {' + '.join(part_lemmas)} match the whole string")
        # We lowercase the parts to support lemmas like:
        # helsingforsare = Helsingfors + -are
        if self.localized_lemma(lexeme=self.lexeme) == "".join(part_lemmas):
            return True
        else:
            return False

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
            table = Table(title=self.localized_lemma(lexeme=self.lexeme))
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
                self.lexeme_uri(lexeme=self.parts[1]),
            )
            return table
        elif self.number_of_parts == 3:
            table = Table(title=self.localized_lemma(lexeme=self.lexeme))
            table.add_column("First", style="cyan", justify="right")
            table.add_column("Second", style="magenta")
            table.add_column("Third", style="blue")
            table.add_row(
                self.localized_lemma(lexeme=self.parts[0]),
                self.localized_lemma(lexeme=self.parts[1]),
                self.localized_lemma(lexeme=self.parts[2]),
            )
            table.add_row(
                self.localized_lexical_category(lexeme=self.parts[0]),
                self.localized_lexical_category(lexeme=self.parts[1]),
                self.localized_lexical_category(lexeme=self.parts[2]),
            )
            table.add_row(
                self.localized_glosses_from_all_senses(lexeme=self.parts[0]),
                self.localized_glosses_from_all_senses(lexeme=self.parts[1]),
                self.localized_glosses_from_all_senses(lexeme=self.parts[2]),
            )
            table.add_row(
                self.lexeme_uri(lexeme=self.parts[0]),
                self.lexeme_uri(lexeme=self.parts[1]),
                self.lexeme_uri(lexeme=self.parts[2]),
            )
            return table
        else:
            raise NotImplementedError()

    @staticmethod
    def localized_lemma(lexeme: Any) -> str:

        if not isinstance(lexeme, LexemeEntity):
            raise ValueError("Not a lexeme")
        if not config.language_code:
            raise MissingInformationError()
        language_value = lexeme.lemmas.get(language=config.language_code)
        if language_value:
            return str(language_value)
        else:
            raise MissingInformationError()

    @staticmethod
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
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

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def localized_glosses_from_all_senses(self, lexeme: LexemeEntity) -> str:
        glosses = []
        for sense in lexeme.senses.senses:
            glosses.append(self.localized_gloss(sense=sense))
        if glosses:
            return ", ".join(glosses)
        else:
            return f"No senses (please add)"

    @staticmethod
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
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

    def upload(self):
        logger.debug("upload: running")
        if config.upload_to_wikidata:
            self.lexeme.add_claims(claims=self.claims)
            summary = f"Added combines with [[Wikidata:Tools/lexeme-combinator]]"
            result = self.lexeme.write(summary=summary)
            if result:
                logger.debug(result)
                console.print(f"Succesfully uploaded combines to {self.lexeme_uri(lexeme=self.lexeme)}")
            else:
                raise WbiWriteError(f"Got {result} from WBI")
