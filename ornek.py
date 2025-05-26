import subprocess
import json

def run_pylint(file_path):
    result = subprocess.run(
        ['pylint', file_path, '--output-format=json', '--disable=c0114'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = []
    return output

# Örnek kullanım
pylint_results = run_pylint('ornek.py')
print(pylint_results)
for i in range(len(pylint_results)):
    print("Line" , pylint_results[i]['line'] , "(" , pylint_results[i]['type'] , "): " , pylint_results[i]['message'])