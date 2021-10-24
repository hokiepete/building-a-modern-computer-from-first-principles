import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('p', help='path to the file to translate')

args = parser.parse_args()

srcfile = args.p
destfile = srcfile.split('.')[0] + '.asm'
print(srcfile)
print(destfile)

INC = '@SP\nM=M+1'
DEC = '@SP\nM=M-1'
HALF_POP = f'{DEC}\nA=M'
POP = f'{HALF_POP}\nD=M'
GET_ST = '@SP\nA=M'
PUSH = f'{GET_ST}\nM=D\n{INC}'


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
# destfile = srcfile.split('.')[0] + '.asm'

def clean_text(text):
    commands = []
    for line in text.split('\n'):
        stripped = line.strip()
        if (stripped[:2] == '//') or (len(stripped) == 0):
            continue
        elif '//' in stripped:
            commands.append(stripped.split('//')[0].strip())
        else:
            commands.append(stripped.split())
    return commands


def parse_cmds(commands):
    assembly = []
    for cmd in commands:
        if len(cmd) == 1:
            # arithmetic/logic operation
            if cmd[0] in JMP_CMDS:
                # commands that need unique JUMP 
                global LOGIC_JUM
                prefix = f'{POP}\n{HALF_POP}\nD=M-D\n@ENTER.{LOGIC_JUM}\nD;J'
                suffix = f'\n{GET_ST}\nM=0\n@EXIT.{LOGIC_JUM}\n0;JMP\n(ENTER.{LOGIC_JUM})\n{GET_ST}\nM=-1\n(EXIT.{LOGIC_JUM})\n{INC}'
                line = prefix + cmd[0].upper() + suffix
                assembly.append(line)
                LOGIC_JUM += 1
            else:
                assembly.append(COMMAND_DICT[cmd[0]])
        else:
            # push/pop operation
            if cmd[0] == 'push':
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
            elif (cmd[0] == 'pop'):
                if cmd[1] == 'pointer':
                    pointer = "THIS" if cmd[2] == '0' else "THAT"
                    assembly.append(f'{POP}\n@{pointer}\nM=D')
                elif cmd[1] in ['temp', 'static']:
                    offset = 5 if cmd[1] == 'temp' else 16
                    assembly.append(f'{POP}\n@R{int(cmd[2]) + offset}\nM=D')
                else:
                    assembly.append(f'@{REGISTER_MAP[cmd[1]]}\nD=M\n@{cmd[2]}\nD=D+A\n@R15\nM=D\n{POP}\n@R15\nA=M\nM=D')
            else:
                raise ValueError('Unrecognized push/pop operation.')

    assembly.append('(END)\n@END\n0;JMP')
    return assembly


with open(srcfile, 'r') as file:
    text = file.read()

commands = clean_text(text)
assembly = parse_cmds(commands)
print(assembly)
with open(destfile, 'w') as file:
    for line in assembly:
        file.write(line+'\n')
        
# subprocess.Popen(['python', 'assembler.py', '-p', destfile])

# print('Done')