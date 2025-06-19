import google.generativeai as genai
import os
from typing import List, Dict, Any

# API keyin tanımlanması
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBVgsYjm3nuQjZlWwL51wGVEVg454PAfyM')

def analyze_with_ai(file_path: str, static_results: List[Dict[str, Any]], language: str) -> str:
    """
    Statik analiz sonuçlarına göre AI ile kod analizi yapma.
    
    Args:
        file_path (str): Kod dosyasının yolu
        static_results (list): Statik analiz sonuçları
        language (str): Programlama dili
        
    Returns:
        str: AI tarafından üretilen analiz sonucu
    """
    if not static_results:
        return generate_clean_code_response(file_path, language)
    
    try:
        # Dosya içeriğini okuma
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        # AI ile analiz yapma
        ai_response = generate_ai_analysis(file_content, static_results, language)
        return ai_response
        
    except Exception as e:
        return f"Error during AI analysis: {str(e)}"

def generate_clean_code_response(file_path: str, language: str) -> str:
    """
    Statik analiz sonucunda sorun bulunmadığında AI ile temiz kod analizi yapma.
    
    Args:
        file_path (str): Kod dosyasının yolu
        language (str): Programlama dili
        
    Returns:
        str: AI tarafından üretilen temiz kod analizi sonucu
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        # Gemini AI'yi yapılandırma
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Analyze this {language.title()} code for overall quality and best practices:

```{language}
{file_content}
```

The static analysis found no issues, but please provide:
1. Overall code quality assessment
2. Potential improvements or optimizations
3. Best practices recommendations
4. Code structure feedback

Keep the response concise and constructive."""

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"✅ No static analysis issues found. Code appears to be well-structured for basic analysis."

def generate_ai_analysis(code_content: str, static_results: List[Dict[str, Any]], language: str) -> str:
    """
    Statik analiz sonuçlarına göre AI ile detaylı kod analizi yapma.
    
    Args:
        code_content (str): Kaynak kod içeriği
        static_results (list): Statik analiz sonuçları
        language (str): Programlama dili
        
    Returns:
        str: AI tarafından üretilen detaylı analiz sonucu
    """
    try:
        # Gemini AI'yi yapılandırma
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Sorunları kategoriye ayırma
        issues_by_category = categorize_issues(static_results)
        
        # Prompt oluşturma
        prompt = build_analysis_prompt(code_content, issues_by_category, language)
        
        # AI yanıtını oluşturma
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}\n\nStatic analysis found {len(static_results)} issues that need attention."

def categorize_issues(static_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Statik analiz sonuçlarını kategoriye ayır.
    
    Args:
        static_results (list): Statik analiz sonuçları
        
    Returns:
        dict: Kategoriye ayrılmış sorunlar
    """
    categories = {}
    
    for issue in static_results:
        category = issue.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(issue)
    
    return categories

def build_analysis_prompt(code_content: str, issues_by_category: Dict[str, List[Dict[str, Any]]], language: str) -> str:
    """
    Detaylı analiz için AI'ye gönderilecek prompt'u oluşturma.
    
    Args:
        code_content (str): Kaynak kod içeriği
        issues_by_category (dict): Kategoriye ayrılmış sorunlar
        language (str): Programlama dili
        
    Returns:
        str: AI'ye gönderilecek prompt
    """
    prompt = f"""As an expert {language.title()} developer, analyze this code and provide detailed feedback:

```{language}
{code_content}
```

## Static Analysis Results:
"""
    
    # Kategorilere göre sorunları ekleme
    for category, issues in issues_by_category.items():
        prompt += f"\n### {category} Issues ({len(issues)} found):\n"
        for issue in issues[:5]:  # Her kategori için ilk 5 sorunu göster. Token sınırlarını aşmamak için
            prompt += f"- **Line {issue['line']}**: {issue['message']}\n"
            if issue.get('symbol'):
                prompt += f"  - Rule: {issue['symbol']}\n"
        
        if len(issues) > 5:
            prompt += f"  ... and {len(issues) - 5} more issues in this category\n"
    
    prompt += f"""
## Please provide:

1. **Issue Analysis**: Explain the most critical issues and their impact
2. **Code Fixes**: Provide specific code corrections for the main problems
3. **Best Practices**: Suggest {language} best practices to prevent these issues
4. **Code Quality**: Overall assessment and improvement recommendations
5. **Priority**: Rank issues by importance (Critical, High, Medium, Low)

Focus on actionable advice and concrete examples. Be concise but thorough."""
    
    return prompt

def format_ai_response(ai_response: str, total_issues: int) -> str:
    """
    AI yanıtını düzenler.
    
    Args:
        ai_response (str): AI tarafından üretilen yanıt
        total_issues (int): Toplam sorun sayısı
        
    Returns:
        str: Düzenlenmiş AI yanıtı
    """
    header = f"## AI Code Review Summary\n**Total Issues Found**: {total_issues}\n\n"
    return header + ai_response

# Test kodu
if __name__ == "__main__":
    test_static_results = [
        {
            'line': 5,
            'column': 0,
            'type': 'warning',
            'symbol': 'unused-variable',
            'message': 'Unused variable "test_var"',
            'category': 'Unused Code',
            'severity': 'medium'
        }
    ]
    
    import tempfile
    test_code = '''
def hello_world():
    test_var = "unused"
    print("Hello, World!")
'''
    
    # Geçici test dosyası oluşturma
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        result = analyze_with_ai(temp_path, test_static_results, 'python')
        print("AI Analysis Result:")
        print(result)
    finally:
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)