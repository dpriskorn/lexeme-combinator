import logging
from typing import List, Any, Dict

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity, ItemEntity
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src.console import console
from src.models.combination import Combination
from src.models.exceptions import WbiWriteError, MissingInformationError

logger = logging.getLogger(__name__)


class LexemeMissingCombines(BaseModel):
    lexeme: LexemeEntity
    lang: str
    possible_first_partwords: List[LexemeEntity] = []
    possible_finished_combinations: List[Combination] = []
    first_part_sparql_results: Dict[str, Any] = {}
    combine_two_validation_approved: bool = False
    wbi: WikibaseIntegrator

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @property
    def localized_lemma(self) -> str:
        return str(self.lexeme.lemmas.get(language=self.lang))

    @property
    def localized_lexeme_category(self) -> str:
        if not self.lexeme:
            raise MissingInformationError()
        if not self.lang:
            raise MissingInformationError()
        return str(
            ItemEntity()
            .get(entity_id=self.lexeme.lexical_category)
            .labels.get(language=self.lang)
        )

    @property
    def lexeme_uri(self) -> str:
        if not self.lexeme:
            raise MissingInformationError()
        return f"{config.wikibase_lexeme_base_uri}{self.lexeme.id}"

    def find_first_partword(self):
        query_all_partwords = f"""
        select distinct ?l ?lem ?lexcatLabel ?genderLabel 
        ?inflectionLabel ?createsLabel {{
          values ?targetlemma {{ "{self.localized_lemma}" }}
          ?l dct:language wd:Q9027;
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
        }} group by ?l ?lem ?lemma ?lexcatLabel ?genderLabel ?inflectionLabel ?createsLabel
        order by desc(strlen(?lem)) strstarts(?lem, "-") strends(?lem, "-") ?lem 
        limit 10
        """
        with console.status("Fetching parts"):
            self.first_part_sparql_results = execute_sparql_query(query_all_partwords)
            # console.print(self.first_part_sparql_results)
            self.__parse_first_part_sparql_result_into_lexemes__()
        if self.possible_first_partwords:
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
                console.print(f"Longest combine lemma candidate found is: {lemma}")
                self.__check_if_two_combine_candidates_cover_the_whole_lemma__(
                    first_part=lexeme
                )
            else:
                console.print(
                    f"combine lemma candidate {lemma} is not "
                    f"found at start of {self.localized_lemma}"
                )

    def __check_if_two_combine_candidates_cover_the_whole_lemma__(
        self, first_part: LexemeEntity
    ):
        logger.debug("check_if_two_combine_candidates_cover_the_whole_lemma: running")
        # we found the start lemma now check if any of the others complete the word
        start_lemma = self.__get_cleaned_localized_lemma__(first_part)
        for lexeme in self.possible_first_partwords:
            if lexeme.id != first_part.id:
                possible_end_lemma = self.__get_cleaned_localized_lemma__(lexeme=lexeme)
                logger.debug(
                    f"checking if {start_lemma} + {possible_end_lemma} match the whole string"
                )
                # We lowercase the parts to support lemmas like:
                # helsingforsare = Helsingfors + -are
                if (
                    self.localized_lemma
                    == start_lemma.lower() + possible_end_lemma.lower()
                ):
                    # logger.info(
                    #     f"{start_lemma} + {possible_end_lemma} match the whole string!"
                    # )
                    combination = Combination(
                        lang=self.lang, parts=[first_part, lexeme]
                    )
                    self.__ask_user_to_validate_combination__(combination=combination)
                    if self.combine_two_validation_approved:
                        self.__upload_combination__(combination=combination)

    def __get_cleaned_localized_lemma__(self, lexeme: LexemeEntity) -> str:
        """We shave of the "-" here"""
        return str(lexeme.lemmas.get(language=self.lang))

    def __ask_user_to_validate_combination__(self, combination: Combination):
        logger.debug("__ask_user_to_validate_combination__: running")
        console.print(str(combination))
        question = f"Do you want to upload this combination to Wikidata?(Y/n)"
        answer = console.input(question)
        if answer == "" or answer.lower() == "y":
            # we got enter/yes
            self.combine_two_validation_approved = True
        else:
            self.combine_two_validation_approved = False

    def __upload_combination__(self, combination: Combination):
        logger.debug("__upload_combination__: running")
        if config.upload_to_wikidata:
            self.lexeme.add_claims(claims=combination.claims)
            summary = f"Added comibnes with [[Wikidata:Tools/lexeme-combinator]]"
            result = self.lexeme.write(summary=summary)
            if result:
                logger.debug(result)
                console.print(f"Succesfully uploaded combines to {self.lexeme_uri}")
            else:
                raise WbiWriteError(f"Got {result} from WBI")
