import os

# srcpath1 = 'ArrayTest\Main.xml'
# srcpath2 = 'ArrayTest\BuiltInResults\Main.xml'

for i in range(3):
    if i == 1:
        srcpath1 = 'ExpressionLessSquare\Main.xml'
        srcpath2 = 'ExpressionLessSquare\BuiltInResults\Main.xml'
    elif i == 2:
        srcpath1 = 'ExpressionLessSquare\Square.xml'
        srcpath2 = 'ExpressionLessSquare\BuiltInResults\Square.xml'
    else:
        srcpath1 = 'ExpressionLessSquare\SquareGame.xml'
        srcpath2 = 'ExpressionLessSquare\BuiltInResults\SquareGame.xml'
# for i in range(3):
#     if i == 1:
#         srcpath1 = 'Square\Main.xml'
#         srcpath2 = 'Square\BuiltInResults\Main.xml'
#     elif i == 2:
#         srcpath1 = 'Square\Square.xml'
#         srcpath2 = 'Square\BuiltInResults\Square.xml'
#     else:
#         srcpath1 = 'Square\SquareGame.xml'
#         srcpath2 = 'Square\BuiltInResults\SquareGame.xml'

    with open(srcpath1, 'r') as file:
        text1 = file.read()

    with open(srcpath2, 'r') as file:
        text2 = file.read()

    print(text1==text2)

    tok1 = text1.split('\n')
    tok2 = text2.split('\n')

    i = 0
    for x, y in zip(tok1, tok2):
        if x != y:
            print(i, x, y)
            break
        i += 1
