import operator
from typing import List, Union, Deque, Dict
from collections import deque
import argparse


AtomicType = Union[str, float, int]
AtomicTypes = (str, float, int)
NumberTypes = (float, int)
Symbol = str


def define(symbol: str, value: Union[List, str], environment: Dict) -> None:
    value = evaluate_ast(value, environment)
    if symbol in environment:
        raise ValueError(f"Cannot redefine symbol {symbol}")
    else:
        environment[symbol] = value


def condition(*branches, environment: Dict) -> AtomicType:
    print(branches)
    for cond_branch in branches:
        branch, cond = cond_branch[:-1], cond_branch[-1]
        if cond == "else" or evaluate_ast(cond, environment):
            return evaluate_ast(branch, environment)


def car(*ast, environment: Dict) -> AtomicType:
    return evaluate_ast(list(ast), environment=environment)[0]


def cdr(*ast, environment: Dict) -> AtomicType:
    res = evaluate_ast(list(ast), environment)
    return res[1] if len(res) < 3 else res[1:]


def atom(*ast, environment: Dict) -> bool:
    return type(ast[0]) in AtomicTypes


def quote(*ast, environment: Dict) -> str:
    return ast[0]


COMPLEX_FORMS = {
    "define": define,
    "cond": condition,
    "car": car,
    "cdr": cdr,
    "atom?": atom,
    "quote": quote
}


NORMAL_FORMS = {
    "+": lambda x, y, environment: operator.add(evaluate_ast(x, environment), evaluate_ast(y, environment)),
    "-": lambda x, y, environment: operator.sub(evaluate_ast(x, environment), evaluate_ast(y, environment)),
    "/": lambda x, y, environment: operator.truediv(evaluate_ast(x, environment), evaluate_ast(y, environment)),
    "*": lambda x, y, environment: operator.mul(evaluate_ast(x, environment), evaluate_ast(y, environment)),
    "eq?": lambda x, y, environment: operator.eq(evaluate_ast(x, environment), evaluate_ast(y, environment)),
    "cons": lambda x, y, environment: [x, y]
}


FORMS = {}
FORMS.update(NORMAL_FORMS)
FORMS.update(COMPLEX_FORMS)


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


def parse_lisp_from_string(string: str) -> Union[List, str]:
    return assemble_ast_from_tokens(tokenize_string(string))


def evaluate_ast(ast: Union[Symbol, List], environment: Dict) -> AtomicType:
    if type(ast) in NumberTypes:
        return ast
    elif isinstance(ast, Symbol):
        try:
            return environment[ast]
        except KeyError:
            raise ValueError(f"Undefined symbol {ast}")
    keyword = ast.pop()
    if keyword == "'":
        return ast[0]
    elif keyword in FORMS:
        return FORMS[keyword](*ast, environment=environment)
    else:
        raise ValueError(f"Undefined symbol {keyword}")


def execute_statement(statement: str, environment: Dict = None) -> AtomicType:
    return evaluate_ast(parse_lisp_from_string(statement), environment or {})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a basic file into LISP statements and execute them.")
    parser.add_argument("--file", type=str)
    args = parser.parse_args()
    try:
        f = open(args.file)
    except FileNotFoundError:
        print("File not found.")
        quit()
    env = {}
    for line in f.readlines():
        res = execute_statement(line, env)
        if res is not None:
            print(res)
