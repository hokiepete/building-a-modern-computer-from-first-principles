// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


@SCREEN
D=A
@R1
M=D
(LOOP)
    // listen for keyboard value
    @KBD
    D=M
    // If key isn't being pressed check if the screen is cleared 
    @CCLR
    D; JEQ

    // If key is being pressed check if the screen is filled
    @CFIL
    0; JMP

(CCLR)
    // If register1 == 0, screen is clear go back to loop
    @R0
    D=M
    @LOOP
    D; JEQ

    // otherwise set up index and jump to clear screen
    @8192
    D=A
    @i
    M=D

    @CLEAR
    0; JMP

(CFIL)
    @R0
    D=M
    @LOOP
    D; JNE

    @8192
    D=A
    @i
    M=D

    @FILL
    0; JMP

(CLEAR)    
    // set image to white
    @R1
    A=M
    M=!M
    D=A+1
    @R1
    M=D
    @i
    MD=M-1
    @CLEAR
    D; JGT

    @SCREEN
    D=A
    @R1
    M=D
    @R0
    M=M-1
    @LOOP
    0; JMP

(FILL)
    // set image to black
    @R1
    A=M
    M=!M
    D=A+1
    @R1
    M=D
    @i
    MD=M-1
    @FILL
    D; JGT

    @SCREEN
    D=A
    @R1
    M=D
    @R0
    M=M+1
    @LOOP
    0; JMP