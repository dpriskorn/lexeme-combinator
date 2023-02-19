from typing import List, Dict, Any

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from src.console import console
from src.models.lexeme_missing_combines import LexemeMissingCombines
from src.exceptions import MissingInformationError


class Combinator(BaseModel):
    """This looks up and holds all the lexemes we work on"""

    lang: str = ""
    # lexical_category: str = ""
    lexemes_without_combines: List[LexemeMissingCombines] = []
    query_no_combines_no_derives_from = """
        SELECT ?lid #?lemma 
        WHERE {
          ?lid dct:language wd:Q9027; # swedish
             wikibase:lemma ?lemma.
          # hardcode finding lexemes with long lemmas for now
          filter(strlen(?lemma) >= 10) 
          minus {?lid wdt:P5238 [].} # combines
          minus {?lid wdt:P5191 [].} # derives from
    }
    limit 1"""
    sparql_result: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    def fetch_lexemes_without_combines(self):
        if not self.lang:
            raise MissingInformationError()
        self.sparql_result = execute_sparql_query(
            self.query_no_combines_no_derives_from
        )

    def parse_sparql_result_into_lexemes(self):
        if not self.sparql_result:
            raise MissingInformationError()
        wbi = WikibaseIntegrator()
        for result in self.sparql_result["results"]["bindings"]:
            console.print(result)
            lexeme = wbi.lexeme.get(
                entity_id=result["lid"]["value"].replace(
                    "http://www.wikidata.org/entity/", ""
                )
            )
            lexeme_missing_combines = LexemeMissingCombines(
                lexeme=lexeme, lang=self.lang
            )
            self.lexemes_without_combines.append(lexeme_missing_combines)

    def iterate_lexemes(self):
        for lexeme in self.lexemes_without_combines:
            lexeme.find_first_partword()
