import logging

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity
from wikibaseintegrator.wbi_config import config as wbi_config

import config
from src.models.lexeme_missing_combines import LexemeMissingCombines

wbi_config["USER_AGENT"] = "lexeme-combinator"

logging.basicConfig(level=config.loglevel)


class TestLexemeMissingCombines:
    test_danish_lexeme = LexemeEntity().get(entity_id="L349060")  # ødipuskompleks
    test_swedish_lexeme = LexemeEntity().get(entity_id="L33694")  # konstutbildning
    wbi = WikibaseIntegrator()

    def test_localized_lemma_da(self):
        config.language_code = "da"
        config.language_qid = "Q9035"  # danish
        lmc = LexemeMissingCombines(lexeme=self.test_danish_lexeme, wbi=self.wbi)
        assert lmc.localized_lemma == "ødipuskompleks"

    def test_localized_lemma_sv(self):
        config.language_code = "sv"
        config.language_qid = "Q9027"  # danish
        lmc = LexemeMissingCombines(lexeme=self.test_swedish_lexeme, wbi=self.wbi)
        assert lmc.localized_lemma == "konstutbildning"

    # def test_localized_lexeme_category(self):
    #     assert False
    #
    # def test_lexeme_uri(self):
    #     assert False
    #
    # def test_find_first_partword(self):
    #     assert False

    # def test_interfix_s(self):
    #     swedish_interfix_s_lexeme = LexemeEntity().get(
    #         entity_id="L60596"
    #     )  # kärleksgåva
    #     lmc = LexemeMissingCombines(lexeme=swedish_interfix_s_lexeme, wbi=self.wbi)
    #     lmc.find_first_partword()
    #     first_part = LexemeEntity().get(
    #         entity_id="L33258"
    #     )  # kärlek
    #     lmc.__check_if_two_combine_candidates_with_s_in_between_cover_the_whole_lemma__(
    #         first_part=first_part
    #     )

    def test__get_interfix_lexeme_if_possible__(self):
        swedish_interfix_s_lexeme = LexemeEntity().get(
            entity_id="L60596"
        )  # kärleksgåva
        lmc = LexemeMissingCombines(lexeme=swedish_interfix_s_lexeme, wbi=self.wbi)
        assert isinstance(lmc.__get_interfix_lexeme_if_possible__(), LexemeEntity)
