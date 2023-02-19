import logging

from wikibaseintegrator.wbi_config import config

from src.console import console
from src.models.combinator import Combinator
import config as myconfig

config["USER_AGENT"] = "lexeme-combinator"
logging.basicConfig(level=myconfig.loglevel)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    console.print("Note: currently we only support lexemes "
                  "combined by exactly two other lexemes. "
                  "We don't currently display senses, so don't match "
                  "if you are not sure based on the presented information."
                  "We don't support creating new lexemes so "
                  f"if you are missing a lexeme, go to {myconfig.ordia_url}.")
    comb = Combinator(lang=myconfig.language_code)
    comb.start()
    # # fetch lexemes without combines
    # comb.fetch_lexemes_without_combines()
    # console.print(comb.sparql_result)
    # comb.parse_sparql_result_into_lexemes()
    # # query for words they could consist of aka partwords
    # comb.iterate_lexemes()
    # # find the longest partword that match the start of the lemma
    # # print
