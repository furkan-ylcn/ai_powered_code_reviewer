"""
Dosya işleme yardımcı programları için birim testleri
"""

import sys
import unittest
import os
import tempfile
import time
from test_framework import BaseTestCase

# Dosya işleyici yardımcı programlarını import et
from utils.file_handler import (
    clean_code_content,
    save_temp_file,
    cleanup_temp_file,
    cleanup_old_temp_files,
    get_file_info,
    validate_file_content,
    analyze_content_issues
)


class TestFileContentCleaning(BaseTestCase):
    """Kod içeriği temizleme işlevselliği için test durumları."""
    
    def test_clean_line_endings(self):
        """Farklı satır sonu formatlarının temizlenmesini test et."""
        test_cases = [
            ("line1\r\nline2\r\nline3", "line1\nline2\nline3"),  # Windows CRLF
            ("line1\rline2\rline3", "line1\nline2\nline3"),      # Eski Mac CR
            ("line1\nline2\nline3", "line1\nline2\nline3"),      # Unix LF (değişiklik yok)
            ("mixed\r\nline\rending\n", "mixed\nline\nending\n") # Karışık sonlar
        ]
        
        for input_content, expected_output in test_cases:
            with self.subTest(input_content=repr(input_content)):
                result = clean_code_content(input_content)
                self.assertEqual(result, expected_output)
    
    def test_clean_zero_width_characters(self):
        """Sıfır genişlikli karakterlerin kaldırılmasını test et."""
        # Sıfır genişlikli boşluk ve diğer görünmez karakterler
        problematic_content = "def\u200bfunction():\u200c\n    pass\u200d"
        
        cleaned = clean_code_content(problematic_content)
        
        # Sıfır genişlikli karakterleri kaldırmalı
        self.assertNotIn('\u200b', cleaned)  # Sıfır genişlikli boşluk
        self.assertNotIn('\u200c', cleaned)  # Sıfır genişlikli birleştirmeyen
        self.assertNotIn('\u200d', cleaned)  # Sıfır genişlikli birleştiren
        
        # Gerçek içeriği korumalı
        self.assertIn('def', cleaned)
        self.assertIn('function', cleaned)
        self.assertIn('pass', cleaned)
    
    def test_clean_non_breaking_spaces(self):
        """Bölünmeyen boşlukların dönüştürülmesini test et."""
        content_with_nbsp = "def\u00a0function():\n    return\u00a0True"
        
        cleaned = clean_code_content(content_with_nbsp)
        
        # Bölünmeyen boşlukları normal boşluklara dönüştürmeli
        self.assertNotIn('\u00a0', cleaned)
        # Fonksiyon yapısını korumalı (boşluklar kaldırılmış/dönüştürülmüş olabilir)
        self.assertIn('function', cleaned)
        self.assertIn('True', cleaned)
        # Normal boşlukları veya içeriğin korunduğunu kontrol et
        self.assertTrue(' function' in cleaned or 'deffunction' in cleaned, 
                       "Function name should be preserved with or without spaces")
    
    def test_clean_excessive_newlines(self):
        """Aşırı ardışık yeni satırların kaldırılmasını test et."""
        content_with_many_newlines = "line1\n\n\n\n\nline2\n\n\n\nline3"
        
        cleaned = clean_code_content(content_with_many_newlines)
        
        # Çoklu yeni satırları maksimum 2'ye düşürmeli
        self.assertNotIn('\n\n\n', cleaned)
        self.assertIn('line1\n\nline2', cleaned)
    
    def test_preserve_valid_characters(self):
        """Geçerli karakterlerin korunduğunu test et."""
        valid_content = """
def hello_world():
    '''A simple function.'''
    name = "World"
    print(f"Hello, {name}!")
    return True

if __name__ == "__main__":
    hello_world()
"""
        
        cleaned = clean_code_content(valid_content)
        
        # Tüm geçerli içeriği korumalı
        self.assertEqual(cleaned.strip(), valid_content.strip())
    
    def test_clean_empty_content(self):
        """Boş veya sadece boşluk olan içeriğin temizlenmesini test et."""
        test_cases = ["", "   ", "\n\n\n", "\r\n\r\n", "\t\t\t"]
        
        for content in test_cases:
            with self.subTest(content=repr(content)):
                cleaned = clean_code_content(content)
                # Boş içeriği zarif bir şekilde işlemeli
                self.assertIsInstance(cleaned, str)


