# Recursive Top-Down Parser
import os
from typing import SupportsAbs

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

OPS = set([
    '<symbol> + </symbol>',
    '<symbol> - </symbol>',
    '<symbol> * </symbol>',
    '<symbol> / </symbol>',
    '<symbol> &amp; </symbol>',
    '<symbol> | </symbol>',
    '<symbol> &lt; </symbol>',
    '<symbol> &gt; </symbol>',
    '<symbol> = </symbol>'
    ])

UNI = set(['<symbol> - </symbol>', '<symbol> ~ </symbol>'])

KEYWORD_CONST = set([
    '<keyword> true </keyword>',
    '<keyword> false </keyword>', 
    '<keyword> null </keyword>',
    '<keyword> this </keyword>'
    ])

class CompilationEngine:
    def __init__(self, tagged_tokens):
        self.tagged_tokens = tagged_tokens[-2:0:-1]
        self.code = []
        self.compile_class(2)
    
    def compile_class(self, padding):
        self.code.append("<class>")
        
        # check that class is defined
        current_token = self.tagged_tokens.pop()
        if current_token != "<keyword> class </keyword>":
            raise ValueError(f"Issue with token {current_token}. Was expecting <keyword> class </keyword>")
        self.code.append(padding*" " + current_token)
    
        # check that an identifier is next
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier.")
        self.code.append(padding*" " + current_token)

        # check that { is next.
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. Was expecting" + " <symbol> { </symbol>")
        self.code.append(padding*" " + current_token)

        while self.tagged_tokens:
            current_token = self.tagged_tokens.pop()
            if current_token in CLASSFIELDS:
                self.code.append(padding*" " + "<classVarDec>")
                self.tagged_tokens.append(current_token)
                self.compile_class_var(padding+2)
                self.code.append(padding*" " + "</classVarDec>")
            elif current_token in SUBROUTES:
                self.code.append(padding*" " + "<subroutineDec>")
                self.tagged_tokens.append(current_token)
                self.compile_subroutine(padding+2)
                self.code.append(padding*" " + "</subroutineDec>")
            elif current_token == "<symbol> } </symbol>":
                self.code.append(padding*" " + current_token)
            else:
                raise ValueError(f"Issue with token {current_token}. Was expecting either a class variable, subroutine or closing bracket")

        self.code.append("</class>")

    def compile_class_var(self, padding):
        # already know the current token static or field
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)
        
        current_token = self.tagged_tokens.pop()
        if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype or class name for class variable type")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier for class variable name.")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ; </symbol>":
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Class variable names must be separated by a comman ',' .")
            self.code.append(padding*" " + current_token)
            
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier for class variable name.")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()
        

        self.code.append(padding*" " + current_token)

    def compile_subroutine(self, padding):
        # already know the current token constructor, function or method
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)
        
        # check that a return type is given
        current_token = self.tagged_tokens.pop()
        if (current_token not in RETURNTYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype, void, or class name for subroutine return type")
        self.code.append(padding*" " + current_token)
        
        # check that function name is given
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Was expecting a subroutine Identifier.")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ( </symbol>":
            raise RuntimeError('is this actually hit')
            if current_token != "<symbol> . </symbol>":
                raise ValueError(f"Issue with token {current_token}. subroutine identifiers must be followed by a '.' or '('.")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Was expecting an Identifier as part of subroutine call.")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()

        # already know current token is (.
        self.code.append(padding*" " + current_token)

        self.code.append(padding*" " + "<parameterList>")
        self.compile_parameter_list(padding+2)
        self.code.append(padding*" " + "</parameterList>")
        
        # already know current token is ).
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        self.code.append(padding*" " + "<subroutineBody>")
        self.compile_subroutine_body(padding+2)
        self.code.append(padding*" " + "</subroutineBody>")
        

    def compile_parameter_list(self, padding):
        current_token = self.tagged_tokens.pop()
        if current_token == "<symbol> ) </symbol>":
            self.tagged_tokens.append(current_token)
            return
        elif (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Subroutine paramater type must be a datatype or class name.")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Subroutine parameters names must be Identifiers.")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ) </symbol>":
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Subroutine paramaters must be separated by a ','.")
            self.code.append(padding*" " + current_token)

            current_token = self.tagged_tokens.pop()
            if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
                raise ValueError(f"Issue with token {current_token}. Subroutine paramater type must be a datatype or class name.")
            self.code.append(padding*" " + current_token)

            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Subroutine parameters names must be Identifiers.")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()
        

        # put ) back in the tagged tokens.
        self.tagged_tokens.append(current_token)

    def compile_subroutine_body(self, padding):
        # check that body starts with {
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. Was expecting" + " <symbol> { </symbol>")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        
        if current_token not in VALID_SUBROUTINE1:
            raise ValueError(f"Issue with token {current_token}. Subroutine body must start with <keyword> var </keyword>, a statement token such as <keyword> let </keyword>, or" + " <symbol> } </symbol>")
        
        while current_token == '<keyword> var </keyword>':
            self.code.append(padding*" " + '<varDec>')
            self.tagged_tokens.append(current_token)
            self.compile_var_dec(padding + 2)
            self.code.append(padding*" " + '</varDec>')
            current_token = self.tagged_tokens.pop()    

        if current_token in STATEMENTS:
            self.code.append(padding*" " + '<statements>')
            self.tagged_tokens.append(current_token)
            self.compile_statements(padding + 2)
            self.code.append(padding*" " + '</statements>')
            current_token = self.tagged_tokens.pop()    
            self.code.append(padding*" " + current_token)
        elif current_token == "<symbol> } </symbol>":
            self.code.append(padding*" " + current_token)
        else:
            raise ValueError(f"Issue with token {current_token}. Subroutine after varDec must start with a statement token such as <keyword> let </keyword>, or" + " <symbol> } </symbol>")
        
    def compile_var_dec(self, padding):
        # already know token is var
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        # check that it is a type
        current_token = self.tagged_tokens.pop()
        if (current_token not in TYPES) and (not current_token.startswith('<identifier>')):
            raise ValueError(f"Issue with token {current_token}. Was expecting either a datatype or class name for class variable type")
        self.code.append(padding*" " + current_token)

        # check that it is a name
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith('<identifier>'):
            raise ValueError(f"Issue with token {current_token}. Variable names must be Identifiers")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        while current_token != "<symbol> ; </symbol>":
            # check that token is ,
            if current_token != "<symbol> , </symbol>":
                raise ValueError(f"Issue with token {current_token}. Variable names must be separated by a comman ',' .")
            self.code.append(padding*" " + current_token)
            
            # check that token is an identifier
            current_token = self.tagged_tokens.pop()
            if not current_token.startswith('<identifier>'):
                raise ValueError(f"Issue with token {current_token}. Variable names must be Identifiers")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()

        # know that token is a ;
        self.code.append(padding*" " + current_token)

    def compile_statements(self, padding):
        current_token = self.tagged_tokens[-1]
        while current_token != "<symbol> } </symbol>":
            if current_token == "<keyword> let </keyword>":
                self.code.append(padding*" " + "<letStatement>")
                self.compile_let(padding + 2)
                self.code.append(padding*" " + "</letStatement>")
            elif current_token == "<keyword> if </keyword>":
                self.code.append(padding*" " + "<ifStatement>")
                self.compile_if(padding + 2)
                self.code.append(padding*" " + "</ifStatement>")
            elif current_token == "<keyword> while </keyword>":
                self.code.append(padding*" " + "<whileStatement>")
                self.compile_while(padding + 2)
                self.code.append(padding*" " + "</whileStatement>")
            elif current_token == "<keyword> do </keyword>":
                self.code.append(padding*" " + "<doStatement>")
                self.compile_do(padding + 2)
                self.code.append(padding*" " + "</doStatement>")
            elif current_token == "<keyword> return </keyword>":
                self.code.append(padding*" " + "<returnStatement>")
                self.compile_return(padding + 2)
                self.code.append(padding*" " + "</returnStatement>")
            else:
                self.tagged_tokens.pop()
                # TODO raise error
                pass
            current_token = self.tagged_tokens[-1]

    def compile_let(self, padding):
        # know let keyword
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        # check that an identifier is next
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Let keyword must be followed by a variable name Identifier.")
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        if current_token == "<symbol> [ </symbol>":
            self.code.append(padding*" " + current_token)
            self.code.append(padding*" " + "<expression>")
            self.compile_expression(padding + 2, ["<symbol> ] </symbol>"])
            self.code.append(padding*" " + "</expression>")
            # know current token is ]
            current_token = self.tagged_tokens.pop()
            # if current_token != "<symbol> ] </symbol>":
            #     raise ValueError(f"Issue with token {current_token}. Expressions beginning with '[' must end with ']'.")
            self.code.append(padding*" " + current_token)
            current_token = self.tagged_tokens.pop()
        
        if current_token != "<symbol> = </symbol>":
            raise ValueError(f"Issue with token {current_token}. Let statement requires a '=' symbol after the variable declaration.")
        self.code.append(padding*" " + current_token)
        
        self.code.append(padding*" " + "<expression>")
        self.compile_expression(padding + 2, ["<symbol> ; </symbol>"])
        self.code.append(padding*" " + "</expression>")
        # know current token is ;
        current_token = self.tagged_tokens.pop()
        # if current_token != "<symbol> ; </symbol>":
        #     raise ValueError(f"Issue with token {current_token}. Let statement must terminate with a ';' symbol.")
        self.code.append(padding*" " + current_token)
        
    def compile_if(self, padding):
        # know keyword if
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ( </symbol>":
            raise ValueError(f"Issue with token {current_token}. If expressions must begin with a '(' symbol.")
        self.code.append(padding*" " + current_token)
        
        self.code.append(padding*" " + "<expression>")
        self.compile_expression(padding + 2, ["<symbol> ) </symbol>"])
        self.code.append(padding*" " + "</expression>")
        # know current token is )
        current_token = self.tagged_tokens.pop()
        # if current_token != "<symbol> ) </symbol>":
        #     raise ValueError(f"Issue with token {current_token}. If expressions must end with a ')' symbol.")
        self.code.append(padding*" " + current_token)
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. If statements must begin with a" + " '{' symbol.")
        self.code.append(padding*" " + current_token)

        self.code.append(padding*" " + "<statements>")
        self.compile_statements(padding + 2)
        self.code.append(padding*" " + "</statements>")
        
        # know current token is }
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        if self.tagged_tokens[-1] == "<keyword> else </keyword>":
            current_token = self.tagged_tokens.pop()
            self.code.append(padding*" " + current_token)

            current_token = self.tagged_tokens.pop()
            if current_token != "<symbol> { </symbol>":
                raise ValueError(f"Issue with token {current_token}. Else statements must begin with a" + " '{' symbol.")
            self.code.append(padding*" " + current_token)

            self.code.append(padding*" " + "<statements>")
            self.compile_statements(padding + 2)
            self.code.append(padding*" " + "</statements>")
            
            # know current token is }
            current_token = self.tagged_tokens.pop()
            self.code.append(padding*" " + current_token)

    def compile_while(self, padding):
        # know keyword while
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ( </symbol>":
            raise ValueError(f"Issue with token {current_token}. While expressions must begin with a '(' symbol.")
        self.code.append(padding*" " + current_token)
        
        self.code.append(padding*" " + "<expression>")
        self.compile_expression(padding + 2, ["<symbol> ) </symbol>"])
        self.code.append(padding*" " + "</expression>")

        # know current token is ) 
        current_token = self.tagged_tokens.pop()
        # if current_token != "<symbol> ) </symbol>":
        #     raise ValueError(f"Issue with token {current_token}. While expressions must end with a ')' symbol.")
        self.code.append(padding*" " + current_token)
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> { </symbol>":
            raise ValueError(f"Issue with token {current_token}. While statements must begin with a" + " '{' symbol.")
        self.code.append(padding*" " + current_token)

        self.code.append(padding*" " + "<statements>")
        self.compile_statements(padding + 2)
        self.code.append(padding*" " + "</statements>")
        
        # know current token is }
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

    def compile_do(self, padding):
        # know keyword do
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        # call Subroutine
        current_token = self.tagged_tokens.pop()
        if not current_token.startswith("<identifier>"):
            raise ValueError(f"Issue with token {current_token}. Subroutine calls must start with either a subroutine, class, or variable name.")
        self.code.append(padding*" " + current_token)   

        current_token = self.tagged_tokens.pop()
        if current_token == "<symbol> ( </symbol>":
            self.code.append(padding*" " + current_token)
            
            self.code.append(padding*" " + "<expressionList>")
            self.compile_expression_list(padding + 2)
            self.code.append(padding*" " + "</expressionList>")

            # know current token is )
            current_token = self.tagged_tokens.pop()
            # if current_token != "<symbol> ) </symbol>":
            #     raise ValueError(f"Issue with token {current_token}. Do expression lists must end with a ')' symbol.")
            self.code.append(padding*" " + current_token)

        elif current_token == "<symbol> . </symbol>":
            self.code.append(padding*" " + current_token)

            current_token = self.tagged_tokens.pop()
            if not current_token.startswith("<identifier>"):
                raise ValueError(f"Issue with token {current_token}. Subroutine calls that start with a class or variable name must contain a subroutine name.")
            self.code.append(padding*" " + current_token)   
    
            current_token = self.tagged_tokens.pop()
            if current_token != "<symbol> ( </symbol>":
                raise ValueError(f"Issue with token {current_token}. Do expression lists must start with a '(' symbol.")
            self.code.append(padding*" " + current_token)
            
            self.code.append(padding*" " + "<expressionList>")
            self.compile_expression_list(padding + 2)
            self.code.append(padding*" " + "</expressionList>")

            # know current token is )
            current_token = self.tagged_tokens.pop()
            # if current_token != "<symbol> ) </symbol>":
            #     raise ValueError(f"Issue with token {current_token}. Do expression lists must end with a ')' symbol.")
            self.code.append(padding*" " + current_token)

        else:
            raise ValueError(f"Issue with token {current_token}. Was expecting either a '(' symbol or a '.' symbol for subroutine call.")
        
        
        current_token = self.tagged_tokens.pop()
        if current_token != "<symbol> ; </symbol>":
            raise ValueError(f"Issue with token {current_token}. Do statements must end with a ';' symbol.")
        self.code.append(padding*" " + current_token)


    def compile_return(self, padding):
        # know keyword return
        current_token = self.tagged_tokens.pop()
        self.code.append(padding*" " + current_token)

        # check if token is ;, if so end, else parse expression
        if self.tagged_tokens[-1] != "<symbol> ; </symbol>":
            self.code.append(padding*" " + "<expression>")
            self.compile_expression(padding + 2, ["<symbol> ; </symbol>"])
            self.code.append(padding*" " + "</expression>")

        # know the current token is ;
        current_token = self.tagged_tokens.pop()
        # if current_token != "<symbol> ; </symbol>":
        #     raise ValueError("Issue with token {current_token}. Return statements must end with a ';' symbol.")
        self.code.append(padding*" " + current_token)
        
    def compile_expression(self, padding, expression_terminators):
        self.code.append(padding*" " + "<term>")
        self.compile_term(padding + 2)
        self.code.append(padding*" " + "</term>")
        
        while self.tagged_tokens[-1] not in expression_terminators:
            current_token = self.tagged_tokens.pop()
            if current_token not in OPS:
                raise ValueError("Issue with token {current_token}. Terms must be separated with a OP such as '+'.")
            self.code.append(padding*" " + current_token)

            self.code.append(padding*" " + "<term>")
            self.compile_term(padding + 2)
            self.code.append(padding*" " + "</term>")

    def compile_expression_list(self, padding):
        if self.tagged_tokens[-1] == "<symbol> ) </symbol>":
            return

        self.code.append(padding*" " + "<expression>")
        self.compile_expression(padding + 2, ["<symbol> , </symbol>", "<symbol> ) </symbol>"])
        self.code.append(padding*" " + "</expression>")

        while self.tagged_tokens[-1] != "<symbol> ) </symbol>":
            current_token = self.tagged_tokens.pop() 
            if current_token != "<symbol> , </symbol>":
                raise ValueError("Issue with token {current_token}. Expressions must be separated with a ',' symbol.")
            self.code.append(padding*" " + current_token)
            
            self.code.append(padding*" " + "<expression>")
            self.compile_expression(padding + 2, ["<symbol> , </symbol>", "<symbol> ) </symbol>"])
            self.code.append(padding*" " + "</expression>")

    def compile_term(self, padding):
        current_token = self.tagged_tokens.pop()
        
        if current_token.startswith('<integerConstant>') \
            or current_token.startswith('<stringConstant>') \
            or current_token in KEYWORD_CONST:
            self.code.append(padding*" " + current_token)
        elif current_token in UNI:
            self.code.append(padding*" " + current_token)
            self.code.append(padding*" " + "<term>")
            self.compile_term(padding + 2)
            self.code.append(padding*" " + "</term>")
        elif current_token == "<symbol> ( </symbol>":
            self.code.append(padding*" " + current_token)
            self.code.append(padding*" " + "<expression>")
            self.compile_expression(padding + 2, ["<symbol> ) </symbol>"])
            self.code.append(padding*" " + "</expression>")
            # know token is ]
            current_token = self.tagged_tokens.pop()
            self.code.append(padding*" " + current_token)
        elif current_token.startswith('<identifier>'):
            self.code.append(padding*" " + current_token)
            # check for [
            if self.tagged_tokens[-1] == "<symbol> [ </symbol>":
                current_token = self.tagged_tokens.pop()
                self.code.append(padding*" " + current_token)
                self.code.append(padding*" " + "<expression>")
                self.compile_expression(padding + 2, ["<symbol> ] </symbol>"])
                self.code.append(padding*" " + "</expression>")
                # know token is ]
                current_token = self.tagged_tokens.pop()
                self.code.append(padding*" " + current_token)
            # check for .
            elif self.tagged_tokens[-1] in ["<symbol> . </symbol>", "<symbol> ( </symbol>"]:
                current_token = self.tagged_tokens.pop()
                if current_token == "<symbol> . </symbol>":
                    self.code.append(padding*" " + current_token)
                    current_token = self.tagged_tokens.pop()
                    if not current_token.startswith('<identifier>'):
                        raise ValueError(f"Issue with token {current_token}. Was expecting a subroutine Identifier.")
                    self.code.append(padding*" " + current_token)
                    current_token = self.tagged_tokens.pop()
                    if current_token != "<symbol> ( </symbol>":
                        raise ValueError(f"Issue with token {current_token}. Subroutine calls must be followed by a '(' symbol.")

                self.code.append(padding*" " + current_token)
                self.code.append(padding*" " + "<expressionList>")
                self.compile_expression_list(padding + 2)
                self.code.append(padding*" " + "</expressionList>")
            
                # know current token is )
                current_token = self.tagged_tokens.pop()
                # if current_token != "<symbol> ) </symbol>":
                #     raise ValueError(f"Issue with token {current_token}. Do expression lists must end with a ')' symbol.")
                self.code.append(padding*" " + current_token)
        else:
            raise ValueError("Issue with token {current_token}. Does not match known Term beginning tokens.")


