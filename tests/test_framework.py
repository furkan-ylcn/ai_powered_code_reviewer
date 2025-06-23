"""
AI Destekli Kod İnceleyici için test framework yapılandırması ve yardımcı programları
"""

import unittest
import tempfile
import os
import json
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

# Import'lar için proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from analyzers.python_analyzer import run_pylint
from analyzers.javascript_analyzer import run_eslint
from analyzers.ai_analyzer import analyze_with_ai
from utils.file_handler import (
    clean_code_content, 
    save_temp_file, 
    cleanup_temp_file,
    analyze_content_issues
)

class BaseTestCase(unittest.TestCase):
    """Ortak yardımcı programları olan temel test durumu."""
    
    def setUp(self):
        """Test ortamını hazırla."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.temp_files = []
        
        # Geçici dizin oluştur
        os.makedirs('temp', exist_ok=True)
    
    def tearDown(self):
        """Testlerden sonra temizle."""
        # Testler sırasında oluşturulan geçici dosyaları temizle
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    
    def create_temp_file(self, content: str, language: str) -> str:
        """Test için geçici dosya oluştur."""
        file_path = save_temp_file(content, language)
        self.temp_files.append(file_path)
        return file_path
    
    def assert_analysis_contains(self, analysis: List[Dict], expected_issues: List[str]):
        """Analizin beklenen sorunları içerdiğini doğrula."""
        found_issues = [issue.get('message', '').lower() for issue in analysis]
        
        for expected in expected_issues:
            found = any(expected.lower() in issue for issue in found_issues)
            self.assertTrue(found, f"Expected issue '{expected}' not found in analysis")
    
    def assert_severity_distribution(self, analysis: List[Dict], expected_counts: Dict[str, int]):
        """Önem derecesi dağılımının beklenen sayılarla eşleştiğini doğrula."""
        severity_counts = {}
        for issue in analysis:
            severity = issue.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity, expected_count in expected_counts.items():
            actual_count = severity_counts.get(severity, 0)
            self.assertEqual(actual_count, expected_count, 
                           f"Expected {expected_count} {severity} issues, got {actual_count}")

class TestDataProvider:
    """Bilinen sorunları olan test kod örnekleri sağlar."""
    
    PYTHON_SAMPLES = {
        "syntax_errors": """
