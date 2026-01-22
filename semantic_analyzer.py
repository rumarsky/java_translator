from ast_nodes import *
from typing import Dict, List, Set, Optional

class Symbol:
    def __init__(self, name: str, symbol_type: str, scope: str = ""):
        self.name = name
        self.symbol_type = symbol_type
        self.scope = scope

class SymbolTable:
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Global scope
        self.classes: Dict[str, ClassDeclaration] = {}
        self.current_scope = 0
    
    def add_scope(self):
        self.scopes.append({})
        self.current_scope += 1
    
    def remove_scope(self):
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def define(self, name: str, symbol_type: str) -> bool:
        if name in self.scopes[self.current_scope]:
            return False
        self.scopes[self.current_scope][name] = Symbol(name, symbol_type)
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def add_class(self, name: str, class_decl: ClassDeclaration):
        self.classes[name] = class_decl

class SemanticAnalyzer:
    # Built-in classes and objects
    BUILT_IN_CLASSES = {
        'System', 'String', 'Math', 'ArrayList', 'HashMap', 'LinkedList'
    }
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_class: Optional[ClassDeclaration] = None
        self.current_method: Optional[MethodDeclaration] = None
        self.errors: List[str] = []
    
    def error(self, message: str):
        self.errors.append(message)
    
    def analyze(self, program: Program) -> bool:
        # First pass: collect all class definitions
        for class_decl in program.classes:
            self.symbol_table.add_class(class_decl.name, class_decl)
        
        # Second pass: analyze each class
        for class_decl in program.classes:
            self.analyze_class(class_decl)
        
        return len(self.errors) == 0
    
    def analyze_class(self, class_decl: ClassDeclaration):
        self.current_class = class_decl
        self.symbol_table.add_scope()
        
        # Add class fields to symbol table
        for field in class_decl.fields:
            self.symbol_table.define(field.name, field.field_type)
            if field.initial_value:
                self.analyze_expression(field.initial_value)
        
        # Analyze methods
        for method in class_decl.methods:
            self.analyze_method(method)
        
        self.symbol_table.remove_scope()
        self.current_class = None
    
    def analyze_method(self, method: MethodDeclaration):
        self.current_method = method
        self.symbol_table.add_scope()
        
        # Add parameters to symbol table
        for param in method.parameters:
            self.symbol_table.define(param.name, param.param_type)
        
        # Analyze method body
        if method.body:
            self.analyze_block(method.body)
        
        self.symbol_table.remove_scope()
        self.current_method = None
    
    def analyze_block(self, block: Block):
        self.symbol_table.add_scope()
        
        for statement in block.statements:
            self.analyze_statement(statement)
        
        self.symbol_table.remove_scope()
    
    def analyze_statement(self, statement: ASTNode):
        if isinstance(statement, VariableDeclaration):
            self.analyze_variable_declaration(statement)
        elif isinstance(statement, Assignment):
            self.analyze_assignment(statement)
        elif isinstance(statement, IfStatement):
            self.analyze_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.analyze_while_statement(statement)
        elif isinstance(statement, ForStatement):
            self.analyze_for_statement(statement)
        elif isinstance(statement, ReturnStatement):
            self.analyze_return_statement(statement)
        elif isinstance(statement, MethodCall):
            self.analyze_expression(statement)
        elif isinstance(statement, Block):
            self.analyze_block(statement)
        elif isinstance(statement, BinaryOperation):
            self.analyze_expression(statement)
        elif isinstance(statement, UnaryOperation):
            self.analyze_expression(statement)
    
    def analyze_variable_declaration(self, var_decl: VariableDeclaration):
        # Check if variable already exists in current scope
        if not self.symbol_table.define(var_decl.name, var_decl.var_type):
            self.error(f"Variable '{var_decl.name}' already defined in this scope")
        
        if var_decl.initial_value:
            self.analyze_expression(var_decl.initial_value)
    
    def analyze_assignment(self, assignment: Assignment):
        # Check if target exists
        if isinstance(assignment.target, Identifier):
            symbol = self.symbol_table.lookup(assignment.target.name)
            if not symbol:
                self.error(f"Variable '{assignment.target.name}' not defined")
        
        self.analyze_expression(assignment.value)
    
    def analyze_if_statement(self, if_stmt: IfStatement):
        self.analyze_expression(if_stmt.condition)
        self.analyze_statement(if_stmt.then_block)
        if if_stmt.else_block:
            self.analyze_statement(if_stmt.else_block)
    
    def analyze_while_statement(self, while_stmt: WhileStatement):
        self.analyze_expression(while_stmt.condition)
        self.analyze_statement(while_stmt.body)
    
    def analyze_for_statement(self, for_stmt: ForStatement):
        self.symbol_table.add_scope()
        
        if for_stmt.init:
            self.analyze_statement(for_stmt.init)
        
        if for_stmt.condition:
            self.analyze_expression(for_stmt.condition)
        
        if for_stmt.update:
            self.analyze_expression(for_stmt.update)
        
        self.analyze_statement(for_stmt.body)
        
        self.symbol_table.remove_scope()
    
    def analyze_return_statement(self, ret_stmt: ReturnStatement):
        if ret_stmt.value:
            self.analyze_expression(ret_stmt.value)
    
    def analyze_expression(self, expr: ASTNode) -> Optional[str]:
        if isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup(expr.name)
            if not symbol:
                # Check if it's a built-in class or method
                if expr.name not in self.BUILT_IN_CLASSES:
                    self.error(f"Variable '{expr.name}' not defined")
                return None
            return symbol.symbol_type
        
        elif isinstance(expr, Literal):
            return expr.literal_type
        
        elif isinstance(expr, BinaryOperation):
            self.analyze_expression(expr.left)
            self.analyze_expression(expr.right)
            return self.get_binary_op_type(expr.operator)
        
        elif isinstance(expr, UnaryOperation):
            self.analyze_expression(expr.operand)
            return self.get_unary_op_type(expr.operator)
        
        elif isinstance(expr, MethodCall):
            if expr.object_ref:
                self.analyze_expression(expr.object_ref)
            
            for arg in expr.arguments:
                self.analyze_expression(arg)
            
            return None  # We don't track return types precisely
        
        elif isinstance(expr, ArrayAccess):
            self.analyze_expression(expr.array)
            self.analyze_expression(expr.index)
            return None
        
        elif isinstance(expr, NewExpression):
            # Don't require class to be defined, allow built-in classes
            for arg in expr.arguments:
                self.analyze_expression(arg)
            
            return expr.class_name
        
        elif isinstance(expr, Assignment):
            self.analyze_assignment(expr)
            return None
        
        return None
    
    def get_binary_op_type(self, operator: str) -> str:
        if operator in ['+', '-', '*', '/', '%']:
            return "numeric"
        elif operator in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
            return "boolean"
        return "unknown"
    
    def get_unary_op_type(self, operator: str) -> str:
        if operator in ['-', '+']:
            return "numeric"
        elif operator == '!':
            return "boolean"
        return "unknown"
