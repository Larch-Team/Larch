import unittest as test
import sys

sys.path.append('../app')
from sentence import Sentence
import lexer, plugins.Lexicon.classic as classic

class TestGenerate(test.TestCase):
    
    def setUp(self) -> None:
        self.lexer = lexer.BuiltLexer(classic.get_lexicon(), use_language=('propositional', 'uses negation'))
        
    def test_simple(self) -> None:
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'or'), 'or_or')
        
    def test_new(self) -> None:
        n = self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'sentvar')
        self.assertTrue(n.startswith('sentvar_'))
        self.assertNotIn(n, ['sentvar_p', 'sentvar_q'])
        
if __name__ == "__main__":
    test.main()