# Syntax hataları test durumu
def broken_function(
    print("Missing closing parenthesis"
    
def another_function():
    if True
        print("Missing colon")
    
x = [1, 2, 3,]  # Trailing comma (stil sorunu olarak tespit edilmeli)
""",
        
        "unused_variables": """
# Kullanılmayan değişkenler test durumu
import os
import sys  # Bu import kullanılmıyor

def calculate_sum(numbers):
    unused_var = "This variable is never used"
    another_unused = 42
    total = 0
    
    for num in numbers:
        total += num
    
    return total

global_unused = "This is also unused"
""",
        
        "code_quality_issues": """
# Kod kalitesi sorunları test durumu
def problematic_function(data):
    # None karşılaştırması için == yerine 'is' kullanılmalı
    if data == None:
        return []
    
    # Potansiyel sıfıra bölme
    result = 10 / len(data)
    
    # Çıplak except clause
    try:
        value = data[0]
    except:
        pass
    
    # Tanımlanmamış değişken
    return undefined_variable

# Eksik docstring
def no_docs(x, y):
    return x + y

# Çok fazla argüman
def too_many_args(a, b, c, d, e, f, g, h, i, j):
    return sum([a, b, c, d, e, f, g, h, i, j])
""",
        
        "security_issues": """
# Güvenlik sorunları test durumu
import subprocess
import pickle

def unsafe_exec(user_input):
    # Tehlikeli: kullanıcı girdisi ile eval
    result = eval(user_input)
    return result

def unsafe_subprocess(command):
    # Shell injection güvenlik açığı
    subprocess.call(command, shell=True)

def unsafe_pickle(data):
    # Güvenli olmayan deserialization
    return pickle.loads(data)

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
""",
        
        "performance_issues": """
# Performans sorunları test durumu
def inefficient_loop():
    items = []
    for i in range(1000):
        # Verimsiz string concatenation
        result = ""
        for j in range(100):
            result = result + str(j)
        items.append(result)
    return items

def unnecessary_lambda():
    numbers = [1, 2, 3, 4, 5]
    # Gereksiz lambda
    squared = map(lambda x: x * x, numbers)
    return list(squared)

def nested_loops():
    # Kötü karmaşıklığa sahip iç içe döngüler
    matrix = []
    for i in range(100):
        row = []
        for j in range(100):
            for k in range(100):
                row.append(i * j * k)
        matrix.append(row)
    return matrix
""",
        
        "clean_code": '''
# Temiz kod örneği
"""Uygun yapıya sahip basit hesap makinesi modülü."""

from typing import List, Union


class Calculator:
    """Basit hesap makinesi sınıfı."""
    
    def add(self, a: float, b: float) -> float:
        """İki sayıyı topla."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """b'yi a'dan çıkar."""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """İki sayıyı çarp."""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """a'yı b'ye böl."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def calculate_average(self, numbers: List[float]) -> float:
        """Sayı listesinin ortalamasını hesapla."""
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        return sum(numbers) / len(numbers)


def main():
    """Hesap makinesi kullanımını gösteren ana fonksiyon."""
    calc = Calculator()
    
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    
    numbers = [1, 2, 3, 4, 5]
    print(f"Average of {numbers} = {calc.calculate_average(numbers)}")


if __name__ == "__main__":
    main()
'''
    }
    
    
    JAVASCRIPT_SAMPLES = {
        "syntax_errors": """
// JavaScript syntax hataları test durumu
function brokenFunction() {
    console.log("Missing semicolon")
    
    if (true) {
        console.log("Missing closing brace"
    
    var x = [1, 2, 3,]  // Trailing comma
}

// Eksik function anahtar kelimesi
invalidFunction() {
    return true;
}
""",
        
        "variable_issues": """
// JavaScript değişken sorunları test durumu
var unusedVariable = "This variable is never used";
let anotherUnused = 42;

function testFunction() {
    var x = 10;  // let veya const kullanmalı
    const y = 20;
    
    // Değişken tanımlamadan önce kullanılmış
    console.log(undeclaredVar);
    var undeclaredVar = "declared later";
    
    // Değişkeni yeniden tanımlama
    var x = 30;
    
    return y;
}

// Global değişken kirliliği
globalVar = "Should be declared with var/let/const";
""",
        
        "code_quality_issues": """
// JavaScript kod kalitesi sorunları test durumu
function problematicCode() {
    var data = null;
    
    // === yerine == kullanımı
    if (data == null) {
        console.log("Loose equality");
    }
    
    // eval kullanımı (tehlikeli)
    var userInput = "alert('XSS')";
    eval(userInput);
    
    // Return statement yok
    var result = calculateSomething();
}

function calculateSomething() {
    // Return olmayan fonksiyon
    var x = 10;
    var y = 20;
}

// Erişilemeyen kod
function unreachableCode() {
    return true;
    console.log("This will never execute");
}

// Çok fazla parametre
function tooManyParams(a, b, c, d, e, f, g, h, i, j) {
    return a + b + c + d + e + f + g + h + i + j;
}
""",
        
        "async_issues": """
// JavaScript async/await sorunları test durumu
async function asyncProblems() {
    // Async fonksiyonu await etmiyor
    fetchData();
    
    // await için eksik try-catch
    const result = await riskyAsyncOperation();
    
    return result;
}

function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve("data"), 1000);
    });
}

async function riskyAsyncOperation() {
    throw new Error("Something went wrong");
}

// Hata işleme olmayan Promise
function promiseWithoutCatch() {
    fetchData().then(data => {
        console.log(data);
    });
    // Eksik .catch()
}
""",
        
        "es6_issues": """
// JavaScript ES6+ sorunları test durumu
function es6Problems() {
    // Değişmeyen değerler için const kullanmalı
    let PI = 3.14159;
    
    // Arrow function kullanmalı
    var numbers = [1, 2, 3, 4, 5];
    var doubled = numbers.map(function(x) {
        return x * 2;
    });
    
    // Template literal kullanmalı
    var name = "John";
    var greeting = "Hello, " + name + "!";
    
    // Destructuring kullanmalı
    var person = {name: "Alice", age: 30};
    var personName = person.name;
    var personAge = person.age;
    
    return {doubled, greeting, personName, personAge};
}

// Class syntax kullanmalı
function Person(name, age) {
    this.name = name;
    this.age = age;
}

Person.prototype.greet = function() {
    return "Hello, I'm " + this.name;
};
""",
        
        "clean_code": """
// Temiz JavaScript kod örneği
'use strict';

/**
 * Uygun ES6+ syntax ile basit hesap makinesi sınıfı
 */
class Calculator {
    /**
     * İki sayıyı topla
     * @param {number} a - İlk sayı
     * @param {number} b - İkinci sayı
     * @returns {number} a ve b'nin toplamı
     */
    add(a, b) {
        return a + b;
    }
    
    /**
     * a'dan b'yi çıkar
     * @param {number} a - İlk sayı
     * @param {number} b - İkinci sayı
     * @returns {number} a ve b'nin farkı
     */
    subtract(a, b) {
        return a - b;
    }
    
    /**
     * İki sayıyı çarp
     * @param {number} a - İlk sayı
     * @param {number} b - İkinci sayı
     * @returns {number} a ve b'nin çarpımı
     */
    multiply(a, b) {
        return a * b;
    }
    
    /**
     * a'yı b'ye böl
     * @param {number} a - Bölünen
     * @param {number} b - Bölen
     * @returns {number} a ve b'nin bölümü
     * @throws {Error} Sıfıra bölme durumunda
     */
    divide(a, b) {
        if (b === 0) {
            throw new Error('Cannot divide by zero');
        }
        return a / b;
    }
    
    /**
     * Sayı dizisinin ortalamasını hesapla
     * @param {number[]} numbers - Sayı dizisi
     * @returns {number} Ortalama değer
     * @throws {Error} Dizi boş olduğunda
     */
    calculateAverage(numbers) {
        if (!Array.isArray(numbers) || numbers.length === 0) {
            throw new Error('Cannot calculate average of empty array');
        }
        
        const sum = numbers.reduce((acc, num) => acc + num, 0);
        return sum / numbers.length;
    }
}

/**
 * Demonstrasyon fonksiyonu
 */
function main() {
    const calc = new Calculator();
    
    console.log(`2 + 3 = ${calc.add(2, 3)}`);
    console.log(`10 - 4 = ${calc.subtract(10, 4)}`);
    console.log(`5 * 6 = ${calc.multiply(5, 6)}`);
    console.log(`15 / 3 = ${calc.divide(15, 3)}`);
    
    const numbers = [1, 2, 3, 4, 5];
    console.log(`Average of [${numbers.join(', ')}] = ${calc.calculateAverage(numbers)}`);
}

// Modül kullanımı için export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Calculator;
}

// Ana modül ise çalıştır
if (require.main === module) {
    main();
}
"""
    }
    
    @classmethod
    def get_sample(cls, language: str, sample_type: str) -> str:
        """Belirli bir test örneği al."""
        samples = cls.PYTHON_SAMPLES if language == 'python' else cls.JAVASCRIPT_SAMPLES
        return samples.get(sample_type, "")
    
    @classmethod
    def get_all_samples(cls, language: str) -> Dict[str, str]:
        """Bir dil için tüm test örneklerini al."""
        return cls.PYTHON_SAMPLES if language == 'python' else cls.JAVASCRIPT_SAMPLES

# Test yardımcı programları
def mock_ai_response(issues_count: int) -> str:
    """Sorun sayısına göre mock AI yanıtı oluştur."""
    if issues_count == 0:
        return """## Code Quality Assessment

**Overall Assessment**: The code appears to be well-structured and follows good practices.

### Positive Aspects:
- Proper code structure and organization
- Good variable naming conventions
- Appropriate error handling
- Clear and readable code

### Recommendations:
- Continue following these good practices
- Consider adding more comprehensive documentation
- Regular code reviews can help maintain quality

The code shows good attention to detail and follows established best practices."""
    
    elif issues_count <= 3:
        return f"""## Code Analysis Summary

**Issues Found**: {issues_count} issues detected that should be addressed.

### Priority Issues:
1. **Code Quality**: Some minor improvements needed
2. **Best Practices**: A few conventions could be better followed

### Recommendations:
- Address the static analysis findings
- Review variable naming and usage
- Consider refactoring for better readability

### Overall Assessment:
The code is generally good but has some minor issues that can be easily fixed."""
    
    else:
        return f"""## Comprehensive Code Review

**Critical Issues Found**: {issues_count} issues requiring attention.

### Major Concerns:
1. **Syntax/Logic Errors**: Critical issues that may prevent execution
2. **Security Vulnerabilities**: Potential security risks identified
3. **Performance Issues**: Code patterns that may impact performance
4. **Code Quality**: Multiple violations of best practices

### Immediate Actions Required:
- Fix all syntax and logic errors
- Address security vulnerabilities
- Refactor problematic code patterns
- Improve error handling

### Code Quality Score: Needs Improvement
This code requires significant refactoring to meet production standards."""

if __name__ == "__main__":
    # Test framework'ün temel doğrulamasını çalıştır
    print("AI Code Reviewer Test Framework")
    print("=" * 40)
    
    provider = TestDataProvider()
    
    print("Available Python test samples:")
    for sample_type in provider.PYTHON_SAMPLES.keys():
        print(f"  - {sample_type}")
    
    print("\nAvailable JavaScript test samples:")
    for sample_type in provider.JAVASCRIPT_SAMPLES.keys():
        print(f"  - {sample_type}")
    
    print("\nTest framework ready!")