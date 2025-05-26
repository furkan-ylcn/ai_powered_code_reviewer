import subprocess
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import spacy

# Pylint ile statik analiz
def run_pylint(file_path):
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

# AI tabanlı kod analizi (CodeBERT ile)
def ai_code_review(code):
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base")
    nlp_pipe = pipeline("feature-extraction", model=model, tokenizer=tokenizer)
    features = nlp_pipe(code)
    # Burada features çıktısı doğrudan hata vermez, ama kodun anlamını çıkarır.
    # Daha gelişmiş hata tespiti için ek model veya fine-tuning gerekir.
    return features

# NLP ile doğal dilde açıklama
def explain_issue_nlp(message):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(message)
    # Basit bir özetleme veya anahtar kelime çıkarımı
    summary = " ".join([sent.text for sent in doc.sents][:2])
    return summary

# Örnek kullanım
if __name__ == "__main__":
    file_path = "ornek.py"
    pylint_results = run_pylint(file_path)
    print("Pylint Sonuçları:")
    for issue in pylint_results:
        print(f"Line {issue['line']} ({issue['type']}): {issue['message']}")
        explanation = explain_issue_nlp(issue['message'])
        print("Açıklama:", explanation)

    # Kodun tamamını oku ve AI ile analiz et
    with open(file_path, "r") as f:
        code = f.read()
    ai_features = ai_code_review(code)
    print("AI (CodeBERT) Özellik Çıktısı:", ai_features[:1])  # Özellik vektörünün ilk kısmı