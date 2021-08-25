import os
from JackTonenizer import JackTokenizer
from CompilationEngine import CompilationEngine

srcpath = 'ExpressionLessSquare'
# srcpath = 'C:\\Users\\pnola\\OneDrive\\Desktop\\nand2tetris\\projects\\09\\my_snake_game'
if os.path.isdir( srcpath):
    # read and parse the system file
    # with open(srcpath + '\\Sys.vm', 'r') as file:
    #     text = file.read()
    # get all the files in the directory minus the system file
    # and parse the files
    files = os.listdir(srcpath)
    for file in files:
        if file.endswith('.jack'):
            with open(srcpath + f'\\{file}', 'r') as f:
                text = f.read()
            tokenizer = JackTokenizer(text)
            try:
                compiler = CompilationEngine(tokenizer.tagged_tokens)
            except ValueError as e:
                raise ValueError(f"Error in file {file}. {e}")
            destfile = f'{srcpath}\\{file.replace(".jack", ".xml")}'
            with open(destfile, 'w') as f:
                f.write('\n'.join(compiler.code)+'\n')
else:
    with open(srcpath, 'r') as file:
        text = file.read()
    tokenizer = JackTokenizer(text)
    compiler = CompilationEngine(tokenizer.tagged_tokens)
    destfile = f'{srcpath.replace(".jack", ".xml")}'
    with open(destfile, 'w') as f:
        f.write('\n'.join(compiler.code)+'\n')