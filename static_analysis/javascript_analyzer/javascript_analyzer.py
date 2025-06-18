import subprocess
import json
import os
import tempfile

def run_eslint(file_path):
    """
    ESLint analizi yapar ve sonuçları döndürür.
    
    Args:
        file_path (str): JavaScript dosyasının yolu
        
    Returns:
        list: Koddaki hataların listesi
    """
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return []
    
    # ESLint v9+ için basit bir yaklaşım - inline config kullanma
    try:
        # ESLint v9+ ile çalışmak için ESLINT_USE_FLAT_CONFIG=false kullanılmalı
        env = os.environ.copy()
        env['ESLINT_USE_FLAT_CONFIG'] = 'false'
        
        command = [
            'npx', 'eslint',
            file_path,
            '--format', 'json',
            '--no-eslintrc',  # ESLint config dosyasını kullanma
            '--rule', 'no-unused-vars: warn',
            '--rule', 'no-console: off',
            '--rule', 'no-undef: error',
            '--rule', 'no-unreachable: error',
            '--rule', 'semi: [warn, always]',
            '--rule', 'quotes: [warn, single]',
            '--rule', 'eqeqeq: warn',
            '--rule', 'no-eval: error',
            '--rule', 'no-var: warn',
            '--rule', 'prefer-const: warn',
            '--env', 'browser,node,es6'
        ]
        
        print(f"Running command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True if os.name == 'nt' else False,
            env=env
        )
        
        # Terminalde debug
        # print(f"ESLint return code: {result.returncode}")
        # print(f"ESLint stdout: {result.stdout}")
        # print(f"ESLint stderr: {result.stderr}")
        
        # ESLint çıktısının işlenmesi
        output_to_parse = result.stdout
        
        # Eğer stdout boşsa stderr'i kontrol edilmesi (ESLint v9+ bazen stderr'e yazıyor)
        if not output_to_parse.strip() and result.stderr.strip():
            # stderr'den JSON çıkarılmaya çalışılması
            lines = result.stderr.split('\n')
            for line in lines:
                if line.strip().startswith('[') or line.strip().startswith('{'):
                    output_to_parse = line
                    break
        
        if output_to_parse.strip():
            try:
                eslint_output = json.loads(output_to_parse)
                print(f"Parsed ESLint output: {eslint_output}")
                
                # Her bir issue için işlenmiş bir liste oluşturulması
                processed_issues = []
                for file_result in eslint_output:
                    for message in file_result.get('messages', []):
                        processed_issue = {
                            'line': message.get('line', 0),
                            'column': message.get('column', 0),
                            'type': 'error' if message.get('severity') == 2 else 'warning',
                            'symbol': message.get('ruleId', ''),
                            'message': message.get('message', ''),
                            'message_id': message.get('ruleId', ''),
                            'severity': get_severity_level(message.get('severity', 1)),
                            'category': categorize_js_issue(message.get('ruleId', ''))
                        }
                        processed_issues.append(processed_issue)
                
                return processed_issues
                
            except json.JSONDecodeError as e:
                print(f"Error parsing ESLint JSON output: {e}")
                print(f"Raw output was: {output_to_parse}")
                return []
        else:
            print("No ESLint output received")
            return []
            
    except subprocess.TimeoutExpired:
        print("ESLint analysis timed out")
        return []
    except subprocess.CalledProcessError as e:
        print(f"ESLint process error: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        
        # ESLint hata bulduğunda non-zero exit code döndürür
        if e.stdout:
            try:
                eslint_output = json.loads(e.stdout)
                processed_issues = []
                for file_result in eslint_output:
                    for message in file_result.get('messages', []):
                        processed_issue = {
                            'line': message.get('line', 0),
                            'column': message.get('column', 0),
                            'type': 'error' if message.get('severity') == 2 else 'warning',
                            'symbol': message.get('ruleId', ''),
                            'message': message.get('message', ''),
                            'message_id': message.get('ruleId', ''),
                            'severity': get_severity_level(message.get('severity', 1)),
                            'category': categorize_js_issue(message.get('ruleId', ''))
                        }
                        processed_issues.append(processed_issue)
                return processed_issues
            except json.JSONDecodeError:
                return []
        return []
    except FileNotFoundError:
        print("ESLint not found. Please install ESLint: npm install eslint")
        return []
    except Exception as e:
        print(f"Error running ESLint: {e}")
        return []

def get_severity_level(eslint_severity):
    """
    ESLint hata şiddet değerini kendi belirlediğimiz seviyelere dönüştürür.
    
    Args:
        eslint_severity (int): ESLint şiddet seviyesi (1=warning, 2=error)
        
    Returns:
        str: Şiddet seviyesi ('low', 'medium', 'high')
    """
    if eslint_severity == 2:
        return 'high'
    elif eslint_severity == 1:
        return 'medium'
    else:
        return 'low'

def categorize_js_issue(rule_id):
    """
    JavaScript hatalarını kategorize eder.
    
    Args:
        rule_id (str): ESLint kuralı ID'si
        
    Returns:
        str: Hata kategorisi
    """
    if not rule_id:
        return 'Other'
    
    # Syntax and logic hatalar
    if rule_id in ['no-undef', 'no-unreachable', 'no-dupe-keys', 'no-duplicate-case']:
        return 'Syntax/Logic Error'
    
    # Stil ve konvansiyon hataları
    elif rule_id in ['semi', 'quotes', 'indent', 'brace-style', 'comma-style']:
        return 'Style/Convention'
    
    # Kod kalitesi
    elif rule_id in ['eqeqeq', 'no-eval', 'no-implied-eval', 'no-with']:
        return 'Code Quality'
    
    # Kullanılmayan kodlar
    elif rule_id in ['no-unused-vars', 'no-unused-expressions']:
        return 'Unused Code'
    
    # Değişken tanımlamaları
    elif rule_id in ['no-var', 'prefer-const', 'no-redeclare']:
        return 'Code Structure'
    
    # En iyi uygulamalar
    elif rule_id in ['no-alert', 'no-console', 'radix']:
        return 'Best Practices'
    
    else:
        return 'Other'

# ESLint kurulumunu test etme debug için
def test_eslint_installation():
    """ESLint'in kurulu ve çalışır durumda olup olmadığını test eder."""
    try:
        result = subprocess.run(['npx', 'eslint', '--version'], 
                              capture_output=True, text=True,
                              shell=True if os.name == 'nt' else False)
        print(f"ESLint version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"ESLint not found or not working: {e}")
        return False

# Test kodu
if __name__ == "__main__":
    print("Testing ESLint installation...")
    if not test_eslint_installation():
        print("Please install ESLint first: npm install -g eslint")
        exit(1)
    
    test_code = '''
var unusedVariable = "This variable is never used";
let duplicateVar = 1;

function testFunction() {
    console.log("Hello World")  // Missing semicolon
    
    if (true) {
        var x = 10
        console.log(x)  // Missing semicolon
    }
    
    // Using == instead of ===
    if (x == 10) {
        console.log("x is 10");
    }
    
    // Unreachable code
    return true;
    console.log("This will never execute");
}

testFunction();
'''
    
    print("Creating test file...")
    # Geçici dosya oluşturma ve ESLint'i çalıştırma
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    print(f"Test file created: {temp_path}")
    # print("Test file contents:")
    # print(test_code)
    # print("=" * 50)
    
    try:
        results = run_eslint(temp_path)
        print("Test Results:")
        if results:
            for issue in results:
                print(f"Line {issue['line']}: {issue['message']} ({issue['severity']}) - Category: {issue['category']}")
        else:
            print("No issues found or ESLint failed to run properly")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print(f"Cleaned up test file: {temp_path}")