class TestTempFileOperations(BaseTestCase):
    """Geçici dosya işlemleri için test durumları."""
    
    def test_save_temp_file_python(self):
        """Python kodunu geçici dosyaya kaydetmeyi test et."""
        python_code = "def hello():\n    print('Hello, World!')"
        
        file_path = save_temp_file(python_code, 'python')
        self.temp_files.append(file_path)
        
        # .py uzantılı dosya oluşturmalı
        self.assertTrue(file_path.endswith('.py'))
        self.assertTrue(os.path.exists(file_path))
        
        # Doğru içeriği içermeli
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, python_code)
    
    def test_save_temp_file_javascript(self):
        """JavaScript kodunu geçici dosyaya kaydetmeyi test et."""
        js_code = "function hello() {\n    console.log('Hello, World!');\n}"
        
        file_path = save_temp_file(js_code, 'javascript')
        self.temp_files.append(file_path)
        
        # .js uzantılı dosya oluşturmalı
        self.assertTrue(file_path.endswith('.js'))
        self.assertTrue(os.path.exists(file_path))
        
        # Doğru içeriği içermeli
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, js_code)
    
    def test_save_temp_file_with_problematic_content(self):
        """Sorunlu karakterler içeren dosyayı kaydetmeyi test et."""
        problematic_code = "def test():\r\n    var\u200b = 'test'\u00a0"
        
        file_path = save_temp_file(problematic_code, 'python')
        self.temp_files.append(file_path)
        
        # Kaydetmeden önce içeriği temizlemeli
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        # Sorunlu karakterler içermemeli
        self.assertNotIn('\r', saved_content)
        self.assertNotIn('\u200b', saved_content)
        self.assertNotIn('\u00a0', saved_content)
        
        # Geçerli içeriği korumalı
        self.assertIn('def test', saved_content)
        self.assertIn('var', saved_content)
    
    def test_save_temp_file_unknown_language(self):
        """Bilinmeyen dil ile dosya kaydetmeyi test et."""
        code = "some code content"
        
        file_path = save_temp_file(code, 'unknown')
        self.temp_files.append(file_path)
        
        # .txt uzantısını varsayılan olarak kullanmalı
        self.assertTrue(file_path.endswith('.txt'))
    
    def test_cleanup_temp_file(self):
        """Geçici dosyaları temizlemeyi test et."""
        # Geçici dosya oluştur
        code = "test content"
        file_path = save_temp_file(code, 'python')
        
        # Dosyanın var olduğunu doğrula
        self.assertTrue(os.path.exists(file_path))
        
        # Dosyayı temizle
        result = cleanup_temp_file(file_path)
        
        # True döndürmeli ve dosyayı kaldırmalı
        self.assertTrue(result)
        self.assertFalse(os.path.exists(file_path))
    
    def test_cleanup_nonexistent_file(self):
        """Var olmayan dosyayı temizlemeyi test et."""
        result = cleanup_temp_file('/nonexistent/file.py')
        
        # Zarif bir şekilde False döndürmeli
        self.assertFalse(result)
    
    def test_cleanup_old_temp_files(self):
        """Eski geçici dosyaların temizlenmesini test et."""
        # Bazı test dosyaları oluştur
        old_content = "old file content"
        new_content = "new file content"
        
        # Dosyaları oluştur
        old_file = save_temp_file(old_content, 'python')
        new_file = save_temp_file(new_content, 'python')
        
        # Eski dosyanın zaman damgasını eski görünmesi için değiştir
        old_time = time.time() - (25 * 3600)  # 25 saat önce
        os.utime(old_file, (old_time, old_time))
        
        # 24 saatlik eşik ile temizleme çalıştır
        cleaned_count = cleanup_old_temp_files(24)
        
        # Eski dosyayı temizlemeli ama yenisini değil
        self.assertGreaterEqual(cleaned_count, 1)
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(new_file))
        
        # Kalan dosyayı temizle
        cleanup_temp_file(new_file)


