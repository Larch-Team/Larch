import unittest as test
import sys

sys.path.append('../app')
from sentence import Sentence
import lexer, plugins.Lexicon.classic as classic

class TestGenerate(test.TestCase):
    
    def setUp(self) -> None:
        self.lexer = lexer.BuiltLexer(classic.get_lexicon(), use_language=('propositional', 'uses negation'))
        
    def test_simple(self) -> None:
        self.assertEqual(self.lexer.generate(Sentence(['not_not','sentvar_p'], None), 'not'), 'not_not')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'or'), 'or_or')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'and_and', 'sentvar_q'], None), 'and'), 'and_and')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'imp_imp', 'sentvar_q'], None), 'imp'), 'imp_imp')
        
    def test_simple2(self) -> None:
        self.assertEqual(self.lexer.generate(Sentence(['not_~','sentvar_p'], None), 'not'), 'not_~')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'or_v', 'sentvar_q'], None), 'or'), 'or_v')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'or_|', 'sentvar_q'], None), 'or'), 'or_|')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'and_^', 'sentvar_q'], None), 'and'), 'and_^')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'and_&', 'sentvar_q'], None), 'and'), 'and_&')
        self.assertEqual(self.lexer.generate(Sentence(['sentvar_p', 'imp_->', 'sentvar_q'], None), 'imp'), 'imp_->') 
    
    def test_new(self) -> None:
        n = self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'sentvar')
        self.assertTrue(n.startswith('sentvar_'))
        self.assertNotIn(n, ['sentvar_p', 'sentvar_q'])
        n1 = self.lexer.generate(Sentence(['sentvar_pies', 'or_or', 'sentvar_quack'], None), 'sentvar')
        self.assertTrue(n1.startswith('sentvar_'))
        self.assertNotIn(n1, ['sentvar_pies', 'sentvar_quack'])
        
    def test_new2(self) -> None:
        n_imp = self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'imp')
        self.assertIn(n_imp, ['imp_imp', 'imp_->'])

        n_or = self.lexer.generate(Sentence(['sentvar_p', 'and_and', 'sentvar_q'], None), 'or')
        self.assertIn(n_or, ['or_or', 'or_|', 'or_v', 'or_lub'])

        n_and = self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'and')
        self.assertIn(n_and, ['and_and', 'and_&', 'and_^', 'and_oraz'])

        n_not = self.lexer.generate(Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None), 'not')
        self.assertIn(n_not, ['not_not', 'not_~', 'not_!'])
    
if __name__ == "__main__":
    test.main()