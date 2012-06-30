import unittest
import lisp

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
            tokens = list(lisp.tokenise(text))
            self.assertEqual(tokens, expected_tokens, "input: \"%s\"" % text)

    def testCons(self):
        self.assertEqual(lisp.cons("a", "b"), ("a", "b"))
        self.assertEqual(lisp.cons("a", ()), ("a", ()))
        self.assertEqual(lisp.cons("a", ("b", ())), ("a", ("b", ())))

    def testCar(self):
        self.assertEqual(lisp.car(("a", ())), "a")
        self.assertEqual(lisp.car(("a", ("b", ()))), "a")
        self.assertEqual(lisp.car(()), ())

    def testCdr(self):
        self.assertEqual(lisp.cdr(()), ())
        self.assertEqual(lisp.cdr(("a", ("b", ()))), ("b", ()))
        self.assertEqual(lisp.cdr(("a", ())), ())

    def testAtom(self):
        self.assertEqual(lisp.atom("xx"), "t")
        self.assertEqual(lisp.atom(("foo", ())), ())
        self.assertEqual(lisp.atom(()), "t")

    def testEq(self):
        self.assertEqual(lisp.eq("abc", "abc"), "t")
        self.assertEqual(lisp.eq((), ()), "t")
        self.assertEqual(lisp.eq("abc", "abcd"), ())
        self.assertEqual(lisp.eq(("foo", ()), ("foo", ())), (),
                "eq does not descend into lists")

if __name__ == "__main__":
    unittest.main()
