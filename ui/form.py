import streamlit as st
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.deployer import DeploymentService
from utils.validators import validate_github_url, extract_repo_name


def old_deployment_form():
    """Enhanced deployment form with real-time validation"""
    
    # Initialize deployment service
    if 'deployment_service' not in st.session_state:
        st.session_state.deployment_service = DeploymentService()
    
    st.subheader("📦 Deploy FastAPI Backend")
    st.markdown("Deploy your FastAPI application to Google Colab with a public API URL!")

    # Form container
    with st.form("deployment_form", clear_on_submit=False):
        
        # GitHub URL input
        st.markdown("#### 🔗 GitHub Repository")
        github_url = st.text_input(
            "Enter your GitHub repository URL",
            placeholder="https://github.com/username/your-fastapi-project",
            help="📋 Your repository should contain a FastAPI application with main.py/app.py",
            key="github_url_input"
        )
        
        # Real-time URL validation
        url_validation_container = st.empty()
        if github_url:
            validation = validate_github_url(github_url)
            if validation["valid"]:
                url_validation_container.success(f"✅ Valid GitHub URL: {extract_repo_name(github_url)}")
            else:
                url_validation_container.error(f"❌ {validation['error']}")
        
        # Environment variables section
        st.markdown("#### 🔐 Environment Variables (Optional)")
        
        # Enhanced environment section with better UI
        env_col1, env_col2 = st.columns([1, 2])
        
        with env_col1:
            env_option = st.radio(
                "Choose environment setup:",
                ["None", "Upload .env file", "Enter manually"],
                help="Environment variables will be securely injected into your deployed application"
            )
        
        with env_col2:
            if env_option == "None":
                st.info("""
                **💡 No environment variables selected**
                
                Your app will run without environment variables. You can add them later if needed.
                """)
            elif env_option == "Upload .env file":
                st.info("""
                **📁 Upload .env file**
                
                Upload your existing .env file with format:
                ```
                DATABASE_URL=your_database_url
                SECRET_KEY=your_secret_key
                API_KEY=your_api_key
                ```
                """)
            else:
                st.info("""
                **✏️ Manual entry**
                
                Type your environment variables directly in KEY=value format.
                """)
        
        env_file_content = None
        
        if env_option == "Upload .env file":
            st.markdown("##### 📁 Upload .env File")
            
            env_file = st.file_uploader(
                "Choose your .env file",
                type=['env', 'txt'],
                help="Upload a .env file containing your environment variables",
                key="env_file_upload"
            )
            
            if env_file:
                env_file_content = env_file.read().decode("utf-8")
                
                # Enhanced preview with validation
                env_lines = [line for line in env_file_content.split('\n') if line.strip() and not line.startswith('#')]
                valid_vars = [line for line in env_lines if '=' in line]
                
                success_col, info_col = st.columns(2)
                
                with success_col:
                    st.success(f"✅ File uploaded successfully!")
                    st.metric("📊 Variables found", len(valid_vars))
                
                with info_col:
                    st.info(f"📄 File size: {len(env_file_content)} bytes")
                    st.metric("📝 Total lines", len(env_file_content.splitlines()))
                
                # Enhanced preview with security
                with st.expander("🔍 Preview environment variables (secure)"):
                    if valid_vars:
                        st.markdown("**✅ Valid Variables:**")
                        for line in valid_vars[:8]:  # Show first 8
                            if '=' in line:
                                key = line.split('=')[0].strip()
                                value_length = len(line.split('=', 1)[1].strip())
                                # Mask sensitive patterns
                                if any(pattern in key.lower() for pattern in ['password', 'secret', 'key', 'token']):
                                    st.code(f"{key} = {'*' * min(value_length, 12)} ({value_length} chars)")
                                else:
                                    value_preview = line.split('=', 1)[1].strip()[:20]
                                    st.code(f"{key} = {value_preview}{'...' if value_length > 20 else ''}")
                        
                        if len(valid_vars) > 8:
                            st.info(f"... and {len(valid_vars) - 8} more variables")
                    
                    # Show any invalid lines
                    invalid_lines = [line for line in env_lines if '=' not in line]
                    if invalid_lines:
                        st.warning(f"⚠️ {len(invalid_lines)} lines might be invalid (no '=' found)")
                        for line in invalid_lines[:3]:
                            st.code(line)
        
        elif env_option == "Enter manually":
            st.markdown("##### ✏️ Enter Environment Variables")
            
            # Enhanced manual entry with templates
            template_col, input_col = st.columns([1, 2])
            
            with template_col:
                st.markdown("**📋 Common Templates:**")
                
                if st.button("🗃️ Database Template", use_container_width=True):
                    st.session_state['env_template'] = """DATABASE_URL=postgresql://user:password@localhost/dbname
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=username
DB_PASSWORD=password"""
                
                if st.button("🔐 API Keys Template", use_container_width=True):
                    st.session_state['env_template'] = """SECRET_KEY=your-secret-key-here
API_KEY=your-api-key
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key"""
                
                if st.button("🌐 Web App Template", use_container_width=True):
                    st.session_state['env_template'] = """DEBUG=False
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=https://yourfrontend.com"""
            
            with input_col:
                # Get template from session state
                default_text = st.session_state.get('env_template', "")
                
                env_text = st.text_area(
                    "Environment variables (KEY=value format)",
                    value=default_text,
                    placeholder="DATABASE_URL=postgresql://...\nSECRET_KEY=your-secret-key\nAPI_KEY=your-api-key",
                    height=150,
                    help="Enter one variable per line in KEY=value format",
                    key="manual_env_input"
                )
                
                if env_text.strip():
                    env_file_content = env_text
                    # Real-time validation
                    lines = env_text.split('\n')
                    valid_vars = [line for line in lines if line.strip() and '=' in line and not line.startswith('#')]
                    invalid_lines = [line for line in lines if line.strip() and '=' not in line and not line.startswith('#') and line.strip()]
                    
                    validation_col1, validation_col2 = st.columns(2)
                    
                    with validation_col1:
                        st.success(f"✅ {len(valid_vars)} valid variables")
                    
                    with validation_col2:
                        if invalid_lines:
                            st.warning(f"⚠️ {len(invalid_lines)} invalid lines")
                        else:
                            st.info("✨ All lines valid!")
        
        # Requirements section
        st.markdown("#### 📦 Dependencies (Optional)")
        req_option = st.radio(
            "How would you like to handle dependencies?",
            ["Auto-detect from repository", "Upload custom requirements.txt", "Enter manually"],
            help="We'll install these packages in your deployment environment"
        )
        
        custom_requirements = None
        
        if req_option == "Upload custom requirements.txt":
            req_file = st.file_uploader(
                "Upload requirements.txt",
                type=['txt'],
                help="Upload a requirements.txt file with your Python dependencies"
            )
            
            if req_file:
                custom_requirements = req_file.read().decode("utf-8")
                package_count = len([line for line in custom_requirements.split('\n') if line.strip() and not line.startswith('#')])
                st.success(f"✅ Uploaded requirements.txt ({package_count} packages)")
        
        elif req_option == "Enter manually":
            req_text = st.text_area(
                "Enter Python packages (one per line)",
                placeholder="fastapi>=0.68.0\nuvicorn[standard]\npython-dotenv\nrequests",
                height=100,
                help="Enter one package per line, optionally with version constraints"
            )
            
            if req_text.strip():
                custom_requirements = req_text
                package_count = len([line for line in req_text.split('\n') if line.strip() and not line.startswith('#')])
                st.success(f"✅ {package_count} custom packages specified")
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            st.markdown("**App Detection:**")
            st.info("We'll automatically detect your FastAPI app from files like main.py, app.py, etc.")
            
            st.markdown("**Deployment Features:**")
            features = [
                "✅ Automatic ngrok tunnel setup",
                "✅ Public HTTPS API URL",
                "✅ Swagger UI (/docs) access",
                "✅ ReDoc (/redoc) documentation",
                "✅ CORS enabled for frontend integration",
                "✅ Environment variables injection",
                "✅ Health monitoring",
                "✅ Error handling and logs"
            ]
            for feature in features:
                st.markdown(feature)
        
        # Deploy button
        st.markdown("---")
        submitted = st.form_submit_button(
            "🚀 Generate Deployment",
            type="primary",
            use_container_width=True,
            help="Create a Google Colab notebook for deploying your FastAPI backend"
        )
    
    return {
        'submitted': submitted,
        'github_url': github_url,
        'env_file_content': env_file_content,
        'custom_requirements': custom_requirements,
        'valid_url': validate_github_url(github_url)["valid"] if github_url else False
    }

