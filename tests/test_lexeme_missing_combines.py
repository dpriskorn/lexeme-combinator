from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity

import config
from src.models.lexeme_missing_combines import LexemeMissingCombines


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
