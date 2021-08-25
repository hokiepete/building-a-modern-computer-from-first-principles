import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', help='path to the file to translate')
args = parser.parse_args()

srcpath = args.p
# destfile = args.p.split('.')[0] + '.hack'
# print(srcpath)
# print(destfile)
import os
import subprocess

LOGIC_JUM = 0
RUNNING_INT = 0
CUR_FUNC = None

INC = '@SP\nM=M+1'
DEC = '@SP\nM=M-1'
HALF_POP = f'{DEC}\nA=M'
POP = f'{HALF_POP}\nD=M'
GOTO_STK = '@SP\nA=M'
PUSH = f'{GOTO_STK}\nM=D\n{INC}'
GET_CUR_VAL = f'@SP\nA=M-1'

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

FUNC_CALL_CNT = {}

# srcpath = '07\\StackArithmetic\\SimpleAdd\\SimpleAdd.vm'
# srcpath = '07\\StackArithmetic\\StackTest\\StackTest.vm'
# srcpath = '07\\MemoryAccess\\BasicTest\\BasicTest.vm'
# srcpath = '07\\MemoryAccess\\PointerTest\\PointerTest.vm'
# srcpath = '07\\MemoryAccess\\StaticTest\\StaticTest.vm'
# srcpath = '08\\ProgramFlow\\BasicLoop\\BasicLoop.vm'
# srcpath = '08\\ProgramFlow\\FibonacciSeries\\FibonacciSeries.vm'
# srcpath = '08\\FunctionCalls\\SimpleFunction\\SimpleFunction.vm'
# srcpath = '08\\FunctionCalls\\NestedCall'
# srcpath = '08\\FunctionCalls\\FibonacciElement'
# srcpath = '08\\FunctionCalls\\StaticsTest'

def parse_text(text, boot_strap=False):
    commands = []
    if boot_strap:
        commands.append(['set_stack'])
        commands.append(['call', 'Sys.init', '0'])
        pass
    for line in text.split('\n'):
        stripped = line.strip()
        if (stripped[:2] == '//') or (len(stripped) == 0):
            continue
        elif '//' in stripped:
            commands.append(stripped.split('//')[0].strip().split())
        else:
            commands.append(stripped.split())
    return commands

def get_goto_label(label_name, filename):
    if CUR_FUNC:
        label = f'{CUR_FUNC}${label_name}'
    elif filename:
        label = f'{filename}${label_name}'
    else:
        label = f'{label_name}'
    return label

