# When?

#### This is a compiler / interpreter for a made up language called When?

This was invented to keep track of when will Wappu be.

for example:

```
VAR wappu IS 2024-05-01
VAR diff  IS wappu - Today()

IF diff = 0 THEN
    PRINT "WAPPU!!!";
ELSE
    PRINT diff, "days until wappu";
ENDIF;
```

Tells us how many days we still have to wait till Wappu is here.
On Wappu it prints out WAPPU!!!

Run: python3 main.py -f ./test/running/ok-wappu.when

This compiler / interpreter has some compile time checks and also some runtime checks.

Makes use of ply.yacc.
https://www.dabeaz.com/ply/
https://github.com/dabeaz/ply


Made as part of a Tampere University course called Principles of Programming Languages.

# How?

**1. Lexical Analysis (lexer.py):**
- The source code is broken down into tokens, which are the smallest units of meaning, by a lexical analyzer (lexer.py).


**2. Syntax Analysis (main.py):**
- The parser analyzes the structure of the source code based on the grammar of the programming language. It builds a syntax tree or an abstract syntax tree (AST) representing the hierarchical structure of the code.

  
**3. Semantic Analysis (simple_semantics_check.py + symtbl_semantics_check.py):**
- The compiler checks the code for semantic errors and ensures that it adheres to the language's rules and constraints. This step involves type checking, scope resolution, and other analyses that go beyond syntax.


**4. Interpretation (semantics_run.py):**
- This is where the generated syntax tree is evaluated.


Runnable functions are not implemented except a built-in function Today() which returns today's date. Control structures, variables, basic math and printing is so actual programs can be developed with this though.
