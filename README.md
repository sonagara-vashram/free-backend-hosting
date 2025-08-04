# 🚀 Free Python Backend Hosting

Deploy your Python backend applications (FastAPI, Flask, etc.) to Google Colab for **completely free** hosting with public API URLs! This platform creates a complete Google Colab notebook that automatically deploys your backend with ngrok tunnels and Swagger UI.

## ✨ Features

- **🆓 Completely Free**: No credit card or paid hosting required
- **⚡ Quick Deployment**: Get your backend live in under 2 minutes
- **🔗 Public API URLs**: Automatic ngrok tunnels for external access
- **🔐 Environment Variables**: Secure .env file injection
- **📦 Smart Dependency Management**: Automatic requirements.txt installation with error handling
- **🎨 Beautiful UI**: Intuitive Streamlit frontend interface
- **☁️ Google Colab Integration**: Leverages Google's free infrastructure
- **📚 Auto Documentation**: Swagger UI and ReDoc automatically generated
- **🔍 Smart App Detection**: Automatically finds FastAPI/Flask apps in your repository
- **🌐 CORS Enabled**: Ready for frontend integration

## 🏗️ How It Works

1. **📤 Upload Your Project**: Provide GitHub repo URL containing your backend code
2. **⚙️ Configure Environment**: Upload .env file and requirements.txt  
3. **📓 Auto-Generation**: Platform creates a custom Google Colab notebook
4. **🚀 Deploy & Access**: Get a shareable Colab link that runs your backend
5. **🌐 Public API**: Notebook provides ngrok URL for external API access

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed on your system
- **Git** installed and configured
- **GitHub repository** with your backend code
- **Internet connection** for downloading dependencies

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sonagara-vashram/free-backend-hosting.git
   cd free-backend-hosting
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the platform**:
   
   **Option A - Using PowerShell (Windows - Recommended)**:
   ```powershell
   .\run.ps1
   ```
   
   **Option B - Using Batch Script (Windows)**:
   ```cmd
   run.bat
   ```
   
   **Option C - Manual Start (All Platforms)**:
   ```bash
   streamlit run app.py
   ```

4. **Access the platform**:
   - **Frontend UI**: http://localhost:8501
   - The platform will automatically open in your default browser

## 📋 Usage Guide

### Step 1: Prepare Your Backend Project

Your GitHub repository should contain:

**✅ Required Files:**
- A **FastAPI/Flask application** (typically `main.py` with `app` variable)
- **`requirements.txt`** file with all dependencies

**📁 Optional Files:**
- `.env` file for environment variables
- Additional modules and packages

**Example FastAPI Repository Structure:**
```
your-project/
├── main.py          # Your FastAPI app (required)
├── requirements.txt # Dependencies (required)
├── .env            # Environment variables (optional)
├── models/         # Additional modules
├── utils/          # Helper functions
└── README.md       # Project documentation
```

**Example `main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="My API",
    description="My awesome API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/api/data")
async def get_data():
    return {"data": "Your API response"}
```

**Example `requirements.txt`:**
```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
pydantic>=2.5.0
requests>=2.31.0
```

### Step 2: Deploy Using the Platform

1. **📱 Open the Platform**: Navigate to http://localhost:8501
2. **🔗 Enter Repository URL**: Paste your GitHub repository URL
3. **📄 Upload .env File**: (Optional) Upload your environment variables
4. **📦 Upload requirements.txt**: Upload your dependencies file
5. **🚀 Deploy**: Click "Deploy to Google Colab"

### Step 3: Complete Deployment in Google Colab

1. **📓 Upload Notebook**: The platform creates a notebook file locally
2. **🌐 Open Google Colab**: Click the provided link to open Google Colab
3. **📤 Upload File**: In Colab, go to File → Upload notebook → Select the created file
4. **▶️ Run Deployment**: Click Runtime → Run all (or run cells individually)
5. **⏳ Wait**: Deployment usually takes 30-90 seconds

### Step 4: Access Your Live API

After deployment completes, you'll see output like:
```
🎉 YOUR BACKEND IS NOW LIVE!
=======================================
🔗 Public URL: https://abc123.ngrok.io
📚 Swagger UI: https://abc123.ngrok.io/docs
📋 ReDoc: https://abc123.ngrok.io/redoc
=======================================
```

**🌐 Use Your API:**
```javascript
// Use the ngrok URL in your frontend
const apiUrl = "https://abc123.ngrok.io"; // Your ngrok URL

fetch(`${apiUrl}/api/data`)
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🛠️ Advanced Configuration

### Environment Variables

Create a `.env` file with your secrets:
```env
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/dbname

# API Keys
OPENAI_API_KEY=sk-your_openai_key_here
SECRET_KEY=your_jwt_secret_key

