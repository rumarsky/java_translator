from ast_nodes import *
from typing import List, Optional

class CodeGenerator:
    def __init__(self, add_main: bool = True):
        self.indent_level = 0
        self.indent_str = "    "
        self.add_main = add_main
    
    def generate(self, program: Program) -> str:
        code = ""
        code += self.generate_usings()
        code += "\n"
        
        for class_decl in program.classes:
            code += self.generate_class(class_decl)
            code += "\n"
        
        return code
    
    def generate_usings(self) -> str:
        usings = [
            "using System;",
            "using System.Collections.Generic;",
            "using System.Linq;",
            "using System.Text;"
        ]
        return "\n".join(usings)
    
    def indent(self):
        self.indent_level += 1
    
    def dedent(self):
        if self.indent_level > 0:
            self.indent_level -= 1
    
    def get_indent(self) -> str:
        return self.indent_str * self.indent_level
    
    def generate_class(self, class_decl: ClassDeclaration) -> str:
        code = f"{self.get_indent()}public class {class_decl.name}\n"
        code += f"{self.get_indent()}{{\n"
        
        self.indent()
        
        # Generate fields
        for field in class_decl.fields:
            code += self.generate_field(field)
        
        if class_decl.fields and class_decl.methods:
            code += "\n"

        # Ensure entry point exists so generated code runs as a console app.
        if self.add_main and not self.has_main_method(class_decl):
            code += self.generate_main_stub()
            if class_decl.methods:
                code += "\n"
        
        # Generate methods
        for i, method in enumerate(class_decl.methods):
            code += self.generate_method(method)
            if i < len(class_decl.methods) - 1:
                code += "\n"
        
        self.dedent()
        
        code += f"{self.get_indent()}}}\n"
        
        return code
    
    def generate_field(self, field: FieldDeclaration) -> str:
        code = f"{self.get_indent()}public {self.convert_type(field.field_type)} {field.name}"
        
        if field.initial_value:
            code += " = " + self.generate_expression(field.initial_value)
        
        code += ";\n"
        return code
    
    def generate_method(self, method: MethodDeclaration) -> str:
        return_type = self.convert_type(method.return_type)
        
        params = ", ".join(
            f"{self.convert_type(p.param_type)} {p.name}" 
            for p in method.parameters
        )
        
        code = f"{self.get_indent()}public {return_type} {method.name}({params})\n"
        code += self.generate_block(method.body)
        
        return code

    def has_main_method(self, class_decl: ClassDeclaration) -> bool:
        return any(method.name == "Main" for method in class_decl.methods)

    def generate_main_stub(self) -> str:
        code = f"{self.get_indent()}public static void Main(string[] args)\n"
        code += f"{self.get_indent()}{{\n"
        self.indent()
        code += f"{self.get_indent()}// Entry point\n"
        self.dedent()
        code += f"{self.get_indent()}}}\n"
        return code
    
    def generate_block(self, block: Block) -> str:
        code = f"{self.get_indent()}{{\n"
        
        self.indent()
        
        for statement in block.statements:
            code += self.generate_statement(statement)
        
        self.dedent()
        
        code += f"{self.get_indent()}}}\n"
        
        return code
    
    def generate_statement(self, statement: ASTNode) -> str:
        if isinstance(statement, VariableDeclaration):
            return self.generate_variable_declaration(statement)
        elif isinstance(statement, Assignment):
            return self.generate_assignment(statement)
        elif isinstance(statement, IfStatement):
            return self.generate_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            return self.generate_while_statement(statement)
        elif isinstance(statement, ForStatement):
            return self.generate_for_statement(statement)
        elif isinstance(statement, ReturnStatement):
            return self.generate_return_statement(statement)
        elif isinstance(statement, Block):
            return self.generate_block(statement)
        elif isinstance(statement, MethodCall):
            return f"{self.get_indent()}{self.generate_expression(statement)};\n"
        elif isinstance(statement, BinaryOperation):
            return f"{self.get_indent()}{self.generate_expression(statement)};\n"
        elif isinstance(statement, UnaryOperation):
            return f"{self.get_indent()}{self.generate_expression(statement)};\n"
        else:
            return f"{self.get_indent()}// Unknown statement\n"
    
    def generate_variable_declaration(self, var_decl: VariableDeclaration) -> str:
        code = f"{self.get_indent()}{self.convert_type(var_decl.var_type)} {var_decl.name}"
        
        if var_decl.initial_value:
            code += " = " + self.generate_expression(var_decl.initial_value)
        
        code += ";\n"
        return code
    
    def generate_assignment(self, assignment: Assignment) -> str:
        target = self.generate_expression(assignment.target)
        value = self.generate_expression(assignment.value)
        return f"{self.get_indent()}{target} = {value};\n"
    
    def generate_if_statement(self, if_stmt: IfStatement) -> str:
        code = f"{self.get_indent()}if ({self.generate_expression(if_stmt.condition)})\n"
        
        if isinstance(if_stmt.then_block, Block):
            code += self.generate_block(if_stmt.then_block)
        else:
            self.indent()
            code += self.generate_statement(if_stmt.then_block)
            self.dedent()
        
        if if_stmt.else_block:
            code += f"{self.get_indent()}else\n"
            
            if isinstance(if_stmt.else_block, Block):
                code += self.generate_block(if_stmt.else_block)
            else:
                self.indent()
                code += self.generate_statement(if_stmt.else_block)
                self.dedent()
        
        return code
    
    def generate_while_statement(self, while_stmt: WhileStatement) -> str:
        code = f"{self.get_indent()}while ({self.generate_expression(while_stmt.condition)})\n"
        
        if isinstance(while_stmt.body, Block):
            code += self.generate_block(while_stmt.body)
        else:
            self.indent()
            code += self.generate_statement(while_stmt.body)
            self.dedent()
        
        return code
    
    def generate_for_statement(self, for_stmt: ForStatement) -> str:
        init_str = ""
        if for_stmt.init:
            if isinstance(for_stmt.init, VariableDeclaration):
                init_str = f"{self.convert_type(for_stmt.init.var_type)} {for_stmt.init.name}"
                if for_stmt.init.initial_value:
                    init_str += " = " + self.generate_expression(for_stmt.init.initial_value)
            else:
                init_str = self.generate_expression(for_stmt.init)
        
        condition_str = ""
        if for_stmt.condition:
            condition_str = self.generate_expression(for_stmt.condition)
        
        update_str = ""
        if for_stmt.update:
            update_str = self.generate_expression(for_stmt.update)
        
        code = f"{self.get_indent()}for ({init_str}; {condition_str}; {update_str})\n"
        
        if isinstance(for_stmt.body, Block):
            code += self.generate_block(for_stmt.body)
        else:
            self.indent()
            code += self.generate_statement(for_stmt.body)
            self.dedent()
        
        return code
    
    def generate_return_statement(self, ret_stmt: ReturnStatement) -> str:
        if ret_stmt.value:
            return f"{self.get_indent()}return {self.generate_expression(ret_stmt.value)};\n"
        else:
            return f"{self.get_indent()}return;\n"
    
    def generate_expression(self, expr: ASTNode) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, Literal):
            return self.generate_literal(expr)
        
        elif isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            return f"({left} {expr.operator} {right})"
        
        elif isinstance(expr, UnaryOperation):
            operand = self.generate_expression(expr.operand)
            if expr.operator in ['post++', 'post--']:
                # Avoid parentheses: C# disallows parenthesized increment as statement-expression.
                return f"{operand}{expr.operator[4:]}"
            elif expr.operator in ['++', '--']:
                # Prefix increment/decrement should also stay un-parenthesized for statement-expression usage.
                return f"{expr.operator}{operand}"
            else:
                return f"({expr.operator}{operand})"
        
        elif isinstance(expr, MethodCall):
            return self.generate_method_call(expr)
        
        elif isinstance(expr, ArrayAccess):
            array = self.generate_expression(expr.array)
            index = self.generate_expression(expr.index)
            return f"{array}[{index}]"
        
        elif isinstance(expr, NewExpression):
            return self.generate_new_expression(expr)
        
        elif isinstance(expr, Assignment):
            target = self.generate_expression(expr.target)
            value = self.generate_expression(expr.value)
            return f"({target} = {value})"
        
        else:
            return ""
    
    def generate_literal(self, literal: Literal) -> str:
        if literal.literal_type == "String":
            # Escape special characters
            value = str(literal.value)
            value = value.replace("\\", "\\\\")
            value = value.replace('"', '\\"')
            value = value.replace("\n", "\\n")
            value = value.replace("\t", "\\t")
            return f'"{value}"'
        elif literal.literal_type == "boolean":
            return "true" if literal.value else "false"
        elif literal.literal_type == "double":
            return str(literal.value)
        else:
            return str(literal.value)
    
    def generate_method_call(self, method_call: MethodCall) -> str:
        args = ", ".join(
            self.generate_expression(arg) 
            for arg in method_call.arguments
        )
        
        if method_call.object_ref:
            # Check if this is System.out.println() before generating the object ref
            # because object_ref might be a MethodCall for System.out()
            if isinstance(method_call.object_ref, MethodCall):
                # Check for System.out() pattern
                obj_ref = method_call.object_ref
                if (obj_ref.method_name == "out" and 
                    isinstance(obj_ref.object_ref, Identifier) and 
                    obj_ref.object_ref.name == "System" and
                    method_call.method_name == "println"):
                    return f"System.Console.WriteLine({args})"
            
            obj = self.generate_expression(method_call.object_ref)
            
            # Handle System.out.println() -> System.Console.WriteLine()
            if obj == "System.out" and method_call.method_name == "println":
                return f"System.Console.WriteLine({args})"
            
            return f"{obj}.{method_call.method_name}({args})"
        else:
            # Static method or function
            return f"{method_call.method_name}({args})"
    
    def generate_new_expression(self, new_expr: NewExpression) -> str:
        args = ", ".join(
            self.generate_expression(arg) 
            for arg in new_expr.arguments
        )
        return f"new {new_expr.class_name}({args})"
    
    def convert_type(self, java_type: str) -> str:
        """Convert Java types to C# types"""
        type_map = {
            "int": "int",
            "double": "double",
            "String": "string",
            "boolean": "bool",
            "void": "void",
        }
        return type_map.get(java_type, java_type)
