import logging

user_name = ""
bot_password = ""
user_name_only = ""
user_agent = f"lexeme-combinator, see https://github.com/dpriskorn/lexeme-combinator User:{user_name_only}"

loglevel = logging.ERROR

# Default values
language_code = "sv"

# we default to wikidata property values
combines_property = "P5238"
series_ordinal_property = "P1545"
upload_to_wikidata = True
wikibase_lexeme_base_uri = "https://www.wikidata.org/wiki/Lexeme:"
ordia_url = "https://ordia.toolforge.org/"
