import json
import os
from typing import Dict, Optional
from datetime import datetime


class ColabNotebookGenerator:
    """Generate Google Colab notebooks for FastAPI deployment"""
    
    def __init__(self):
        self.notebook_template = {
            "nbformat": 4,
            "nbformat_minor": 0,
            "metadata": {
                "colab": {
                    "provenance": [],
                    "toc_visible": True
                },
                "kernelspec": {
                    "name": "python3",
                    "display_name": "Python 3"
                },
                "language_info": {
                    "name": "python"
                }
            },
            "cells": []
        }
    
    def generate_deployment_notebook(self,
                                   github_url: str,
                                   app_file: str,
                                   app_variable: str,
                                   env_vars: Optional[Dict[str, str]] = None,
                                   requirements: Optional[str] = None,
                                   deployment_id: str = None,
                                   app_name: Optional[str] = None,
                                   ngrok_auth: Optional[str] = None,
                                   python_version: str = "3.10") -> Dict:
        """Generate complete deployment notebook"""
        
        if not deployment_id:
            deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create notebook
        notebook = self.notebook_template.copy()
        notebook["cells"] = []
        
        # Add cells in sequence
        notebook["cells"].extend([
            self._create_title_cell(github_url, deployment_id, app_name),
            self._create_install_cell(requirements, python_version),
            self._create_clone_cell(github_url),
            self._create_env_cell(env_vars),
            self._create_app_detection_cell(app_file, app_variable),
            self._create_ngrok_cell(ngrok_auth),
            self._create_monitoring_cell()
        ])
        
        return {
            "notebook": notebook,
            "deployment_id": deployment_id,
            "success": True
        }
    
    def _create_title_cell(self, github_url: str, deployment_id: str, app_name: Optional[str] = None) -> Dict:
        """Create title and info cell"""
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# 🚀 Free FastAPI Deployment - {deployment_id}\n\n",
                f"**Repository:** {github_url}\n\n",
                "**Status:** Ready for deployment\n\n",
                "---\n\n",
                "## 📋 Instructions:\n",
                "1. Run all cells in sequence (Runtime → Run all)\n",
                "2. Wait for deployment to complete (~2-3 minutes)\n",
                "3. Copy your public API URL from the output\n",
                "4. Keep this notebook running to maintain the API\n\n",
                "---\n\n",
                "## ⚡ Quick Deploy:\n",
                "Click **Runtime → Run all** to auto-deploy your FastAPI backend!"
            ]
        }
    
    def _create_install_cell(self, requirements: Optional[str] = None, python_version: str = "3.10") -> Dict:
        """Create package installation cell"""
        
        # Base packages needed for deployment
        base_packages = [
            "pyngrok",
            "fastapi", 
            "uvicorn[standard]",
            "python-dotenv",
            "requests",
            "aiofiles"
        ]
        
        # Parse custom requirements
        custom_packages = []
        if requirements:
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    custom_packages.append(line)
        
        # Combine packages
        all_packages = base_packages + custom_packages
        packages_str = ' '.join(all_packages)
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 📦 Installing required packages\n",
                "print('🔧 Installing packages...')\n",
                f"!pip install -q {packages_str}\n",
                "\n",
                "print('✅ All packages installed successfully!')\n",
                "print('📦 Installed packages:')\n",
                f"packages = {repr(all_packages)}\n",
                "for pkg in packages[:5]:  # Show first 5\n",
                "    print(f'  ✓ {pkg}')\n",
                "if len(packages) > 5:\n",
                f"    print(f'  ... and {{len(packages) - 5}} more packages')"
            ]
        }
    
    def _create_clone_cell(self, github_url: str) -> Dict:
        """Create repository cloning cell"""
        return {
            "cell_type": "code", 
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 📁 Cloning repository\n",
                "import os\n",
                "print('📥 Cloning repository...')\n",
                "\n",
                "# Remove existing directory if present\n",
                "if os.path.exists('/content/app'):\n",
                "    !rm -rf /content/app\n",
                "\n",
                f"!git clone {github_url} /content/app\n",
                "\n",
                "# Change to app directory\n",
                "os.chdir('/content/app')\n",
                "\n",
                "print('✅ Repository cloned successfully!')\n",
                "print('📂 Repository contents:')\n",
                "!ls -la\n",
                "\n",
                "# Install project requirements if exists\n",
                "if os.path.exists('requirements.txt'):\n",
                "    print('\\n📋 Installing project requirements...')\n",
                "    !pip install -q -r requirements.txt\n",
                "    print('✅ Project requirements installed!')\n",
                "else:\n",
                "    print('\\n⚠️ No requirements.txt found in repository')"
            ]
        }
    
    def _create_env_cell(self, env_vars: Optional[Dict[str, str]] = None) -> Dict:
        """Create environment variables cell"""
        
        if not env_vars:
            env_code = "print('ℹ️ No environment variables configured')"
        else:
            env_lines = ["# 🔐 Setting up environment variables", "import os", ""]
            
            for key, value in env_vars.items():
                escaped_value = value.replace('"', '\\"')
                env_lines.append(f'os.environ["{key}"] = "{escaped_value}"')
            
            env_lines.extend([
                "",
                f"print('✅ Set {len(env_vars)} environment variables')",
                "print('🔐 Environment variables configured:')",
                "for key in os.environ.keys():",
                "    if key in " + str(list(env_vars.keys())) + ":",
                "        print(f'  ✓ {key}')"
            ])
            
            env_code = "\n".join(env_lines)
        
        return {
            "cell_type": "code",
            "execution_count": None, 
            "metadata": {},
            "outputs": [],
            "source": env_code
        }
    
    def _create_app_detection_cell(self, app_file: str, app_variable: str) -> Dict:
        """Create FastAPI app detection and startup cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 🔍 FastAPI App Detection and Startup\n",
                "import threading\n",
                "import time\n",
                "import uvicorn\n",
                "import importlib.util\n",
                "import sys\n",
                "\n",
                f"app_file = '{app_file}'\n",
                f"app_variable = '{app_variable}'\n",
                "\n",
                "print(f'🔍 Loading FastAPI app from {app_file}...')\n",
                "\n",
                "# Import the module\n",
                "try:\n",
                "    spec = importlib.util.spec_from_file_location('main_app', app_file)\n",
                "    app_module = importlib.util.module_from_spec(spec)\n",
                "    spec.loader.exec_module(app_module)\n",
                "    \n",
                "    # Get the FastAPI app instance\n",
                "    if hasattr(app_module, app_variable):\n",
                "        fastapi_app = getattr(app_module, app_variable)\n",
                "        print(f'✅ Found FastAPI app: {app_variable}')\n",
                "        print(f'📊 App type: {type(fastapi_app)}')\n",
                "    else:\n",
                "        print(f'❌ App variable \"{app_variable}\" not found in {app_file}')\n",
                "        print('📋 Available variables:')\n",
                "        for attr in dir(app_module):\n",
                "            if not attr.startswith('_'):\n",
                "                print(f'  - {attr}: {type(getattr(app_module, attr))}')\n",
                "        raise Exception(f'App variable not found')\n",
                "    \n",
                "    # Start FastAPI server in background\n",
                "    def start_server():\n",
                "        uvicorn.run(fastapi_app, host='0.0.0.0', port=8000, log_level='warning')\n",
                "    \n",
                "    print('🚀 Starting FastAPI server...')\n",
                "    server_thread = threading.Thread(target=start_server, daemon=True)\n",
                "    server_thread.start()\n",
                "    \n",
                "    # Wait for server to start\n",
                "    time.sleep(8)\n",
                "    print('✅ FastAPI server started on port 8000!')\n",
                "    \n",
                "except Exception as e:\n",
                "    print(f'❌ Error starting FastAPI app: {e}')\n",
                "    print('\\n🔧 Troubleshooting tips:')\n",
                "    print('1. Check if your FastAPI app variable name is correct')\n",
                "    print('2. Ensure your app file has no syntax errors')\n",
                "    print('3. Verify all dependencies are installed')\n",
                "    raise"
            ]
        }
    
    def _create_ngrok_cell(self, ngrok_auth: Optional[str] = None) -> Dict:
        """Create ngrok tunnel cell with proper auth setup"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 🌐 Creating Public API with ngrok\n",
                "from pyngrok import ngrok\n",
                "import requests\n",
                "import time\n",
                "from google.colab import userdata\n",
                "\n",
                "print('🔗 Creating ngrok tunnel...')\n",
                "\n",
                "try:\n",
                "    # Set ngrok authtoken\n",
                "    # You need to get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken\n",
                "    # Add it to Colab secrets with the name 'NGROK_AUTH_TOKEN'\n",
                "    try:\n",
                "        ngrok_auth_token = userdata.get('NGROK_AUTH_TOKEN')\n",
                "        ngrok.set_auth_token(ngrok_auth_token)\n",
                "        print('✅ ngrok authtoken retrieved from Colab secrets!')\n",
                "    except:\n",
                "        # Fallback: Use default free ngrok (limited sessions)\n",
                "        print('⚠️ NGROK_AUTH_TOKEN not found in Colab secrets.')\n",
                "        print('💡 Using free ngrok (sessions may be limited)')\n",
                "        print('📋 To get unlimited sessions:')\n",
                "        print('   1. Sign up at https://ngrok.com (free)')\n",
                "        print('   2. Get your auth token from dashboard')\n",
                "        print('   3. Add it to Colab secrets as NGROK_AUTH_TOKEN')\n",
                "\n",
                "    # Create HTTP tunnel to port 8000\n",
                "    public_tunnel = ngrok.connect(8000)\n",
                "    public_url = public_tunnel.public_url\n",
                "    \n",
                "    print('\\n🎉 DEPLOYMENT SUCCESSFUL! 🎉')\n",
                "    print('=' * 60)\n",
                "    print(f'🔗 Public API URL: {public_url}')\n",
                "    print(f'📚 Swagger UI: {public_url}/docs')\n",
                "    print(f'📋 ReDoc: {public_url}/redoc')\n",
                "    print('=' * 60)\n",
                "    \n",
                "    # Test the API\n",
                "    print('\\n🧪 Testing API connection...')\n",
                "    try:\n",
                "        response = requests.get(f'{public_url}/', timeout=10)\n",
                "        if response.status_code == 200:\n",
                "            print('✅ API is responding correctly!')\n",
                "            print(f'📊 Response: {response.text[:100]}...')\n",
                "        else:\n",
                "            print(f'⚠️ API returned status code: {response.status_code}')\n",
                "    except Exception as test_error:\n",
                "        print(f'⚠️ API test failed: {test_error}')\n",
                "    \n",
                "    print('\\n🎯 Your FastAPI backend is now live and accessible worldwide!')\n",
                "    print('💡 Copy the Public API URL above to use in your frontend')\n",
                "    print('⚠️ Keep this notebook running to maintain the API')\n",
                "    print('\\n📱 Quick Links:')\n",
                "    print(f'   🏠 Homepage: {public_url}/')\n",
                "    print(f'   📚 API Docs: {public_url}/docs')\n",
                "    print(f'   📋 ReDoc: {public_url}/redoc')\n",
                "    \n",
                "    # Store URL for monitoring\n",
                "    globals()['PUBLIC_API_URL'] = public_url\n",
                "    \n",
                "except Exception as e:\n",
                "    print(f'❌ Failed to create ngrok tunnel: {e}')\n",
                "    print('\\n🔧 Troubleshooting:')\n",
                "    print('1. Ensure FastAPI server is running (check previous cell)')\n",
                "    print('2. Wait a moment and try running this cell again')\n",
                "    print('3. Check if port 8000 is accessible')\n",
                "    print('4. For unlimited ngrok sessions, add NGROK_AUTH_TOKEN to Colab secrets')\n",
                "    print('   📋 Get token from: https://dashboard.ngrok.com/get-started/your-authtoken')\n",
                "    raise"
            ]
        }
    
    def _create_monitoring_cell(self) -> Dict:
        """Create API monitoring cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 📊 API Health Monitoring\n",
                "import requests\n",
                "import time\n",
                "from datetime import datetime\n",
                "\n",
                "# Get the public URL from previous cell\n",
                "if 'PUBLIC_API_URL' in globals():\n",
                "    api_url = PUBLIC_API_URL\n",
                "    print(f'🔄 Monitoring API: {api_url}')\n",
                "    print('\\n📊 Health Check Status:')\n",
                "    print('Press Ctrl+C to stop monitoring\\n')\n",
                "    \n",
                "    try:\n",
                "        check_count = 0\n",
                "        while True:\n",
                "            try:\n",
                "                start_time = time.time()\n",
                "                response = requests.get(f'{api_url}/', timeout=5)\n",
                "                response_time = round((time.time() - start_time) * 1000, 2)\n",
                "                \n",
                "                timestamp = datetime.now().strftime('%H:%M:%S')\n",
                "                \n",
                "                if response.status_code == 200:\n",
                "                    print(f'✅ {timestamp} - API healthy (Status: {response.status_code}, Response: {response_time}ms)')\n",
                "                else:\n",
                "                    print(f'⚠️ {timestamp} - API warning (Status: {response.status_code})')\n",
                "                \n",
                "                check_count += 1\n",
                "                if check_count % 10 == 0:\n",
                "                    print(f'\\n📈 Completed {check_count} health checks')\n",
                "                    print(f'🌐 Your API: {api_url}')\n",
                "                    print(f'📚 Swagger: {api_url}/docs\\n')\n",
                "                \n",
                "            except requests.RequestException as e:\n",
                "                timestamp = datetime.now().strftime('%H:%M:%S')\n",
                "                print(f'❌ {timestamp} - API unreachable: {e}')\n",
                "            \n",
                "            time.sleep(30)  # Check every 30 seconds\n",
                "            \n",
                "    except KeyboardInterrupt:\n",
                "        print('\\n🛑 Monitoring stopped by user')\n",
                "        print(f'📊 Total health checks performed: {check_count}')\n",
                "        print(f'🌐 Your API is still running at: {api_url}')\n",
                "        \n",
                "else:\n",
                "    print('❌ No API URL found. Please run the ngrok cell first.')"
            ]
        }
    
    def save_notebook(self, notebook: Dict, filename: str) -> str:
        """Save notebook to file"""
        try:
            # Ensure notebooks directory exists
            os.makedirs('generated_notebooks', exist_ok=True)
            
            filepath = os.path.join('generated_notebooks', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to save notebook: {e}")
    
    def create_colab_url(self, notebook_path: str) -> str:
        """Create Google Colab URL (placeholder for now)"""
        # In a real implementation, you would upload to GitHub or use Colab's API
        base_url = "https://colab.research.google.com/github/"
        
        # For now, return instructions for manual upload
        return f"Upload {notebook_path} to Google Colab manually"
