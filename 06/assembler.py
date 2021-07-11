import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', help='path to the file to translate')
args = parser.parse_args()

srcfile = args.p
destfile = args.p.split('.')[0] + '.hack'


DEST_TABLE = {
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}
JUMP_TABLE = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}
COMP_TABLE = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000',
    'M': '1110000',
    '!D': '0001101',
    '!A': '0110001',
    '!M': '1110001',
    '-D': '0001111',
    '-A': '0110011',
    '-M': '1110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'M-1': '1110010',
    'D+A': '0000010',
    'D+M': '1000010',
    'D-A': '0010011',
    'D-M': '1010011',
    'A-D': '0000111',
    'M-D': '1000111',
    'D&A': '0000000',
    'D&M': '1000000',
    'D|A': '0010101',
    'D|M': '1010101'
}
SYM_TABLE = {
    "SP": bin(0)[2:].rjust(16, '0'),
    "LCL": bin(1)[2:].rjust(16, '0'),
    "ARG": bin(2)[2:].rjust(16, '0'),
    "THIS": bin(3)[2:].rjust(16, '0'),
    "THAT": bin(4)[2:].rjust(16, '0'),
    "R0": bin(0)[2:].rjust(16, '0'),
    "R1": bin(1)[2:].rjust(16, '0'),
    "R2": bin(2)[2:].rjust(16, '0'),
    "R3": bin(3)[2:].rjust(16, '0'),
    "R4": bin(4)[2:].rjust(16, '0'),
    "R5": bin(5)[2:].rjust(16, '0'),
    "R6": bin(6)[2:].rjust(16, '0'),
    "R7": bin(7)[2:].rjust(16, '0'),
    "R8": bin(8)[2:].rjust(16, '0'),
    "R9": bin(9)[2:].rjust(16, '0'),
    "R10": bin(10)[2:].rjust(16, '0'),
    "R11": bin(11)[2:].rjust(16, '0'),
    "R12": bin(12)[2:].rjust(16, '0'),
    "R13": bin(13)[2:].rjust(16, '0'),
    "R14": bin(14)[2:].rjust(16, '0'),
    "R15": bin(15)[2:].rjust(16, '0'),
    "SCREEN": bin(16384)[2:].rjust(16, '0'),
    "KBD": bin(24576)[2:].rjust(16, '0'),
}
CURRENT_ADD = 16
LINE_NUMBER = 0

def binarize(val):
    return bin(int(val))[2:].rjust(16, '0')

def add_blocks(sym):
    if sym in SYM_TABLE.keys():
        raise KeyError(f"BLOCK Label {sym} has already been assigned")
    SYM_TABLE[sym] = binarize(LINE_NUMBER)

def add_sym(sym):
    global CURRENT_ADD
    value = binarize(CURRENT_ADD)
    if value >= SYM_TABLE['SCREEN']:
        raise MemoryError('MEMORY IS FULL')
    SYM_TABLE[sym] = value
    CURRENT_ADD += 1

with open(srcfile, 'r') as file:
    text = file.read()

# FIRST PASS
# split file one \n, remove comments and strip 
code = []
for line in text.split('\n'):
    stripped = line.strip()
    # skip comments and whitespace
    if (stripped[:2] == '//') or len(stripped) == 0:
        continue
    
    # remove comments from lines
    if '//' in stripped:
        stripped = stripped.split('//')[0].strip()

    # identify code blocks
    if stripped[0] == '(':
        sym  = stripped[1:-1].strip()
        add_blocks(sym)
    else:           
        LINE_NUMBER += 1
        code.append(stripped)
        
# SECOND PASS
mach = []
for line in code:
    # A operation
    if line[0] == '@':
        # a numerical value
        if line[1].isnumeric():
            mach.append(binarize(line[1:]))
        # symbolic
        else:
            if line[1:] not in SYM_TABLE.keys():
                add_sym(line[1:])
            mach.append(SYM_TABLE[line[1:]])

    # C operation
    else:
        if '=' in line:
            pre, line = map(lambda x: x.strip(), line.split('='))
            dst = DEST_TABLE[pre]
        else:
            dst = '000'
        
        if ';' in line:
            line, suf = map(lambda x: x.strip(), line.split(';'))
            jmp = JUMP_TABLE[suf]
        else:
            jmp = '000'

        comp = COMP_TABLE[line]

        mach.append('111' + comp + dst + jmp)


with open(destfile, 'w') as file:
    for line in mach:
        file.write(line+'\n')