"""
Single Cell Colab Generator
Creates a complete deployment in one cell that user can copy-paste
"""

from typing import Dict, Optional


class SingleCellGenerator:
    """Generate single cell deployment code for Google Colab"""
    
    def generate_single_cell_deployment(self,
                                      github_url: str,
                                      app_file: str,
                                      app_variable: str,
                                      env_vars: Optional[Dict[str, str]] = None,
                                      requirements: Optional[str] = None,
                                      app_name: Optional[str] = None,
                                      ngrok_auth: Optional[str] = None) -> str:
        """Generate complete single cell deployment code"""
        
        # Parse requirements
        base_packages = ["pyngrok", "fastapi", "uvicorn[standard]", "python-dotenv", "requests", "aiofiles"]
        custom_packages = []
        
        if requirements:
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    custom_packages.append(line)
        
        all_packages = base_packages + custom_packages
        packages_str = ' '.join([f'"{pkg}"' for pkg in all_packages])
        
        # Environment variables setup
        env_setup = ""
        if env_vars:
            env_lines = []
            for key, value in env_vars.items():
                escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                env_lines.append(f'os.environ["{key}"] = "{escaped_value}"')
            env_setup = "\n".join(env_lines)
        
        # Generate the complete single cell code
        cell_code = f'''# 🚀 ONE-CLICK FASTAPI DEPLOYMENT
# Copy this entire cell to Google Colab and run it!

import os
import subprocess
import sys
import time
import threading
import requests
from datetime import datetime

print("🎯 ONE-CLICK FASTAPI DEPLOYMENT STARTING...")
print("=" * 60)

# Step 1: Install packages
print("\\n📦 Installing required packages...")
packages_to_install = [{packages_str}]

for package in packages_to_install:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
        print(f"✅ Installed: {{package}}")
    except:
        print(f"⚠️ Failed to install: {{package}}")

print("✅ Package installation completed!")

# Step 2: Clone repository
print("\\n📥 Cloning repository...")
github_url = "{github_url}"

if os.path.exists('/content/app'):
    subprocess.run(['rm', '-rf', '/content/app'], check=False)

try:
    subprocess.run(['git', 'clone', github_url, '/content/app'], check=True)
    os.chdir('/content/app')
    print("✅ Repository cloned successfully!")
    
    # Show repository contents
    print("\\n📂 Repository contents:")
    subprocess.run(['ls', '-la'])
    
    # Install project requirements if exists
    if os.path.exists('requirements.txt'):
        print("\\n📋 Installing project requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
        print("✅ Project requirements installed!")
        
except Exception as e:
    print(f"❌ Error cloning repository: {{e}}")
    raise

# Step 3: Set environment variables
print("\\n🔐 Setting up environment variables...")
{env_setup if env_setup else 'print("ℹ️ No environment variables configured")'}

if "{env_setup}":
    print("✅ Environment variables configured!")

# Step 4: Import and start FastAPI app
print("\\n🔍 Loading FastAPI application...")
app_file = "{app_file}"
app_variable = "{app_variable}"

try:
    import importlib.util
    
    spec = importlib.util.spec_from_file_location('main_app', app_file)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    if hasattr(app_module, app_variable):
        fastapi_app = getattr(app_module, app_variable)
        print(f"✅ Found FastAPI app: {{app_variable}}")
        print(f"📊 App type: {{type(fastapi_app)}}")
    else:
        print(f"❌ App variable '{{app_variable}}' not found in {{app_file}}")
        print("Available variables:")
        for attr in dir(app_module):
            if not attr.startswith('_'):
                print(f"  - {{attr}}: {{type(getattr(app_module, attr))}}")
        raise Exception("App variable not found")
        
except Exception as e:
    print(f"❌ Error loading FastAPI app: {{e}}")
    raise

# Step 5: Start FastAPI server
print("\\n🚀 Starting FastAPI server...")

import uvicorn

def start_server():
    uvicorn.run(fastapi_app, host='0.0.0.0', port=8000, log_level='warning')

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Wait for server to start
print("⏳ Waiting for server to start...")
time.sleep(8)
print("✅ FastAPI server started on port 8000!")

# Step 6: Create ngrok tunnel
print("\\n🌐 Creating public URL with ngrok...")

try:
    from pyngrok import ngrok
    from google.colab import userdata
    
    # Try to get auth token from Colab secrets
    try:
        ngrok_auth_token = userdata.get('NGROK_AUTH_TOKEN')
        ngrok.set_auth_token(ngrok_auth_token)
        print("✅ Using ngrok auth token from Colab secrets!")
    except:
        print("⚠️ No NGROK_AUTH_TOKEN in Colab secrets - using free tier")
        print("💡 For unlimited sessions: Add NGROK_AUTH_TOKEN to Colab secrets")
    
    # Create tunnel
    public_tunnel = ngrok.connect(8000)
    public_url = public_tunnel.public_url
    
    print("\\n🎉 DEPLOYMENT SUCCESSFUL! 🎉")
    print("=" * 60)
    print(f"🔗 PUBLIC API URL: {{public_url}}")
    print(f"📚 Swagger UI: {{public_url}}/docs")
    print(f"📋 ReDoc: {{public_url}}/redoc")
    print("=" * 60)
    
    # Test the API
    print("\\n🧪 Testing API...")
    try:
        response = requests.get(f"{{public_url}}/", timeout=10)
        if response.status_code == 200:
            print("✅ API is responding correctly!")
            print(f"📊 Response preview: {{response.text[:100]}}...")
        else:
            print(f"⚠️ API returned status: {{response.status_code}}")
    except Exception as test_error:
        print(f"⚠️ API test failed: {{test_error}}")
    
    print("\\n🎯 YOUR FASTAPI BACKEND IS NOW LIVE!")
    print("💡 Copy the PUBLIC API URL above for your frontend")
    print("⚠️ Keep this notebook running to maintain the API")
    
    # Store URL globally
    globals()['PUBLIC_API_URL'] = public_url
    
    print("\\n📱 QUICK LINKS:")
    print(f"🏠 Homepage: {{public_url}}/")
    print(f"📚 API Docs: {{public_url}}/docs")
    print(f"📋 ReDoc: {{public_url}}/redoc")
    
    print("\\n✨ DEPLOYMENT COMPLETED SUCCESSFULLY! ✨")
    
except Exception as e:
    print(f"❌ Failed to create ngrok tunnel: {{e}}")
    print("\\n🔧 Troubleshooting:")
    print("1. Ensure FastAPI server is running")
    print("2. Check if port 8000 is accessible")
    print("3. Try running this cell again")
    print("4. For unlimited ngrok: Add NGROK_AUTH_TOKEN to Colab secrets")
    raise

# Optional: Simple monitoring function
def monitor_api():
    """Simple API monitoring function"""
    if 'PUBLIC_API_URL' in globals():
        api_url = globals()['PUBLIC_API_URL']
        print(f"\\n🔄 Monitoring API: {{api_url}}")
        print("Run this function to check API health:")
        print("monitor_api()")
        
        try:
            response = requests.get(f"{{api_url}}/", timeout=5)
            timestamp = datetime.now().strftime('%H:%M:%S')
            if response.status_code == 200:
                print(f"✅ {{timestamp}} - API healthy ({{response.status_code}})")
            else:
                print(f"⚠️ {{timestamp}} - API status: {{response.status_code}}")
        except Exception as e:
            print(f"❌ {{timestamp}} - API check failed: {{e}}")
    else:
        print("❌ No API URL found")

print("\\n🎯 To monitor your API, run: monitor_api()")
'''

        return cell_code
    
    def create_colab_link(self, cell_code: str) -> str:
        """Create a direct Colab link with the code"""
        import urllib.parse
        import base64
        
        # Create a simple notebook structure
        notebook_content = {
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
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": cell_code.split('\\n')
                }
            ]
        }
        
        # For now, return instructions to manually create
        return "https://colab.research.google.com/"
