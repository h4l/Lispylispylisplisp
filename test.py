import unittest
from lisp import *

def lst(*exprs):
    l = ()
    for expr in reversed(exprs):
        l = cons(expr, l)
    return l

class LispTest(unittest.TestCase):

    def testLst(self):
        self.assertEqual(lst(), ())
        self.assertEqual(lst("foo"), ("foo", ()))
        self.assertEqual(lst("foo", "bar"), ("foo", ("bar", ())))

    def testTokenise(self):
        tests = [
            ("", []),
            ("abc", ["abc"]),
            ("abc def", ["abc", "def"]),
            ("(abc)", ["(", "abc", ")"]),
            ("(abc def)", ["(", "abc", "def", ")"]),
            ("(abc def ())", ["(", "abc", "def", "(", ")", ")"]),
            ("(abc def (zzz))", ["(", "abc", "def", "(", "zzz", ")", ")"]),
            ("""(
            abc
            )""", ["(", "abc", ")"]),
        ]
        for text, expected_tokens in tests:
            tokens = list(tokenise(text))
            self.assertEqual(tokens, expected_tokens)

    def testCons(self):
        self.assertEqual(cons("a", "b"), ("a", "b"))
        self.assertEqual(cons("a", ()), ("a", ()))
        self.assertEqual(cons("a", ("b", ())), ("a", ("b", ())))

    def testCar(self):
        self.assertEqual(car(("a", ())), "a")
        self.assertEqual(car(("a", ("b", ()))), "a")

    def testCdr(self):
        self.assertEqual(cdr(("a", ("b", ()))), ("b", ()))
        self.assertEqual(cdr(("a", ())), ())

    def testAtom(self):
        self.assertEqual(atom("xx"), "t")
        self.assertEqual(atom(("foo", ())), ())
        self.assertEqual(atom(()), "t")

    def testEq(self):
        self.assertEqual(eq("abc", "abc"), "t")
        self.assertEqual(eq((), ()), "t")
        self.assertEqual(eq("abc", "abcd"), ())
        self.assertEqual(eq(("foo", ()), ("foo", ())), (),
                "eq does not descend into lists")

    def testRead(self):
        self.assertEqual(read("abc").next(),
                "abc")
        self.assertEqual(read("()").next(),
                ())
        self.assertEqual(read("(abc)").next(),
                cons("abc", ()))
        self.assertEqual(read("(abc def)").next(),
                cons("abc", cons("def", ())))
        self.assertEqual(read(tokenise(
                "(abc (def ()))")).next(),
                ("abc", (("def", ((), ())), ()))
        )
        self.assertEqual(list(read("abc def")),
                ["abc", "def"])

#        self.assertEqual(read("`abc").next(),
#                lst("quote", "abc"))
#        self.assertEqual(read("(`abc def)").next(),
#                lst(lst("quote", "abc"), "def"))

    def testToString(self):
        self.assertEqual(to_string(read("abc").next()), "abc")
        self.assertEqual(to_string(read("(abc)").next()), "(abc)")
        self.assertEqual(to_string(read("(abc def)").next()), "(abc def)")
        self.assertEqual(to_string(read("(abc (def ()))").next()), "(abc (def ()))")

    def testLookup(self):
        self.assertEqual(lookup((), ()), ())
        self.assertEqual(lookup((), lst(
                    lst("a", "b")
                )), ())
        self.assertEqual(lookup("a", lst(
                    lst("a", "b")
                )), "b")
        self.assertEqual(lookup("c", lst(
                    lst("a", "foo"),
                    lst("b", "bar"),
                    lst("c", lst("b", "c"))
                )), lst("b", "c"))
        self.assertEqual(lookup("z", lst(
                    lst("a", "foo"),
                    lst("z", "bar"),
                    lst("z", lst("b" "c"))
                )), "bar")

    def testEvaluate(self):
        def e(s, env=()):
            return evaluate(read_postprocess(s, expand_backticks).next(), env)

        self.assertEqual(e("abc"), ())
        self.assertEqual(e("abc", lst(lst("abc", "def"))), "def")

        self.assertEqual(e("(quote abc)"), "abc")
        self.assertEqual(e("(quote (abc def))"), lst("abc", "def"))

        self.assertEqual(e("(atom (quote (abc def)))"), ())
        self.assertEqual(e("(atom (quote abc))"), "t")

        self.assertEqual(e("(cons (quote ()) (quote ()))"),
                lst(()))
        self.assertEqual(e("(cons (quote abc) (quote ()))"),
                lst("abc"))
        self.assertEqual(e("(cons (quote abc) (quote def))"),
                ("abc", "def"))

        self.assertEqual(e("(car (quote (a b c)))"), "a")
        self.assertEqual(e("(car (quote (x)))"), "x")

        self.assertEqual(e("(cdr (quote (a b c)))"), lst("b", "c"))
        self.assertEqual(e("(cdr (quote (x)))"), ())

        self.assertEqual(e("(eq (quote ()) (quote ()))"), "t")
        self.assertEqual(e("(eq (quote abc) (quote abc))"), "t")
        self.assertEqual(e("(eq (quote abc) (quote def))"), ())
        self.assertEqual(e("(eq (quote (abc)) (quote (abc)))"), ())

        self.assertEqual(e("(cond ((quote t) (quote yay)))"), "yay")
        self.assertEqual(e("""(cond
                                  ((atom (quote (abc))) (quote abc))
                                  ((quote t) (quote yay)))"""), "yay")


        self.assertEqual(e("""((lambda () (quote abc)))"""), "abc")
        self.assertEqual(e("""((lambda () (quote abc)))"""), "abc")
        self.assertEqual(e("""((lambda (x) x)
                               (quote a))"""), "a")
        self.assertEqual(e("""((lambda (x y) (cons x y))
                               (quote a) (quote (b c)))"""), lst("a", "b", "c"))
        self.assertEqual(e("(%s `t `t)" % self.lambda_and), "t")
        self.assertEqual(e("(%s `t `foo)" % self.lambda_and), ())
        self.assertEqual(e("(%s `bar `t)" % self.lambda_and), ())
        self.assertEqual(e("(%s `foo `bar)" % self.lambda_and), ())
        self.assertEqual(e("(%s `() `())" % self.lambda_and), ())

        self.assertEqual(e("((label foo (quote bar)) foo)"), read("(label foo (quote bar))").next())
        self.assertEqual(e("""((label foo (lambda (x y z) z))
                               (quote a) (quote b) (quote c))"""), "a")
    lambda_and = """
        (lambda (x y) (cond
          (x (cond
            (y `t)
            (`t `())))
          (`t `())))
        """

if __name__ == "__main__":
    unittest.main()
