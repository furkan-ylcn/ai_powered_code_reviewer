import subprocess
import json
import os

def run_pylint(file_path):
    """
    Pylint'in koşulması ve sonuçların döndürülmesi
    
    Args:
        file_path (str): python dosyasının yeri
        
    Returns:
        list: Koddaki hataların listesi
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        # Pylintin koşulması ve JSON çıktısının alınması
        result = subprocess.run(
            [
                'pylint', 
                file_path, 
                '--output-format=json', 
                '--disable=C0114,C0116,C0115',  # docstring hatalarının devre dışı bırakılması
                '--score=no'  # skorlamanın devre dışı bırakılması
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        # Çıktının işlenmesi and JSON formatında döndürülmesi
        if result.stdout.strip():
            try:
                issues = json.loads(result.stdout)
                
                # Her bir issue için işlenmiş bir liste oluşturulması
                processed_issues = []
                for issue in issues:
                    processed_issue = {
                        'line': issue.get('line', 0),
                        'column': issue.get('column', 0),
                        'type': issue.get('type', 'unknown'),
                        'symbol': issue.get('symbol', ''),
                        'message': issue.get('message', ''),
                        'message_id': issue.get('message-id', ''),
                        'severity': get_severity_level(issue.get('type', '')),
                        'category': categorize_issue(issue.get('type', ''), issue.get('symbol', ''))
                    }
                    processed_issues.append(processed_issue)
                
                return processed_issues
                
            except json.JSONDecodeError as e:
                print(f"Error parsing pylint JSON output: {e}")
                return []
        else:
            # Hata yoksa boş liste döndürülmesi
            return []
            
    except subprocess.TimeoutExpired:
        print("Pylint analysis timed out")
        return []
    except subprocess.CalledProcessError as e:
        # Eğer hata varsa Pylint 0 harici bir çıkış döndürür. Sonrasında hatalar işlenir.
        if e.stdout:
            try:
                issues = json.loads(e.stdout)
                processed_issues = []
                for issue in issues:
                    processed_issue = {
                        'line': issue.get('line', 0),
                        'column': issue.get('column', 0),
                        'type': issue.get('type', 'unknown'),
                        'symbol': issue.get('symbol', ''),
                        'message': issue.get('message', ''),
                        'message_id': issue.get('message-id', ''),
                        'severity': get_severity_level(issue.get('type', '')),
                        'category': categorize_issue(issue.get('type', ''), issue.get('symbol', ''))
                    }
                    processed_issues.append(processed_issue)
                return processed_issues
            except json.JSONDecodeError:
                return []
        return []
    except FileNotFoundError:
        print("Pylint not found. Please install pylint: pip install pylint")
        return []
    except Exception as e:
        print(f"Error running pylint: {e}")
        return []

def get_severity_level(issue_type):
    """
    Hatanın şiddet seviyesini belirleme.
    
    Args:
        issue_type (str): Pylint hata bilgisi (e.g., 'error', 'warning')
        
    Returns:
        str: Hata şiddeti ('high', 'medium', 'low', 'critical', 'info')
    """
    severity_map = {
        'error': 'high',
        'fatal': 'critical',
        'warning': 'medium',
        'refactor': 'low',
        'convention': 'low',
        'information': 'info'
    }
    return severity_map.get(issue_type.lower(), 'medium')

def categorize_issue(issue_type, symbol):
    """
    Hata tipine göre kategoriyi belirleme.
    
    Args:
        issue_type (str): Pylint hata tipi (e.g., 'error', 'warning')
        symbol (str): Hata sembolü (e.g., 'unused-variable')
        
    Returns:
        str: Hata kategorisi
    """
    if issue_type in ['error', 'fatal']:
        return 'Syntax/Logic Error'
    elif issue_type == 'warning':
        if 'unused' in symbol:
            return 'Unused Code'
        elif 'import' in symbol:
            return 'Import Issue'
        else:
            return 'Code Quality'
    elif issue_type == 'refactor':
        return 'Code Structure'
    elif issue_type == 'convention':
        return 'Style/Convention'
    else:
        return 'Other'

# Test kodu
if __name__ == "__main__":
    test_code = '''
import os
import sys

def test_function():
    x = 1
    y = 2
    print("Hello World")
    
unused_var = "This is unused"
'''
    
    # Geçici dosya oluşturma ve Pylint'i çalıştırma
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        results = run_pylint(temp_path)
        print("Test Results:")
        for issue in results:
            print(f"Line {issue['line']}: {issue['message']} ({issue['severity']})")
    finally:
        os.unlink(temp_path)