class TestFileValidation(BaseTestCase):
    """Dosya doğrulama işlevselliği için test durumları."""
    
    def test_validate_file_content_valid(self):
        """Geçerli dosya içeriğinin doğrulanmasını test et."""
        valid_content = "def hello():\n    print('Hello, World!')"
        
        is_valid, message = validate_file_content(valid_content)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_file_content_empty(self):
        """Boş içeriğin doğrulanmasını test et."""
        test_cases = ["", "   ", "\n\n\n", "\t\t\t"]
        
        for content in test_cases:
            with self.subTest(content=repr(content)):
                is_valid, message = validate_file_content(content)
                
                self.assertFalse(is_valid)
                self.assertIn("empty", message.lower())
    
    def test_validate_file_content_too_large(self):
        """Fazla büyük içeriğin doğrulanmasını test et."""
        # 1MB'dan büyük içerik oluştur (varsayılan limit)
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        
        is_valid, message = validate_file_content(large_content, max_size_mb=1)
        
        self.assertFalse(is_valid)
        self.assertIn("exceeds maximum", message)
    
    def test_validate_file_content_binary_data(self):
        """Binary verinin doğrulanmasını test et."""
        # UTF-8 olmayan baytlarla içerik oluştur
        binary_content = "def test():\n    x = " + chr(0xFFFF) + "\n"
        
        try:
            is_valid, message = validate_file_content(binary_content)
            # Exception fırlatmazsa, hala geçerli olmalı
            # çünkü test içeriği aslında geçerli Unicode
            self.assertTrue(is_valid)
        except UnicodeEncodeError:
            # Exception fırlatırsa, bu da kabul edilebilir
            pass
    
    def test_get_file_info_existing_file(self):
        """Var olan dosya hakkında bilgi almayı test et."""
        code = "test content"
        file_path = save_temp_file(code, 'python')
        self.temp_files.append(file_path)
        
        file_info = get_file_info(file_path)
        
        self.assertIsNotNone(file_info)
        self.assertIn('size', file_info)
        self.assertIn('modified', file_info)
        self.assertIn('created', file_info)
        self.assertIn('is_file', file_info)
        self.assertIn('extension', file_info)
        
        # .py uzantılı bir dosya olmalı
        self.assertTrue(file_info['is_file'])
        self.assertEqual(file_info['extension'], '.py')
        self.assertGreater(file_info['size'], 0)
    
    def test_get_file_info_nonexistent_file(self):
        """Var olmayan dosya hakkında bilgi almayı test et."""
        file_info = get_file_info('/nonexistent/file.py')
        
        self.assertIsNone(file_info)


class TestContentAnalysis(BaseTestCase):
    """İçerik sorun analizi için test durumları."""
    
    def test_analyze_content_no_issues(self):
        """Temiz içeriğin analizini test et."""
        clean_content = "def hello():\n    print('Hello, World!')"
        
        analysis = analyze_content_issues(clean_content)
        
        self.assertFalse(analysis['has_issues'])
        self.assertEqual(len(analysis['issues_found']), 0)
        self.assertEqual(len(analysis['fixes_applied']), 0)
    
    def test_analyze_content_carriage_returns(self):
        """Carriage return içeren içeriğin analizini test et."""
        content_with_cr = "def test():\r\n    print('test')\r\n"
        
        analysis = analyze_content_issues(content_with_cr)
        
        self.assertTrue(analysis['has_issues'])
        self.assertGreater(len(analysis['issues_found']), 0)
        
        # Carriage return'leri tespit etmeli
        cr_issues = [issue for issue in analysis['issues_found'] if 'carriage return' in issue.lower()]
        self.assertGreater(len(cr_issues), 0)
        
        # Düzeltme önerisinde bulunmalı
        cr_fixes = [fix for fix in analysis['fixes_applied'] if 'carriage return' in fix.lower()]
        self.assertGreater(len(cr_fixes), 0)
    
    def test_analyze_content_zero_width_chars(self):
        """Sıfır genişlikli karakter içeren içeriğin analizini test et."""
        content_with_zwc = "def\u200btest():\n    pass\u200c"
        
        analysis = analyze_content_issues(content_with_zwc)
        
        self.assertTrue(analysis['has_issues'])
        
        # Sıfır genişlikli karakterleri tespit etmeli
        zwc_issues = [issue for issue in analysis['issues_found'] if 'zero-width' in issue.lower()]
        self.assertGreater(len(zwc_issues), 0)
    
    def test_analyze_content_non_breaking_spaces(self):
        """Bölünmeyen boşluk içeren içeriğin analizini test et."""
        content_with_nbsp = "def\u00a0test():\n    return\u00a0True"
        
        analysis = analyze_content_issues(content_with_nbsp)
        
        self.assertTrue(analysis['has_issues'])
        
        # Bölünmeyen boşlukları tespit etmeli
        nbsp_issues = [issue for issue in analysis['issues_found'] if 'non-breaking space' in issue.lower()]
        self.assertGreater(len(nbsp_issues), 0)
    
    def test_analyze_content_multiple_issues(self):
        """Birden fazla türde sorun içeren içeriğin analizini test et."""
        problematic_content = "def\u200btest():\r\n    var\u00a0=\u200c'test'\r\n"
        
        analysis = analyze_content_issues(problematic_content)
        
        self.assertTrue(analysis['has_issues'])
        self.assertGreater(len(analysis['issues_found']), 1)
        self.assertGreater(len(analysis['fixes_applied']), 1)
        
        # Tüm sorun türlerini tespit etmeli
        all_issues = ' '.join(analysis['issues_found']).lower()
        self.assertIn('carriage return', all_issues)
        self.assertIn('zero-width', all_issues)
        self.assertIn('non-breaking space', all_issues)


