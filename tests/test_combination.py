from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity

import config
from src.models.combination import Combination
from src.models.lexeme_missing_combines import LexemeMissingCombines


class TestCombination:
    test_danish_lexeme = LexemeEntity().get(
        entity_id="L676834"
    )  # specialist missing a danish gloss
    test_swedish_lexeme = LexemeEntity().get(entity_id="L33694")  # konstutbildning
    wbi = WikibaseIntegrator()

    def test_claims(self):
        pass

    def test_table(self):
        pass

    def test_localized_lemma(self):
        pass

    def test_localized_gloss(self):
        pass

    def test_localized_glosses_from_all_senses_da(self):
        config.language_code = "da"
        c = Combination(lexeme=self.test_danish_lexeme, parts=[self.test_danish_lexeme])
        assert (
            c.localized_glosses_from_all_senses(lexeme=self.test_danish_lexeme)
            == "No gloss for 'da' language for this sense, please add one"
        )

    def test_localized_glosses_from_all_senses(self):
        pass

    def test_localized_lexical_category(self):
        pass

    def test_number_of_parts(self):
        pass

    def test_lexeme_uri(self):
        pass

    def test_interfix_s_cover(self):
        config.language_code = "sv"
        swedish_interfix_s_lexeme = LexemeEntity().get(
            entity_id="L60596"
        )  # kärleksgåva
        first_part = LexemeEntity().get(
            entity_id="L33258"
        )  # kärlek
        last_part = LexemeEntity().get(
            entity_id="L243182"
        )  # gåva
        lmc = LexemeMissingCombines(lexeme=swedish_interfix_s_lexeme, wbi=self.wbi)
        c = Combination(
            lexeme=swedish_interfix_s_lexeme,
            parts=[first_part, lmc.__get_interfix_lexeme_if_possible__(), last_part]
        )
        assert c.the_parts_cover_the_whole_lemma is True
