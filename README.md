# AI-Powered Code Reviewer

An intelligent web application that analyzes Python and JavaScript code using static analysis tools combined with AI-powered feedback to help developers improve their code quality.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### 📊 Static Code Analysis
- **Python**: Integrated with Pylint for comprehensive Python code analysis
- **JavaScript**: Uses ESLint for JavaScript code quality checking
- **Real-time Detection**: Identifies syntax errors, code smells, and best practice violations

### 🤖 AI-Powered Insights
- **Intelligent Feedback**: Uses Google's Gemini AI for detailed code analysis
- **Contextual Suggestions**: Provides specific improvement recommendations
- **Priority-based Issues**: Categorizes problems by severity (Critical, High, Medium, Low)

### 🛡️ Content Processing
- **Smart Cleaning**: Automatically removes problematic characters (zero-width characters, carriage returns)
- **Encoding Handling**: Robust UTF-8 support with automatic encoding detection
- **File Validation**: Comprehensive input validation and sanitization

### 🌐 User Interface
- **Dual Input Methods**: Support for both text input and file upload
- **Responsive Design**: Modern Bootstrap-based UI that works on all devices
- **Real-time Feedback**: Interactive code editor with syntax highlighting
- **Export Options**: Print-friendly results with detailed reports

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js (for ESLint)
- npm (Node Package Manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/furkan-ylcn/ai_powered_code_reviewer.git
cd ai_powered_code_reviewer
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies
```bash
# Install ESLint globally
npm install -g eslint

# Or install locally in your project
npm install eslint
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
# Required: Google Gemini AI API Key
GEMINI_API_KEY=gemini_api_key

# Optional: Flask configuration
SECRET_KEY=secret_key
FLASK_ENV=development
```

## 🚀 Usage

### Running the Application
```bash
# Start the Flask development server
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Web Interface

1. **Select Language**: Choose between Python or JavaScript
2. **Input Method**: 
   - **Text Input**: Paste or type code directly
   - **File Upload**: Upload `.py`, `.js`, or `.mjs` files
3. **Analyze**: Click "Analyze Code" to start the analysis
4. **Review Results**: View static analysis issues and AI recommendations

### API Usage

The application also provides a REST API endpoint:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code_content": "def hello():\n    print(\"Hello, World!\")"
  }'
```

**API Response:**
```json
{
  "success": true,
  "language": "python",
  "static_analysis": [],
  "ai_analysis": "Code analysis results...",
  "total_issues": 0,
  "content_cleaning": {
    "has_issues": false,
    "issues_found": [],
    "fixes_applied": []
  }
}
```

## 📁 Project Structure

```
ai-powered-code-reviewer/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── .env                 # Environment variables (create from template)
├── .gitignore           # Git ignore rules
├── analyzers/           # Code analysis modules
│   ├── __init__.py
│   ├── python_analyzer.py
│   ├── javascript_analyzer.py
│   └── ai_analyzer.py
├── utils/               # Utility functions
│   ├── __init__.py
│   └── file_handler.py
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── results.html
├── static/             # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── tests/              # Test suite
│   ├── test_framework.py
│   ├── test_analyzers.py
│   ├── test_ai_analyzer.py
│   ├── test_file_handler.py
│   ├── test_flask_app.py
│   └── run_all_tests.py
└── temp/               # Temporary files (auto-created)
```

## 🧪 Testing

- Static analyzer functionality
- AI analysis quality
- File handling operations
- Flask application endpoints

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run quick validation tests
python tests/run_all_tests.py --quick

# Run specific test modules
python tests/test_analyzers.py
python tests/test_ai_analyzer.py
python tests/test_file_handler.py
python tests/test_flask_app.py

# Generate test documentation
python tests/run_all_tests.py --doc
```

### Test Coverage

| Component | Test Coverage | Key Features |
|-----------|---------------|--------------|
| Python Analyzer | 94%+ | Syntax errors, unused variables, PEP 8 violations |
| JavaScript Analyzer | 94%+ | ESLint integration, variable issues, best practices |
| AI Analysis | 87%+ | Response quality, issue categorization, recommendations |
| File Handler | 100% | Content cleaning, encoding handling, validation |
| Flask App | 76%+ | Endpoints, security, error handling, performance |

## 🔧 Configuration

### Supported File Types
- **Python**: `.py` files
- **JavaScript**: `.js`, `.mjs` files

### Limits
- **File Size**: 16MB maximum
- **Analysis Timeout**: 30 seconds for static analysis, 60 seconds for AI analysis
- **Concurrent Requests**: Supports multiple simultaneous analyses

### AI Analysis Categories

The AI analyzer groups issues into these categories:
- **Syntax/Logic Error**: Critical issues that prevent execution
- **Code Quality**: Best practices and maintainability issues
- **Unused Code**: Dead code and unused variables
- **Style/Convention**: Formatting and naming conventions
- **Security Issues**: Potential security vulnerabilities
- **Performance**: Code patterns that may impact performance

## 🛡️ Security Features

- **File Validation**: Strict file type and size validation
- **Content Cleaning**: Automatic removal of potentially harmful characters
- **Safe Execution**: Code is analyzed but never executed
- **Input Limits**: Protection against oversized requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write tests for new features
- Update documentation as needed
- Run the full test suite before submitting

## 🐛 Troubleshooting

### Common Issues

**ESLint not found:**
```bash
npm install -g eslint
# or
export PATH="./node_modules/.bin:$PATH"
```

**Pylint issues:**
```bash
pip install --upgrade pylint
```

**AI Analysis fails:**
- Verify your `GEMINI_API_KEY` is set correctly
- Check internet connectivity
- Ensure API key has proper permissions

**File upload issues:**
- Check file size (max 16MB)
- Verify file extension matches selected language
- Ensure file is UTF-8 encoded

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pylint](https://pylint.org/) for Python static analysis
- [ESLint](https://eslint.org/) for JavaScript analysis
- [Google Gemini AI](https://ai.google.dev/) for intelligent code insights
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the responsive UI

## 📞 Contact

**Furkan Yalçın** - Developer

- GitHub: [@furkan-ylcn](https://github.com/furkan-ylcn)
- Project Link: [https://github.com/furkan-ylcn/ai_powered_code_reviewer](https://github.com/furkan-ylcn/ai_powered_code_reviewer)

---

⭐ Star this repository if you find it helpful!