def write_cmds(commands, filename=None):
    global CUR_FUNC
    assembly = []
    for cmd in commands:
        # arithmetic/logic operation
        if cmd[0] in JMP_CMDS:
            # Logic commands that need unique JUMP 
            global LOGIC_JUM
            prefix = f'{POP}\n{HALF_POP}\nD=M-D\n@VM_INTERNAL_LGC_ENTER_.{LOGIC_JUM}\nD;J'
            suffix = f'\n{GOTO_STK}\nM=0\n@VM_INTERNAL_LGC_EXIT_.{LOGIC_JUM}\n0;JMP\n' \
                + f'(VM_INTERNAL_LGC_ENTER_.{LOGIC_JUM})\n{GOTO_STK}\nM=-1\n' \
                + f'(VM_INTERNAL_LGC_EXIT_.{LOGIC_JUM})\n{INC}'
            # append the prefix and the suffix to the comparison, i.e. EQ, LT, GT.
            assembly_cmds = prefix + cmd[0].upper() + suffix
            assembly.append(assembly_cmds)
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
            elif cmd[1] == 'temp':
                assembly.append(f'@R{int(cmd[2]) + 5}\nD=M\n{PUSH}')
            elif cmd[1] == 'static':
                if filename:
                    assembly.append(f'@{filename}.{cmd[2]}\nD=M\n{PUSH}')
                else:
                    assembly.append(f'@static.{cmd[2]}\nD=M\n{PUSH}')
            else:
                assembly.append(f"@{REGISTER_MAP[cmd[1]]}\nD=M\n@{cmd[2]}\nA=D+A\nD=M\n{PUSH}")
        elif cmd[0] == 'pop':
            if cmd[1] == 'pointer':
                pointer = "THIS" if cmd[2] == '0' else "THAT"
                assembly.append(f'{POP}\n@{pointer}\nM=D')
            elif cmd[1] == 'temp':
                assembly.append(f'{POP}\n@R{int(cmd[2]) + 5}\nM=D')
            elif cmd[1] == 'static':
                if filename:
                    assembly.append(f'{POP}\n@{filename}.{cmd[2]}\nM=D')
                else:
                    assembly.append(f'{POP}\n@static.{cmd[2]}\nM=D')
            else:
                assembly.append(f'@{REGISTER_MAP[cmd[1]]}\nD=M\n@{cmd[2]}\nD=D+A\n@R15\nM=D\n{POP}\n@R15\nA=M\nM=D')
        # Generate Label for code block
        elif cmd[0] == 'label':
            if CUR_FUNC:
                label = f'({CUR_FUNC}${cmd[1]})'
            elif filename:
                label = f'({filename}${cmd[1]})'
            else:
                label = f'({cmd[1]})'
            assembly.append(label)
        # GOTO Jumps
        elif cmd[0] == 'if-goto':
            label = get_goto_label(cmd[1], filename)
            assembly.append(f'{POP}\n@{label}\nD;JNE')
        elif cmd[0] == 'goto':
            label = get_goto_label(cmd[1], filename)
            assembly.append(f'@{label}\n0;JMP')
        # Function code
        elif cmd[0] == 'call':
            if cmd[1] in FUNC_CALL_CNT:
                ret_add = f'{cmd[1]}$ret.{FUNC_CALL_CNT[cmd[1]]}'
                FUNC_CALL_CNT[cmd[1]] += 1
            else:
                ret_add = f'{cmd[1]}$ret.0'
                FUNC_CALL_CNT[cmd[1]] = 1
            stk_drop = 5 + int(cmd[2])
            line = f"@{ret_add}\nD=A\n{PUSH}\n@LCL\nD=M\n{PUSH}\n@ARG\nD=M\n{PUSH}\n@THIS\nD=M\n{PUSH}\n@THAT\nD=M\n{PUSH}\n@SP\nD=M\n@{stk_drop}\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@{cmd[1]}\n0;JMP\n({ret_add})"
            assembly.append(line)
        elif cmd[0] == 'function':
            CUR_FUNC = cmd[1]
            if cmd[2] == '0':
                line= f'({cmd[1]})' 
            else:
                line = f'({cmd[1]})\nD=0' + int(cmd[2]) * f'\n{PUSH}'
            assembly.append(line)
        elif cmd[0] == 'return':
            assembly.append(f"@LCL\nD=M\n@frame\nM=D\n@5\nA=D-A\nD=M\n@retAddr\nM=D\n{POP}\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n@frame\nD=M\n@1\nA=D-A\nD=M\n@THAT\nM=D\n@frame\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n@frame\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n@frame\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n@retAddr\nA=M\n0;JMP")    
        # Bootstrap code
        elif cmd[0] == 'set_stack':
            assembly.append('@256\nD=A\n@SP\nM=D')
        else:
             raise ValueError(f'Unrecognized operation {cmd[0]}.')
    return assembly


if os.path.isdir(srcpath):
    # read and parse the system file
    # with open(srcpath + '\\Sys.vm', 'r') as file:
    #     text = file.read()
    # get all the files in the directory minus the system file
    # and parse the files
    files = os.listdir(srcpath)
    # files.remove('Sys.vm')
    commands = parse_text('',boot_strap=True)
    assembly = write_cmds(commands)
    for file in files:
        if file.endswith('.vm'):
            with open(srcpath + f'\\{file}', 'r') as f:
                text = f.read()
            assembly += write_cmds(parse_text(text), file.split('.')[0])
      
    # figure out destination path
    filename = srcpath.split('\\')[-1]
    destfile = f'{srcpath}\\{filename}.asm'
    
else:
    with open(srcpath, 'r') as file:
        text = file.read()
    commands = parse_text(text)
    assembly = write_cmds(commands)
    destfile = srcpath.split('.')[0] + '.asm'

assembly.append('(_END_ALL_CODE_)\n@_END_ALL_CODE_\n0;JMP')
with open(destfile, 'w') as file:
    for line in assembly:
        file.write(line+'\n')

subprocess.Popen(['python', 'assembler.py', '-p', destfile])

print('Done')