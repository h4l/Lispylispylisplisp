import re

def tokenise(text):
    token = ""
    for char in text:
        if re.match("\s|\(|\)", char):
            if token:
                yield token
                token = ""
            if char in "()":
                yield char
        else:
            token += char
    if token:
        yield token

def cons(a, b):
    return (a, b)

def car(x):
    if atom(x):
        raise RuntimeError("car() called on atom: %s" % x)
    head, _ = x
    return head

def cdr(x):
    if atom(x):
        raise RuntimeError("cdr() called on atom: %s" % x)
    _, tail = x
    return tail

def atom(x):
    if x == () or isinstance(x, basestring):
        return "t"
    return ()

def eq(x, y):
    if (isinstance(x, basestring) or x == ()) and x == y:
        return "t"
    return ()

def read_list(tokens):
    token = tokens.next()
    if token == ")":
        return ()
    elif token == "(":
        return cons(read_list(tokens), read_list(tokens))
    else:
        return cons(token, read_list(tokens))

def read(src):
    tokens = tokenise(src) if isinstance(src, basestring) else iter(src)
    while True:
        try:
            token = tokens.next()
        except StopIteration:
            return

        if token == ")":
            raise SyntaxError
        elif token == "(":
            try:
                yield read_list(tokens)
            except StopIteration:
                raise SyntaxError("Unexpected end of input")
        else:
            yield token

def lst(exprs):
    try:
        i = iter(exprs)
        return cons(i.next(), lst(i))
    except StopIteration:
        return ()

def read_postprocess(src, *postprocessors):
    exprs = lst(read(src))
    for pp in postprocessors:
        exprs = pp(exprs)
    return iterate(exprs)

def backtick_filter(exprs):
    expecting_expr = False
    try:
        while True:
            e = exprs.next()
            if atom(e) and not eq((), e) and e == "`":
                expecting_expr = True
                yield car(expand_backticks(lst([e, exprs.next()])))
                expecting_expr = False
            else:
                yield expand_backticks(e)
    except StopIteration:
        if expecting_expr:
            yield ()
        pass

def expand_backticks(expr):
    if eq((), expr):
        return ()
    if atom(expr):
        if expr.startswith("`"):
            assert len(expr) > 1, "orphaned backtick"
            return cons("quote", cons(expand_backticks(expr[1:]), ()))
        return expr
    head, tail = car(expr), cdr(expr)
    if atom(head) and head == "`":
        th, tt = car(tail), cdr(tail)
        return cons(cons("quote", cons(expand_backticks(th), ())), expand_backticks(tt))
    return cons(expand_backticks(head), expand_backticks(tail))


def iterate(expr):
    while not eq(expr, ()):
        yield car(expr)
        expr = cdr(expr)

def to_string(expr):
    if atom(expr):
        return str(expr)
    return "(" + " ".join(to_string(e) for e in iterate(expr)) + ")"

def caar(lst): return car(car(lst))
def caadr(lst): return car(car(cdr(lst)))
def cadar(lst): return car(cdr(car(lst)))
def cadr(lst): return car(cdr(lst))
def caddr(lst): return car(cdr(cdr(lst)))
def cadadr(lst): return car(cdr(car(cdr(lst))))

def lookup(atom, env):
    if eq(env, ()):
        return ()
    elif eq(atom, caar(env)):
        return cadar(env)
    return lookup(atom, cdr(env))

def cond(cases, env):
    if eq(cases, ()):
        return ()
    if eq(evaluate(caar(cases), env), "t"):
        return evaluate(cadar(cases), env)
    return cond(cdr(cases), env)

def evaluate(expr, env):
    if atom(expr):
        return lookup(expr, env)
    elif atom(car(expr)):
        if car(expr) == "quote": return cadr(expr)
        elif car(expr) == "atom": return atom(evaluate(cadr(expr), env))
        elif car(expr) == "cons": return cons(
                evaluate(cadr(expr), env),
                evaluate(caddr(expr), env))
        elif car(expr) == "car": return car(evaluate(cadr(expr), env))
        elif car(expr) == "cdr": return cdr(evaluate(cadr(expr), env))
        elif car(expr) == "eq": return eq(
                evaluate(cadr(expr), env),
                evaluate(caddr(expr), env))
        elif car(expr) == "cond": return cond(cdr(expr), env)
        else: return evaluate(cons(evaluate(car(expr), env), cdr(expr)), env)
    elif atom(caar(expr)):
        if eq(caar(expr), "lambda"):
            # TODO: zip arg atoms with eval'd argument params, then eval body with arg pairs added to env
            arg_atoms = cadar(expr)
            arg_exprs = cdr(expr)
            lambda_body = car(cdr(cdr(car(expr))))
            return evaluate(lambda_body, prepend(
                    arglist(arg_atoms, arg_exprs, env), env))
        if eq(caar(expr), "label"):
            name = cadar(expr)
            value = car(expr)
            subexpr = cadr(expr)
            return evaluate(subexpr, cons(cons(name, cons(value, ())), env))
    raise ValueError("Unable to evaluate expr: %s" % to_string(expr))

def arglist(atoms, exprs, env):
    if eq(atoms, ()) or eq(exprs, ()):
        return ()
    ah, at, eh, et = car(atoms), cdr(atoms), car(exprs), cdr(exprs)
    return cons(cons(ah, cons(evaluate(eh, env), ())), arglist(at, et, env))

def prepend(items, dest):
    if eq(items, ()):
        return dest
    h, t = car(items), cdr(items)
    return cons(h, prepend(t, dest))

class PromptTokeniser(object):
    def __init__(self):
        import sys
        self.expression_complete = True
        self.normal_prompt = ">>> "
        self.continuation_prompt = "... "
        self.input = sys.stdin
        self.output = sys.stdout

    def on_expression_completed(self):
        self.expression_complete = True

    def get_prompt(self):
        if self.expression_complete:
            return self.normal_prompt
        return self.continuation_prompt

    def tokens(self):
        while True:
            self.output.write(self.get_prompt())
            line = self.input.readline()
            for token in tokenise(line):
                self.expression_complete = False
                yield token

def repl(filters=[backtick_filter]):
    tokeniser = PromptTokeniser()
    expressions = reduce(lambda stream, f: f(stream),
            filters, read(tokeniser.tokens()))
    for expression in expressions:
        tokeniser.on_expression_completed()
        print to_string(evaluate(expression, ()))

if __name__ == "__main__":
    print "Lispylispylisplisp!! v0.0.0.0.0.1"
    repl()
