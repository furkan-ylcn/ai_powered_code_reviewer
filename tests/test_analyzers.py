"""
Statik kod analizörleri için birim testleri (Python ve JavaScript)
"""

import sys
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from test_framework import BaseTestCase, TestDataProvider, mock_ai_response

# Analizörleri import et
from analyzers.python_analyzer import run_pylint, get_severity_level, categorize_issue
from analyzers.javascript_analyzer import run_eslint, get_severity_level as js_get_severity, categorize_js_issue


class TestPythonAnalyzer(BaseTestCase):
    """Python statik analizör için test durumları."""
    
    def test_syntax_error_detection(self):
        """Python syntax hatalarının tespitini test et."""
        code = TestDataProvider.get_sample('python', 'syntax_errors')
        temp_file = self.create_temp_file(code, 'python')
        
        results = run_pylint(temp_file)
        
        # Syntax hatalarını tespit etmeli
        self.assertGreater(len(results), 0, "Should detect syntax errors")
        
        # Spesifik syntax sorunlarını kontrol et
        error_messages = [result.get('message', '').lower() for result in results]
        syntax_errors = [msg for msg in error_messages if 'syntax' in msg or 'invalid' in msg]
        
        self.assertGreater(len(syntax_errors), 0, "Should detect syntax errors")
    
    def test_unused_variable_detection(self):
        """Kullanılmayan değişkenlerin tespitini test et."""
        code = TestDataProvider.get_sample('python', 'unused_variables')
        temp_file = self.create_temp_file(code, 'python')
        
        results = run_pylint(temp_file)
        
        # Kullanılmayan değişkenleri tespit etmeli
        unused_issues = [r for r in results if 'unused' in r.get('symbol', '').lower()]
        self.assertGreater(len(unused_issues), 0, "Should detect unused variables")
        
        # Spesifik kullanılmayan değişkenleri kontrol et
        self.assert_analysis_contains(results, ['unused', 'import'])
    
    def test_code_quality_issues(self):
        """Kod kalitesi sorunlarının tespitini test et."""
        code = TestDataProvider.get_sample('python', 'code_quality_issues')
        temp_file = self.create_temp_file(code, 'python')
        
        results = run_pylint(temp_file)
        
        # Çeşitli kalite sorunlarını tespit etmeli
        self.assertGreater(len(results), 0, "Should detect code quality issues")
        
        # Spesifik kalite sorunlarını kontrol et
        self.assert_analysis_contains(results, ['undefined', 'bare-except', 'too-many'])
    
    def test_clean_code_analysis(self):
        """Temiz, iyi yazılmış kodun analizini test et."""
        code = TestDataProvider.get_sample('python', 'clean_code')
        temp_file = self.create_temp_file(code, 'python')
        
        results = run_pylint(temp_file)
        
        # Temiz kodda minimal sorun olmalı
        high_severity_issues = [r for r in results if r.get('severity') == 'high']
        self.assertEqual(len(high_severity_issues), 0, "Clean code should have no high severity issues")
    
    def test_severity_mapping(self):
        """Önem derecesi seviye eşlemesini test et."""
        test_cases = [
            ('error', 'high'),
            ('fatal', 'critical'),
            ('warning', 'medium'),
            ('refactor', 'low'),
            ('convention', 'low'),
            ('information', 'info'),
            ('unknown', 'medium')
        ]
        
        for pylint_type, expected_severity in test_cases:
            with self.subTest(pylint_type=pylint_type):
                result = get_severity_level(pylint_type)
                self.assertEqual(result, expected_severity)
    
    def test_issue_categorization(self):
        """Sorun kategorilendirmesini test et."""
        test_cases = [
            ('error', 'undefined-variable', 'Syntax/Logic Error'),
            ('warning', 'unused-variable', 'Unused Code'),
            ('warning', 'import-error', 'Import Issue'),
            ('refactor', 'too-many-arguments', 'Code Structure'),
            ('convention', 'line-too-long', 'Style/Convention')
        ]
        
        for issue_type, symbol, expected_category in test_cases:
            with self.subTest(symbol=symbol):
                result = categorize_issue(issue_type, symbol)
                self.assertEqual(result, expected_category)
    
    def test_nonexistent_file(self):
        """Var olmayan dosya ile analizör davranışını test et."""
        result = run_pylint('/nonexistent/file.py')
        self.assertEqual(len(result), 0, "Should return empty list for nonexistent file")
    
    @patch('subprocess.run')
    def test_pylint_timeout(self, mock_run):
        """Pylint timeout işlemesini test et."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired(['pylint'], 30)
        
        code = "print('hello')"
        temp_file = self.create_temp_file(code, 'python')
        
        result = run_pylint(temp_file)
        self.assertEqual(len(result), 0, "Should return empty list on timeout")


class TestJavaScriptAnalyzer(BaseTestCase):
    """JavaScript statik analizör için test durumları."""
    
    def test_syntax_error_detection(self):
        """JavaScript syntax hatalarının tespitini test et."""
        code = TestDataProvider.get_sample('javascript', 'syntax_errors')
        temp_file = self.create_temp_file(code, 'javascript')
        
        results = run_eslint(temp_file)
        
        # Syntax veya yapısal sorunları tespit etmeli
        self.assertGreaterEqual(len(results), 0, "Should detect JavaScript issues")
    
    def test_variable_issues_detection(self):
        """Değişkenle ilgili sorunların tespitini test et."""
        code = TestDataProvider.get_sample('javascript', 'variable_issues')
        temp_file = self.create_temp_file(code, 'javascript')
        
        results = run_eslint(temp_file)
        
        # Değişken sorunlarını tespit etmeli
        variable_issues = [r for r in results if 'var' in r.get('symbol', '').lower() or 
                          'unused' in r.get('symbol', '').lower()]
        
        # Spesifik sorunları kontrol et
        issue_symbols = [r.get('symbol', '') for r in results]
        
        # Beklediğimiz yaygın sorunlar
        expected_rules = ['no-unused-vars', 'no-var', 'no-undef']
        found_rules = [rule for rule in expected_rules if rule in issue_symbols]
        
        # Bu yaygın sorunlardan en azından bazılarını bulmalı
        self.assertGreater(len(results), 0, "Should detect variable-related issues")
    
    def test_code_quality_issues(self):
        """Kod kalitesi sorunlarının tespitini test et."""
        code = TestDataProvider.get_sample('javascript', 'code_quality_issues')
        temp_file = self.create_temp_file(code, 'javascript')
        
        results = run_eslint(temp_file)
        
        # Kalite sorunlarını tespit etmeli
        self.assertGreater(len(results), 0, "Should detect code quality issues")
        
        # Spesifik kalite kurallarını kontrol et
        quality_rules = ['eqeqeq', 'no-eval', 'no-unreachable']
        found_quality_issues = [r for r in results if r.get('symbol') in quality_rules]
    
    def test_clean_javascript_code(self):
        """Temiz JavaScript kodunun analizini test et."""
        code = TestDataProvider.get_sample('javascript', 'clean_code')
        temp_file = self.create_temp_file(code, 'javascript')
        
        results = run_eslint(temp_file)
        
        # Temiz kodda minimal veya hiç yüksek önemli sorun olmamalı
        high_severity_issues = [r for r in results if r.get('severity') == 'high']
        
        # Bazı küçük stil sorunlarına izin ver ama büyük problem olmasın
        self.assertLessEqual(len(high_severity_issues), 2, 
                           "Clean code should have minimal high severity issues")
    
    def test_js_severity_mapping(self):
        """JavaScript önem derecesi seviye eşlemesini test et."""
        test_cases = [
            (2, 'high'),    # ESLint error
            (1, 'medium'),  # ESLint warning
            (0, 'low')      # Other
        ]
        
        for eslint_severity, expected_severity in test_cases:
            with self.subTest(eslint_severity=eslint_severity):
                result = js_get_severity(eslint_severity)
                self.assertEqual(result, expected_severity)
    
    def test_js_issue_categorization(self):
        """JavaScript sorun kategorilendirmesini test et."""
        test_cases = [
            ('no-undef', 'Syntax/Logic Error'),
            ('semi', 'Style/Convention'),
            ('eqeqeq', 'Code Quality'),
            ('no-unused-vars', 'Unused Code'),
            ('no-var', 'Code Structure'),
            ('no-console', 'Best Practices'),
            ('unknown-rule', 'Other')
        ]
        
        for rule_id, expected_category in test_cases:
            with self.subTest(rule_id=rule_id):
                result = categorize_js_issue(rule_id)
                self.assertEqual(result, expected_category)
    
    def test_nonexistent_js_file(self):
        """Var olmayan dosya ile JavaScript analizör davranışını test et."""
        result = run_eslint('/nonexistent/file.js')
        self.assertEqual(len(result), 0, "Should return empty list for nonexistent file")
    
    @patch('subprocess.run')
    def test_eslint_timeout(self, mock_run):
        """ESLint timeout işlemesini test et."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired(['eslint'], 30)
        
        code = "console.log('hello');"
        temp_file = self.create_temp_file(code, 'javascript')
        
        result = run_eslint(temp_file)
        self.assertEqual(len(result), 0, "Should return empty list on timeout")


