import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.layout import main_layout
from ui.form import deployment_form
from ui.response import show_success_response
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
    
    # Add "New Deployment" button if previous deployment exists
    if hasattr(st.session_state, 'deployment_successful'):
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Start New Deployment", type="secondary"):
            # Clear previous deployment state
            if 'deployment_result' in st.session_state:
                del st.session_state.deployment_result
            if 'deployment_successful' in st.session_state:
                del st.session_state.deployment_successful
            if 'deployment_error' in st.session_state:
                del st.session_state.deployment_error
            st.experimental_rerun()
    
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
            
            # Store result in session state to prevent loss on rerun
            if result.get("success"):
                st.session_state.deployment_result = result
                st.session_state.deployment_successful = True
            else:
                st.session_state.deployment_error = result.get('error', 'Unknown error')
                st.session_state.deployment_successful = False
                
        except Exception as e:
            error_msg = str(e)
            st.session_state.deployment_error = error_msg
            st.session_state.deployment_successful = False
    
    # Show results from session state
    if hasattr(st.session_state, 'deployment_successful'):
        if st.session_state.deployment_successful:
            show_success_response(st.session_state.deployment_result)
        else:
            st.error(f"❌ Deployment failed: {st.session_state.deployment_error}")
            
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

if __name__ == "__main__":
    main()
