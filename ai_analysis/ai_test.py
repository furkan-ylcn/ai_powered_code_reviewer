from google import genai
from static_analysis.python_analyzer import run_pylint

def analyze_with_ai(file_path, pylint_results):
    """Pylint sonuçlarını ve kod içeriğini kullanarak AI analizi yapar."""
    if not pylint_results:
        return "Kod analizi sonucunda herhangi bir sorun tespit edilmedi."

    # Dosya içeriğini al
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Sorunları kategorilere ayır
    issues_by_category = {}
    for issue in pylint_results:
        category = issue['type']
        if category not in issues_by_category:
            issues_by_category[category] = []
        issues_by_category[category].append(issue)

    # AI için prompt hazırla
    prompt = f"""Aşağıdaki Python kodunu ve tespit edilen sorunları analiz et:

```python
{file_content}
Tespit edilen sorunlar:
"""

    for category, issues in issues_by_category.items():
        prompt += f"\n{category.upper()} sorunlar:\n"
        for issue in issues:
            prompt += f"- Satır {issue['line']}: {issue['message']}\n"

    prompt += """Her sorun için:
- Sorunun ne olduğunu açıkla
- Sorunu nasıl düzeltebileceğini öner
- Bu tür sorunlardan kaçınmak için en iyi uygulamaları öner
"""
    # OpenAI API'sini kullan
    client = genai.Client(api_key="AIzaSyBVgsYjm3nuQjZlWwL51wGVEVg454PAfyM")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text


pylint_results = run_pylint('ornek.py')
ai_results = analyze_with_ai("ornek.py", pylint_results)
print("AI Analiz Sonuçları:")
print(ai_results)

# client = genai.Client(api_key="AIzaSyBVgsYjm3nuQjZlWwL51wGVEVg454PAfyM")

# response = client.models.generate_content(
#     model="gemini-2.0-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)