import os
import tempfile
import shutil
import requests
from typing import Dict, Optional, Tuple
import subprocess
import stat
import time
from urllib.parse import urlparse


class GitHubRepoHandler:
    """Handle GitHub repository operations"""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_info = {}
    
    def validate_github_url(self, github_url: str) -> Dict[str, any]:
        """Validate GitHub repository URL"""
        try:
            # Basic URL validation
            if not github_url.startswith('https://github.com/'):
                return {
                    "valid": False,
                    "error": "Must be a valid GitHub HTTPS URL (https://github.com/username/repo)"
                }
            
            # Extract owner and repo
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                return {
                    "valid": False,
                    "error": "Invalid GitHub URL format"
                }
            
            owner, repo = path_parts[0], path_parts[1]
            
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            
            # Check if repository exists and is public
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 404:
                return {
                    "valid": False,
                    "error": "Repository not found or is private"
                }
            elif response.status_code != 200:
                return {
                    "valid": False,
                    "error": f"GitHub API error: {response.status_code}"
                }
            
            repo_data = response.json()
            
            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language"),
                "clone_url": github_url
            }
            
        except requests.RequestException as e:
            return {
                "valid": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def analyze_repository_structure(self, github_url: str) -> Dict[str, any]:
        """Analyze repository structure for FastAPI compatibility"""
        try:
            validation = self.validate_github_url(github_url)
            if not validation["valid"]:
                return validation
            
            owner = validation["owner"]
            repo = validation["repo"]
            
            # Get repository contents
            contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            response = requests.get(contents_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    "valid": False,
                    "error": "Could not access repository contents"
                }
            
            contents = response.json()
            
            # Extract file names
            files = [item["name"] for item in contents if item["type"] == "file"]
            directories = [item["name"] for item in contents if item["type"] == "dir"]
            
            # Check for FastAPI app files
            app_files = ["main.py", "app.py", "server.py", "api.py", "run.py"]
            found_app_files = [f for f in app_files if f in files]
            
            # Check for requirements.txt
            has_requirements = "requirements.txt" in files
            
            # Check for common FastAPI patterns
            fastapi_indicators = []
            if found_app_files:
                fastapi_indicators.append(f"Found potential app files: {', '.join(found_app_files)}")
            
            if has_requirements:
                fastapi_indicators.append("Has requirements.txt")
            
            if any(d in directories for d in ["api", "routes", "endpoints"]):
                fastapi_indicators.append("Has API directory structure")
            
            return {
                "valid": True,
                "files": files,
                "directories": directories,
                "app_files": found_app_files,
                "has_requirements": has_requirements,
                "fastapi_indicators": fastapi_indicators,
                "repo_info": validation
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Analysis error: {str(e)}"
            }
    
    def get_requirements_content(self, github_url: str) -> Optional[str]:
        """Get requirements.txt content from repository"""
        try:
            validation = self.validate_github_url(github_url)
            if not validation["valid"]:
                return None
            
            owner = validation["owner"]
            repo = validation["repo"]
            
            # Get requirements.txt content
            req_url = f"https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt"
            response = requests.get(req_url, timeout=10)
            
            if response.status_code == 200:
                import base64
                content_data = response.json()
                content = base64.b64decode(content_data["content"]).decode("utf-8")
                return content
            
            return None
            
        except Exception as e:
            print(f"Error getting requirements: {e}")
            return None
    
    def clone_repository_temp(self, github_url: str) -> Tuple[bool, str, str]:
        """Clone repository to temporary directory"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="fastapi_deploy_")
            
            # Clone repository
            result = subprocess.run(
                ["git", "clone", github_url, self.temp_dir],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, self.temp_dir, "Repository cloned successfully"
            else:
                return False, "", f"Git clone failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "", "Clone operation timed out"
        except FileNotFoundError:
            return False, "", "Git not found. Please install Git."
        except Exception as e:
            return False, "", f"Clone error: {str(e)}"
    
    def cleanup_temp_directory(self):
        """Clean up temporary directory with Windows-specific handling"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                # Windows-specific cleanup for git repositories
                self._force_remove_readonly(self.temp_dir)
                self.temp_dir = None
                print("✅ Temporary files cleaned up successfully")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
                # Don't fail the whole process for cleanup issues
                self.temp_dir = None
    
    def _force_remove_readonly(self, path):
        """Force remove read-only files (Windows git issue)"""
        def handle_remove_readonly(func, path, exc):
            """Error handler for Windows read-only files"""
            if os.path.exists(path):
                # Make the file writable and try again
                os.chmod(path, stat.S_IWRITE)
                func(path)
        
        try:
            # First try normal removal
            shutil.rmtree(path)
        except PermissionError:
            try:
                # If that fails, use Windows-specific approach
                shutil.rmtree(path, onerror=handle_remove_readonly)
            except Exception:
                # Last resort: use system command
                try:
                    if os.name == 'nt':  # Windows
                        subprocess.run(['cmd', '/c', 'rmdir', '/s', '/q', path], 
                                     check=False, capture_output=True)
                    else:
                        subprocess.run(['rm', '-rf', path], 
                                     check=False, capture_output=True)
                except Exception:
                    # If all else fails, just leave it for garbage collection
                    pass
