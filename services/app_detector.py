import os
import re
from typing import Dict, List, Optional
import ast


class FastAPIDetector:
    """Detect FastAPI applications in repository"""
    
    def __init__(self):
        self.app_patterns = [
            r'app\s*=\s*FastAPI\(',
            r'application\s*=\s*FastAPI\(',
            r'api\s*=\s*FastAPI\(',
            r'server\s*=\s*FastAPI\(',
            r'fastapi_app\s*=\s*FastAPI\(',
        ]
        
        self.import_patterns = [
            r'from\s+fastapi\s+import\s+FastAPI',
            r'import\s+fastapi',
            r'from\s+fastapi\s+import\s+.*FastAPI',
        ]
    
    def scan_directory_for_fastapi(self, directory: str) -> Dict[str, any]:
        """Scan directory for FastAPI applications"""
        try:
            results = {
                "found_apps": [],
                "python_files": [],
                "potential_main_files": [],
                "has_fastapi": False
            }
            
            # Common main file names
            main_file_names = ["main.py", "app.py", "server.py", "api.py", "run.py"]
            
            # Scan for Python files
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, directory)
                        results["python_files"].append(rel_path)
                        
                        # Check if it's a potential main file
                        if file in main_file_names:
                            results["potential_main_files"].append(rel_path)
                        
                        # Analyze file for FastAPI
                        fastapi_info = self.analyze_python_file(file_path)
                        if fastapi_info["has_fastapi"]:
                            results["has_fastapi"] = True
                            results["found_apps"].append({
                                "file": rel_path,
                                "app_instances": fastapi_info["app_instances"],
                                "imports": fastapi_info["imports"],
                                "confidence": fastapi_info["confidence"]
                            })
            
            # Determine best app file
            if results["found_apps"]:
                results["recommended_app"] = self.get_recommended_app(results["found_apps"])
            
            return results
            
        except Exception as e:
            return {
                "found_apps": [],
                "python_files": [],
                "potential_main_files": [],
                "has_fastapi": False,
                "error": str(e)
            }
    
    def analyze_python_file(self, file_path: str) -> Dict[str, any]:
        """Analyze a Python file for FastAPI usage"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                "has_fastapi": False,
                "app_instances": [],
                "imports": [],
                "confidence": 0
            }
            
            # Check for FastAPI imports
            for pattern in self.import_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result["has_fastapi"] = True
                    result["imports"].append(pattern)
                    result["confidence"] += 30
            
            # Check for FastAPI app instances
            for pattern in self.app_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result["has_fastapi"] = True
                    result["app_instances"].extend(matches)
                    result["confidence"] += 40
            
            # Additional checks
            if '@app.route' in content or '@app.get' in content or '@app.post' in content:
                result["confidence"] += 20
            
            if 'uvicorn' in content:
                result["confidence"] += 10
            
            return result
            
        except Exception as e:
            return {
                "has_fastapi": False,
                "app_instances": [],
                "imports": [],
                "confidence": 0,
                "error": str(e)
            }
    
    def get_recommended_app(self, found_apps: List[Dict]) -> Dict[str, any]:
        """Get the most likely main application file"""
        if not found_apps:
            return {}
        
        # Sort by confidence and prefer main file names
        main_names = ["main.py", "app.py", "server.py", "api.py"]
        
        def score_app(app):
            score = app["confidence"]
            
            # Bonus for common main file names
            filename = os.path.basename(app["file"])
            if filename in main_names:
                score += 50
            
            # Bonus for being in root directory
            if '/' not in app["file"] and '\\' not in app["file"]:
                score += 20
            
            return score
        
        sorted_apps = sorted(found_apps, key=score_app, reverse=True)
        return sorted_apps[0]
    
    def extract_app_variable_name(self, file_content: str) -> Optional[str]:
        """Extract the variable name of FastAPI app instance"""
        try:
            # Try to parse with AST
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # Check if right side is a FastAPI call
                    if isinstance(node.value, ast.Call):
                        if hasattr(node.value.func, 'id') and node.value.func.id == 'FastAPI':
                            if node.targets and hasattr(node.targets[0], 'id'):
                                return node.targets[0].id
                        elif hasattr(node.value.func, 'attr') and node.value.func.attr == 'FastAPI':
                            if node.targets and hasattr(node.targets[0], 'id'):
                                return node.targets[0].id
            
            # Fallback to regex
            patterns = [
                r'(\w+)\s*=\s*FastAPI\(',
                r'(\w+)\s*=\s*fastapi\.FastAPI\(',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, file_content)
                if match:
                    return match.group(1)
            
            return "app"  # Default fallback
            
        except Exception:
            return "app"  # Default fallback
    
    def get_uvicorn_command(self, app_file: str, app_variable: str = "app") -> str:
        """Generate uvicorn command for the app"""
        # Remove .py extension and convert path separators
        module_path = app_file.replace('.py', '').replace('/', '.').replace('\\', '.')
        
        return f"uvicorn {module_path}:{app_variable} --host 0.0.0.0 --port 8000"
