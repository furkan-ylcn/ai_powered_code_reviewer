/**
 * Main JavaScript dosyası
 * Frontend etkileşimlşeri, form doğrulama ve dinamik içerik
 */

// Örnek kod parçaları
const sampleCode = {
    python: `import os
import sys

# This function has several issues
def calculate_average(numbers):
    unused_var = "This variable is never used"
    total = 0
    count = 0
    
    for num in numbers:
        total += num
        count += 1
    
    # Potential division by zero
    return total / count

# Missing function documentation
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

# Main execution
if __name__ == "__main__":
    test_numbers = [1, 2, 3, 4, 5]
    avg = calculate_average(test_numbers)
    print(f"Average: {avg}")`,

    javascript: `// JavaScript code with various issues
var unusedVariable = "This variable is never used";
let duplicateVar = 1;

function calculateTotal(items) {
    var sum = 0;  // Should use let/const
    
    for (var i = 0; i < items.length; i++) {
        sum += items[i]  // Missing semicolon
    }
    
    // Using == instead of ===
    if (sum == 0) {
        console.log("Total is zero");
    }
    
    return sum;
}

// Function with unused parameter
function processItem(item, unusedParam) {
    return item * 2;
}

// Missing const for variable that never changes
let PI_VALUE = 3.14159;

// Inconsistent quotes
let message1 = "Hello World";
let message2 = 'Hello World';

calculateTotal([1, 2, 3, 4, 5]);`
};

