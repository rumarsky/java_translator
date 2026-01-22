from typing import List, Optional
from lexer import Token, TokenType, Lexer
from ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def error(self, message: str):
        token = self.current_token()
        raise SyntaxError(f"Parse error at line {token.line}, column {token.column}: {message}")
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return EOF token
    
    def peek_token(self, offset: int = 1) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token
    
    def advance(self) -> Token:
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type}, got {token.type}")
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType) -> bool:
        if self.match(token_type):
            self.advance()
            return True
        return False
    
    def parse(self) -> Program:
        classes = []
        while not self.match(TokenType.EOF):
            classes.append(self.parse_class())
        return Program(classes)
    
    def parse_class(self) -> ClassDeclaration:
        self.expect(TokenType.CLASS)
        name_token = self.expect(TokenType.IDENTIFIER)
        class_name = name_token.value
        
        self.expect(TokenType.LBRACE)
        
        fields = []
        methods = []
        
        while not self.match(TokenType.RBRACE):
            # Check if it's a field or method
            self.parse_modifiers()
            
            field_type = self.parse_type()
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value
            
            if self.match(TokenType.ASSIGN):
                # It's a field with initialization
                self.advance()  # consume =
                initial_value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                fields.append(FieldDeclaration(name, field_type, initial_value))
            elif self.match(TokenType.SEMICOLON):
                # It's a field without initialization
                self.advance()  # consume ;
                fields.append(FieldDeclaration(name, field_type))
            elif self.match(TokenType.LPAREN):
                # It's a method
                method = self.parse_method(field_type, name)
                methods.append(method)
            else:
                self.error("Expected '=', ';' or '(' after field/method declaration")
        
        self.expect(TokenType.RBRACE)
        return ClassDeclaration(class_name, methods, fields)
    
    def parse_type(self) -> str:
        base_type = None
        if self.match(TokenType.INT):
            self.advance()
            base_type = "int"
        elif self.match(TokenType.DOUBLE):
            self.advance()
            base_type = "double"
        elif self.match(TokenType.STRING):
            self.advance()
            base_type = "String"
        elif self.match(TokenType.BOOLEAN):
            self.advance()
            base_type = "boolean"
        elif self.match(TokenType.VOID):
            self.advance()
            base_type = "void"
        elif self.match(TokenType.IDENTIFIER):
            token = self.advance()
            base_type = token.value
        else:
            self.error("Expected type")

        # Parse array suffixes: [], [][]
        while self.consume(TokenType.LBRACKET):
            self.expect(TokenType.RBRACKET)
            base_type += "[]"
        return base_type

    def parse_modifiers(self):
        # Allow any order of modifiers like "public static" or "static public"
        while self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED, TokenType.STATIC):
            self.advance()
    
    def parse_method(self, return_type: str, name: str) -> MethodDeclaration:
        self.expect(TokenType.LPAREN)
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters = self.parse_parameters()
        
        self.expect(TokenType.RPAREN)
        
        body = self.parse_block()
        
        return MethodDeclaration(name, return_type, parameters, body)
    
    def parse_parameters(self) -> List[Parameter]:
        parameters = []
        
        param_type = self.parse_type()
        param_name = self.expect(TokenType.IDENTIFIER).value
        parameters.append(Parameter(param_name, param_type))
        
        while self.consume(TokenType.COMMA):
            param_type = self.parse_type()
            param_name = self.expect(TokenType.IDENTIFIER).value
            parameters.append(Parameter(param_name, param_type))
        
        return parameters
    
    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_statement(self) -> ASTNode:
        # Variable declaration
        if self.match(TokenType.INT, TokenType.DOUBLE, TokenType.STRING, 
                      TokenType.BOOLEAN, TokenType.IDENTIFIER):
            # Check if it's a type (variable declaration)
            saved_pos = self.pos
            try:
                var_type = self.parse_type()
                if self.match(TokenType.IDENTIFIER):
                    var_name = self.expect(TokenType.IDENTIFIER).value
                    
                    initial_value = None
                    if self.consume(TokenType.ASSIGN):
                        initial_value = self.parse_expression()
                    
                    self.expect(TokenType.SEMICOLON)
                    return VariableDeclaration(var_name, var_type, initial_value)
                else:
                    # Restore position and parse as expression
                    self.pos = saved_pos
            except:
                self.pos = saved_pos
        
        # If statement
        if self.consume(TokenType.IF):
            return self.parse_if_statement()
        
        # While loop
        if self.consume(TokenType.WHILE):
            return self.parse_while_statement()
        
        # For loop
        if self.consume(TokenType.FOR):
            return self.parse_for_statement()
        
        # Return statement
        if self.consume(TokenType.RETURN):
            return self.parse_return_statement()
        
        # Block
        if self.match(TokenType.LBRACE):
            return self.parse_block()
        
        # Expression statement
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return expr
    
    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_block = self.parse_statement()
        
        else_block = None
        if self.consume(TokenType.ELSE):
            else_block = self.parse_statement()
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        body = self.parse_statement()
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        self.expect(TokenType.LPAREN)
        
        # Parse init
        init = None
        if not self.match(TokenType.SEMICOLON):
            if self.match(TokenType.INT, TokenType.DOUBLE, TokenType.STRING, TokenType.BOOLEAN, TokenType.IDENTIFIER):
                var_type = self.parse_type()
                var_name = self.expect(TokenType.IDENTIFIER).value
                
                initial_value = None
                if self.consume(TokenType.ASSIGN):
                    initial_value = self.parse_expression()
                
                init = VariableDeclaration(var_name, var_type, initial_value)
            else:
                init = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        # Parse condition
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        # Parse update
        update = None
        if not self.match(TokenType.RPAREN):
            update = self.parse_expression()
        
        self.expect(TokenType.RPAREN)
        
        body = self.parse_statement()
        
        return ForStatement(init, condition, update, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        return ReturnStatement(value)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_assignment()
    
    def parse_assignment(self) -> ASTNode:
        expr = self.parse_logical_or()
        
        if self.consume(TokenType.ASSIGN):
            value = self.parse_expression()
            return Assignment(expr, value)
        elif self.consume(TokenType.PLUS_ASSIGN):
            value = self.parse_expression()
            return Assignment(expr, BinaryOperation(expr, '+', value))
        elif self.consume(TokenType.MINUS_ASSIGN):
            value = self.parse_expression()
            return Assignment(expr, BinaryOperation(expr, '-', value))
        
        return expr
    
    def parse_logical_or(self) -> ASTNode:
        expr = self.parse_logical_and()
        
        while self.consume(TokenType.OR):
            operator = '||'
            right = self.parse_logical_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_logical_and(self) -> ASTNode:
        expr = self.parse_equality()
        
        while self.consume(TokenType.AND):
            operator = '&&'
            right = self.parse_equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_equality(self) -> ASTNode:
        expr = self.parse_comparison()
        
        while True:
            if self.consume(TokenType.EQUALS):
                operator = '=='
                right = self.parse_comparison()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.NOT_EQUALS):
                operator = '!='
                right = self.parse_comparison()
                expr = BinaryOperation(expr, operator, right)
            else:
                break
        
        return expr
    
    def parse_comparison(self) -> ASTNode:
        expr = self.parse_additive()
        
        while True:
            if self.consume(TokenType.LESS):
                operator = '<'
                right = self.parse_additive()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.GREATER):
                operator = '>'
                right = self.parse_additive()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.LESS_EQUALS):
                operator = '<='
                right = self.parse_additive()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.GREATER_EQUALS):
                operator = '>='
                right = self.parse_additive()
                expr = BinaryOperation(expr, operator, right)
            else:
                break
        
        return expr
    
    def parse_additive(self) -> ASTNode:
        expr = self.parse_multiplicative()
        
        while True:
            if self.consume(TokenType.PLUS):
                operator = '+'
                right = self.parse_multiplicative()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.MINUS):
                operator = '-'
                right = self.parse_multiplicative()
                expr = BinaryOperation(expr, operator, right)
            else:
                break
        
        return expr
    
    def parse_multiplicative(self) -> ASTNode:
        expr = self.parse_unary()
        
        while True:
            if self.consume(TokenType.MULTIPLY):
                operator = '*'
                right = self.parse_unary()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.DIVIDE):
                operator = '/'
                right = self.parse_unary()
                expr = BinaryOperation(expr, operator, right)
            elif self.consume(TokenType.MODULO):
                operator = '%'
                right = self.parse_unary()
                expr = BinaryOperation(expr, operator, right)
            else:
                break
        
        return expr
    
    def parse_unary(self) -> ASTNode:
        if self.consume(TokenType.NOT):
            operator = '!'
            expr = self.parse_unary()
            return UnaryOperation(operator, expr)
        
        if self.consume(TokenType.MINUS):
            operator = '-'
            expr = self.parse_unary()
            return UnaryOperation(operator, expr)
        
        if self.consume(TokenType.PLUS):
            operator = '+'
            expr = self.parse_unary()
            return UnaryOperation(operator, expr)
        
        if self.consume(TokenType.INCREMENT):
            operator = '++'
            expr = self.parse_postfix()
            return UnaryOperation(operator, expr)
        
        if self.consume(TokenType.DECREMENT):
            operator = '--'
            expr = self.parse_postfix()
            return UnaryOperation(operator, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        expr = self.parse_primary()
        
        while True:
            if self.consume(TokenType.INCREMENT):
                expr = UnaryOperation('post++', expr)
            elif self.consume(TokenType.DECREMENT):
                expr = UnaryOperation('post--', expr)
            elif self.consume(TokenType.DOT):
                method_name = self.expect(TokenType.IDENTIFIER).value
                
                if self.consume(TokenType.LPAREN):
                    arguments = []
                    if not self.match(TokenType.RPAREN):
                        arguments = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, method_name, arguments)
                else:
                    # Field access
                    expr = MethodCall(expr, method_name, [])
            elif self.consume(TokenType.LBRACKET):
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ArrayAccess(expr, index)
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        # Literal
        if self.match(TokenType.INTEGER_LITERAL):
            token = self.advance()
            return Literal(int(token.value), "int")
        
        if self.match(TokenType.DOUBLE_LITERAL):
            token = self.advance()
            return Literal(float(token.value), "double")
        
        if self.match(TokenType.STRING_LITERAL):
            token = self.advance()
            return Literal(token.value, "String")
        
        if self.consume(TokenType.TRUE):
            return Literal(True, "boolean")
        
        if self.consume(TokenType.FALSE):
            return Literal(False, "boolean")
        
        # Identifier or method call
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            name = token.value
            
            if self.consume(TokenType.LPAREN):
                arguments = []
                if not self.match(TokenType.RPAREN):
                    arguments = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                return MethodCall(None, name, arguments)
            
            return Identifier(name)
        
        # New expression
        if self.consume(TokenType.NEW):
            class_name_token = self.expect(TokenType.IDENTIFIER)
            class_name = class_name_token.value
            
            self.expect(TokenType.LPAREN)
            arguments = []
            if not self.match(TokenType.RPAREN):
                arguments = self.parse_arguments()
            self.expect(TokenType.RPAREN)
            
            return NewExpression(class_name, arguments)
        
        # Parenthesized expression
        if self.consume(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.error("Expected expression")
    
    def parse_arguments(self) -> List[ASTNode]:
        arguments = []
        
        arguments.append(self.parse_expression())
        
        while self.consume(TokenType.COMMA):
            arguments.append(self.parse_expression())
        
        return arguments


def parse(code: str) -> Program:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
