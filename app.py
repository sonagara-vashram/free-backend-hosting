import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from ui.layout import main_layout
from ui.form import deployment_form, old_deployment_form
from ui.response import show_deployment_response, show_success_response
from services.deployer import DeploymentService

def main():
    """Main Streamlit application for Free Backend Hosting"""
    
    # Configure page
    st.set_page_config(
        page_title="Free Backend Hosting",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply main layout
    main_layout()
    
    # Initialize deployment service
    if 'deployment_service' not in st.session_state:
        st.session_state.deployment_service = DeploymentService()
    
    # Show enhanced deployment form
    github_url, env_file, requirements_file, submit = deployment_form()
    
    # Handle deployment submission
    if submit and github_url and requirements_file:
        # Read files
        env_file_content = None
        if env_file:
            env_file_content = env_file.read().decode("utf-8")
            env_file.seek(0)  # Reset file pointer
        
        requirements_content = None
        if requirements_file:
            requirements_content = requirements_file.read().decode("utf-8")
            requirements_file.seek(0)  # Reset file pointer
        
        # Deploy with enhanced error handling
        try:
            with st.spinner("🔄 Processing deployment..."):
                result = st.session_state.deployment_service.deploy_repository(
                    github_url=github_url,
                    env_file_content=env_file_content,
                    custom_requirements=requirements_content
                )
            
            if result.get("success"):
                show_success_response(result)
            else:
                st.error(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
                
                # Show troubleshooting tips
                with st.expander("🔧 Troubleshooting Tips"):
                    st.markdown("""
                    **Common issues and solutions:**
                    
                    1. **Repository validation failed**
                       - Ensure the GitHub URL is correct and public
                       - Check your internet connection
                    
                    2. **FastAPI not detected**
                       - Verify your repository has FastAPI app with `app = FastAPI()`
                       - Check files like `main.py`, `app.py`, or similar
                    
                    3. **File access issues (Windows)**
                       - Temporary files cleanup may show warnings (this is normal)
                       - The deployment process should still work correctly
                    
                    4. **Requirements issues**
                       - Ensure requirements.txt has valid package names
                       - Check for any syntax errors in the file
                    
                    **Need more help?** Try with a different repository or check our documentation.
                    """)
                    
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ An unexpected error occurred: {error_msg}")
            
            # Enhanced error details
            with st.expander("🐛 Error Details & Debugging"):
                st.code(error_msg)
                
                st.markdown("""
                **Debugging steps:**
                1. Check your internet connection
                2. Verify the GitHub repository URL is accessible
                3. Ensure all uploaded files are valid
                4. Try refreshing the page and attempting again
                
                **Windows Users:** File cleanup warnings are normal and don't affect functionality.
                """)
                
                # Add debug info for development
                if "streamlit" in error_msg.lower() or "debug" in os.environ.get("APP_MODE", "").lower():
                    st.markdown("**Technical Details:**")
                    st.exception(e)

if __name__ == "__main__":
    main()