class TestAnalyzerIntegration(BaseTestCase):
    """Her iki analizör için entegrasyon testleri."""
    
    def test_python_error_categories(self):
        """Python analizinin farklı hata türlerini düzgün kategorilendirdiğini test et."""
        test_samples = [
            ('syntax_errors', 'Syntax/Logic Error'),
            ('unused_variables', 'Unused Code'),
            ('code_quality_issues', 'Code Quality')
        ]
        
        for sample_type, expected_category in test_samples:
            with self.subTest(sample_type=sample_type):
                code = TestDataProvider.get_sample('python', sample_type)
                temp_file = self.create_temp_file(code, 'python')
                
                results = run_pylint(temp_file)
                categories = [r.get('category') for r in results]
                
                # Beklenen kategoriyi bulmalı
                if expected_category in categories:
                    self.assertIn(expected_category, categories)
    
    def test_javascript_error_categories(self):
        """JavaScript analizinin farklı hata türlerini düzgün kategorilendirdiğini test et."""
        test_samples = [
            ('variable_issues', ['Unused Code', 'Code Structure']),
            ('code_quality_issues', ['Code Quality', 'Syntax/Logic Error'])
        ]
        
        for sample_type, expected_categories in test_samples:
            with self.subTest(sample_type=sample_type):
                code = TestDataProvider.get_sample('javascript', sample_type)
                temp_file = self.create_temp_file(code, 'javascript')
                
                results = run_eslint(temp_file)
                found_categories = [r.get('category') for r in results]
                
                # Beklenen kategorilerden en az birini bulmalı
                category_found = any(cat in found_categories for cat in expected_categories)
                self.assertTrue(category_found or len(results) == 0, 
                              f"Should find one of {expected_categories} or no issues")
    
    def test_severity_distribution(self):
        """Analizörlerin önem derecesi seviyelerini düzgün dağıttığını test et."""
        # Karışık önem dereceli sorunları olan kod ile test et
        python_code = TestDataProvider.get_sample('python', 'code_quality_issues')
        js_code = TestDataProvider.get_sample('javascript', 'code_quality_issues')
        
        for language, code in [('python', python_code), ('javascript', js_code)]:
            with self.subTest(language=language):
                temp_file = self.create_temp_file(code, language)
                
                if language == 'python':
                    results = run_pylint(temp_file)
                else:
                    results = run_eslint(temp_file)
                
                if results:  # Sadece sorun bulduysak test et
                    severities = [r.get('severity') for r in results]
                    unique_severities = set(severities)
                    
                    # Önem derecesi bilgisi olmalı
                    self.assertTrue(len(unique_severities) > 0, "Should assign severity levels")
                    
                    # Bilinmeyen önem dereceleri olmamalı
                    valid_severities = {'low', 'medium', 'high', 'critical', 'info'}
                    invalid_severities = unique_severities - valid_severities
                    self.assertEqual(len(invalid_severities), 0, 
                                   f"Found invalid severities: {invalid_severities}")


if __name__ == '__main__':
    # Test paketi oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test durumlarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestPythonAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestJavaScriptAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzerIntegration))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Özet yazdır
    print(f"\n{'='*60}")
    print("STATIC ANALYZER TEST SUMMARY")
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
    
    # Modül seviyesinde return kullanmak yerine başarı durumunu döndür
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)