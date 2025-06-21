import os
import tempfile
import uuid
import re
from typing import Optional

def clean_code_content(content: str) -> str:
    """
    Girilen kod içeriğindeki sorunlu karakterleri temizler.
    
    Args:
        content (str): Girilecek kod içeriği
        
    Returns:
        str: Temizlenmiş kod içeriği
    """
    # Satır sonu karakterlerini normalize et
    content = content.replace('\r\n', '\n')  # Windows satır sonları
    content = content.replace('\r', '\n')    # Mac satır sonları
    
    # Diğer sıkıntılı karakterleri temizle
    # gerekli beyaz boşluklar hariç (space, tab, newline)
    cleaned_content = ''
    for char in content:
        # yazdırılabilen karakterleri, newlines, tabs ve regular spaces tut
        if char.isprintable() or char in ['\n', '\t']:
            cleaned_content += char
        elif char == '\r':
            # kalan carriagereturnler newlines yap
            cleaned_content += '\n'
    
    # sorun yaratabilecek zero-width karakterlerin kaldırılması
    zero_width_chars = [
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\u2060',  # Word joiner
        '\ufeff',  # Byte order mark
    ]
    
    for char in zero_width_chars:
        cleaned_content = cleaned_content.replace(char, '')
    
    # non-breaking spaceleri normal boşluklarla değiştir
    cleaned_content = cleaned_content.replace('\u00a0', ' ')
    
    # birden fazla ardışık yeni satırı temizle
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    
    return cleaned_content

def save_temp_file(content: str, language: str) -> str:
    """
    Temizlenen kod içeriğini geçici bir dosyaya kaydeder.
    
    Args:
        content (str): Kod içeriği
        language (str): Programlama dili ('python', 'javascript')
        
    Returns:
        str: Geçici dosya yolu
    """
    # ilk olarak içeriği temizle
    cleaned_content = clean_code_content(content)
    
    # dosya uzantısını belirle
    extensions = {
        'python': '.py',
        'javascript': '.js'
    }
    
    extension = extensions.get(language, '.txt')
    
    # geçici dosya adını oluştur (unique)
    filename = f"code_analysis_{uuid.uuid4().hex[:8]}{extension}"
    file_path = os.path.join('temp', filename)
    
    # geçici dosyanın oluşturulduğundan emin ol
    os.makedirs('temp', exist_ok=True)
    
    # temizlenmiş içeriği dosyaya yaz
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(cleaned_content)
        return file_path
    except Exception as e:
        raise Exception(f"Failed to save temporary file: {str(e)}")

def cleanup_temp_file(file_path: str) -> bool:
    """
    Geçici dosyayı temizler.
    
    Args:
        file_path (str): Geçici dosya yolu
        
    Returns:
        bool: Başarılı ise True, aksi halde False
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Warning: Failed to cleanup temporary file {file_path}: {str(e)}")
        return False

def cleanup_old_temp_files(max_age_hours: int = 24) -> int:
    """
    temp dizinindeki eski dosyaları temizler.
    
    Args:
        max_age_hours (int): Maksimum yaş (saat cinsinden) eski dosyalar için
        
    Returns:
        int: Temizlenen dosya sayısı
    """
    if not os.path.exists('temp'):
        return 0
    
    import time
    
    cleaned_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for filename in os.listdir('temp'):
            file_path = os.path.join('temp', filename)
            
            # eğer bu bir dosya değilse atla
            if not os.path.isfile(file_path):
                continue
            
            # dosyanın yaşını kontrol et
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception as e:
                    print(f"Warning: Failed to remove old temp file {file_path}: {str(e)}")
    
    except Exception as e:
        print(f"Warning: Error during temp file cleanup: {str(e)}")
    
    return cleaned_count

def get_file_info(file_path: str) -> Optional[dict]:
    """
    Dosya hakkında bilgi alır.
    
    Args:
        file_path (str): Dosya yolu
        
    Returns:
        dict or None: Dosya bilgileri (boyut, son değişiklik zamanı, oluşturulma zamanı, dosya türü, uzantı) veya None
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        stat_info = os.stat(file_path)
        return {
            'size': stat_info.st_size,
            'modified': stat_info.st_mtime,
            'created': stat_info.st_ctime,
            'is_file': os.path.isfile(file_path),
            'extension': os.path.splitext(file_path)[1]
        }
    except Exception as e:
        print(f"Error getting file info for {file_path}: {str(e)}")
        return None

