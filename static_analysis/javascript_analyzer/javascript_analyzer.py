import subprocess
import json

def run_eslint(file_path):
    command = [
        'npx', 'eslint',
        '--config', '.\\static_analysis\\javascript_analyzer\\eslint.config.mjs',
        file_path,
        '--format', 'json'
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = []
        return output
    except subprocess.CalledProcessError as e:
        try:
            output = json.loads(e.stdout)
        except (json.JSONDecodeError, TypeError):
            output = []
        return output
    except FileNotFoundError:
        print("Command not found. Make sure Node.js and ESLint are installed and accessible.")
        return []

# Örnek kullanım:
# eslint_results = run_eslint('.\\static_analysis\\javascript_analyzer\\testing_file.js')
# print(eslint_results)