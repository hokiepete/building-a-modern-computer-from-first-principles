# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('-p', help='path to the file to translate')
# args = parser.parse_args()

# srcfile = args.p
# destfile = args.p.split('.')[0] + '.hack'
# print(srcfile)
# print(destfile)

import subprocess

INC = '@SP\nM=M+1'
DEC = '@SP\nM=M-1'
HALF_POP = f'{DEC}\nA=M'
POP = f'{HALF_POP}\nD=M'
GOTO_STK = '@SP\nA=M'
PUSH = f'{GOTO_STK}\nM=D\n{INC}'
GET_CUR_VAL = f'@SP\nA=M-1'


LOGIC_JUM = 0

COMMAND_DICT = {
    'add': f'{POP}\n{HALF_POP}\nM=D+M\n{INC}',
    'sub': f'{POP}\n{HALF_POP}\nM=M-D\n{INC}',
    'neg': f'{HALF_POP}\nM=-M\n{INC}',
    'and': f'{POP}\n{HALF_POP}\nM=D&M\n{INC}',
    'or': f'{POP}\n{HALF_POP}\nM=D|M\n{INC}',
    'not': f'{HALF_POP}\nM=!M\n{INC}'
}

JMP_CMDS = set(['eq','lt','gt'])

REGISTER_MAP = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT'
}

# srcfile = '07\\StackArithmetic\\SimpleAdd\\SimpleAdd.vm'
# srcfile = '07\\StackArithmetic\\StackTest\\StackTest.vm'
# srcfile = '07\\MemoryAccess\\BasicTest\\BasicTest.vm'
# srcfile = '07\\MemoryAccess\\PointerTest\\PointerTest.vm'
# srcfile = '07\\MemoryAccess\\StaticTest\\StaticTest.vm'
# srcfile = '08\\ProgramFlow\\BasicLoop\\BasicLoop.vm'
srcfile = '08\\ProgramFlow\\FibonacciSeries\\FibonacciSeries.vm'
destfile = srcfile.split('.')[0] + '.asm'

def clean_text(text):
    commands = []
    for line in text.split('\n'):
        stripped = line.strip()
        if (stripped[:2] == '//') or (len(stripped) == 0):
            continue
        elif '//' in stripped:
            commands.append(stripped.split('//')[0].strip().split())
        else:
            commands.append(stripped.split())
    return commands


def parse_cmds(commands):
    assembly = []
    for cmd in commands:
        # arithmetic/logic operation
        if cmd[0] in JMP_CMDS:
            # Logic commands that need unique JUMP 
            global LOGIC_JUM
            prefix = f'{POP}\n{HALF_POP}\nD=M-D\n@_LGC_ENTER_.{LOGIC_JUM}\nD;J'
            suffix = f'\n{GOTO_STK}\nM=0\n@_LGC_EXIT_.{LOGIC_JUM}\n0;JMP\n(_LGC_ENTER_.{LOGIC_JUM})\n{GOTO_STK}\nM=-1\n(_LGC_EXIT_.{LOGIC_JUM})\n{INC}'
            # append the prefix and the suffix to the comparison, i.e. EQ, LT, GT.
            line = prefix + cmd[0].upper() + suffix
            assembly.append(line)
            LOGIC_JUM += 1
        elif cmd[0] in COMMAND_DICT:
            assembly.append(COMMAND_DICT[cmd[0]])
        # push/pop operation
        elif cmd[0] == 'push':
            if cmd[1] == 'constant':
                assembly.append(f'@{cmd[2]}\nD=A\n{PUSH}')
            elif cmd[1] == 'pointer':
                pointer = "THIS" if cmd[2] == '0' else "THAT"
                assembly.append(f'@{pointer}\nD=M\n{PUSH}')
            elif cmd[1] in ['temp', 'static']:
                offset = 5 if cmd[1] == 'temp' else 16
                assembly.append(f'@R{int(cmd[2]) + offset}\nD=M\n{PUSH}')
            else:
                assembly.append(f"@{REGISTER_MAP[cmd[1]]}\nD=M\n@{cmd[2]}\nA=D+A\nD=M\n{PUSH}")
        elif cmd[0] == 'pop':
            if cmd[1] == 'pointer':
                pointer = "THIS" if cmd[2] == '0' else "THAT"
                assembly.append(f'{POP}\n@{pointer}\nM=D')
            elif cmd[1] in ['temp', 'static']:
                offset = 5 if cmd[1] == 'temp' else 16
                assembly.append(f'{POP}\n@R{int(cmd[2]) + offset}\nM=D')
            else:
                assembly.append(f'@{REGISTER_MAP[cmd[1]]}\nD=M\n@{cmd[2]}\nD=D+A\n@R15\nM=D\n{POP}\n@R15\nA=M\nM=D')
        # Generate Label for code block
        elif cmd[0] == 'label':
            assembly.append(f'({cmd[1]})')
        elif cmd[0] == 'if-goto':
            assembly.append(f'{POP}\n@{cmd[1]}\nD;JNE')
        elif cmd[0] == 'goto':
            assembly.append(f'@{cmd[1]}\n0;JMP')
        else:
            raise ValueError('Unrecognized operation.')

    assembly.append('(_END_ALL_CODE_)\n@_END_ALL_CODE_\n0;JMP')
    return assembly


with open(srcfile, 'r') as file:
    text = file.read()

commands = clean_text(text)
assembly = parse_cmds(commands)

with open(destfile, 'w') as file:
    for line in assembly:
        file.write(line+'\n')

subprocess.Popen(['python', 'assembler.py', '-p', destfile])

print('Done')