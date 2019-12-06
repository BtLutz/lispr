from unittest import TestCase
import lispr


class TestLispr(TestCase):
    def setUp(self):
        self.environment = lispr.standard_env()
        self.default_tokens = ["(", "1", "2", "+", ")"]
        self.default_ast = [1, 2, "+"]
        self.nested_tokens = ["(", "(", "1", "2", "+", ")", "1", "+", ")"]
        self.quote_tokens = ["(", "(", "1", "2", ")", "'", "quote", ")"]
        self.quote_ast = [[1, 2], "'", "quote"]
        self.nested_ast = [[1, 2, "+"], 1, "+"]
        self.define_ast = ["a", 1, "define"]
        self.eq_false_ast = [1, 2, "eq?"]
        self.eq_true_ast = [1, 1, "eq?"]
        self.eq_nested_true_ast = [[1, 2, "+"], 3, "eq?"]
        self.cons_ast = [1, 2, "cons"]
        self.car_ast = [[1, 2], "'", "car"]
        self.cdr_ast = [[1, 2], "'", "cdr"]
        self.cdr_list_ast = [[1, 2, 3], "'", "cdr"]
        self.atom_true_ast = [1, "atom?"]
        self.atom_false_ast = [[1, 2], "'", "atom?"]
        self.cond = [["one", "'", [1, 2, "eq?"]], ["two", "'", [1, 1, "eq?"]], "cond"]
        self.cond_else = [["one", "'", [1, 2, "eq?"]], ["two", "'", [1, 3, "eq?"]], ["three", "'", "else"], "cond"]
        self.cond_list_exp = [[[1, 1], "'", [1, 1, "eq?"]], ["two", "'", [1, 2, "eq?"]], "cond"]
        self.lambda_exp = ["square", ["x", ["x", "x", "*"], "lambda"], "define"]
        self.default_lambda = [5, "square"]

    def test_tokenize_default(self):
        res = lispr.tokenize("(1 2 +)")
        self.assertEqual(self.default_tokens, res)

    def test_tokenize_nested(self):
        res = lispr.tokenize("((1 2 +) 1 +)")
        self.assertEqual(self.nested_tokens, res)

    def test_tokenize_quote(self):
        res = lispr.tokenize("((1 2)' quote)")
        self.assertEqual(self.quote_tokens, res)

    def test_tokenize_quote_atom(self):
        res = lispr.tokenize("(a' atom?)")
        self.assertEqual(["(", "a", "'", "atom?", ")"], res)

    def test_read_from_tokens_default(self):
        res = lispr.read_from_tokens(self.default_tokens)
        self.assertEqual(self.default_ast, res)

    def test_read_from_tokens_nested(self):
        res = lispr.read_from_tokens(self.nested_tokens)
        self.assertEqual(self.nested_ast, res)

    def test_read_from_tokens_quote(self):
        res = lispr.read_from_tokens(self.quote_tokens)
        self.assertEqual(self.quote_ast, res)

    def test_eval_define(self):
        lispr.eval(self.define_ast, self.environment)
        self.assertIn("a", self.environment)

    def test_evaluate_true_ast_eq(self):
        res = lispr.eval(self.eq_true_ast, self.environment)
        self.assertTrue(res)

    def test_evaluate_false_ast_eq(self):
        res = lispr.eval(self.eq_false_ast, self.environment)
        self.assertFalse(res)

    def test_evaluate_nested_true_ast(self):
        res = lispr.eval(self.eq_nested_true_ast, self.environment)
        self.assertTrue(res)

    def test_evaluate_cons(self):
        res = lispr.eval(self.cons_ast, self.environment)
        self.assertEqual([1, 2], res)

    def test_evaluate_car(self):
        res = lispr.eval(self.car_ast, self.environment)
        self.assertEqual(1, res)

    def test_evaluate_cdr(self):
        res = lispr.eval(self.cdr_ast, self.environment)
        self.assertEqual(2, res)

    def test_evaluate_cdr_list(self):
        res = lispr.eval(self.cdr_list_ast, self.environment)
        self.assertEqual([2, 3], res)

    def test_atom_true(self):
        res = lispr.eval(self.atom_true_ast, self.environment)
        self.assertTrue(res)

    def test_atom_false(self):
        res = lispr.eval(self.atom_false_ast, self.environment)
        self.assertFalse(res)

    def test_eq_mul_div(self):
        res = lispr.eval([[5, [5, 5, "/"], "*"], 5, "eq?"], self.environment)
        self.assertTrue(res)

    def test_define_mul(self):
        lispr.eval(self.define_ast, self.environment)
        res = lispr.eval(["a", 2, "*"], self.environment)
        self.assertEqual(2, res)

    def test_cond(self):
        res = lispr.eval(self.cond, self.environment)
        self.assertEqual("two", res)

    def test_cond_else(self):
        res = lispr.eval(self.cond_else, self.environment)
        self.assertEqual("three", res)

    def test_cond_list_exp(self):
        res = lispr.eval(self.cond_list_exp, self.environment)
        self.assertEqual("(1 1)", res)

    def test_lambda_default(self):
        lispr.eval(self.lambda_exp, self.environment)
        res = lispr.eval(self.default_lambda, self.environment)
        self.assertEqual(25, res)
