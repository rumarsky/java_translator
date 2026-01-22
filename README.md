# Java to C# Translator 🔄

Простой транслятор, который преобразует Java код в C#. Проект реализован на Python с фронтэнд на Streamlit.

## Архитектура

Транслятор состоит из 4 основных компонентов:

### 1. **Лексер** (`lexer.py`)
- Разбивает Java исходный код на токены
- Поддерживает:
  - Ключевые слова (class, public, if, while, for и т.д.)
  - Идентификаторы и литералы
  - Операторы и разделители
  - Комментарии (однострочные и многострочные)

### 2. **Парсер** (`parser.py`)
- Строит Abstract Syntax Tree (AST) из токенов
- Использует рекурсивный спуск для парсинга
- Поддерживает:
  - Объявления классов и методов
  - Переменные и присваивания
  - Управление потоком (if/else, while, for)
  - Выражения и вызовы методов

### 3. **Семантический анализатор** (`semantic_analyzer.py`)
- Проверяет корректность AST дерева
- Отслеживает области видимости переменных
- Обнаруживает ошибки:
  - Использование неопределённых переменных
  - Повторное определение переменных
  - Использование неопределённых классов

### 4. **Генератор кода** (`code_generator.py`)
- Генерирует C# код на основе AST дерева
- Преобразует:
  - Типы данных (int → int, String → string, boolean → bool)
  - Структуры управления потоком
  - Вызовы методов

## Поддерживаемые функции

✅ **Поддерживается:**
- Классы и методы
- Поля класса
- Основные типы данных: `int`, `double`, `String`, `boolean`, `void`
- Переменные и присваивания
- Условные операторы: `if`, `else`
- Циклы: `while`, `for`
- Операторы: `+`, `-`, `*`, `/`, `%`
- Логические операторы: `&&`, `||`, `!`
- Операторы сравнения: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Вызовы методов
- Создание объектов (`new`)
- Встроенные классы: `System`, `String`, `Math`
- Комментарии

❌ **Не поддерживается:**
- Наследование и интерфейсы
- Обобщения (Generics)
- Аннотации
- Обработка исключений
- Массивы (частично)
- Lambda выражения
- Вложенные классы
- Статические переменные

## Установка и использование

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск Streamlit приложения

```bash
streamlit run app.py
```

Приложение откроется в браузере по адресу `http://localhost:8501`

### Тестирование

```bash
python3 test.py
```

## Примеры

### Пример 1: Простой класс с методами

**Java код:**
```java
class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
}
```

**Сгенерированный C# код:**
```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class Calculator
{
    public int add(int a, int b)
    {
        return (a + b);
    }
    
    public int multiply(int a, int b)
    {
        return (a * b);
    }
}
```

### Пример 2: Управление потоком

**Java код:**
```java
class Logic {
    public void processNumber(int n) {
        if (n > 0) {
            System.out.println("Positive");
        } else if (n < 0) {
            System.out.println("Negative");
        } else {
            System.out.println("Zero");
        }
    }
}
```

**Сгенерированный C# код:**
```csharp
public class Logic
{
    public void processNumber(int n)
    {
        if ((n > 0))
        {
            System.out().println("Positive");
        }
        else if ((n < 0))
        {
            System.out().println("Negative");
        }
        else
        {
            System.out().println("Zero");
        }
    }
}
```

### Пример 3: Циклы

**Java код:**
```java
class Counter {
    public int sumNumbers(int n) {
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum = sum + i;
        }
        return sum;
    }
}
```

## Структура проекта

```
java_translator/
├── app.py                    # Streamlit приложение (фронтэнд)
├── lexer.py                 # Лексический анализатор
├── parser.py                # Синтаксический анализатор
├── semantic_analyzer.py     # Семантический анализатор
├── code_generator.py        # Генератор C# кода
├── ast_nodes.py             # Определения узлов AST
├── test.py                  # Тестовый скрипт
├── requirements.txt         # Python зависимости
├── README.md                # Документация
└── examples/                # Примеры Java кода
    ├── example1_calculator.java
    ├── example2_control_flow.java
    ├── example3_loops.java
    └── example4_fields.java
```

## Типы данных - Отображение

| Java | C# |
|------|-----|
| `int` | `int` |
| `double` | `double` |
| `String` | `string` |
| `boolean` | `bool` |
| `void` | `void` |

## Ограничения

1. **Конвертация методов**: Методы вроде `System.out.println()` конвертируются буквально, что может не работать в C#. Они требуют ручного преобразования.

2. **Встроенные методы**: Встроенные Java методы (как `String.length()`, `Math.sqrt()`) требуют ручного переписания на C# эквиваленты.

3. **Импорты**: Импорты не обрабатываются и не включаются в сгенерированный код.

4. **Проверка типов**: Семантический анализатор не проверяет совместимость типов полностью.

## Развитие проекта

Возможные улучшения:
- Поддержка массивов
- Поддержка наследования
- Лучшая обработка встроенных методов
- Генерация автоматического маппинга методов (System.out.println → Console.WriteLine)
- Поддержка исключений
- Оптимизация сгенерированного кода

## Автор

Проект создан для обучения основам трансляции и компиляции.

## Лицензия

MIT
