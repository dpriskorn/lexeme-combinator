from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import LexemeEntity

from src.models.combination import Combination


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
