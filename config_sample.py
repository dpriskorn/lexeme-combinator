import logging

user_name = ""
bot_password = ""
user_name_only = ""
user_agent = f"lexeme-combinator, see https://github.com/dpriskorn/lexeme-combinator User:{user_name_only}"

loglevel = logging.ERROR

# Default values
number_of_lexemes_to_fetch = 10
minimum_lemma_characters = 10
# language_code = "sv"
# language_qid = "Q9027"  # swedish
language_code = "da"
language_qid = "Q9035"  # danish
# language_code = "nb"
# language_qid = "Q25167"  # bokmål

# we default to wikidata property values
combines_property = "P5238"
series_ordinal_property = "P1545"
upload_to_wikidata = True
wikibase_lexeme_base_uri = "https://www.wikidata.org/wiki/Lexeme:"
ordia_url = "https://ordia.toolforge.org/"
