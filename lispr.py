import operator
from typing import List, Union, Deque, Optional, Dict
from collections import deque
OPEN_PAREN = "("
CLOS_PAREN = ")"
NEWLINE_CHAR = "\n"
SPAC_CHAR = " "


def define(ast: Deque[str], environment: Dict) -> None:
    try:
        symbol = ast[0]
        value = evaluate_ast(ast[1], environment)
    except IndexError:
        raise SyntaxError("Define lists must be two elements long.")
    if symbol in environment:
        raise ValueError(f"Cannot redefine symbol {symbol}")
    else:
        environment[symbol] = value


# def dlambda(parameters: List[Any], )
COMPLEX_FORMS = {
    "define": define
}

NORMAL_FORMS = {
    "+": lambda x, y, environment: operator.add(x, y),
    "-": lambda x, y, environment: operator.sub(x, y),
    "/": lambda x, y, environment: operator.truediv(x, y),
    "*": lambda x, y, environment: operator.mul(x, y),
    "eq?": lambda x, y, environment: operator.eq(x, y),
    "cons": lambda x, y, environment: [x, y]
}

SPECIAL_FORMS = {
    "quote": lambda x, environment: str(x),
    "car": lambda x, environment: x[0],
    "cdr": lambda x, environment: x[1] if len(x) < 3 else x[1:],
    "atom?": lambda x, environment: type(x) in AtomicTypes
}

FORMS = {}
FORMS.update(NORMAL_FORMS)
FORMS.update(SPECIAL_FORMS)
FORMS.update(COMPLEX_FORMS)

AtomicTypes = (str, float, int)
NumberTypes = (float, int)
Symbol = str


def tokenize_string(string: str) -> Deque[str]:
    return deque(string.replace("(", " ( ").replace(")", " ) ").split())


def assemble_ast_from_tokens(tokens: Deque[str]) -> Union[Symbol, List]:
    if len(tokens) == 0:
        raise ValueError("Unexpected EOF")
    elif tokens[0] == "(":
        tokens.popleft()
        res = []
        while tokens[0] != ")":
            res.append(assemble_ast_from_tokens(tokens))
        tokens.popleft()
        return res
    elif tokens[0] == "(":
        raise ValueError("Unexpected closure")
    else:
        if tokens[0].isdigit():
            res = int(tokens[0])
        elif tokens[0].isdecimal():
            res = float(tokens[0])
        else:
            res = tokens[0]
        tokens.popleft()
        return res


def new_environment(existing: Optional[Dict] = None) -> Dict:
    return existing if existing else {}


def evaluate_ast(ast: Union[Symbol, List], environment: Dict) -> Union[float, int, Symbol]:
    print("ast: " + str(ast))
    if type(ast) in NumberTypes:
        return ast
    elif type(ast) == Symbol:
        try:
            return environment[ast]
        except KeyError:
            from pdb import set_trace
            set_trace()
            raise ValueError(f"Undefined symbol {ast}")
    elif len(ast) == 0:
        raise ValueError("Unexpectedly empty syntax tree :(")
    keyword = ast.pop()
    quoted = ast[-1] == "'"
    if quoted:
        ast.pop()
        ast = ast[0]
    if keyword in NORMAL_FORMS or keyword in SPECIAL_FORMS and not quoted:
        print(keyword, FORMS[keyword](*(evaluate_ast(token, environment) for token in ast), environment=environment))
        return FORMS[keyword](*(evaluate_ast(token, environment) for token in ast), environment=environment)
    elif keyword in COMPLEX_FORMS or (quoted and keyword in FORMS):
        return FORMS[keyword](ast, environment)
    else:
        from pdb import set_trace
        set_trace()
        raise ValueError(f"Undefined symbol {keyword}")
