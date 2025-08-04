"""
Google Colab Integration Utilities
"""
import streamlit as st
import base64
import os
from typing import Optional


def create_colab_button(notebook_path: str, button_text: str = "🚀 Open in Google Colab") -> bool:
    """Create a button to open notebook in Google Colab"""
    
    if not os.path.exists(notebook_path):
        st.error(f"Notebook file not found: {notebook_path}")
        return False
    
    # Create download button for notebook
    with open(notebook_path, 'rb') as f:
        notebook_data = f.read()
    
    # Create download button
    download_clicked = st.download_button(
        label="📥 Download Notebook",
        data=notebook_data,
        file_name=os.path.basename(notebook_path),
        mime="application/json",
        help="Download the notebook file to upload to Google Colab"
    )
    
    # Create Colab link
    st.markdown("""
    ### 🚀 Deploy to Google Colab:
    1. **Download the notebook** using the button above
    2. **Open Google Colab** in a new tab: [colab.research.google.com](https://colab.research.google.com)
    3. **Upload the notebook** (File → Upload notebook)
    4. **Run all cells** (Runtime → Run all)
    5. **Copy your public API URL** from the output
    """)
    
    # Colab launch button
    colab_clicked = st.button(
        "🌐 Open Google Colab",
        help="Opens Google Colab in a new tab"
    )
    
    if colab_clicked:
        st.markdown("""
        <script>
        window.open('https://colab.research.google.com', '_blank');
        </script>
        """, unsafe_allow_html=True)
        
        st.success("✅ Google Colab opened in new tab! Upload your downloaded notebook there.")
    
    return download_clicked or colab_clicked


def display_colab_instructions(deployment_id: str):
    """Display detailed Colab deployment instructions"""
    
    st.markdown("---")
    st.markdown("## 📋 Deployment Instructions")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        ### 🎯 Quick Steps:
        1. Download notebook ⬆️
        2. Open Google Colab
        3. Upload notebook file
        4. Run all cells
        5. Get public API URL
        """)
    
    with col2:
        st.markdown(f"""
        ### 📝 Detailed Process:
        
        **Step 1: Download Notebook**
        - Click the "📥 Download Notebook" button above
        - Save the file to your computer
        
        **Step 2: Open Google Colab**
        - Go to [colab.research.google.com](https://colab.research.google.com)
        - Sign in with your Google account
        
        **Step 3: Upload Notebook**
        - Click "File" → "Upload notebook"
        - Select the downloaded notebook file
        
        **Step 4: Run Deployment**
        - Click "Runtime" → "Run all"
        - Wait 2-3 minutes for completion
        
        **Step 5: Get Your API URL**
        - Copy the public URL from the output
        - Use it in your frontend applications
        
        **Deployment ID:** `{deployment_id}`
        """)


def create_colab_status_monitor():
    """Create a status monitor for Colab deployment"""
    
    st.markdown("---")
    st.markdown("## 📊 Deployment Monitoring")
    
    # Status indicators
    status_container = st.container()
    
    with status_container:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📥 Download",
                value="Ready",
                delta="Notebook generated"
            )
        
        with col2:
            st.metric(
                label="🚀 Deploy",
                value="Pending",
                delta="Upload to Colab"
            )
        
        with col3:
            st.metric(
                label="🌐 Public URL",
                value="Waiting",
                delta="Run notebook"
            )
        
        with col4:
            st.metric(
                label="⏱️ Est. Time",
                value="2-3 min",
                delta="Full deployment"
            )


def display_api_usage_examples(api_url: Optional[str] = None):
    """Display examples of how to use the deployed API"""
    
    st.markdown("---")
    st.markdown("## 💡 API Usage Examples")
    
    placeholder_url = api_url or "https://your-api-url.ngrok.io"
    
    tab1, tab2, tab3 = st.tabs(["🐍 Python", "🌐 JavaScript", "📱 cURL"])
    
    with tab1:
        st.code(f"""
# Python example using requests
import requests

# Make a GET request to your API
response = requests.get("{placeholder_url}/")
print(response.json())

# POST request example
data = {{"key": "value"}}
response = requests.post("{placeholder_url}/endpoint", json=data)
print(response.json())
        """, language="python")
    
    with tab2:
        st.code(f"""
// JavaScript example using fetch
// GET request
fetch('{placeholder_url}/')
  .then(response => response.json())
  .then(data => console.log(data));

// POST request
const data = {{ key: 'value' }};
fetch('{placeholder_url}/endpoint', {{
  method: 'POST',
  headers: {{
    'Content-Type': 'application/json',
  }},
  body: JSON.stringify(data),
}})
.then(response => response.json())
.then(data => console.log(data));
        """, language="javascript")
    
    with tab3:
        st.code(f"""
# cURL examples
# GET request
curl {placeholder_url}/

# POST request with JSON data
curl -X POST {placeholder_url}/endpoint \\
  -H "Content-Type: application/json" \\
  -d '{{"key": "value"}}'
        """, language="bash")


def show_troubleshooting_tips():
    """Display troubleshooting tips for common issues"""
    
    with st.expander("🔧 Troubleshooting Tips"):
        st.markdown("""
        ### Common Issues & Solutions:
        
        **❌ "FastAPI app not found"**
        - Ensure your repository has a FastAPI app instance
        - Check that FastAPI is imported: `from fastapi import FastAPI`
        - Verify app variable name (usually `app = FastAPI()`)
        
        **❌ "Requirements installation failed"**
        - Check your requirements.txt for typos
        - Ensure all packages are available on PyPI
        - Try running without custom requirements first
        
        **❌ "Environment variables not working"**
        - Verify .env file format: `KEY=value`
        - No spaces around the equals sign
        - Use quotes for values with spaces: `KEY="value with spaces"`
        
        **❌ "Ngrok tunnel failed"**
        - Wait for FastAPI server to start completely
        - Try running the ngrok cell again
        - Check if port 8000 is accessible
        
        **❌ "API not responding"**
        - Ensure your FastAPI app runs locally first
        - Check for syntax errors in your code
        - Verify all dependencies are installed
        
        ### 💡 Pro Tips:
        - Keep the Colab notebook running to maintain your API
        - Colab sessions timeout after ~12 hours of inactivity
        - Save your API URL before the session ends
        - Test your API with the Swagger UI (/docs endpoint)
        """)