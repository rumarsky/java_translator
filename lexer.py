import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    CLASS = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    STATIC = auto()
    VOID = auto()
    INT = auto()
    DOUBLE = auto()
    STRING = auto()
    BOOLEAN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    NEW = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Literals
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    DOUBLE_LITERAL = auto()
    STRING_LITERAL = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUALS = auto()
    GREATER_EQUALS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Special
    EOF = auto()
    UNKNOWN = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    KEYWORDS = {
        'class': TokenType.CLASS,
        'public': TokenType.PUBLIC,
        'private': TokenType.PRIVATE,
        'protected': TokenType.PROTECTED,
        'static': TokenType.STATIC,
        'void': TokenType.VOID,
        'int': TokenType.INT,
        'double': TokenType.DOUBLE,
        'String': TokenType.STRING,
        'boolean': TokenType.BOOLEAN,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'return': TokenType.RETURN,
        'new': TokenType.NEW,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
    }
    
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.code):
            return self.code[pos]
        return None
    
    def advance(self) -> Optional[str]:
        if self.pos < len(self.code):
            char = self.code[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None
    
    def skip_whitespace(self):
        while self.peek() and self.peek().isspace():
            self.advance()
    
    def skip_line_comment(self):
        # Skip //
        self.advance()
        self.advance()
        while self.peek() and self.peek() != '\n':
            self.advance()
    
    def skip_block_comment(self):
        # Skip /*
        self.advance()
        self.advance()
        while self.peek():
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance()
                self.advance()
                break
            self.advance()
    
    def read_string(self) -> str:
        quote = self.advance()  # Skip opening quote
        value = ""
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                else:
                    value += next_char
            else:
                value += self.advance()
        
        if self.peek() != quote:
            self.error("Unterminated string")
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        value = ""
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            value += self.advance()
        
        if '.' in value:
            return Token(TokenType.DOUBLE_LITERAL, value, start_line, start_column)
        else:
            return Token(TokenType.INTEGER_LITERAL, value, start_line, start_column)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_column = self.column
        value = ""
        
        while self.peek() and (self.peek().isalnum() or self.peek() in '_$'):
            value += self.advance()
        
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_column)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            self.skip_whitespace()
            
            if self.pos >= len(self.code):
                break
            
            char = self.peek()
            start_line = self.line
            start_column = self.column
            
            # Comments
            if char == '/' and self.peek(1) == '/':
                self.skip_line_comment()
                continue
            
            if char == '/' and self.peek(1) == '*':
                self.skip_block_comment()
                continue
            
            # Strings
            if char in '"\'':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING_LITERAL, value, start_line, start_column))
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char in '_$':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators and delimiters
            if char == '+':
                self.advance()
                if self.peek() == '+':
                    self.advance()
                    self.tokens.append(Token(TokenType.INCREMENT, '++', start_line, start_column))
                elif self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_column))
            elif char == '-':
                self.advance()
                if self.peek() == '-':
                    self.advance()
                    self.tokens.append(Token(TokenType.DECREMENT, '--', start_line, start_column))
                elif self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_column))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_column))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_column))
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_column))
            elif char == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUALS, '==', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_column))
            elif char == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUALS, '!=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', start_line, start_column))
            elif char == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUALS, '<=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.LESS, '<', start_line, start_column))
            elif char == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUALS, '>=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.GREATER, '>', start_line, start_column))
            elif char == '&':
                self.advance()
                if self.peek() == '&':
                    self.advance()
                    self.tokens.append(Token(TokenType.AND, '&&', start_line, start_column))
            elif char == '|':
                self.advance()
                if self.peek() == '|':
                    self.advance()
                    self.tokens.append(Token(TokenType.OR, '||', start_line, start_column))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_column))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_column))
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_column))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_column))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_column))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_column))
            else:
                self.error(f"Unknown character: {char}")
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
