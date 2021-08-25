import os
from JackTonenizer import JackTokenizer
from CompilationEngine import CompilationEngine

# srcpath = '11\\Seven'
# srcpath = '11\\ConvertToBin'
# srcpath = '11\\Square'
srcs = ['11\\Seven', '11\\ConvertToBin', '11\\Square', '11\\Average', '11\\Pong', '11\\ComplexArrays']
# srcs = ['11\\Pong\\Ball.jack']
for srcpath in srcs:
    print(srcpath)
    if os.path.isdir(srcpath):
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
                destfile = f'{srcpath}\\{file.replace(".jack", ".vm")}'
                with open(destfile, 'w') as f:
                    f.write('\n'.join(compiler.code)+'\n')
    else:
        with open(srcpath, 'r') as file:
            text = file.read()
        tokenizer = JackTokenizer(text)
        compiler = CompilationEngine(tokenizer.tagged_tokens)
        destfile = f'{srcpath.replace(".jack", ".vm")}'
        with open(destfile, 'w') as f:
            f.write('\n'.join(compiler.code)+'\n')
