import logging
import random
from typing import List, Dict, Any

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_login import Login

import config
from src.console import console
from src.models.exceptions import MissingInformationError
from src.models.lexeme_missing_combines import LexemeMissingCombines

logger = logging.getLogger(__name__)


class Combinator(BaseModel):
    """This looks up and holds all the lexemes we work on"""

    lang: str = ""
    # lexical_category: str = ""
    lexemes_without_combines: List[LexemeMissingCombines] = []
    sparql_result: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    def start(self):
        """Helper method"""
        logger.debug("start: running")
        with console.status("Fetching lexemes to work on"):
            self.__fetch_lexemes_without_combines__()
            self.__parse_sparql_result_into_lexemes__()
        self.__iterate_lexemes__()

    def __fetch_lexemes_without_combines__(self):
        if not self.lang:
            raise MissingInformationError()
        random_offset = random.randint(0, 1000)
        logger.info(f"Random offset: {random_offset}")
        query_no_combines_no_derives_from = f"""
            SELECT ?lid #?lemma 
            WHERE {{
              ?lid dct:language wd:Q9027; # swedish
                 wikibase:lemma ?lemma.
              # hardcode finding lexemes with long lemmas for now
              filter(strlen(?lemma) >= 10) 
              minus {{?lid wdt:P5238 [].}} # combines
              minus {{?lid wdt:P5191 [].}} # derives from
        }}
        offset {random_offset}
        limit 10"""
        self.sparql_result = execute_sparql_query(
            query_no_combines_no_derives_from
        )

    def __parse_sparql_result_into_lexemes__(self):
        if not self.sparql_result:
            raise MissingInformationError()
        wbi = WikibaseIntegrator(
            login=Login(user=config.user_name, password=config.bot_password)
        )
        for result in self.sparql_result["results"]["bindings"]:
            # console.print(result)
            lexeme = wbi.lexeme.get(
                entity_id=result["lid"]["value"].replace(
                    "http://www.wikidata.org/entity/", ""
                )
            )
            lexeme_missing_combines = LexemeMissingCombines(
                lexeme=lexeme, lang=self.lang, wbi=wbi
            )
            self.lexemes_without_combines.append(lexeme_missing_combines)

    def __iterate_lexemes__(self):
        for lexeme in self.lexemes_without_combines:
            console.print(f"Working on {lexeme.localized_lemma}")
            lexeme.find_first_partword()