// Main application objesi
const CodeReviewer = {
    // uygulamanın initialize edilmesi
    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.initializeCodeEditor();
    },

    // Event binding
    bindEvents() {
        // input metodunun seçilmesi
        const textareaMethod = document.getElementById('textarea_method');
        const fileMethod = document.getElementById('file_method');
        
        if (textareaMethod && fileMethod) {
            textareaMethod.addEventListener('change', this.toggleInputMethod.bind(this));
            fileMethod.addEventListener('change', this.toggleInputMethod.bind(this));
        }

        const codeForm = document.getElementById('codeForm');
        if (codeForm) {
            codeForm.addEventListener('submit', this.handleFormSubmission.bind(this));
        }

        // kod temizleme butonu
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', this.clearForm.bind(this));
        }

        // dil seçimi değişikliği
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', this.handleLanguageChange.bind(this));
        }

        // dosya input metodunun değiştirilmesi
        const fileInput = document.getElementById('code_file');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelection.bind(this));
        }

        // kod kontent textarea'sının input ve paste olayları
        const codeTextarea = document.getElementById('code_content');
        if (codeTextarea) {
            codeTextarea.addEventListener('input', this.handleCodeInput.bind(this));
            codeTextarea.addEventListener('paste', this.handleCodePaste.bind(this));
        }
    },

    // form doğrulama setup ı
    setupFormValidation() {
        const form = document.getElementById('codeForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    },

    // kod editörünün initialize edilmesi (codemirror)
    initializeCodeEditor() {
        const textarea = document.getElementById('code_content');
        if (!textarea || typeof CodeMirror === 'undefined') return;

        this.codeEditor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: 'python',
            theme: 'default',
            indentUnit: 4,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            showCursorWhenSelecting: true,
            extraKeys: {
                'Ctrl-Space': 'autocomplete',
                'Tab': (cm) => {
                    if (cm.somethingSelected()) {
                        cm.indentSelection('add');
                    } else {
                        cm.replaceSelection('    ', 'end');
                    }
                }
            }
        });

        // dil değişirse editörün güncellenmesi
        this.codeEditor.on('change', () => {
            textarea.value = this.codeEditor.getValue();
        });
    },

    // input metodunun değiştirilmesi
    toggleInputMethod() {
        const textareaSection = document.getElementById('textarea_section');
        const fileUploadSection = document.getElementById('file_upload_section');
        const textareaMethod = document.getElementById('textarea_method');
        const fileInput = document.getElementById('code_file');

        if (!textareaSection || !fileUploadSection || !textareaMethod) return;

        if (textareaMethod.checked) {
            textareaSection.style.display = 'block';
            fileUploadSection.style.display = 'none';
            if (fileInput) fileInput.removeAttribute('required');
        } else {
            textareaSection.style.display = 'none';
            fileUploadSection.style.display = 'block';
            if (fileInput) fileInput.setAttribute('required', 'required');
        }
    },

    // handle form
    handleFormSubmission(e) {
        if (!this.validateForm()) {
            e.preventDefault();
            return false;
        }

        // loading modal
        this.showLoadingModal();
        
        // hata olursa 30 saniye sonra loading modalı gizle
        setTimeout(() => {
            this.hideLoadingModal();
        }, 30000);
    },

    // form datasını validate etme
    validateForm() {
        const language = document.getElementById('language').value;
        const textareaMethod = document.getElementById('textarea_method').checked;
        const codeContent = document.getElementById('code_content').value.trim();
        const fileInput = document.getElementById('code_file');

        // dil seçimi kontrolü
        if (!language) {
            this.showAlert('Please select a programming language.', 'warning');
            return false;
        }

        // content kontrolü
        if (textareaMethod) {
            if (!codeContent) {
                this.showAlert('Please enter some code to analyze.', 'warning');
                return false;
            }
            if (codeContent.length < 10) {
                this.showAlert('Code content seems too short. Please provide more code for analysis.', 'warning');
                return false;
            }
        } else {
            if (!fileInput.files || !fileInput.files[0]) {
                this.showAlert('Please select a file to upload.', 'warning');
                return false;
            }
            
            // dosya uzantısı kontrolü
            const file = fileInput.files[0];
            const validExtensions = this.getValidExtensions(language);
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!validExtensions.includes(fileExtension)) {
                this.showAlert(`Invalid file extension. Expected: ${validExtensions.join(', ')}`, 'warning');
                return false;
            }

            // dosya boyutunu kontrol et (16MB limit)
            if (file.size > 16 * 1024 * 1024) {
                this.showAlert('File size exceeds 16MB limit.', 'warning');
                return false;
            }
        }

        return true;
    },

    // dillere göre geçerli uzantıları döndürme
    getValidExtensions(language) {
        const extensions = {
            python: ['.py'],
            javascript: ['.js', '.mjs']
        };
        return extensions[language] || [];
    },

    // dil değişikliğini handle etme
    handleLanguageChange(e) {
        const language = e.target.value;
        
        // codemirror güncelleme
        if (this.codeEditor && language) {
            const modes = {
                python: 'python',
                javascript: 'javascript'
            };
            this.codeEditor.setOption('mode', modes[language] || 'text');
        }

        // dosya input metodunun değiştirilmesi
        const fileInput = document.getElementById('code_file');
        if (fileInput && language) {
            const validExtensions = this.getValidExtensions(language);
            fileInput.setAttribute('accept', validExtensions.join(','));
        }
    },

    // dosya seçimini handle etme
    handleFileSelection(e) {
        const file = e.target.files[0];
        if (!file) return;

        // dosya bilgilerini gosterme
        const fileInfo = document.createElement('div');
        fileInfo.className = 'mt-2 text-muted'; // still için stil ekleme
        fileInfo.innerHTML = `
            <small>
                <i class="fas fa-file me-1"></i>
                Selected: ${file.name} (${this.formatFileSize(file.size)})
            </small>
        `;

        // hali hazırda bulunan file-info yu kaldırma
        const existingInfo = e.target.parentNode.querySelector('.file-info');
        if (existingInfo) {
            existingInfo.remove();
        }

        fileInfo.className += ' file-info';
        e.target.parentNode.appendChild(fileInfo);

        // eğer dil seçilmemişse dosya uzantısına göre dil seçimini yapma
        const languageSelect = document.getElementById('language');
        if (languageSelect && !languageSelect.value) {
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            if (extension === '.py') {
                languageSelect.value = 'python';
            } else if (['.js', '.mjs'].includes(extension)) {
                languageSelect.value = 'javascript';
            }
            this.handleLanguageChange({ target: languageSelect });
        }
    },

    // kod inputunu handle etme
    handleCodeInput(e) {
        const content = e.target.value;
        
        // eğer dil seçilmemişse içeriğe göre dil tespiti
        const languageSelect = document.getElementById('language');
        if (languageSelect && !languageSelect.value && content.trim()) {
            const detectedLanguage = this.detectLanguage(content);
            if (detectedLanguage) {
                languageSelect.value = detectedLanguage;
                this.handleLanguageChange({ target: languageSelect });
            }
        }
    },

    // kod yapıştırma
    handleCodePaste(e) {
        // kodun yapıştırılmasını beklemek için delay
        setTimeout(() => {
            this.handleCodeInput(e);
        }, 100);
    },

    // dil tespiti
    detectLanguage(content) {
        // Python indicators
        if (/def\s+\w+\s*\(/m.test(content) || 
            /import\s+\w+/m.test(content) || 
            /from\s+\w+\s+import/m.test(content) ||
            /print\s*\(/m.test(content)) {
            return 'python';
        }
        
        // JavaScript indicators
        if (/function\s+\w+\s*\(/m.test(content) || 
            /const\s+\w+\s*=/m.test(content) || 
            /let\s+\w+\s*=/m.test(content) ||
            /console\.log\s*\(/m.test(content) ||
            /=>\s*{/m.test(content)) {
            return 'javascript';
        }
        
        return null;
    },

    // formu temizleme
    clearForm() {
        const form = document.getElementById('codeForm');
        if (form) {
            form.reset();
            form.classList.remove('was-validated');
        }

        // codemirror temizleme
        if (this.codeEditor) {
            this.codeEditor.setValue('');
        }

        // file info temizleme
        const fileInfo = document.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.remove();
        }

        // input metodunu temizleme
        const textareaMethod = document.getElementById('textarea_method');
        if (textareaMethod) {
            textareaMethod.checked = true;
            this.toggleInputMethod();
        }
    },

    // örnek kodu yükleme
    loadSampleCode(language) {
        if (!sampleCode[language]) return;

        // dili seç
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.value = language;
            this.handleLanguageChange({ target: languageSelect });
        }

        // textarea_method set et
        const textareaMethod = document.getElementById('textarea_method');
        if (textareaMethod) {
            textareaMethod.checked = true;
            this.toggleInputMethod();
        }

        // code_content set et
        const codeTextarea = document.getElementById('code_content');
        if (codeTextarea) {
            codeTextarea.value = sampleCode[language];
        }

        // codemirroru güncelle
        if (this.codeEditor) {
            this.codeEditor.setValue(sampleCode[language]);
        }

        // textarea_section scroll
        const textareaSection = document.getElementById('textarea_section');
        if (textareaSection) {
            textareaSection.scrollIntoView({ behavior: 'smooth' });
        }

        this.showAlert(`${language.charAt(0).toUpperCase() + language.slice(1)} sample code loaded!`, 'success');
    },

    // loading modal
    showLoadingModal() {
        const modal = document.getElementById('loadingModal');
        if (modal && typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            this.loadingModal = bsModal;
        }
    },

    // loading modalı gizleme
    hideLoadingModal() {
        if (this.loadingModal) {
            this.loadingModal.hide();
            this.loadingModal = null;
        }
    },

    // show alert
    showAlert(message, type = 'info') {
        // alert olusturma
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // container bul veya oluştur
        let container = document.querySelector('.alert-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container';
            document.querySelector('main').prepend(container);
        }

        // alert ekle
        container.appendChild(alert);

        // 5 sn sonra alerti kaldır
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    },

    // alert ikonunu döndürme
    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            danger: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // dosya boyutunu formatlama
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // sonuç sayfasını initialize etme
    initResultsPage() {
        this.formatAIAnalysis();
        this.initCodeToggle();
        this.initPrintButton();
        
        // syntax highlight
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    },

    // ai analiz sonuçlarını formatlama
    formatAIAnalysis() {
        const content = document.querySelector('.ai-analysis-content');
        if (!content) return;

        let html = content.innerHTML;

        // Convert markdown-style headers to HTML
        html = html.replace(/^## (.*$)/gim, '<h4 class="mt-4 mb-3 text-primary"><i class="fas fa-chevron-right me-2"></i>$1</h4>');
        html = html.replace(/^### (.*$)/gim, '<h5 class="mt-3 mb-2 text-secondary">$1</h5>');

        // Convert **bold** to HTML
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Convert bullet points
        html = html.replace(/^- (.*$)/gim, '<li class="mb-1">$1</li>');

        // Wrap consecutive list items in ul tags
        html = html.replace(/(<li.*?<\/li>\s*)+/g, '<ul class="mb-3">$&</ul>');

        // Convert code blocks
        html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-light p-3 rounded"><code class="language-$1">$2</code></pre>');

        // Convert inline code
        html = html.replace(/`([^`]+)`/g, '<code class="bg-light px-2 py-1 rounded">$1</code>');

        // Convert line breaks
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>\s*<h/g, '<h');
        html = html.replace(/<\/h([1-6])>\s*<\/p>/g, '</h$1>');
        html = html.replace(/<p>\s*<ul/g, '<ul');
        html = html.replace(/<\/ul>\s*<\/p>/g, '</ul>');

        content.innerHTML = html;
    },

    // kod toggle butonunu initialize etme
    initCodeToggle() {
        const toggleBtn = document.querySelector('[onclick="toggleCode()"]');
        if (toggleBtn) {
            toggleBtn.onclick = this.toggleCode.bind(this);
        }
    },

    // kod toggle fonksiyonu
    toggleCode() {
        const container = document.getElementById('codeContainer');
        if (!container) return;

        const pre = container.querySelector('pre');
        if (!pre) return;

        if (pre.style.maxHeight === 'none' || !pre.style.maxHeight) {
            pre.style.maxHeight = '400px';
            pre.style.overflowY = 'auto';
        } else {
            pre.style.maxHeight = 'none';
            pre.style.overflowY = 'visible';
        }
    },

    // print butonunu initialize etme
    initPrintButton() {
        const printBtn = document.querySelector('[onclick="window.print()"]');
        if (printBtn) {
            printBtn.onclick = (e) => {
                e.preventDefault();
                this.printResults();
            };
        }
    },

    // print işlemi
    printResults() {
        // print stilleri
        const printStyles = `
            @media print {
                .btn, .navbar, .modal { display: none !important; }
                .card { border: 1px solid #dee2e6 !important; page-break-inside: avoid; }
                .card-header { background-color: #f8f9fa !important; color: #000 !important; }
                pre { font-size: 10px; page-break-inside: avoid; }
                .alert { border: 1px solid #dee2e6; page-break-inside: avoid; }
                h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
                .ai-analysis-content h4, .ai-analysis-content h5 { color: #000 !important; }
                body { font-size: 12px; }
            }
        `;

        // print stylesheet ekleme
        const styleSheet = document.createElement('style');
        styleSheet.textContent = printStyles;
        document.head.appendChild(styleSheet);

        // print
        window.print();

        // yazdırma sonrası stylesheet kaldırma
        setTimeout(() => {
            document.head.removeChild(styleSheet);
        }, 1000);
    }
};

// backward compatibility için global fonksiyonlar
function loadSampleCode(language) {
    CodeReviewer.loadSampleCode(language);
}

function toggleCode() {
    CodeReviewer.toggleCode();
}

// DOM yüklendiğinde uygulamayı başlatma
document.addEventListener('DOMContentLoaded', function() {
    CodeReviewer.init();
    
    // result sayfasında olunup olunmadığını kontrol etme
    if (document.querySelector('.ai-analysis-content')) {
        CodeReviewer.initResultsPage();
    }
    
    // sayfa görünürlüğü değiştiğinde loading modalını gizleme
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            CodeReviewer.hideLoadingModal();
        }
    });
});

// handle window beforeunload
window.addEventListener('beforeunload', function() {
    CodeReviewer.hideLoadingModal();
});

// modül export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeReviewer;
}