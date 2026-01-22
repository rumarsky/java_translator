import streamlit as st
from parser import parse
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator

def translate_java_to_csharp(java_code: str) -> tuple[bool, str]:
    """
    Translates Java code to C# code.
    Returns (success: bool, result: str)
    """
    try:
        # Lexical analysis and parsing
        ast = parse(java_code)
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            errors = "\n".join(analyzer.errors)
            return False, f"Ошибки семантического анализа:\n{errors}"
        
        # Code generation
        generator = CodeGenerator()
        csharp_code = generator.generate(ast)
        
        return True, csharp_code
    
    except SyntaxError as e:
        return False, f"Ошибка синтаксиса: {str(e)}"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def main():
    st.set_page_config(
        page_title="Транслятор Java в C#",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("☕ Транслятор Java в C# 🔷")
    st.markdown("""
    Этот транслятор преобразует простой код Java в код C#.
    
    **Поддерживаемые функции:**
    - Классы и методы
    - Основные типы данных (int, double, String, boolean)
    - Переменные и присваивания
    - Управление потоком (if/else, while, for циклы)
    - Вызовы методов и создание объектов
    - Основные операторы и выражения
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Ввод Java кода")
        
        # Tabs для ввода и загрузки файла
        input_tab, upload_tab = st.tabs(["📄 Текст", "📁 Файл"])
        
        java_code = ""
        
        with input_tab:
            java_code = st.text_area(
                "Вставьте ваш Java код здесь:",
                height=400,
                placeholder="""class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}"""
            )
        
        with upload_tab:
            uploaded_file = st.file_uploader(
                "Загрузите Java файл",
                type=["java"]
            )
            if uploaded_file is not None:
                java_code_from_file = uploaded_file.read().decode("utf-8")
                st.success(f"✅ Файл загружен: {uploaded_file.name}")
                st.code(java_code_from_file, language="java")
                # Используем загруженный код для трансляции
                java_code = java_code_from_file
    
    with col2:
        st.subheader("🎯 Вывод кода на C#")
        
        if st.button("▶️ Транслировать", use_container_width=True):
            if not java_code.strip():
                st.warning("⚠️ Пожалуйста, введите Java код!")
            else:
                success, result = translate_java_to_csharp(java_code)
                
                if success:
                    st.success("✅ Трансляция успешна!")
                    st.code(result, language="csharp")
                    
                    # Download button
                    st.download_button(
                        label="📥 Скачать C# код",
                        data=result,
                        file_name="translated_code.cs",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Ошибка трансляции!")
                    st.code(result, language="plaintext")
    
    st.divider()
    
    # Examples section
    st.subheader("📚 Примеры")
    
    examples = {
        "Простой класс": """class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}""",
        "Управление потоком": """class Controller {
    public void checkNumber(int num) {
        if (num > 0) {
            System.out.println("Положительное");
        } else if (num < 0) {
            System.out.println("Отрицательное");
        } else {
            System.out.println("Ноль");
        }
    }
}""",
        "Циклы": """class Counter {
    public int sumNumbers(int n) {
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum = sum + i;
        }
        return sum;
    }
}""",
        "Переменные": """class Person {
    public String name = "John";
    public int age = 30;
    
    public void displayInfo() {
        System.out.println(name);
    }
}"""
    }
    
    selected_example = st.selectbox(
        "Выберите пример:",
        list(examples.keys())
    )
    
    if selected_example:
        example_code = examples[selected_example]
        
        col1_ex, col2_ex = st.columns(2)
        
        with col1_ex:
            st.code(example_code, language="java")
        
        with col2_ex:
            if st.button("🔄 Транслировать этот пример", use_container_width=True):
                success, result = translate_java_to_csharp(example_code)
                
                if success:
                    st.success("✅ Трансляция успешна!")
                    st.code(result, language="csharp")
                    st.download_button(
                        label="📥 Скачать результат",
                        data=result,
                        file_name="translated_example.cs",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Ошибка трансляции!")
                    st.code(result, language="plaintext")
    
    st.divider()
    
    # Info section
    with st.expander("ℹ️ О приложении"):
        st.markdown("""
        ### Архитектура
        
        Этот транслятор состоит из 4 основных компонентов:
        
        1. **Лексер** - Разбивает Java код на токены
        2. **Парсер** - Строит синтаксическое дерево (AST)
        3. **Семантический анализатор** - Проверяет корректность кода
        4. **Генератор кода** - Генерирует C# код
        
        ### Поддерживаемые функции
        
        **Поддерживается:**
        - ✅ Классы, методы и поля
        - ✅ Основные типы: int, double, String, boolean
        - ✅ Управление потоком: if/else, while, for
        - ✅ Операторы и выражения
        - ✅ Вызовы методов и создание объектов
        
        **Не поддерживается:**
        - ❌ Наследование и интерфейсы
        - ❌ Обобщения (Generics)
        - ❌ Аннотации
        - ❌ Обработка исключений
        - ❌ Массивы (полная поддержка)
        - ❌ Lambda выражения
        - ❌ Продвинутые функции Java
        
        ### Отображение типов
        
        | Java | C# |
        |------|-----|
        | `int` | `int` |
        | `double` | `double` |
        | `String` | `string` |
        | `boolean` | `bool` |
        | `void` | `void` |
        """)

if __name__ == "__main__":
    main()