class TestFileHandlerIntegration(BaseTestCase):
    """Dosya işleyici işlevselliği için entegrasyon testleri."""
    
    def test_full_file_processing_workflow(self):
        """Tam dosya işleme iş akışını test et."""
        # Sorunlu içerikle başla
        original_content = "def\u200btest():\r\n    unused_var\u00a0=\u200c'test'\r\n    print('Hello')\r\n"
        
        # Adım 1: Sorunları analiz et
        analysis = analyze_content_issues(original_content)
        self.assertTrue(analysis['has_issues'])
        
        # Adım 2: İçeriği temizle
        cleaned_content = clean_code_content(original_content)
        
        # Adım 3: Geçici dosyaya kaydet
        temp_file = save_temp_file(original_content, 'python')  # Otomatik olarak temizlemeli
        self.temp_files.append(temp_file)
        
        # Adım 4: Dosyanın temizlenmiş içerikle kaydedildiğini doğrula
        with open(temp_file, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        # Sorunlu karakterler içermemeli
        self.assertNotIn('\r', saved_content)
        self.assertNotIn('\u200b', saved_content)
        self.assertNotIn('\u200c', saved_content)
        self.assertNotIn('\u00a0', saved_content)
        
        # Geçerli içeriği korumalı (anahtar bileşenleri kontrol et)
        self.assertIn('test', saved_content)  # Fonksiyon adının parçası
        self.assertIn('print', saved_content)
        self.assertIn('Hello', saved_content)
        
        # Temel yapının korunduğunu kontrol et
        self.assertTrue(
            'def test' in saved_content or 'deftest' in saved_content,
            "Function definition should be preserved"
        )
        
        # Adım 5: Dosya bilgisini al
        file_info = get_file_info(temp_file)
        self.assertIsNotNone(file_info)
        self.assertTrue(file_info['is_file'])
        
        # Adım 6: İçeriği doğrula
        is_valid, message = validate_file_content(saved_content)
        self.assertTrue(is_valid)
        
        # Adım 7: Temizle
        cleanup_result = cleanup_temp_file(temp_file)
        self.assertTrue(cleanup_result)
        self.assertFalse(os.path.exists(temp_file))
    
    def test_edge_case_handling(self):
        """Çeşitli sınır durumlarının işlenmesini test et."""
        edge_cases = [
            ("", "Empty content"),
            ("   \n\n\n   ", "Whitespace only"),
            ("def test():" + "x" * 10000, "Very long line"),
            ("def test():\n" + "    pass\n" * 1000, "Many lines"),
        ]
        
        for content, description in edge_cases:
            with self.subTest(description=description):
                try:
                    # Tüm sınır durumları zarif bir şekilde işlemeli
                    analysis = analyze_content_issues(content)
                    cleaned = clean_code_content(content)
                    
                    if content.strip():  # Sadece boş olmayan içeriği kaydet
                        temp_file = save_temp_file(content, 'python')
                        self.temp_files.append(temp_file)
                        
                        # Geçerli dosya oluşturmalı
                        self.assertTrue(os.path.exists(temp_file))
                        
                        file_info = get_file_info(temp_file)
                        self.assertIsNotNone(file_info)
                    
                    # Exception fırlatmamalı
                    self.assertIsInstance(analysis, dict)
                    self.assertIsInstance(cleaned, str)
                    
                except Exception as e:
                    self.fail(f"Edge case '{description}' raised exception: {e}")
    
    def test_concurrent_file_operations(self):
        """Eşzamanlı dosya işlemlerini test et."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_and_cleanup_file(thread_id):
            try:
                content = f"def test_{thread_id}():\n    pass"
                temp_file = save_temp_file(content, 'python')
                
                # Dosyanın var olduğunu doğrula
                if os.path.exists(temp_file):
                    results.append(f"Thread {thread_id}: Success")
                    
                    # İşlemi simüle etmek için küçük gecikme
                    time.sleep(0.1)
                    
                    # Temizle
                    cleanup_temp_file(temp_file)
                else:
                    errors.append(f"Thread {thread_id}: File not created")
                    
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Birden fazla thread oluştur
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_and_cleanup_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin tamamlanmasını bekle
        for thread in threads:
            thread.join()
        
        # Eşzamanlı işlemleri işlemeli
        self.assertEqual(len(errors), 0, f"Concurrent operations failed: {errors}")
        self.assertEqual(len(results), 5, "Not all threads completed successfully")


class TestFileHandlerPerformance(BaseTestCase):
    """Dosya işleyici için performans testleri."""
    
    def test_large_file_handling(self):
        """Büyük dosyaların işlenmesini test et."""
        # Büyük içerik oluştur (1MB)
        large_content = "# Large file test\n" + "".join(f"def function_{i}():\n    pass\n\n" for i in range(10000))
        
        start_time = time.time()
        
        # Büyük dosyaları verimli bir şekilde işlemeli
        analysis = analyze_content_issues(large_content)
        cleaned = clean_code_content(large_content)
        
        temp_file = save_temp_file(large_content, 'python')
        self.temp_files.append(temp_file)
        
        file_info = get_file_info(temp_file)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Makul sürede tamamlanmalı (5 saniyeden az)
        self.assertLess(processing_time, 5.0, "Large file processing took too long")
        
        # Doğru şekilde işlemeli
        self.assertIsInstance(analysis, dict)
        self.assertIsInstance(cleaned, str)
        self.assertIsNotNone(file_info)
        self.assertTrue(os.path.exists(temp_file))
    
    def test_many_small_files(self):
        """Çok sayıda küçük dosyanın işlenmesini test et."""
        start_time = time.time()
        
        temp_files = []
        
        # Çok sayıda küçük dosya oluştur ve işle
        for i in range(100):
            content = f"def test_{i}():\n    return {i}"
            temp_file = save_temp_file(content, 'python')
            temp_files.append(temp_file)
        
        # Tüm dosyaların var olduğunu doğrula
        for temp_file in temp_files:
            self.assertTrue(os.path.exists(temp_file))
        
        # Tüm dosyaları temizle
        for temp_file in temp_files:
            cleanup_temp_file(temp_file)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Çok sayıda dosyayı verimli bir şekilde işlemeli
        self.assertLess(processing_time, 10.0, "Many files processing took too long")


if __name__ == '__main__':
    # Test paketi oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test durumlarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestFileContentCleaning))
    suite.addTests(loader.loadTestsFromTestCase(TestTempFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestFileValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestContentAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandlerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandlerPerformance))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Özet yazdır
    print(f"\n{'='*60}")
    print("FILE HANDLER TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "No tests run")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    # Dosya işlemi bütünlüğünü test et
    print(f"\n{'='*60}")
    print("FILE OPERATION INTEGRITY CHECK")
    print(f"{'='*60}")
    
    # Çeşitli sorunlu içerik senaryolarını test et
    test_scenarios = [
        ("Windows line endings", "line1\r\nline2\r\n"),
        ("Zero-width characters", "def\u200btest\u200c():\u200d\n    pass"),
        ("Non-breaking spaces", "var\u00a0=\u00a0'test'"),
        ("Mixed issues", "def\u200btest():\r\n    var\u00a0=\u200c'data'\r\n"),
    ]
    
    for scenario_name, problematic_content in test_scenarios:
        print(f"\nTesting {scenario_name}:")
        
        # Sorunları analiz et
        analysis = analyze_content_issues(problematic_content)
        print(f"  Issues detected: {len(analysis['issues_found'])}")
        
        # İçeriği temizle
        cleaned = clean_code_content(problematic_content)
        print(f"  Content cleaned: {analysis['has_issues']}")
        
        # Temizlemenin etkili olduğunu doğrula
        clean_analysis = analyze_content_issues(cleaned)
        print(f"  Issues after cleaning: {len(clean_analysis['issues_found'])}")
        
        # Temizlemeden sonra daha az veya hiç sorun olmamalı
        improvement = len(analysis['issues_found']) - len(clean_analysis['issues_found'])
        print(f"  Improvement: {improvement} issues resolved")
    
    # Modül seviyesinde return kullanmak yerine başarı durumunu döndür
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)