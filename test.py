import unittest
from lisp import *

class LispTest(unittest.TestCase):

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

    def testToString(self):
        self.assertEqual(to_string(read("abc").next()), "abc")
        self.assertEqual(to_string(read("(abc)").next()), "(abc)")
        self.assertEqual(to_string(read("(abc def)").next()), "(abc def)")
        self.assertEqual(to_string(read("(abc (def ()))").next()), "(abc (def ()))")

if __name__ == "__main__":
    unittest.main()
