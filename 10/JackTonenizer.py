# Main program that sets up and invokes the other modules
import os

KEYWORDS = set([
    'class','constructor','function','method','field','static','var','int','char','boolean',
    'void','true','false','null','this','let','do','if','else','while','return'
])
SYMBOL = set([
    '{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~'
])

SUBS = {'<':'&lt;', '>': '&gt;', '\'': '&quot;', '\"': '&quot;', '&': '&amp;'}

class JackTokenizer:
    def __init__(self, input_string):
        self.raw_string = input_string
        self.tokens = []
        self.tagged_tokens = []
        self.clean_lines()
        self.tokenize()
        self.tag_tokens()

    def clean_lines(self):
        lines = self.raw_string.split('\n')
        cleaned = []
        IN_COMMENT = False
        for line in lines:
            if IN_COMMENT:
                if "*/" in line:
                    IN_COMMENT = False
                    cleaned_line = line.split('*/')[1].strip()
                else:
                    continue
            elif '//' in line:
                cleaned_line = line.split('//')[0].strip()
            elif "//*" in line:
                if '*/' in line:
                    pref, suff = line.split('//*')
                    cleaned_line = pref.strip() + ' ' + suff.split('*/')[1].strip()
                else:
                    IN_COMMENT = True
                    cleaned_line = line.split('//*')[0].strip()
            elif "/*" in line:
                if '*/' in line:
                    pref, suff = line.split('/*')
                    cleaned_line = pref.strip() + ' ' + suff.split('*/')[1].strip()
                else:
                    IN_COMMENT = True
                    cleaned_line = line.split('/*')[0].strip()
            else:
                cleaned_line = line.strip()
            if cleaned_line and (not cleaned_line.isspace()):
                cleaned.append(cleaned_line)
        
        self.cleaned_string = ' '.join(cleaned)

    def tokenize(self):
        while self.cleaned_string:
            token = self.get_next_token()
            if token:
                self.tokens.append(token)

    def get_next_token(self):
        token = ''
        literal = False
        for i, char in enumerate(self.cleaned_string):
            if char in ['\'', "\""]:
                if literal:
                    literal = False
                else:
                    literal = True
            if not literal:
                if char == ' ':
                    self.cleaned_string = self.cleaned_string[i+1:]
                    return token
                if char in SYMBOL:
                    if token:
                        self.cleaned_string = self.cleaned_string[i:]
                        return token
                    else:
                        self.cleaned_string = self.cleaned_string[i+1:]
                        return char
                if token.isnumeric() and not char.isnumeric():
                    raise ValueError(
                        f"Variable names cannot start with a numeric character. Please fix token beginning with {token + char}"
                        )
            token += char
        
        return token
                    
    def tag_tokens(self):
        self.tagged_tokens.append('<tokens>')
        for token in self.tokens:
            if token in KEYWORDS:
                self.tagged_tokens.append(f"<keyword> {token} </keyword>")
            elif token in SUBS:
                self.tagged_tokens.append(f"<symbol> {SUBS[token]} </symbol>")
            elif token in SYMBOL:
                self.tagged_tokens.append(f"<symbol> {token} </symbol>")
            elif token[0] in ['\'', '\"']:
                self.tagged_tokens.append(f"<stringConstant> {token[1:-1]} </stringConstant>")
            elif token.isnumeric():
                self.tagged_tokens.append(f"<integerConstant> {token} </integerConstant>")
            else:
                self.tagged_tokens.append(f"<identifier> {token} </identifier>")
        self.tagged_tokens.append('</tokens>')
                
            
if __name__ == '__main__':
 
    srcpath = 'ArrayTest\Main.jack'
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
                analyzer = JackTokenizer(text)
                destfile = f'{srcpath}\\{file.replace(".jack", "T.xml")}'
                with open(destfile, 'w') as f:
                    f.write('\n'.join(analyzer.tagged_tokens)+'\n')
    else:
        with open(srcpath, 'r') as file:
            text = file.read()
        analyzer = JackTokenizer(text)
        destfile = f'{srcpath.replace(".jack", "T.xml")}'
        with open(destfile, 'w') as f:
            f.write('\n'.join(analyzer.tagged_tokens)+'\n')
