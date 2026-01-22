import streamlit as st
from parser import parse
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from datetime import datetime

class TranslationLogger:
    def __init__(self):
        self.logs = []
    
    def add_log(self, level: str, message: str):
        """Добавить логи с меткой времени"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append((level, log_entry))
    
    def info(self, message: str):
        self.add_log("INFO", message)
    
    def error(self, message: str):
        self.add_log("ERROR", message)
    
    def warning(self, message: str):
        self.add_log("WARNING", message)
    
    def success(self, message: str):
        self.add_log("SUCCESS", message)
    
    def get_logs(self):
        return self.logs
    
    def clear(self):
        self.logs = []

# Инициализируем логгер в session_state
if "logger" not in st.session_state:
    st.session_state.logger = TranslationLogger()

def translate_java_to_csharp(java_code: str, add_main: bool) -> tuple[bool, str]:
    """
    Translates Java code to C# code.
    Returns (success: bool, result: str)
    """
    logger = st.session_state.logger
    logger.clear()
    
    try:
        logger.info("🔍 Начало анализа Java кода...")
        
        # Lexical analysis and parsing
        logger.info("📝 Лексический анализ (tokenization)...")
        ast = parse(java_code)
        logger.success("✅ Лексический анализ завершен успешно")
        
        # Semantic analysis
        logger.info("🔎 Семантический анализ...")
        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            errors = "\n".join(analyzer.errors)
            for error in analyzer.errors:
                logger.error(f"Ошибка валидации: {error}")
            return False, f"Ошибки семантического анализа:\n{errors}"
        logger.success("✅ Семантический анализ завершен успешно")
        
        # Code generation
        logger.info("⚙️ Генерация C# кода...")
        generator = CodeGenerator(add_main=add_main)
        csharp_code = generator.generate(ast)
        logger.success("✅ Код на C# сгенерирован успешно")
        
        logger.success("🎉 Трансляция завершена успешно!")
        return True, csharp_code
    
    except SyntaxError as e:
        error_msg = f"Ошибка синтаксиса: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Непредвиденная ошибка: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def display_terminal_logs():
    """Отобразить терминал с логами"""
    logger = st.session_state.logger
    logs = logger.get_logs()
    
    # Контейнер для терминала
    st.subheader("🖥️ Терминал логов")
    
    # Стиль для терминала
    terminal_content = ""
    for level, log_entry in logs:
        if level == "ERROR":
            terminal_content += f"🔴 {log_entry}\n"
        elif level == "SUCCESS":
            terminal_content += f"🟢 {log_entry}\n"
        elif level == "WARNING":
            terminal_content += f"🟡 {log_entry}\n"
        else:
            terminal_content += f"⚪ {log_entry}\n"
    
    # Отобразить логи в контейнере похожем на терминал
    if logs:
        # Используем text_area для скроллируемого вывода
        st.text_area(
            "Вывод:",
            value=terminal_content,
            height=150,
            disabled=True
        )
    else:
        st.info("⏳ Логи будут отображаться здесь после запуска трансляции...")

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
    - Массивы: типы `T[]` и доступ по индексу
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
        
        add_main = st.checkbox("✅ Добавлять Main", value=True)

        if st.button("▶️ Транслировать", use_container_width=True):
            if not java_code.strip():
                st.warning("⚠️ Пожалуйста, введите Java код!")
                st.session_state.logger.warning("Попытка трансляции пустого кода")
            else:
                success, result = translate_java_to_csharp(java_code, add_main)
                
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
    
    # Постоянный терминал логов сразу после ввода кода
    display_terminal_logs()
    
    st.divider()
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
                success, result = translate_java_to_csharp(example_code, True)
                
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
        - ✅ Основные типы: int, double, String, boolean, void
        - ✅ Массивы: типы `T[]` и доступ по индексу
        - ✅ Управление потоком: if/else, while, for
        - ✅ Операторы и выражения
        - ✅ Вызовы методов и создание объектов
        - ✅ System.out.println → System.Console.WriteLine
        
        **Не поддерживается:**
        - ❌ Наследование и интерфейсы
        - ❌ Обобщения (Generics)
        - ❌ Аннотации
        - ❌ Обработка исключений
        - ❌ Создание массивов с размером (`new int[10]`) и литералы массивов
        - ❌ Lambda выражения
        - ❌ Полное сохранение модификаторов (public/private/protected/static)
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
