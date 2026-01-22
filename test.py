"""
Simple test script to verify the translator works correctly
"""

from parser import parse
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator

def test_translator():
    test_cases = [
        # Test 1: Simple calculator
        (
            "Simple Calculator",
            """class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}"""
        ),
        # Test 2: Control flow
        (
            "Control Flow",
            """class Logic {
    public void checkNumber(int n) {
        if (n > 0) {
            System.out.println("Positive");
        } else {
            System.out.println("Negative");
        }
    }
}"""
        ),
        # Test 3: Fields
        (
            "Fields",
            """class Data {
    public int value = 42;
    public String name = "Test";
}"""
        ),
    ]
    
    for test_name, java_code in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"{'='*60}")
        print("\nJava Code:")
        print(java_code)
        
        try:
            # Parse
            ast = parse(java_code)
            print("\n✓ Parsing successful")
            
            # Semantic analysis
            analyzer = SemanticAnalyzer()
            if analyzer.analyze(ast):
                print("✓ Semantic analysis successful")
            else:
                print("✗ Semantic errors:")
                for error in analyzer.errors:
                    print(f"  - {error}")
                continue
            
            # Code generation
            generator = CodeGenerator()
            csharp_code = generator.generate(ast)
            print("✓ Code generation successful")
            
            print("\nGenerated C# Code:")
            print(csharp_code)
        
        except Exception as e:
            print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    test_translator()
