# Recursive Top-Down Parser

SUBROUTES = set([
    "<keyword> constructor </keyword>",
    "<keyword> function </keyword>",
    "<keyword> method </keyword>"
])

CLASSFIELDS = set(['<keyword> static </keyword>', '<keyword> field </keyword>'])

TYPES = set(['<keyword> int </keyword>', '<keyword> char </keyword>', '<keyword> boolean </keyword>'])

RETURNTYPES = set(['<keyword> void </keyword>']).union(TYPES)

STATEMENTS = set([
    "<keyword> let </keyword>",
    "<keyword> if </keyword>",
    "<keyword> while </keyword>",
    "<keyword> do </keyword>",
    "<keyword> return </keyword>"
    ])

VALID_SUBROUTINE1 = set(["<keyword> var </keyword>", "<symbol> } </symbol>"]).union(STATEMENTS)

OPS = {
    '<symbol> + </symbol>': 'add',
    '<symbol> - </symbol>': 'sub',
    '<symbol> * </symbol>': 'call Math.multiply 2',
    '<symbol> / </symbol>': 'call Math.divide 2',
    '<symbol> &amp; </symbol>': 'and',
    '<symbol> | </symbol>': 'or',
    '<symbol> &lt; </symbol>': 'lt',
    '<symbol> &gt; </symbol>': 'gt',
    '<symbol> = </symbol>': 'eq'
}

UNI = {'<symbol> - </symbol>': 'neg', '<symbol> ~ </symbol>': 'not'}

KEYWORD_CONST = {
    '<keyword> true </keyword>' : 'push constant 0\nnot',
    '<keyword> false </keyword>': 'push constant 0', 
    '<keyword> null </keyword>': 'push constant 0',
    # '<keyword> this </keyword>': 'push argument 0\npop pointer 0'
    '<keyword> this </keyword>': 'push pointer 0'
}

VAR_CONV = {'var': 'local', 'arg': 'argument', 'field': 'this', 'static': 'static'}

CHAR_MAP = {
    ' ': '32', '!': '33', '"': '34', '#': '35', '$': '36', '%': '37', '&': '38', "'": '39',
    '(': '40', ')': '41', '*': '42', '+': '43', ',': '44', '-': '45', '.': '46', '/': '47',
    '0': '48', '1': '49', '2': '50', '3': '51', '4': '52', '5': '53', '6': '54', '7': '55',
    '8': '56', '9': '57', ':': '58', ';': '59', '<': '60', '=': '61', '>': '62', '?': '63',
    '@': '64', 'A': '65', 'B': '66', 'C': '67', 'D': '68', 'E': '69', 'F': '70', 'G': '71',
    'H': '72', 'I': '73', 'J': '74', 'K': '75', 'L': '76', 'M': '77', 'N': '78', 'O': '79',
    'P': '80', 'Q': '81', 'R': '82', 'S': '83', 'T': '84', 'U': '85', 'V': '86', 'W': '87',
    'X': '88', 'Y': '89', 'Z': '90', '[': '91', '\\': '92', ']': '93', '^': '94', '_': '95',
    '`': '96', 'a': '97', 'b': '98', 'c': '99', 'd': '100', 'e': '101', 'f': '102', 'g': '103',
    'h': '104', 'i': '105', 'j': '106', 'k': '107', 'l': '108', 'm': '109', 'n': '110', 'o': '111',
    'p': '112', 'q': '113', 'r': '114', 's': '115', 't': '116', 'u': '117', 'v': '118', 'w': '119',
    'x': '120', 'y': '121', 'z': '122', '{': ' 123', '|': '124', '}': '125', '~': '126'
}