# Configuration
DEBUG=False
ENVIRONMENT=production
```

### Complex Dependencies

For projects with complex dependencies:
```txt
# Web Framework
fastapi>=0.104.1
uvicorn[standard]>=0.24.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0
requests>=2.31.0
```

### Flask Applications

The platform also supports Flask applications:
```python
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/data')
def get_data():
    return jsonify({"data": [1, 2, 3]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

## 🔧 Platform Architecture

```
free-backend-hosting/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Platform dependencies
├── run.ps1                # PowerShell startup script
├── run.bat                # Batch startup script
├── backend/
│   ├── main.py            # FastAPI backend server (optional)
│   ├── credentials/       # Google OAuth credentials
│   ├── routers/
│   │   └── deploy_route.py # Deployment API endpoints
│   ├── schemas/
│   │   └── deploy.py      # Pydantic models
│   └── services/
│       ├── colab_gen.py   # Notebook generation logic
│       ├── deploy.py      # Main deployment orchestration
│       ├── git_clone.py   # GitHub repository cloning
│       ├── file_ops.py    # File operations utilities
│       └── google_drive.py # Enhanced notebook creation
├── ui/
│   ├── form.py           # Enhanced input form components
│   ├── layout.py         # Main layout and styling
│   ├── response.py       # Enhanced result display
│   └── styles.py         # Custom CSS styles
├── utils/
│   └── colab_button.py   # Utility components
└── static/
    └── logo.png          # Platform logo
```

## 🚨 Important Notes & Limitations

### ⏰ Session Limits
- **Free ngrok**: 2-hour sessions without auth token
- **With ngrok auth**: 8-hour sessions
- **Google Colab**: 12-24 hour maximum session duration
- **Idle timeout**: ~90 minutes of inactivity

### 🔒 Security Considerations
- **Environment Variables**: Safely injected, not exposed in logs
- **Public Repositories**: Only works with public GitHub repos
- **HTTPS**: All deployed APIs automatically get SSL certificates
- **CORS**: Enabled by default for frontend integration

### 💡 Best Practices
- **Keep Sessions Active**: Interact with your Colab notebook periodically
- **Monitor Usage**: Check Google Colab usage limits
- **Test Thoroughly**: Use Swagger UI to test all endpoints
- **Save URLs**: Bookmark your API URLs before closing
- **Version Control**: Keep your code in version control

### 🎯 Ideal Use Cases
- ✅ **Development and testing**
- ✅ **Prototyping and demos**
- ✅ **Educational projects**
- ✅ **API development and learning**
- ✅ **Small personal projects**
- ✅ **MVP development**

### 🚫 Not Recommended For
- ❌ **Production applications** with high availability requirements
- ❌ **Applications handling sensitive data** without proper security
- ❌ **High-traffic applications** (use proper cloud hosting)
- ❌ **Long-running background tasks**

## 🔧 Troubleshooting

### Common Issues

**❓ "No FastAPI app found"**
- Ensure your main file has `app = FastAPI()` or similar
- Check file naming: use `main.py`, `app.py`, `server.py`, or `api.py`

**❓ "Requirements installation failed"**
- Verify package names in requirements.txt
- Remove version conflicts
- Check for typos in package names

**❓ "Repository clone failed"**
- Ensure repository is public
- Check GitHub URL format
- Verify repository exists and is accessible

**❓ "Ngrok tunnel failed"**
- Try running deployment again
- Check internet connection
- Consider using your own ngrok auth token

**❓ "Server won't start"**
- Check your app for syntax errors
- Verify all imports are available
- Review error messages in Colab

### Getting Help

1. **Check Error Messages**: Review the detailed error output in Colab
2. **Try Again**: Many issues are temporary network problems
3. **Verify Repository**: Ensure your GitHub repo is structured correctly
4. **Test Locally**: Try running your FastAPI app locally first
5. **GitHub Issues**: Report bugs or ask questions in the repository

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Report Bugs**: Open an issue with detailed reproduction steps
2. **💡 Suggest Features**: Share ideas for platform improvements
3. **📖 Improve Documentation**: Help make the docs clearer
4. **🔧 Code Contributions**: Submit pull requests for new features

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

If you find this project helpful:
- **🌟 Star the repository** to show your support
- **🐦 Share on social media** to help others discover it  
- **🤝 Contribute** to make it even better
- **🐛 Report issues** to help us improve

For support and questions:
- **📚 Check the documentation** above
- **🐛 Open an issue** for bugs or feature requests
- **💬 Start a discussion** for general questions

## 🙏 Acknowledgments

- **Google Colab** for providing free computational resources
- **Ngrok** for free tunneling services
- **Streamlit** for the amazing web framework
- **FastAPI** for the excellent API framework
- **Open Source Community** for inspiration and tools

---

**✨ Made with ❤️ for the developer community**

**🎯 Turn your ideas into live APIs in minutes, not hours!**