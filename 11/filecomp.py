import os

for i in range(11):
    if i == 0:
        srcpath1 = '11\\Seven\\Main.vm'
        srcpath2 = '11\\Seven\\Main.bvm'
    elif i == 1:
        srcpath1 = '11\\ConvertToBin\\Main.vm'
        srcpath2 = '11\\ConvertToBin\\Main.bvm'
    elif i == 2:
        srcpath1 = '11\\Square\\Main.vm'
        srcpath2 = '11\\Square\\Main.bvm'
    elif i == 3:
        srcpath1 = '11\\Square\\Square.vm'
        srcpath2 = '11\\Square\\Square.bvm'
    elif i == 4:
        srcpath1 = '11\\Square\\SquareGame.vm'
        srcpath2 = '11\\Square\\SquareGame.bvm'
    elif i == 5:
        srcpath1 = '11\\Average\\Main.vm'
        srcpath2 = '11\\Average\\Main.bvm'
    elif i == 6:
        srcpath1 = '11\\Pong\\Main.vm'
        srcpath2 = '11\\Pong\\Main.bvm'
    elif i == 7:
        srcpath1 = '11\\Pong\\Ball.vm'
        srcpath2 = '11\\Pong\\Ball.bvm'
    elif i == 8:
        srcpath1 = '11\\Pong\\Bat.vm'
        srcpath2 = '11\\Pong\\Bat.bvm'
    elif i == 9:
        srcpath1 = '11\\Pong\\PongGame.vm'
        srcpath2 = '11\\Pong\\PongGame.bvm'
    elif i == 10:
        srcpath1 = '11\\ComplexArrays\\Main.vm'
        srcpath2 = '11\\ComplexArrays\\Main.bvm'

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
