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
        ]
        for text, expected_tokens in tests:
            tokens = list(tokenise(text))
            self.assertEqual(tokens, expected_tokens, "input: \"%s\"" % text)

    def testCons(self):
        self.assertEqual(cons("a", "b"), ("a", "b"))
        self.assertEqual(cons("a", ()), ("a", ()))
        self.assertEqual(cons("a", ("b", ())), ("a", ("b", ())))

    def testCar(self):
        self.assertEqual(car(("a", ())), "a")
        self.assertEqual(car(("a", ("b", ()))), "a")
        self.assertEqual(car(()), ())

    def testCdr(self):
        self.assertEqual(cdr(()), ())
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
            return evaluate(read(s).next(), env=env)

        self.assertEqual(e("abc"), ())
        self.assertEqual(e("abc", lst(lst("abc", "def"))), "def")
        self.assertEqual(e("(quote abc)"), "abc")
if __name__ == "__main__":
    unittest.main()
