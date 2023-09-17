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