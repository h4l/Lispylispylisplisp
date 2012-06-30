def tokenise(text):
    token = ""
    for char in text:
        if char in "() ":
            if token:
                yield token
                token = ""
            if char != " ":
                yield char
        else:
            token += char
    if token:
        yield token

def cons(a, b):
    return (a, b)

def car(x):
    if not len(x):
        return ()
    head, _ = x
    return head

def cdr(x):
    if not len(x):
        return ()
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
    token = tokens.next()
    if token == ")":
        raise SyntaxError
    elif token == "(":
        try:
            yield read_list(tokens)
        except StopIteration:
            raise SyntaxError("Unexpected end of input")
    else:
        yield token

def iterate(expr):
    while not eq(expr, ()):
        yield car(expr)
        expr = cdr(expr)

def to_string(expr):
    if atom(expr):
        return str(expr)
    return "(" + " ".join(to_string(e) for e in iterate(expr)) + ")"
