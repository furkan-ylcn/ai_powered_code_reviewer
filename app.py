from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from analyzers.python_analyzer import run_pylint
from analyzers.javascript_analyzer import run_eslint
from analyzers.ai_analyzer import analyze_with_ai
from utils.file_handler import save_temp_file, cleanup_temp_file, clean_code_content, analyze_content_issues

app = Flask(__name__)
app.secret_key = 'furkan123'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# temp klasörünün varlığını kontrol et veya oluştur
os.makedirs('temp', exist_ok=True)

SUPPORTED_LANGUAGES = {
    'python': {
        'extensions': ['.py'],
        'analyzer': run_pylint,
        'mode': 'python'
    },
    'javascript': {
        'extensions': ['.js', '.mjs'],
        'analyzer': run_eslint,
        'mode': 'javascript'
    }
}

@app.route('/')
def index():
    """Input formun görüntülendiği ana sayfa."""
    return render_template('index.html', languages=SUPPORTED_LANGUAGES.keys())

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Gönderilen kodu analiz eder ve sonuçları döner."""
    try:
        # form verilerini al
        language = request.form.get('language')
        code_content = request.form.get('code_content', '').strip()
        uploaded_file = request.files.get('code_file')
        
        # dilin doğruluğunu kontrol et
        if language not in SUPPORTED_LANGUAGES:
            flash('Unsupported language selected.', 'error')
            return redirect(url_for('index'))
        
        # dosyadan veya textareadan kod içeriğini al
        if uploaded_file and uploaded_file.filename:
            # dosya yükle
            filename = secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in SUPPORTED_LANGUAGES[language]['extensions']:
                flash(f'Invalid file extension for {language}. Expected: {", ".join(SUPPORTED_LANGUAGES[language]["extensions"])}', 'error')
                return redirect(url_for('index'))
            
            try:
                code_content = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                flash('File encoding error. Please ensure the file is UTF-8 encoded.', 'error')
                return redirect(url_for('index'))
        
        elif not code_content:
            flash('Please provide code content either by typing or uploading a file.', 'error')
            return redirect(url_for('index'))
        
        if not code_content.strip():
            flash('Code content cannot be empty.', 'error')
            return redirect(url_for('index'))
        
        # işlenmeden önce kod içeriğini olası hatalar için kontrol et
        content_analysis = analyze_content_issues(code_content)
        
        # kod içeriğini temizle
        original_content = code_content
        cleaned_content = clean_code_content(code_content)
        
        # temizlenmiş kodu geçici bir dosyaya kaydet
        temp_file_path = save_temp_file(cleaned_content, language)
        
        try:
            # statik analiz çalıştır
            analyzer_func = SUPPORTED_LANGUAGES[language]['analyzer']
            static_results = analyzer_func(temp_file_path)
            
            # carriage return hatalarını filtrele
            filtered_results = []
            for result in static_results:
                if (result.get('symbol') == 'syntax-error' and 
                    'invalid non-printable character U+000D' in result.get('message', '')):
                    if '\r' not in cleaned_content:
                        continue 
                filtered_results.append(result)
            
            # ai analizi çalıştır
            ai_analysis = analyze_with_ai(temp_file_path, filtered_results, language)
            
            # eğer kod temizlenirken işlemler yapıldıysa bu bilgiyi ai analizine ekle
            if content_analysis['has_issues']:
                cleaning_info = "\n\n**Content Cleaning Applied:**\n"
                for fix in content_analysis['fixes_applied']:
                    cleaning_info += f"- {fix}\n"
                ai_analysis = cleaning_info + ai_analysis
            
            # sonuçları hazırla
            results = {
                'language': language,
                'code_content': original_content,  
                'cleaned_content': cleaned_content, 
                'static_analysis': filtered_results,
                'ai_analysis': ai_analysis,
                'total_issues': len(filtered_results),
                'content_issues': content_analysis
            }
            
            return render_template('results.html', results=results)
            
        finally:
            # geçici dosyayı temizle
            cleanup_temp_file(temp_file_path)
            
    except UnicodeDecodeError:
        flash('File encoding error. Please ensure your file is saved with UTF-8 encoding.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred during analysis: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Kod analizinin yapıldığı API endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        language = data.get('language')
        code_content = data.get('code_content', '').strip()
        
        # girdiyi doğrula
        if not language or language not in SUPPORTED_LANGUAGES:
            return jsonify({'error': 'Invalid or missing language'}), 400
        
        if not code_content:
            return jsonify({'error': 'Code content is required'}), 400
        
        # kod içeriğini temizle ve analiz et
        content_analysis = analyze_content_issues(code_content)
        cleaned_content = clean_code_content(code_content)
        
        # kodu geçici bir dosyaya kaydet
        temp_file_path = save_temp_file(cleaned_content, language)
        
        try:
            # statik analiz çalıştır
            analyzer_func = SUPPORTED_LANGUAGES[language]['analyzer']
            static_results = analyzer_func(temp_file_path)
            
            # carriage return hatalarını filtrele
            filtered_results = []
            for result in static_results:
                if (result.get('symbol') == 'syntax-error' and 
                    'invalid non-printable character U+000D' in result.get('message', '')):
                    if '\r' not in cleaned_content:
                        continue
                filtered_results.append(result)
            
            # ai analizi çalıştır
            ai_analysis = analyze_with_ai(temp_file_path, filtered_results, language)
            
            # sonuçları döndür
            return jsonify({
                'success': True,
                'language': language,
                'static_analysis': filtered_results,
                'ai_analysis': ai_analysis,
                'total_issues': len(filtered_results),
                'content_cleaning': content_analysis
            })
            
        finally:
            # geçici dosyayı temizle
            cleanup_temp_file(temp_file_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', languages=SUPPORTED_LANGUAGES.keys()), 404

@app.errorhandler(500)
def server_error(e):
    flash('An internal server error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)