from typing import Dict, List
import streamlit as st


class EnvironmentHandler:
    """Handle environment variables processing"""
    
    def __init__(self):
        self.env_vars = {}
    
    def parse_env_file(self, env_content: str) -> Dict[str, str]:
        """Parse .env file content"""
        env_vars = {}
        
        try:
            lines = env_content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split on first = only
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
            
            return env_vars
            
        except Exception as e:
            st.error(f"Error parsing .env file: {e}")
            return {}
    
    def validate_env_vars(self, env_vars: Dict[str, str]) -> Dict[str, any]:
        """Validate environment variables"""
        result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "processed_vars": {}
        }
        
        try:
            for key, value in env_vars.items():
                # Basic validation
                if not key:
                    result["errors"].append("Empty environment variable name found")
                    result["valid"] = False
                    continue
                
                # Check for invalid characters in key
                if not key.replace('_', '').replace('-', '').isalnum():
                    result["warnings"].append(f"Variable '{key}' contains special characters")
                
                # Check for sensitive data patterns
                sensitive_patterns = ['password', 'secret', 'key', 'token', 'api']
                if any(pattern in key.lower() for pattern in sensitive_patterns):
                    result["warnings"].append(f"Variable '{key}' appears to contain sensitive data")
                
                result["processed_vars"][key] = value
            
            return result
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {e}")
            return result
    
    def generate_env_injection_code(self, env_vars: Dict[str, str]) -> str:
        """Generate Python code to inject environment variables"""
        if not env_vars:
            return "# No environment variables to set\nprint('No environment variables configured')"
        
        code_lines = [
            "# Setting up environment variables",
            "import os",
            "print('Setting environment variables...')",
            ""
        ]
        
        for key, value in env_vars.items():
            # Escape quotes in value
            escaped_value = value.replace('"', '\\"')
            code_lines.append(f'os.environ["{key}"] = "{escaped_value}"')
        
        code_lines.extend([
            "",
            f"print(f'✅ Set {len(env_vars)} environment variables')",
            "print('Environment variables: ' + ', '.join(env_vars.keys()))"
        ])
        
        return "\n".join(code_lines)
    
    def create_env_file_content(self, env_vars: Dict[str, str]) -> str:
        """Create .env file content"""
        if not env_vars:
            return "# No environment variables"
        
        lines = ["# Environment variables for deployment"]
        
        for key, value in env_vars.items():
            # Add quotes if value contains spaces
            if ' ' in value:
                lines.append(f'{key}="{value}"')
            else:
                lines.append(f'{key}={value}')
        
        return "\n".join(lines)
    
    def get_sample_env_vars(self) -> Dict[str, str]:
        """Get sample environment variables for demonstration"""
        return {
            "DATABASE_URL": "postgresql://user:password@localhost/dbname",
            "SECRET_KEY": "your-secret-key-here",
            "API_KEY": "your-api-key-here",
            "DEBUG": "False",
            "PORT": "8000"
        }
    
    def format_for_display(self, env_vars: Dict[str, str]) -> List[str]:
        """Format environment variables for display"""
        if not env_vars:
            return ["No environment variables configured"]
        
        formatted = []
        for key, value in env_vars.items():
            # Mask sensitive values
            if any(pattern in key.lower() for pattern in ['password', 'secret', 'key', 'token']):
                masked_value = '*' * min(len(value), 8)
                formatted.append(f"{key} = {masked_value}")
            else:
                formatted.append(f"{key} = {value}")
        
        return formatted
