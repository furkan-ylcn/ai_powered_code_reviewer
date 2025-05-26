import subprocess
import json
import os
from openai import OpenAI

# OpenAI API anahtarınızı buraya ekleyin veya çevre değişkenlerinden alın
client = OpenAI(api_key="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")

def run_pylint(file_path):
    """Pylint ile statik kod analizi yapar ve sonuçları JSON formatında döndürür."""
    result = subprocess.run(
        ['pylint', file_path, '--output-format=json', '--disable=c0114,C0116'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = []
    return output

def get_file_content(file_path):
    """Dosya içeriğini okur."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def analyze_with_ai(file_path, pylint_results):
    """Pylint sonuçlarını ve kod içeriğini kullanarak AI analizi yapar."""
    if not pylint_results:
        return "Kod analizi sonucunda herhangi bir sorun tespit edilmedi."

    # Dosya içeriğini al
    file_content = get_file_content(file_path)

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

    prompt += """
Her sorun için:

Sorunun ne olduğunu açıkla
Nasıl düzeltilebileceğini göster (düzeltilmiş kod parçası ile)
Bu tür sorunlardan kaçınmak için en iyi uygulamaları öner
Yanıtını kategorilere göre düzenle ve markdown formatında ver.
"""

    # OpenAI API'sini kullan
    response = client.chat.completions.create(
        model="gpt-3.5", # veya erişiminiz olan başka bir model
        messages=[
            {"role": "system", "content": "Sen deneyimli bir Python geliştiricisi ve kod inceleme uzmanısın. Kod kalitesi, temiz kod yazma ve Python en iyi uygulamaları konusunda derin bilgiye sahipsin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

def main():
    """Ana program akışı."""
    file_path = "./ornek.py"

    # Dosyanın varlığını kontrol et
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} dosyası bulunamadı.")
        return

    print(f"\n{file_path} dosyası analiz ediliyor...\n")

    # Pylint ile statik analiz yap
    pylint_results = run_pylint(file_path)

    # Sonuçları ekrana yazdır
    print("Statik analiz sonuçları:")
    if pylint_results:
        for i, issue in enumerate(pylint_results, 1):
            print(f"{i}. Satır {issue['line']} ({issue['type']}): {issue['message']}")
    else:
        print("Statik analiz sonucunda herhangi bir sorun tespit edilmedi.")

    print("\nAI analizi çalıştırılıyor...\n")

    # AI ile analiz yap
    ai_analysis = analyze_with_ai(file_path, pylint_results)

    print("AI Analiz Sonuçları:")
    print(ai_analysis)

    # Sonuçları dosyaya kaydet
    output_file = f"{os.path.splitext(file_path)[0]}_review.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {file_path} Kod İncelemesi\n\n")
        f.write("## Statik Analiz Sonuçları\n\n")
        if pylint_results:
            for i, issue in enumerate(pylint_results, 1):
                f.write(f"{i}. Satır {issue['line']} ({issue['type']}): {issue['message']}\n")
        else:
            f.write("Statik analiz sonucunda herhangi bir sorun tespit edilmedi.\n")

        f.write("\n## AI Analiz Sonuçları\n\n")
        f.write(ai_analysis)

    print(f"\nSonuçlar {output_file} dosyasına kaydedildi.")

if __name__ == "__main__":
    main()