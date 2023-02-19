import logging

from wikibaseintegrator.wbi_config import config

from src.models.combinator import Combinator
from src.console import console

config["USER_AGENT"] = "lexeme-combinator"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    comb = Combinator(lang="sv")
    # fetch lexemes without combines
    comb.fetch_lexemes_without_combines()
    console.print(comb.sparql_result)
    comb.parse_sparql_result_into_lexemes()
    # query for words they could consist of aka partwords
    comb.iterate_lexemes()
    # find the longest partword that match the start of the lemma
    # print