def validate_file_content(content: str, max_size_mb: int = 1) -> tuple[bool, str]:
    """
    Dosya içeriğini doğrular.
    
    Args:
        content (str): Dosya içeriği
        max_size_mb (int): Maksimum izin verilen dosya boyutu (MB cinsinden)(16)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "File content cannot be empty"
    
    # boyut kontrolü
    content_size_mb = len(content.encode('utf-8')) / (1024 * 1024)
    if content_size_mb > max_size_mb:
        return False, f"File size ({content_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
    
    # karakter seti kontrolü
    try:
        content.encode('utf-8')
    except UnicodeEncodeError:
        return False, "File appears to contain binary data"
    
    return True, ""

def analyze_content_issues(content: str) -> dict:
    """
    İçeriği analiz eder ve sorunlu karakterleri tespit eder.
    
    Args:
        content (str): Kod içeriği
        
    Returns:
        dict: İçerikteki sorunlar ve düzeltmeler hakkında bilgi
    """
    issues = []
    fixes_applied = []
    
    # carriage return karakterlerini kontrol et
    if '\r' in content:
        cr_count = content.count('\r')
        issues.append(f"Found {cr_count} carriage return character(s) that may cause issues")
        fixes_applied.append("Converted carriage returns to line feeds")
    
    # zero-width karakterleri kontrol et
    zero_width_chars = ['\u200b', '\u200c', '\u200d', '\u2060', '\ufeff']
    for char in zero_width_chars:
        if char in content:
            char_count = content.count(char)
            issues.append(f"Found {char_count} zero-width character(s) (U+{ord(char):04X})")
            fixes_applied.append(f"Removed zero-width character U+{ord(char):04X}")
    
    # non-breaking space karakterlerini kontrol et
    if '\u00a0' in content:
        nbsp_count = content.count('\u00a0')
        issues.append(f"Found {nbsp_count} non-breaking space(s)")
        fixes_applied.append("Converted non-breaking spaces to regular spaces")
    
    return {
        'issues_found': issues,
        'fixes_applied': fixes_applied,
        'has_issues': len(issues) > 0
    }

# Test kodu
# if __name__ == "__main__":
    # Test file operations with problematic content
    # test_content = "import google\rprint('hello world')"  # Contains carriage return
    
    # print("Testing file operations...")
    # print(f"Original content repr: {repr(test_content)}")
    
    # # Analyze issues
    # analysis = analyze_content_issues(test_content)
    # print(f"Issues found: {analysis['issues_found']}")
    # print(f"Fixes applied: {analysis['fixes_applied']}")
    
    # # Clean content
    # cleaned_content = clean_code_content(test_content)
    # print(f"Cleaned content repr: {repr(cleaned_content)}")
    
    # # Test save and cleanup
    # file_path = save_temp_file(test_content, 'python')
    # print(f"Saved temporary file: {file_path}")
    
    # # Read back and verify
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     read_content = f.read()
    # print(f"File content repr: {repr(read_content)}")
    
    # # Validate content
    # is_valid, message = validate_file_content(cleaned_content)
    # print(f"Content validation: {'Valid' if is_valid else 'Invalid'} - {message}")
    
    # # Cleanup
    # if cleanup_temp_file(file_path):
    #     print("File cleaned up successfully")
    # else:
    #     print("Failed to cleanup file")