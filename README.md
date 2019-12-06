# Introduction
This project is designed to act as a LISP interpreter. Now, I know by this point that you're
familiar with LISP.

But hold up!
Have you ever wanted to do *postfix* LISP? Do I have a surprise for you!

# Installation
There are a whopping __zero__ dependencies for this project. That's right: the
only modules I use in this project are those provided by the Python Standard Library.
Therefore, as long as you have a working Python 3 installation, you can use this project.
Otherwise, navigate over to http://python.org to find yourself a distribution. After that,
simply clone the repository and `cd` into the directory.
```
git clone https://github.com/BtLutz/lispr.git
cd lispr
```

# Usage
You can spin up an instance of the interpreter by running the following in your terminal.
Make sure that your default python version is >=3.0:
```
python lispr.py
```

After that, you can execute scheme statements in your terminal. Try it out!
```
lis.py> (1 1 +)
2
lis.py> (1 2 eq?)
False
lis.py> (a 5 define)
lis.py> (a 1 +)
6
lis.py> (square ((x) (x x *) lambda) define)
lis.py> (a square)
25
```

A list of all available forms can be found below.

| **Form**       | **Use**              | **Usage**   | **Result**|
| -----------    | -------------------- | ------------|-----------|
| +, -, *, /     | Math operators       | `(1 1 +)`     | `2`
| `atom?`        | Returns `True` if the next expression is atomic (float, int, or string), `False` otherwise. | `((1 2)' atom?)` | `False`|
| `eq?`          | Returns `True` if the next two expressions evaluate to the same value, `False` otherwise.   | `(1 2 eq?)` | `False` |
| `quote`        | Returns the rest of the list expression, unevaluated. | `((1 1 +)' quote)` | `(1 1 +)` |
| `cons`         | Concatenate two atomic expressions. | `(1 1 cons)`   | `(1 1)` |
| `car`          | Extract the first element of a list expression. | `((1 1)' car)` | `1` |
| `cdr`          | Extract the elements following element 0 of a list expression. | `((1 2 3)' cdr)` | `(2 3)` |
| `define`       | Add a symbol to the environment. Symbols can be atomic, or procedural. | `(a 1 define)` | a is now accessible in further statements. |
| `lambda`       | Define a *new operator*. | `(square ((x) (x x *) lambda) define)` | square is now accessible as an operator. |
| `cond`         | Do an if-else block. | `((one' (1 2 eq?)) (two' (1 3 eq?)) (three' else) cond)` | `three` |

# Known Bugs
* Right now, `atom?` produces the wrong result for quoted symbols like `a'`. I think it's because of how I handle quotes on lines 160 and 183.
A fix might be to change `atom?` from a lambda function into code in the eval function, so it can check if the next expression is suffixed with
a `'`.