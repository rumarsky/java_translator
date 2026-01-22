# AST Node definitions for the translator

class ASTNode:
    """Base class for all AST nodes"""
    pass

class Program(ASTNode):
    def __init__(self, classes):
        self.classes = classes

class ClassDeclaration(ASTNode):
    def __init__(self, name, methods, fields):
        self.name = name
        self.methods = methods
        self.fields = fields

class MethodDeclaration(ASTNode):
    def __init__(self, name, return_type, parameters, body):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
        self.body = body

class FieldDeclaration(ASTNode):
    def __init__(self, name, field_type, initial_value=None):
        self.name = name
        self.field_type = field_type
        self.initial_value = initial_value

class Parameter(ASTNode):
    def __init__(self, name, param_type):
        self.name = name
        self.param_type = param_type

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VariableDeclaration(ASTNode):
    def __init__(self, name, var_type, initial_value=None):
        self.name = name
        self.var_type = var_type
        self.initial_value = initial_value

class Assignment(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStatement(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class MethodCall(ASTNode):
    def __init__(self, object_ref, method_name, arguments):
        self.object_ref = object_ref
        self.method_name = method_name
        self.arguments = arguments

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOperation(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class Literal(ASTNode):
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type

class ReturnStatement(ASTNode):
    def __init__(self, value=None):
        self.value = value

class ArrayAccess(ASTNode):
    def __init__(self, array, index):
        self.array = array
        self.index = index

class NewExpression(ASTNode):
    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments
