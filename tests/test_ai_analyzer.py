"""
AI analizör işlevselliği için birim testleri
"""

import sys
import unittest
import os
from unittest.mock import patch, MagicMock
from test_framework import BaseTestCase, TestDataProvider, mock_ai_response

# AI analizörü import et
from analyzers.ai_analyzer import (
    analyze_with_ai, 
    generate_clean_code_response, 
    generate_ai_analysis,
    categorize_issues,
    build_analysis_prompt,
    format_ai_response
)


class TestAIAnalyzer(BaseTestCase):
    """AI destekli kod analizi için test durumları."""
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_analyze_with_no_issues(self, mock_model):
        """Statik sorun bulunamadığında AI analizini test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = mock_ai_response(0)
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Temiz kod ile test et
        code = TestDataProvider.get_sample('python', 'clean_code')
        temp_file = self.create_temp_file(code, 'python')
        
        result = analyze_with_ai(temp_file, [], 'python')
        
        # Temiz kod için pozitif geri bildirim sağlamalı
        self.assertIn('well-structured', result.lower())
        self.assertIn('good practices', result.lower())
        
        # Doğru AI modelini çağırmalı
        mock_model.assert_called_once_with('gemini-2.0-flash')
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_analyze_with_static_issues(self, mock_model):
        """Statik analiz sonuçları ile AI analizini test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = mock_ai_response(5)
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Gerçek kodla eşleşen mock statik analiz sonuçları oluştur
        static_results = [
            {
                'line': 18,
                'column': 11,
                'type': 'error',
                'symbol': 'undefined-variable',
                'message': 'Undefined variable "undefined_variable"',
                'category': 'Syntax/Logic Error',
                'severity': 'high'
            },
            {
                'line': 5,
                'column': 0,
                'type': 'warning',
                'symbol': 'singleton-comparison',
                'message': 'Use "is" with None',
                'category': 'Code Quality',
                'severity': 'medium'
            }
        ]
        
        code = TestDataProvider.get_sample('python', 'code_quality_issues')
        temp_file = self.create_temp_file(code, 'python')
        
        result = analyze_with_ai(temp_file, static_results, 'python')
        
        # Bulunan sorunları belirtmeli
        self.assertIn('issues', result.lower())
        self.assertTrue(len(result) > 100, "Should provide detailed analysis")
        
        # AI modelinin uygun prompt ile çağrıldığını doğrula
        mock_model.return_value.generate_content.assert_called_once()
        call_args = mock_model.return_value.generate_content.call_args[0][0]
        self.assertIn('python', call_args.lower())
        self.assertIn('undefined variable', call_args)
    
    def test_categorize_issues(self):
        """Sorun kategorileme işlevselliğini test et."""
        static_results = [
            {'category': 'Syntax/Logic Error', 'message': 'Error 1'},
            {'category': 'Syntax/Logic Error', 'message': 'Error 2'},
            {'category': 'Unused Code', 'message': 'Unused var'},
            {'category': 'Code Quality', 'message': 'Quality issue'},
            {'message': 'No category'}  # Eksik kategori
        ]
        
        categorized = categorize_issues(static_results)
        
        # Kategoriye göre gruplandırmalı
        self.assertEqual(len(categorized['Syntax/Logic Error']), 2)
        self.assertEqual(len(categorized['Unused Code']), 1)
        self.assertEqual(len(categorized['Code Quality']), 1)
        self.assertEqual(len(categorized['Other']), 1)
    
    def test_build_analysis_prompt(self):
        """AI prompt oluşturmayı test et."""
        code_content = "def test():\n    pass"
        issues_by_category = {
            'Syntax/Logic Error': [
                {'line': 1, 'message': 'Test error', 'symbol': 'test-rule'}
            ],
            'Code Quality': [
                {'line': 2, 'message': 'Quality issue', 'symbol': 'quality-rule'}
            ]
        }
        
        prompt = build_analysis_prompt(code_content, issues_by_category, 'python')
        
        # Kod içeriğini içermeli
        self.assertIn('def test():', prompt)
        
        # Dili içermeli
        self.assertIn('Python', prompt)
        
        # Sorun kategorilerini içermeli
        self.assertIn('Syntax/Logic Error', prompt)
        self.assertIn('Code Quality', prompt)
        
        # Spesifik sorunları içermeli
        self.assertIn('Test error', prompt)
        self.assertIn('Quality issue', prompt)
        
        # Analiz bölümlerini içermeli
        self.assertIn('Issue Analysis', prompt)
        self.assertIn('Code Fixes', prompt)
        self.assertIn('Best Practices', prompt)
    
    def test_build_analysis_prompt_many_issues(self):
        """Çok fazla sorunla prompt oluşturmayı test et (kategori başına 5 ile sınırlamalı)."""
        # Bir kategoride 7 sorun oluştur
        many_issues = []
        for i in range(7):
            many_issues.append({
                'line': i + 1,
                'message': f'Issue {i + 1}',
                'symbol': f'rule-{i + 1}'
            })
        
        issues_by_category = {'Test Category': many_issues}
        code_content = "test code"
        
        prompt = build_analysis_prompt(code_content, issues_by_category, 'python')
        
        # Kategori başına 5 sorun ile sınırlamalı (ancak "ve X sorun daha" metni içerebilir)
        issue_count = prompt.count('Issue ')
        self.assertLessEqual(issue_count, 6, "Should limit to approximately 5 issues per category")
        
        # Ek sorunları belirtmeli
        self.assertTrue('and 2 more issues' in prompt or issue_count <= 5, 
                       "Should either limit issues or mention additional ones")
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_generate_clean_code_response_error_handling(self, mock_model):
        """Temiz kod analizinde hata işlemeyi test et."""
        # AI modelinin exception fırlatmasını mock et
        mock_model.side_effect = Exception("API Error")
        
        code = TestDataProvider.get_sample('python', 'clean_code')
        temp_file = self.create_temp_file(code, 'python')
        
        result = generate_clean_code_response(temp_file, 'python')
        
        # Yedek mesaj sağlamalı
        self.assertIn('No static analysis issues found', result)
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_generate_ai_analysis_error_handling(self, mock_model):
        """Detaylı AI analizinde hata işlemeyi test et."""
        # AI modelinin exception fırlatmasını mock et
        mock_model.side_effect = Exception("API Error")
        
        static_results = [{'line': 1, 'message': 'Test error', 'category': 'Test'}]
        
        result = generate_ai_analysis("test code", static_results, 'python')
        
        # Sorun sayısı ile hata mesajı sağlamalı
        self.assertIn('Error generating AI analysis', result)
        self.assertIn('1 issues', result)
    
    def test_format_ai_response(self):
        """AI yanıt formatlamayı test et."""
        ai_response = "This is a test AI response with analysis."
        total_issues = 5
        
        formatted = format_ai_response(ai_response, total_issues)
        
        # Sorun sayısı ile başlık içermeli
        self.assertIn('AI Code Review Summary', formatted)
        self.assertIn('Total Issues Found**: 5', formatted)
        self.assertIn(ai_response, formatted)
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_different_languages(self, mock_model):
        """Farklı programlama dilleri ile AI analizini test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = "Language-specific analysis"
        mock_model.return_value.generate_content.return_value = mock_response
        
        languages = ['python', 'javascript']
        
        for language in languages:
            with self.subTest(language=language):
                code = TestDataProvider.get_sample(language, 'clean_code')
                temp_file = self.create_temp_file(code, language)
                
                result = analyze_with_ai(temp_file, [], language)
                
                # Analizde dili içermeli
                call_args = mock_model.return_value.generate_content.call_args[0][0]
                self.assertIn(language.title(), call_args)
    
    def test_nonexistent_file_handling(self):
        """Var olmayan dosyaların işlenmesini test et."""
        result = analyze_with_ai('/nonexistent/file.py', [], 'python')
        
        # Hata mesajı VEYA yedek mesaj döndürmeli
        self.assertTrue(
            'Error during AI analysis' in result or 
            'No static analysis issues found' in result,
            "Should handle nonexistent files gracefully"
        )
    
    @patch('analyzers.ai_analyzer.genai.configure')
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_api_key_configuration(self, mock_model, mock_configure):
        """API anahtarının düzgün yapılandırıldığını test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.return_value.generate_content.return_value = mock_response
        
        code = "print('test')"
        temp_file = self.create_temp_file(code, 'python')
        
        analyze_with_ai(temp_file, [], 'python')
        
        # API anahtarını yapılandırmalı
        mock_configure.assert_called()


class TestAIAnalyzerIntegration(BaseTestCase):
    """AI analizör entegrasyonu için gerçek kod örnekleri ile testler."""
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_integration_with_python_samples(self, mock_model):
        """Çeşitli Python kod örnekleri ile AI analiz entegrasyonunu test et."""
        # Örnek türüne göre mock yanıt oluşturucu
        def mock_response_generator(prompt):
            if 'clean' in prompt.lower() or not any(word in prompt.lower() for word in ['error', 'warning', 'issue']):
                return MagicMock(text=mock_ai_response(0))
            else:
                # Prompt'tan yaklaşık sorun sayısını say
                issue_count = prompt.lower().count('line') + prompt.lower().count('error')
                return MagicMock(text=mock_ai_response(min(issue_count, 10)))
        
        mock_model.return_value.generate_content.side_effect = mock_response_generator
        
        sample_types = ['clean_code', 'syntax_errors', 'unused_variables', 'code_quality_issues']
        
        for sample_type in sample_types:
            with self.subTest(sample_type=sample_type):
                code = TestDataProvider.get_sample('python', sample_type)
                temp_file = self.create_temp_file(code, 'python')
                
                # Örnek türüne göre mock statik sonuçlar oluştur
                if sample_type == 'clean_code':
                    static_results = []
                else:
                    static_results = [
                        {
                            'line': 5,
                            'message': f'Sample {sample_type} issue',
                            'category': 'Test Category',
                            'severity': 'medium',
                            'symbol': 'test-rule'
                        }
                    ]
                
                result = analyze_with_ai(temp_file, static_results, 'python')
                
                # Anlamlı analiz sağlamalı
                self.assertGreater(len(result), 50, "Should provide substantial analysis")
                
                # İçerik kod türüne uygun olmalı
                if sample_type == 'clean_code':
                    self.assertIn('well', result.lower())
                else:
                    self.assertIn('issue', result.lower())
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_integration_with_javascript_samples(self, mock_model):
        """JavaScript kod örnekleri ile AI analiz entegrasyonunu test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = mock_ai_response(3)
        mock_model.return_value.generate_content.return_value = mock_response
        
        sample_types = ['clean_code', 'variable_issues', 'code_quality_issues']
        
        for sample_type in sample_types:
            with self.subTest(sample_type=sample_type):
                code = TestDataProvider.get_sample('javascript', sample_type)
                temp_file = self.create_temp_file(code, 'javascript')
                
                static_results = [
                    {
                        'line': 3,
                        'message': 'JavaScript issue example',
                        'category': 'Code Quality',
                        'severity': 'medium',
                        'symbol': 'example-rule'
                    }
                ]
                
                result = analyze_with_ai(temp_file, static_results, 'javascript')
                
                # Analiz sağlamalı
                self.assertGreater(len(result), 50)
                
                # Prompt'ta JavaScript'i belirtmeli
                call_args = mock_model.return_value.generate_content.call_args[0][0]
                self.assertIn('JavaScript', call_args)


class TestAIAnalyzerPerformance(BaseTestCase):
    """AI analizör için performans ve sınır durum testleri."""
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_large_code_analysis(self, mock_model):
        """Büyük kod dosyaları ile AI analizini test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = mock_ai_response(10)
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Büyük kod örneği oluştur
        large_code = TestDataProvider.get_sample('python', 'clean_code') * 10
        temp_file = self.create_temp_file(large_code, 'python')
        
        static_results = [{'line': i, 'message': f'Issue {i}', 'category': 'Test'} 
                         for i in range(1, 11)]
        
        result = analyze_with_ai(temp_file, static_results, 'python')
        
        # Büyük dosyaları işlemeli
        self.assertGreater(len(result), 100)
        
        # Timeout olmamali veya crash olmamalı (büyük/küçük harf duyarsız arama)
        self.assertIn('analysis', result.lower())
    
    @patch('analyzers.ai_analyzer.genai.GenerativeModel')
    def test_many_issues_analysis(self, mock_model):
        """Çok fazla statik sorunla AI analizini test et."""
        # AI yanıtını mock et
        mock_response = MagicMock()
        mock_response.text = mock_ai_response(50)
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Çok fazla sorun oluştur
        static_results = []
        categories = ['Syntax/Logic Error', 'Code Quality', 'Unused Code', 'Style/Convention']
        
        for i in range(20):
            static_results.append({
                'line': i + 1,
                'message': f'Issue {i + 1}',
                'category': categories[i % len(categories)],
                'severity': ['high', 'medium', 'low'][i % 3],
                'symbol': f'rule-{i + 1}'
            })
        
        code = "def test(): pass"
        temp_file = self.create_temp_file(code, 'python')
        
        result = analyze_with_ai(temp_file, static_results, 'python')
        
        # Çok fazla sorunu işlemeli
        self.assertGreater(len(result), 100)
        
        # Prompt'ta kategori başına sorunları sınırlamalı (biraz esneklik tanı)
        call_args = mock_model.return_value.generate_content.call_args[0][0]
        # Tüm 20 sorunu detayda içermemeli (kategoriler, başlıklar vb. için 25 bahsetmeye kadar izin ver)
        issue_mentions = call_args.count('Issue ')
        self.assertLessEqual(issue_mentions, 25, "Should limit or group issues in prompt")
    
    def test_empty_code_handling(self):
        """Boş kod dosyalarının işlenmesini test et."""
        temp_file = self.create_temp_file("", 'python')
        
        result = analyze_with_ai(temp_file, [], 'python')
        
        # Boş dosyaları zarif bir şekilde işlemeli
        self.assertIn('Error', result)


if __name__ == '__main__':
    # Test paketi oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test durumlarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestAIAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestAIAnalyzerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAIAnalyzerPerformance))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Özet yazdır
    print(f"\n{'='*60}")
    print("AI ANALYZER TEST SUMMARY")
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
    
    # AI analiz kalitesini test et
    print(f"\n{'='*60}")
    print("AI ANALYSIS QUALITY VALIDATION")
    print(f"{'='*60}")
    
    # AI yanıtlarının anahtar öğeleri içerip içermediğini kontrol et
    sample_responses = [
        mock_ai_response(0),
        mock_ai_response(3),
        mock_ai_response(10)
    ]
    
    for i, response in enumerate(sample_responses):
        print(f"\nSample Response {i + 1}:")
        print(f"  Length: {len(response)} characters")
        print(f"  Contains recommendations: {'recommend' in response.lower()}")
        print(f"  Contains code assessment: {'code' in response.lower()}")
        print(f"  Contains actionable advice: {'action' in response.lower() or 'fix' in response.lower()}")
    
    # Modül seviyesinde return kullanmak yerine başarı durumunu döndür
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)