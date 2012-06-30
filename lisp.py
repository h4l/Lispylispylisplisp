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