def deployment_form():
    """Enhanced deployment form for production use"""

    # GitHub URL input with enhanced validation
    st.markdown("#### 🔗 GitHub Repository")
    github_url = st.text_input(
        "Enter your GitHub repository URL",
        placeholder="https://github.com/username/your-fastapi-project",
        help="📋 Your repository should contain a FastAPI or Flask application with main.py/app.py",
        label_visibility="collapsed"
    )
    
    # Enhanced URL validation with visual feedback
    if github_url:
        if github_url.startswith(("https://github.com/", "http://github.com/")):
            # Extract repo info for display
            try:
                parts = github_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    st.success(f"✅ Repository: **{owner}/{repo}**")
                else:
                    st.warning("⚠️ Please provide the complete repository path")
            except:
                st.warning("⚠️ Please check the repository URL format")
        elif github_url.startswith("git@github.com:"):
            st.info("ℹ️ SSH URL detected - please use HTTPS format for public access")
        else:
            st.error("❌ Please enter a valid GitHub URL (must start with https://github.com/)")

    # Repository requirements info
    with st.expander("📋 Repository Requirements", expanded=False):
        st.markdown("""
        **Your GitHub repository should contain:**
        
        ✅ **FastAPI/Flask Application:**
        - `main.py`, `app.py`, `server.py`, or similar
        - Must have `app = FastAPI()` or `app = Flask()` instance
        
        ✅ **Dependencies File:**
        - `requirements.txt` with all needed packages
        
        ✅ **Optional Files:**
        - `.env` file for environment variables
        - Additional modules and packages
        
        **📁 Example Repository Structure:**
        ```
        your-repo/
        ├── main.py          # Your FastAPI app
        ├── requirements.txt # Dependencies
        ├── .env            # Environment variables (optional)
        ├── models/         # Additional modules
        └── utils/          # Helper functions
        ```
        """)

    st.markdown("---")

    # File uploaders with better descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Environment Variables (Optional)")
        env_file = st.file_uploader(
            "Upload your .env file",
            type=["env", "txt"],
            help="🔐 Environment variables will be securely injected into your deployment",
            label_visibility="collapsed"
        )
        
        if env_file:
            # Preview env file content (safely)
            try:
                env_content = env_file.read().decode("utf-8")
                env_lines = [line for line in env_content.split('\n') if line.strip() and not line.startswith('#')]
                st.success(f"✅ **{len(env_lines)} environment variables** loaded")
                
                with st.expander("👀 Preview (values hidden for security)"):
                    for line in env_lines:
                        if '=' in line:
                            key = line.split('=')[0]
                            st.text(f"{key}=***")
                        
                # Reset file pointer for later use
                env_file.seek(0)
            except Exception as e:
                st.error(f"❌ Error reading .env file: {e}")
    
    with col2:
        st.markdown("#### 📦 Dependencies (Required)")
        requirements_file = st.file_uploader(
            "Upload your requirements.txt",
            type=["txt"],
            help="📦 All packages your backend needs to run",
            label_visibility="collapsed"
        )
        
        if requirements_file:
            # Preview requirements content
            try:
                req_content = requirements_file.read().decode("utf-8")
                req_lines = [line.strip() for line in req_content.split('\n') if line.strip() and not line.startswith('#')]
                st.success(f"✅ **{len(req_lines)} packages** to install")
                
                with st.expander("👀 Preview packages"):
                    for line in req_lines:
                        st.text(f"📦 {line}")
                        
                # Reset file pointer for later use
                requirements_file.seek(0)
            except Exception as e:
                st.error(f"❌ Error reading requirements.txt: {e}")

    # Enhanced examples section
    st.markdown("---")
    st.markdown("#### 💡 Need Examples?")
    
    tab1, tab2, tab3 = st.tabs(["📦 Requirements.txt", "📄 .env File", "🐍 FastAPI Example"])
    
    with tab1:
        st.markdown("**Basic FastAPI requirements.txt:**")
        st.code("""fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
pydantic>=2.5.0
requests>=2.31.0
aiofiles>=23.2.0""", language="text")
        
        st.markdown("**With Database (PostgreSQL):**")
        st.code("""fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0
python-dotenv>=1.0.0""", language="text")

    with tab2:
        st.markdown("**Sample .env file:**")
        st.code("""# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname

# API Keys
API_KEY=your_secret_api_key_here
OPENAI_API_KEY=sk-your_openai_key

# Security
SECRET_KEY=your_jwt_secret_key
DEBUG=False

# External Services
REDIS_URL=redis://localhost:6379
EMAIL_HOST=smtp.gmail.com""", language="bash")

    with tab3:
        st.markdown("**Simple FastAPI application (main.py):**")
        st.code("""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="My API",
    description="My awesome API deployed via Google Colab",
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
    return {"data": [1, 2, 3], "status": "success"}

@app.get("/api/env-test")
async def test_env():
    # Test environment variable
    api_key = os.getenv("API_KEY", "not_set")
    return {"api_key_configured": api_key != "not_set"}""", language="python")

    st.markdown("---")

    # Enhanced Deploy button with pre-deployment summary
    st.markdown("### 🚀 Ready to Deploy?")
    
    # Pre-deployment validation and summary
    validation_issues = []
    if not github_url:
        validation_issues.append("GitHub repository URL required")
    elif not github_url.startswith(("https://github.com/", "http://github.com/")):
        validation_issues.append("Invalid GitHub URL format")
    
    if not requirements_file:
        validation_issues.append("Requirements.txt file required")
    
    # Show deployment summary
    if github_url and requirements_file:
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            repo_name = github_url.split('/')[-1] if '/' in github_url else "Unknown"
            st.metric("📁 Repository", repo_name)
        
        with summary_col2:
            env_status = "None"
            if env_file:
                env_status = "✅ Uploaded"
            st.metric("🔐 Environment", env_status)
        
        with summary_col3:
            if requirements_file:
                try:
                    req_content = requirements_file.read().decode("utf-8")
                    req_lines = [line.strip() for line in req_content.split('\n') if line.strip() and not line.startswith('#')]
                    st.metric("📦 Packages", len(req_lines))
                    requirements_file.seek(0)  # Reset file pointer
                except:
                    st.metric("📦 Packages", "Error")
    
    # Deployment info box
    if not validation_issues:
        st.success("""
        **🎯 What happens next:**
        1. ✨ We'll analyze your FastAPI repository
        2. 📝 Generate a custom Google Colab notebook  
        3. 🔗 Provide you with a direct link to run it
        4. 🌐 Your API will be live with a public URL!
        
        **⏱️ Estimated time: 2-3 minutes**
        """)
    else:
        st.warning("**⚠️ Please complete the following:**\n" + "\n".join(f"• {issue}" for issue in validation_issues))
    
    # Enhanced deploy button
    can_deploy = bool(github_url and requirements_file and not validation_issues)
    
    # Center the deploy button with better styling
    deploy_col1, deploy_col2, deploy_col3 = st.columns([1, 2, 1])
    
    with deploy_col2:
        submit = st.button(
            "🚀 **Deploy to Colab**",
            type="primary",
            disabled=not can_deploy,
            help="Generate and open Google Colab notebook for deployment",
            use_container_width=True
        )
    
    # Progress tracking during deployment
    if submit and can_deploy:
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Preparing Your Deployment...")
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Repository validation
                status_text.text("🔍 Validating GitHub repository...")
                progress_bar.progress(25)
                time.sleep(0.8)
                
                # Step 2: File processing
                status_text.text("📁 Processing uploaded files...")
                progress_bar.progress(50)
                time.sleep(0.6)
                
                # Step 3: Environment setup
                if env_file:
                    status_text.text("🔐 Configuring environment variables...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                
                # Step 4: Notebook generation
                status_text.text("📝 Generating Google Colab notebook...")
                progress_bar.progress(90)
                time.sleep(0.7)
                
                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Deployment package ready!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_container.empty()
                
                # Show completion message
                st.success("🎉 **Deployment package created successfully!**")
                st.info("� You can now proceed to the deployment results below.")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error during preparation: {str(e)}")
                
                with st.expander("🔧 Troubleshooting"):
                    st.markdown("""
                    **Common issues:**
                    - Check your internet connection
                    - Ensure uploaded files are valid
                    - Verify GitHub repository is public
                    - Try refreshing and uploading files again
                    """)

    return github_url, env_file, requirements_file, submit
