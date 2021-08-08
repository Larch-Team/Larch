import unittest as test
import sys


sys.path.append('../app')
import lexer, plugins.Lexicon.classic as classic

class TestTokenize(test.TestCase):
    
    def setUp(self) -> None:
        self.lexer = lexer.BuiltLexer(classic.get_lexicon(), use_language=('propositional', 'uses negation'))

    def test_full_word(self):
        self.assertEqual(self.lexer.tokenize("p or q"), ["sentvar_p", "or_or", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p and q"), ["sentvar_p", "and_and", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p imp q"), ["sentvar_p", "imp_imp", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize('not p'), ['not_not','sentvar_p'])

    def test_full_symbol(self):
        self.assertEqual(self.lexer.tokenize("p v q"), ["sentvar_p", "or_v", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p | q"), ["sentvar_p", "or_|", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p ^ q"), ["sentvar_p", "and_^", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p & q"), ["sentvar_p", "and_&", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize("p -> q"), ["sentvar_p", "imp_->", "sentvar_q"])
        self.assertEqual(self.lexer.tokenize('~ p'), ['not_~','sentvar_p'])

    def test_bracket(self):
        self.assertEqual(self.lexer.tokenize("(p v q)"), ["(", "sentvar_p", "or_v", "sentvar_q", ")"])
        self.assertEqual(self.lexer.tokenize("(p | q)"), ['(',"sentvar_p", "or_|", "sentvar_q",')'])
        self.assertEqual(self.lexer.tokenize("(p ^ q)"), ['(',"sentvar_p", "and_^", "sentvar_q",')'])
        self.assertEqual(self.lexer.tokenize("(p & q)"), ['(',"sentvar_p", "and_&", "sentvar_q",')'])
        self.assertEqual(self.lexer.tokenize("(p -> q)"), ['(',"sentvar_p", "imp_->", "sentvar_q",')'])
        self.assertEqual(self.lexer.tokenize('(~ p)'), ['(','not_~','sentvar_p',')'])

    def test_string(self):
        self.assertEqual(self.lexer.tokenize("pies"), ["sentvar_pies"])
        self.assertEqual(self.lexer.tokenize("pies or kot"), ["sentvar_pies", "or_or", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies | kot"), ["sentvar_pies", "or_|", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies v kot"), ["sentvar_pies", "or_v", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies and kot"), ["sentvar_pies", "and_and", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies ^ kot"), ["sentvar_pies", "and_^", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies & kot"), ["sentvar_pies", "and_&", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies imp kot"), ["sentvar_pies", "imp_imp", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize("pies -> kot"), ["sentvar_pies", "imp_->", "sentvar_kot"])
        self.assertEqual(self.lexer.tokenize('not pies'), ['not_not','sentvar_pies'])


if __name__ == "__main__":
    test.main()