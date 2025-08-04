"""
FastAPI Deployment Orchestrator
"""
import os
import tempfile
from typing import Dict, Optional
from datetime import datetime

from .git_clone import GitHubRepoHandler
from .app_detector import FastAPIDetector
from .env_handler import EnvironmentHandler
from .colab_generator import ColabNotebookGenerator
from .single_cell_generator import SingleCellGenerator


class DeploymentService:
    """Main deployment service orchestrator"""
    
    def __init__(self):
        self.repo_handler = GitHubRepoHandler()
        self.app_detector = FastAPIDetector()
        self.env_handler = EnvironmentHandler()
        self.notebook_generator = ColabNotebookGenerator()
        self.single_cell_generator = SingleCellGenerator()
        
        self.deployment_status = {}
    
    def deploy_repository(self, 
                         github_url: str,
                         env_file_content: Optional[str] = None,
                         custom_requirements: Optional[str] = None,
                         app_name: Optional[str] = None,
                         ngrok_auth: Optional[str] = None,
                         python_version: str = "3.10") -> Dict:
        """Main deployment function"""
        
        deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Step 1: Validate and analyze repository
            print("🔍 Validating GitHub repository...")
            repo_analysis = self.repo_handler.analyze_repository_structure(github_url)
            
            if not repo_analysis["valid"]:
                return {
                    "success": False,
                    "error": repo_analysis["error"],
                    "step": "repository_validation"
                }
            
            # Step 2: Clone repository temporarily for detailed analysis
            print("📥 Cloning repository for analysis...")
            clone_success, temp_dir, clone_message = self.repo_handler.clone_repository_temp(github_url)
            
            if not clone_success:
                return {
                    "success": False,
                    "error": clone_message,
                    "step": "repository_cloning"
                }
            
            try:
                # Step 3: Detect FastAPI application
                print("🔍 Detecting FastAPI application...")
                fastapi_analysis = self.app_detector.scan_directory_for_fastapi(temp_dir)
                
                if not fastapi_analysis["has_fastapi"]:
                    return {
                        "success": False,
                        "error": "No FastAPI application found in repository",
                        "step": "fastapi_detection",
                        "suggestions": [
                            "Ensure your repository contains a FastAPI app",
                            "Check that FastAPI is imported in your Python files",
                            "Verify your main application file is named main.py, app.py, or similar"
                        ]
                    }
                
                # Get recommended app
                recommended_app = fastapi_analysis.get("recommended_app")
                if not recommended_app:
                    recommended_app = fastapi_analysis["found_apps"][0]
                
                app_file = recommended_app["file"]
                
                # Extract app variable name
                with open(os.path.join(temp_dir, app_file), 'r', encoding='utf-8') as f:
                    app_content = f.read()
                app_variable = self.app_detector.extract_app_variable_name(app_content)
                
                # Step 4: Get requirements
                print("📋 Processing requirements...")
                requirements_content = custom_requirements
                
                if not requirements_content:
                    # Try to get from repository
                    requirements_content = self.repo_handler.get_requirements_content(github_url)
                
                # Step 5: Process environment variables
                print("🔐 Processing environment variables...")
                env_vars = {}
                env_validation = {"valid": True}
                
                if env_file_content:
                    env_vars = self.env_handler.parse_env_file(env_file_content)
                    env_validation = self.env_handler.validate_env_vars(env_vars)
                
                # Step 6: Generate Colab notebook
                print("📓 Generating deployment notebook...")
                notebook_result = self.notebook_generator.generate_deployment_notebook(
                    github_url=github_url,
                    app_file=app_file,
                    app_variable=app_variable,
                    env_vars=env_vars,
                    requirements=requirements_content,
                    deployment_id=deployment_id,
                    app_name=app_name,
                    ngrok_auth=ngrok_auth,
                    python_version=python_version
                )
                
                if not notebook_result["success"]:
                    return {
                        "success": False,
                        "error": "Failed to generate notebook",
                        "step": "notebook_generation"
                    }
                
                # Step 7: Generate single cell code
                single_cell_code = self.single_cell_generator.generate_single_cell_deployment(
                    github_url=github_url,
                    app_file=app_file,
                    app_variable=app_variable,
                    env_vars=env_vars,
                    requirements=requirements_content,
                    app_name=app_name,
                    ngrok_auth=ngrok_auth
                )
                
                # Step 8: Save single cell code to TXT file
                single_cell_filename = f"fastapi_deploy_single_cell_{deployment_id}.txt"
                single_cell_path = os.path.join('generated_notebooks', single_cell_filename)
                
                os.makedirs('generated_notebooks', exist_ok=True)
                with open(single_cell_path, 'w', encoding='utf-8') as f:
                    f.write(single_cell_code)
                
                # Step 9: Save notebook
                notebook_filename = f"fastapi_deploy_{deployment_id}.ipynb"
                notebook_path = self.notebook_generator.save_notebook(
                    notebook_result["notebook"], 
                    notebook_filename
                )
                
                # Step 9: Prepare response
                return {
                    "success": True,
                    "deployment_id": deployment_id,
                    "notebook_path": notebook_path,
                    "notebook_filename": notebook_filename,
                    "single_cell_code": single_cell_code,
                    "single_cell_path": single_cell_path,
                    "single_cell_filename": single_cell_filename,
                    "colab_url": "https://colab.research.google.com/",
                    "repository_info": {
                        "url": github_url,
                        "owner": repo_analysis["repo_info"]["owner"],
                        "repo": repo_analysis["repo_info"]["repo"],
                        "description": repo_analysis["repo_info"].get("description", ""),
                        "language": repo_analysis["repo_info"].get("language", "Python")
                    },
                    "fastapi_info": {
                        "app_file": app_file,
                        "app_variable": app_variable,
                        "confidence": recommended_app["confidence"],
                        "total_apps_found": len(fastapi_analysis["found_apps"])
                    },
                    "environment": {
                        "vars_count": len(env_vars),
                        "has_sensitive_vars": any(
                            pattern in key.lower() 
                            for key in env_vars.keys() 
                            for pattern in ['password', 'secret', 'key', 'token']
                        ) if env_vars else False,
                        "validation_warnings": env_validation.get("warnings", [])
                    },
                    "requirements": {
                        "has_custom": bool(requirements_content),
                        "source": "uploaded" if custom_requirements else ("repository" if requirements_content else "default")
                    },
                    "deployment_steps": [
                        "✅ Repository validated",
                        "✅ FastAPI app detected", 
                        "✅ Environment configured",
                        "✅ Notebook generated",
                        "🚀 Ready for Colab deployment"
                    ],
                    "colab_instructions": [
                        f"1. Download the generated notebook: {notebook_filename}",
                        "2. Open Google Colab (colab.research.google.com)",
                        "3. Upload the notebook file",
                        "4. Run all cells (Runtime → Run all)",
                        "5. Copy your public API URL from the output"
                    ],
                    "estimated_deployment_time": "2-3 minutes"
                }
                
            finally:
                # Cleanup temporary directory
                self.repo_handler.cleanup_temp_directory()
                
        except Exception as e:
            # Ensure cleanup happens even on error
            self.repo_handler.cleanup_temp_directory()
            
            return {
                "success": False,
                "error": f"Deployment preparation failed: {str(e)}",
                "step": "general_error"
            }
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """Get status of a deployment"""
        return self.deployment_status.get(deployment_id, {
            "status": "not_found",
            "error": "Deployment ID not found"
        })
    
    def validate_github_url_quick(self, github_url: str) -> Dict:
        """Quick validation of GitHub URL"""
        return self.repo_handler.validate_github_url(github_url)
    
    def get_sample_env_content(self) -> str:
        """Get sample .env file content"""
        sample_vars = self.env_handler.get_sample_env_vars()
        return self.env_handler.create_env_file_content(sample_vars)
    
    def analyze_repository_quick(self, github_url: str) -> Dict:
        """Quick repository analysis without cloning"""
        return self.repo_handler.analyze_repository_structure(github_url)
