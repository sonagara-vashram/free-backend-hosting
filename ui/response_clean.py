import streamlit as st
import webbrowser
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.colab_button import create_colab_button, display_colab_instructions, display_api_usage_examples, show_troubleshooting_tips


def show_deployment_response(deployment_data):
    """Show deployment results with enhanced UI"""
    
    if not deployment_data['submitted'] or not deployment_data['valid_url']:
        return
    
    # Initialize deployment service
    if 'deployment_service' not in st.session_state:
        from services.deployer import DeploymentService
        st.session_state.deployment_service = DeploymentService()
    
    # Run deployment
    with st.spinner("🚀 Preparing your deployment..."):
        try:
            result = st.session_state.deployment_service.deploy_repository(
                github_url=deployment_data['github_url'],
                env_file_content=deployment_data['env_file_content'],
                custom_requirements=deployment_data['custom_requirements']
            )
            
            if result['success']:
                show_success_response(result)
            else:
                show_error_response(result)
                
        except Exception as e:
            show_error_response({
                "success": False,
                "error": f"Deployment failed: {str(e)}",
                "step": "deployment_execution"
            })


def show_success_response(result):
    """Display successful deployment results"""
    
    st.success("🎉 Deployment Ready!")
    
    # Deployment Summary
    st.markdown("## 📊 Deployment Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📁 Repository",
            value=result['repository_info']['repo'],
            delta=result['repository_info']['owner']
        )
    
    with col2:
        st.metric(
            label="🐍 FastAPI App",
            value=result['fastapi_info']['app_file'],
            delta=f"Confidence: {result['fastapi_info']['confidence']}%"
        )
    
    with col3:
        st.metric(
            label="🔐 Environment",
            value=f"{result['environment']['vars_count']} variables",
            delta="Secure injection" if result['environment']['vars_count'] > 0 else "No variables"
        )
    
    # Progress Steps
    st.markdown("## ✅ Deployment Steps Completed")
    for step in result['deployment_steps']:
        st.markdown(step)
    
    # Download and Deploy Section
    st.markdown("---")
    st.markdown("## 🚀 Deploy to Google Colab")
    
    # Notebook download and Colab instructions
    if os.path.exists(result['notebook_path']):
        # Create download button and Colab link
        create_colab_button(result['notebook_path'])
        
        # Show detailed instructions
        display_colab_instructions(result['deployment_id'])
        
        # Show usage examples
        display_api_usage_examples()
        
        # Troubleshooting
        show_troubleshooting_tips()
        
    else:
        st.error("❌ Notebook file not found. Please try again.")
    
    # Additional Info
    with st.expander("📋 Detailed Information"):
        st.json(result)


def show_error_response(result):
    """Display error response with helpful guidance"""
    
    st.error(f"❌ Deployment Failed")
    
    error_message = result.get('error', 'Unknown error occurred')
    step = result.get('step', 'unknown')
    
    st.markdown(f"**Error:** {error_message}")
    st.markdown(f"**Failed at:** {step}")
    
    # Show suggestions based on error type
    suggestions = result.get('suggestions', [])
    if suggestions:
        st.markdown("### 💡 Suggestions:")
        for suggestion in suggestions:
            st.markdown(f"- {suggestion}")
    
    # Common troubleshooting
    with st.expander("🔧 Common Solutions"):
        st.markdown("""
        ### Repository Issues:
        - Ensure your repository is public
        - Check that it contains FastAPI code
        - Verify the GitHub URL is correct
        
        ### FastAPI Detection Issues:
        - Make sure you have `app = FastAPI()` in your code
        - Check that fastapi is imported: `from fastapi import FastAPI`
        - Ensure your main file is named main.py, app.py, or similar
        
        ### Environment Variables:
        - Check .env file format: KEY=value
        - No spaces around the equals sign
        - Use quotes for values with spaces
        
        ### Dependencies:
        - Verify all packages in requirements.txt are correct
        - Check for typos in package names
        - Ensure packages are available on PyPI
        """)
    
    # Retry option
    if st.button("🔄 Try Again", type="primary"):
        st.rerun()


def show_response(result):
    """Legacy function for backward compatibility"""
    
    if not result:
        st.error("❌ No response received from deployment service")
        return
    
    # Handle different response types
    if isinstance(result, dict):
        if result.get("success"):
            show_success_response(result)
        else:
            show_error_response(result)
    elif isinstance(result, str):
        st.info(result)
    else:
        st.error(f"❌ Unexpected response format: {type(result)}")


def show_api_testing_section(api_url):
    """Show API testing section"""
    
    with st.expander("🧪 **Quick API Test**", expanded=True):
        st.markdown("**Test your API endpoints:**")
        
        test_col1, test_col2 = st.columns(2)
        
        with test_col1:
            st.markdown("**🔗 Basic Test:**")
            st.code(f"curl {api_url}/", language="bash")
            
            st.markdown("**❤️ Health Check:**")
            st.code(f"curl {api_url}/health", language="bash")
        
        with test_col2:
            st.markdown("**📱 In Browser:**")
            st.markdown(f"- [Root Endpoint]({api_url}/)")
            st.markdown(f"- [Health Check]({api_url}/health)")
            st.markdown(f"- [API Status]({api_url}/status)")


def show_integration_guide(api_url):
    """Show integration guide for the API"""
    
    with st.expander("🔧 **Integration Guide**"):
        st.markdown(f"""
        **JavaScript/Frontend Integration:**
        ```javascript
        // Fetch API data
        fetch('{api_url}/')
          .then(response => response.json())
          .then(data => console.log(data));
        ```
        
        **Python Integration:**
        ```python
        import requests
        
        response = requests.get('{api_url}/')
        data = response.json()
        print(data)
        ```
        
        **React Example:**
        ```jsx
        const [data, setData] = useState(null);
        
        useEffect(() => {{
          fetch('{api_url}/')
            .then(res => res.json())
            .then(setData);
        }}, []);
        ```
        
        **Features Available:**
        - ✅ CORS enabled for web apps
        - ✅ JSON responses
        - ✅ Automatic API documentation
        - ✅ Global accessibility
        - ✅ HTTPS security (via ngrok)
        """)


# Legacy functions for compatibility
def handle_dict_response(result):
    show_response(result)

def handle_string_response(result):
    st.info(result)