class CompilationEngine:
    def __init__(self, tagged_tokens):
        self.tagged_tokens = tagged_tokens[-2:0:-1]
        self.code = []
        self.class_name = None  # will be set in next function
        self.class_variables = {}
        self.subroutine_variables = {}
        self.var_count = 0
        self.arg_count = 0
        self.static_count = 0
        self.field_count = 0
        self.while_counter = 0
        self.if_counter = 0
        self.compile_class()
    
    def compile_class(self):

        # check that class is defined
        current_token = self.tagged_tokens.pop()
        if current_token != "<keyword> class </keyword>":
            raise ValueError(f"Issue with token {current_token}. Was expecting <keyword> class </keyword>")
        
        # check that an identifier is next
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier.")
        self.class_name = current_token.split()[1]

        # check that { is next.
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. Was expecting" + " <symbol> { </symbol>")
        
        while self.tagged_tokens:
            current_token = self.tagged_tokens.pop()
            if current_token in CLASSFIELDS:
                self.tagged_tokens.append(current_token)
                class_code = self.compile_class_var()
            elif current_token in SUBROUTES:
                self.tagged_tokens.append(current_token)
                class_code = self.compile_subroutine()
                self.code += class_code
            elif current_token == "<symbol> } </symbol>":
                continue
            else:
                raise ValueError(f"Issue with token {current_token}. Was expecting either a class variable, subroutine or closing bracket")

        
    def compile_class_var(self):
        # already know the current token static or field
        current_token = self.tagged_tokens.pop()
        var_kind = current_token.split()[1]

        current_token = self.tagged_tokens.pop()
        if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype or class name for class variable type")
        var_type = current_token.split()[1]

        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier for class variable name.")
        var_name = current_token.split()[1]

        if var_kind == 'static':
            self.class_variables[var_name] = [var_type, var_kind, self.static_count]
            self.static_count += 1
        elif var_kind == 'field':
            self.class_variables[var_name] = [var_type, var_kind, self.field_count]
            self.field_count += 1
        else:
            raise ValueError('Class variables must be of kind static or field.')

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ; </symbol>":
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Class variable names must be separated by a comman ',' .")
            
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier for class variable name.")
            var_name = current_token.split()[1]
            if var_kind == 'static':
                self.class_variables[var_name] = [var_type, var_kind, self.static_count]
                self.static_count += 1
            elif var_kind == 'field':
                self.class_variables[var_name] = [var_type, var_kind, self.field_count]
                self.field_count += 1
            else:
                raise ValueError('Class variables must be of kind static or field.')

            current_token = self.tagged_tokens.pop()
    
    def compile_subroutine(self):
        # clear subroutine variables
        self.subroutine_variables = {}
        # reset variable counters
        self.arg_count = 0
        self.var_count = 0
        self.while_counter = 0
        self.if_counter = 0
        
        subroutine_code = []
        # already know the current token constructor, function or method
        current_token = self.tagged_tokens.pop()
        func_type = current_token.split()[1]
        line = 'function'

        # check that a return type is given
        current_token = self.tagged_tokens.pop()
        if (current_token not in RETURNTYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype, void, or class name for subroutine return type")
        return_type = current_token

        # check that function name is given
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Was expecting a subroutine Identifier.")
        line += f' {self.class_name}.{current_token.split()[1]}'
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ( </symbol>":
            raise ValueError(f"Issue with token {current_token}. Was expecting a ( symbol during subroutine definition.")
        
        if func_type == 'method':
            self.subroutine_variables['this'] = [self.class_name, 'arg', self.arg_count]
            self.arg_count += 1

        self.compile_parameter_list()
        

        # already know current token is ).
        current_token = self.tagged_tokens.pop()
        
        subrout_body = self.compile_subroutine_body()
        
        n = self.var_count
        subroutine_code.append(f'{line} {n}')
        if func_type == 'constructor':
            subroutine_code.append(f'push constant {self.field_count}')
            subroutine_code.append(f'call Memory.alloc 1')
            subroutine_code.append('pop pointer 0')
        elif func_type == 'method':
            subroutine_code.append(f'push argument 0')
            subroutine_code.append(f'pop pointer 0')
        
        subroutine_code += subrout_body

        # if func_type == 'constructor':
        #     return_code = subroutine_code.pop()
        #     subroutine_code.append('push pointer 0')
        #     subroutine_code.append(return_code)
        # elif return_type == 'void':
        #     return_code = subroutine_code.pop()
        #     subroutine_code.append('push constant 0')
        #     subroutine_code.append(return_code)
        return subroutine_code
        

    def compile_parameter_list(self):
        current_token = self.tagged_tokens.pop()
        if current_token == "<symbol> ) </symbol>":
            self.tagged_tokens.append(current_token)
            return
        
        elif (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Subroutine paramater type must be a datatype or class name.")
        var_type = current_token.split()[1]

        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Subroutine parameters names must be Identifiers.")
        var_name = current_token.split()[1]

        self.subroutine_variables[var_name] = [var_type, 'arg', self.arg_count]
        self.arg_count += 1
        
        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ) </symbol>":
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Subroutine paramaters must be separated by a ','.")

            current_token = self.tagged_tokens.pop()
            if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
                raise ValueError(f"Issue with token {current_token}. Subroutine paramater type must be a datatype or class name.")
            var_type = current_token.split()[1]

            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Subroutine parameters names must be Identifiers.")
            var_name = current_token.split()[1]

            self.subroutine_variables[var_name] = [var_type, 'arg', self.arg_count]
            self.arg_count += 1
            
            current_token = self.tagged_tokens.pop()
        

        # put ) back in the tagged tokens.
        self.tagged_tokens.append(current_token)

    def compile_subroutine_body(self):
        subrout_body = []
        # check that body starts with {
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. Was expecting" + " <symbol> { </symbol>")
        
        current_token = self.tagged_tokens.pop()
        if current_token not in VALID_SUBROUTINE1:
            raise ValueError(f"Issue with token {current_token}. Subroutine body must start with <keyword> var </keyword>, a statement token such as <keyword> let </keyword>, or" + " <symbol> } </symbol>")
        
        while current_token == '<keyword> var </keyword>':
            self.tagged_tokens.append(current_token)
            self.compile_var_dec()
            current_token = self.tagged_tokens.pop()    

        if current_token in STATEMENTS:
            self.tagged_tokens.append(current_token)
            statement_code = self.compile_statements()
            subrout_body += statement_code
            # know current token is }
            current_token = self.tagged_tokens.pop()    

        elif current_token == "<symbol> } </symbol>":
            pass
        else:
            raise ValueError(f"Issue with token {current_token}. Subroutine after varDec must start with a statement token such as <keyword> let </keyword>, or" + " <symbol> } </symbol>")
        
        return subrout_body

    def compile_var_dec(self):
        # already know token is var
        current_token = self.tagged_tokens.pop()
        
        # check that it is a type
        current_token = self.tagged_tokens.pop()
        if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype or class name for class variable type")
        var_type = current_token.split()[1]

        # check that it is a name
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Variable names must be Identifiers")
        var_name = current_token.split()[1]
        
        self.subroutine_variables[var_name] = [var_type, 'var', self.var_count]
        self.var_count += 1

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ; </symbol>":
            # check that token is ,
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Variable names must be separated by a comman ',' .")
            
            # check that token is an identifier
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Variable names must be Identifiers")

            var_name = current_token.split()[1]
            self.subroutine_variables[var_name] = [var_type, 'var', self.var_count]
            self.var_count += 1
    
            current_token = self.tagged_tokens.pop()


    def compile_statements(self):
        statement_code = []
        current_token = self.tagged_tokens[-1]
        while current_token != "<symbol> } </symbol>":
            if current_token == "<keyword> let </keyword>":
                let_code = self.compile_let()
                statement_code += let_code
            elif current_token == "<keyword> if </keyword>":
                if_code = self.compile_if()
                statement_code += if_code
            elif current_token == "<keyword> while </keyword>":
                while_code = self.compile_while()
                statement_code += while_code
            elif current_token == "<keyword> do </keyword>":
                do_code = self.compile_do()
                statement_code += do_code
            elif current_token == "<keyword> return </keyword>":
                return_code = self.compile_return()
                statement_code += return_code
            else:
                raise ValueError(f'Issue with token {current_token}. Tag must be a valid Statement declaration.')
            current_token = self.tagged_tokens[-1]
        return statement_code

    def compile_let(self):
        let_code = []
        # know let keyword
        current_token = self.tagged_tokens.pop()
        
        # check that an identifier is next
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Let keyword must be followed by a variable name Identifier.")
        var_name = current_token.split()[1]

        current_token = self.tagged_tokens.pop()
        return_exp = False
        if current_token == "<symbol> [ </symbol>":
            return_exp = True
            if var_name in self.subroutine_variables:
                arr_code = ['push ' +
                VAR_CONV[self.subroutine_variables[var_name][1]] +
                ' ' + str(self.subroutine_variables[var_name][2])
                ]
            else:
                arr_code = ['push ' +
                VAR_CONV[self.class_variables[var_name][1]] +
                ' ' + str(self.class_variables[var_name][2])
                ]
            exp_code = self.compile_expression(["<symbol> ] </symbol>"])
            arr_code = exp_code + arr_code
            arr_code.append('add')
            
            # self.code.append("</expression>")
            # know current token is ]
            current_token = self.tagged_tokens.pop()
            # if current_token != "<symbol> ] </symbol>":
            #     raise ValueError(f"Issue with token {current_token}. Expressions beginning with '[' must end with ']'.")
            # self.code.append(current_token)
            current_token = self.tagged_tokens.pop()
        
        if current_token != "<symbol> = </symbol>":
            raise ValueError(f"Issue with token {current_token}. Let statement requires a '=' symbol after the variable declaration.")
        exp_code = self.compile_expression(["<symbol> ; </symbol>"])
        let_code += exp_code

        if not return_exp:
            if var_name in self.subroutine_variables:
                let_code.append('pop ' +
                VAR_CONV[self.subroutine_variables[var_name][1]] +
                ' ' + str(self.subroutine_variables[var_name][2])
                )
            else:
                let_code.append('pop ' +
                VAR_CONV[self.class_variables[var_name][1]] +
                ' ' + str(self.class_variables[var_name][2])
                )
        else:
            # self.code.append('<><>return value')
            let_code = arr_code + let_code
            let_code.append('pop temp 0')
            let_code.append('pop pointer 1')
            let_code.append('push temp 0')
            let_code.append('pop that 0')
            
        # know current token is ;
        current_token = self.tagged_tokens.pop()
        # if current_token != "<symbol> ; </symbol>":
        #     raise ValueError(f"Issue with token {current_token}. Let statement must terminate with a ';' symbol.")
        
        return let_code
        
    def compile_if(self):
        if_code = []
        label1 = f'IF_TRUE{self.if_counter}'
        label2 = f'IF_FALSE{self.if_counter}'
        label3 = f'IF_END{self.if_counter}'
        self.if_counter += 1
        false_statement_code = None
        # know keyword if
        current_token = self.tagged_tokens.pop()
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ( </symbol>":
            raise ValueError(f"Issue with token {current_token}. If expressions must begin with a '(' symbol.")
        
        exp_code = self.compile_expression(["<symbol> ) </symbol>"])
        
        # know current token is )
        current_token = self.tagged_tokens.pop()
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. If statements must begin with a" + " '{' symbol.")
        
        true_statement_code = self.compile_statements()
        
        # know current token is }
        current_token = self.tagged_tokens.pop()
        if self.tagged_tokens[-1] == "<keyword> else </keyword>":
            current_token = self.tagged_tokens.pop()
            
            current_token = self.tagged_tokens.pop()
            if current_token != "<symbol> { </symbol>":
                raise ValueError(f"Issue with token {current_token}. Else statements must begin with a" + " '{' symbol.")
            
            false_statement_code = self.compile_statements()
            # know current token is }
            current_token = self.tagged_tokens.pop()
        
        if_code += exp_code
        if_code.append(f'if-goto {label1}')
        if false_statement_code:
            if_code.append(f'goto {label2}')
            if_code.append(f'label {label1}')
            if_code += true_statement_code
            if_code.append(f'goto {label3}')
            if_code.append(f'label {label2}')
            if_code += false_statement_code
            if_code.append(f'label {label3}')
        else:
            if_code.append(f'goto {label2}')
            if_code.append(f'label {label1}')
            if_code += true_statement_code
            if_code.append(f'label {label2}')
        return if_code

    def compile_while(self):
        while_code = []
        label1 = f'WHILE_EXP{self.while_counter}'
        label2 = f'WHILE_END{self.while_counter}'
        self.while_counter += 1
        # know keyword while
        current_token = self.tagged_tokens.pop()
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ( </symbol>":
            raise ValueError(f"Issue with token {current_token}. While expressions must begin with a '(' symbol.")
        
        while_code.append(f'label {label1}')
        exp_code = self.compile_expression(["<symbol> ) </symbol>"])
        while_code += exp_code
        while_code.append('not')
        while_code.append(f'if-goto {label2}')

        # know current token is ) 
        current_token = self.tagged_tokens.pop()

        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. While statements must begin with a" + " '{' symbol.")

        statement_code = self.compile_statements()
        while_code += statement_code

        while_code.append(f'goto {label1}')
        while_code.append(f'label {label2}')
        # know current token is }
        current_token = self.tagged_tokens.pop()
        return while_code

    def compile_do(self):
        do_code = []
        num_exp = 0
        # know keyword do
        current_token = self.tagged_tokens.pop()
        
        # call Subroutine
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Subroutine calls must start with either a subroutine, class, or variable name.")
        
        varname = current_token.split()[1]
        current_token = self.tagged_tokens.pop()
        if varname in self.subroutine_variables:
            varinfo = self.subroutine_variables[varname]
            do_code.append(f'push {VAR_CONV[varinfo[1]]} {varinfo[2]}')
            line =f'call {varinfo[0]}'
            num_exp += 1
        elif varname in self.class_variables:
            varinfo = self.class_variables[varname]
            do_code.append(f'push {VAR_CONV[varinfo[1]]} {varinfo[2]}')
            line = f'call {varinfo[0]}'
            num_exp += 1
        elif current_token == "<symbol> . </symbol>":
            # assume it is a function inside current class
            line = f'call {varname}'
        else:
            do_code.append(f'push pointer 0')
            line = f'call {self.class_name}.{varname}'
            num_exp += 1

        if current_token == "<symbol> ( </symbol>":
            
            n_exp, exp_lst_code = self.compile_expression_list()
            do_code += exp_lst_code
            num_exp += n_exp
            # know current token is )
            current_token = self.tagged_tokens.pop()
            
        elif current_token == "<symbol> . </symbol>":
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith("<identifier>"):
                raise ValueError(f"Issue with token {current_token}. Subroutine calls that start with a class or variable name must contain a subroutine name.")
            
            line += f'.{current_token.split()[1]}'
    
            current_token = self.tagged_tokens.pop()
            if current_token != "<symbol> ( </symbol>":
                raise ValueError(f"Issue with token {current_token}. Do expression lists must start with a '(' symbol.")
            
            # this = False
            # if self.tagged_tokens[-1] == "<keyword> this </keyword>":
            #     this = True
            n_exp, exp_lst_code = self.compile_expression_list()
            num_exp += n_exp
            # if this:
            #     exp_lst_code = exp_lst_code[:1] + ['push pointer 0'] + exp_lst_code[1:]
            do_code += exp_lst_code
            # know current token is )
            current_token = self.tagged_tokens.pop()

        else:
            raise ValueError(f"Issue with token {current_token}. Was expecting either a '(' symbol or a '.' symbol for subroutine call.")
        
        line += f' {num_exp}'
        do_code.append(line)
        do_code.append('pop temp 0')

        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ; </symbol>":
            raise ValueError(f"Issue with token {current_token}. Do statements must end with a ';' symbol.")
        
        return do_code

    def compile_return(self):
        return_code = []
        # know keyword return
        self.tagged_tokens.pop()
        
        # check if token is ;, if so end, else parse expression
        if self.tagged_tokens[-1] == "<keyword> this </keyword>":
            return_code.append('push pointer 0')
            self.tagged_tokens.pop()
        elif self.tagged_tokens[-1] != "<symbol> ; </symbol>":
            exp_code = self.compile_expression(["<symbol> ; </symbol>"])
            return_code += exp_code
        else:
            return_code.append('push constant 0')
        # know the current token is ;
        self.tagged_tokens.pop()
        
        return_code.append('return')
        return return_code

    def compile_expression(self, expression_terminators):
        exp_code = []
        term_code = self.compile_term()
        exp_code += term_code
        
        while self.tagged_tokens[-1] not in expression_terminators:
            current_token = self.tagged_tokens.pop()
            if current_token not in OPS:
                raise ValueError("Issue with token {current_token}. Terms must be separated with a OP such as '+'.")
            op_code = OPS[current_token]

            term_code = self.compile_term()
            exp_code += term_code
            exp_code.append(op_code)
        return exp_code
            
    def compile_expression_list(self):
        num_exp = 0
        exp_lst_code = []

        if self.tagged_tokens[-1] == "<symbol> ) </symbol>":
            return num_exp, exp_lst_code

        num_exp += 1
        exp_code = self.compile_expression(["<symbol> , </symbol>", "<symbol> ) </symbol>"])
        exp_lst_code += exp_code            
        
        while self.tagged_tokens[-1] != "<symbol> ) </symbol>":
            current_token = self.tagged_tokens.pop() 
            if current_token != "<symbol> , </symbol>":
                raise ValueError("Issue with token {current_token}. Expressions must be separated with a ',' symbol.")
            
            num_exp += 1
            exp_code = self.compile_expression(["<symbol> , </symbol>", "<symbol> ) </symbol>"])
            exp_lst_code += exp_code            
            
        return num_exp, exp_lst_code

    def compile_term(self):
        term_code = []
        current_token = self.tagged_tokens.pop()
        
        if current_token.startswith('<integerConstant>'):
            term_code.append(f'push constant {current_token.split()[1]}')
        elif current_token.startswith('<stringConstant>'):
            # term_code.append('<><>string')
            # term_code.append(current_token)
            _, mid = current_token.split('> ')
            string, _ = mid.split(' <')
            term_code.append(f'push constant {len(string)}')
            term_code.append('call String.new 1')
            for char in string:
                term_code.append(f'push constant {CHAR_MAP[char]}')
                term_code.append('call String.appendChar 2')
        elif current_token in KEYWORD_CONST:
            term_code.append(KEYWORD_CONST[current_token])
        elif current_token in UNI:
            sub_term = self.compile_term()
            term_code += sub_term
            term_code.append(UNI[current_token])
        elif current_token == "<symbol> ( </symbol>":
            exp_code = self.compile_expression(["<symbol> ) </symbol>"])
            term_code += exp_code
            # know token is ]
            current_token = self.tagged_tokens.pop()
        elif current_token.startswith('<identifier>'):
            line = ''
            n = 0
            var_name = current_token.split()[1]
            if var_name in self.subroutine_variables:
                term_code.append('push '
                    + VAR_CONV[self.subroutine_variables[var_name][1]]
                    + ' ' + str(self.subroutine_variables[var_name][2])
                    )
                if self.tagged_tokens[-1] == "<symbol> . </symbol>":
                    line = 'call ' + self.subroutine_variables[var_name][0]
                    n += 1
            elif var_name in self.class_variables:
                term_code.append('push '
                    + VAR_CONV[self.class_variables[var_name][1]]
                    + ' ' + str(self.class_variables[var_name][2])
                    )
                if self.tagged_tokens[-1] == "<symbol> . </symbol>":
                    line = 'call ' + self.class_variables[var_name][0]
                    n += 1
            else:
                line = 'call ' + var_name
            # check for [
            if self.tagged_tokens[-1] == "<symbol> [ </symbol>":
                current_token = self.tagged_tokens.pop()
                exp_code = self.compile_expression(["<symbol> ] </symbol>"])
                term_code = exp_code + term_code
                term_code.append('add')
                term_code.append('pop pointer 1')
                term_code.append('push that 0')
                #  know token is ]
                current_token = self.tagged_tokens.pop()
                
            # check for .
            elif self.tagged_tokens[-1] in ["<symbol> . </symbol>", "<symbol> ( </symbol>"]:
                current_token = self.tagged_tokens.pop()
                if current_token == "<symbol> . </symbol>":
                    current_token = self.tagged_tokens.pop()
                    if not current_token.startswith('<identifier>'):
                        raise ValueError(f"Issue with token {current_token}. Was expecting a subroutine Identifier.")
                    
                    var_name = current_token.split()[1]
                    line += '.' + var_name

                    current_token = self.tagged_tokens.pop()
                    if current_token != "<symbol> ( </symbol>":
                        raise ValueError(f"Issue with token {current_token}. Subroutine calls must be followed by a '(' symbol.")

                n_exp, exp_lst_code = self.compile_expression_list()
                n += n_exp
                line += " " + str(n)
                term_code += exp_lst_code
                term_code.append(line)

                # know current token is )
                current_token = self.tagged_tokens.pop()
                # if current_token != "<symbol> ) </symbol>":
                #     raise ValueError(f"Issue with token {current_token}. Do expression lists must end with a ')' symbol.")

        else:
            raise ValueError("Issue with token {current_token}. Does not match known Term beginning tokens.")

        return term_code

