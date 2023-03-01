import logging
from typing import List, Any, Dict, Optional

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src.console import console
from src.enums import InterfixS
from src.models.combination import Combination
from src.models.combinator_base_model import CombinatorBaseModel
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class LexemeMissingCombines(CombinatorBaseModel):
    lexeme: LexemeEntity
    possible_first_partwords: List[LexemeEntity] = []
    first_part_sparql_results: Dict[str, Any] = {}
    wbi: WikibaseIntegrator
    done: bool = False

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @property
    def localized_lemma(self) -> str:
        if not config.language_code:
            raise MissingInformationError()
        language_value = self.lexeme.lemmas.get(language=config.language_code)
        if language_value:
            return str(language_value)
        else:
            return ""

    @property
    def localized_lexeme_category(self) -> str:
        if not self.lexeme:
            raise MissingInformationError()
        if not config.language_code:
            raise MissingInformationError()
        return str(
            ItemEntity()
            .get(entity_id=self.lexeme.lexical_category)
            .labels.get(language=config.language_code)
        )

    def find_first_partword(self):
        query_all_partwords = f"""
        select distinct ?l ?lem ?lexcatLabel ?genderLabel 
        ?inflectionLabel ?createsLabel {{
          values ?targetlemma {{ "{self.localized_lemma}" }}
          ?l dct:language wd:{config.language_qid};
          wikibase:lemma ?lem.
          filter(contains(lcase(?targetlemma), replace(lcase(?lem), "(^-|-$)", ""))).
          # remove this lexeme from the results
          filter (?l != wd:{self.lexeme.id}).
          ?l wikibase:lexicalCategory ?lexcat.
          filter (?lexcat not in (wd:Q102786,wd:Q9788)) # remove abbreviations/letters
          minus {{ ?l wdt:P31 wd:Q102786 }} # remove abbreviations
          optional {{ ?l wdt:P5185 ?gender }}
          optional {{ ?l wdt:P5911 ?inflection }}
          optional {{ ?l wdt:P5923 ?creates }}
          service wikibase:label {{ bd:serviceParam wikibase:language "sv" }}
        }} group by ?l ?lem ?lexcatLabel ?genderLabel ?inflectionLabel ?createsLabel
        order by desc(strlen(?lem)) strstarts(?lem, "-") strends(?lem, "-") ?lem 
        limit 10
        """
        with console.status("Fetching parts"):
            self.first_part_sparql_results = execute_sparql_query(query_all_partwords)
            # console.print(self.first_part_sparql_results)
            self.__parse_first_part_sparql_result_into_lexemes__()
        if self.possible_first_partwords:
            # todo maybe we should just detect and warn the user about homonymous parts?
            self.__iterate_first_part_lexemes__()
        else:
            console.print("No possible lemmas to combine found")

    def __parse_first_part_sparql_result_into_lexemes__(self):
        if not self.first_part_sparql_results:
            raise MissingInformationError()
        wbi = WikibaseIntegrator()
        for result in self.first_part_sparql_results["results"]["bindings"]:
            # console.print(result)
            lexeme = wbi.lexeme.get(
                entity_id=result["l"]["value"].replace(
                    "http://www.wikidata.org/entity/", ""
                )
            )
            self.possible_first_partwords.append(lexeme)

    def __iterate_first_part_lexemes__(self):
        console.print(
            f"Found {len(self.possible_first_partwords)} possible parts of this lemma"
        )
        for lexeme in self.possible_first_partwords:
            lemma = self.__get_cleaned_localized_lemma__(lexeme=lexeme)
            if self.localized_lemma.startswith(lemma):
                logger.info(f"Longest combine lemma candidate found is: {lemma}")
                self.__check_if_two_combine_candidates_cover_the_whole_lemma__(
                    first_part=lexeme
                )
                if not self.done:
                    self.__check_if_two_combine_candidates_with_s_in_between_cover_the_whole_lemma__(
                        first_part=lexeme
                    )
            else:
                logger.info(
                    f"combine lemma candidate {lemma} is not "
                    f"found at start of {self.localized_lemma}"
                )

    def __check_if_two_combine_candidates_cover_the_whole_lemma__(
        self, first_part: LexemeEntity
    ):
        logger.debug("check_if_two_combine_candidates_cover_the_whole_lemma: running")
        # we found the start lemma now check if any of the others complete the word
        for lexeme in self.possible_first_partwords:
            if lexeme.id != first_part.id:
                combination = Combination(
                    lexeme=self.lexeme,
                    parts=[first_part, lexeme],
                )
                if combination.the_parts_cover_the_whole_lemma:
                    if not self.done:
                        logger.debug("No match already approved")
                        if combination.ask_user_to_validate:
                            logger.debug("match was approved")
                            combination.upload()
                            self.done = True

    def __check_if_two_combine_candidates_with_s_in_between_cover_the_whole_lemma__(
        self, first_part: LexemeEntity
    ):
        logger.debug(
            "__check_if_two_combine_candidates_with_s_in_between_cover_the_whole_lemma__: running"
        )
        if not self.done:
            interfix_lexeme = self.__get_interfix_lexeme_if_possible__()
            if interfix_lexeme:
                # we found the start lemma now check if any of the others complete the word
                for current_part in self.possible_first_partwords:
                    if current_part.id != first_part.id:
                        combination = Combination(
                            lexeme=self.lexeme,
                            parts=[first_part, interfix_lexeme, current_part],
                        )
                        if combination.the_parts_cover_the_whole_lemma:
                            if (
                                combination.ask_user_to_validate
                            ):
                                logger.debug("match was approved")
                                combination.upload()
                                self.done = True
                    break

    @staticmethod
    def __get_interfix_lexeme_if_possible__() -> Optional[LexemeEntity]:
        logger.debug("__get_interfix_lexeme_if_possible__: running")
        for language_code in InterfixS:
            logger.debug(f"Checking if {language_code.name} == {config.language_code}")
            if language_code.name == config.language_code:
                logger.info("Found supported interfix language code")
                return LexemeEntity().get(
                    entity_id=InterfixS[config.language_code].value
                )

