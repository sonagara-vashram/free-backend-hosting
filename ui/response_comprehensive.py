import streamlit as st
import webbrowser
import os
import sys

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
    """Display successful deployment results with enhanced UI"""
    
    # Success animation
    st.success("🎉 Deployment Package Ready!")
    st.balloons()
    
    # Hero section
    st.markdown("""
    <div style="background: linear-gradient(90deg, #4CAF50, #45a049); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; text-align: center; margin: 0;">
            🚀 Your FastAPI Backend is Ready to Deploy!
        </h2>
        <p style="color: white; text-align: center; margin: 10px 0 0 0;">
            Everything is configured and ready for Google Colab deployment
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Deployment Summary Cards
    st.markdown("## 📊 Deployment Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📁 Repository",
            value=result['repository_info']['repo'],
            delta=f"by {result['repository_info']['owner']}"
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
    
    # Progress indicator
    st.markdown("---")
    st.markdown("## ✅ Preparation Steps Completed")
    
    progress_cols = st.columns(5)
    steps = [
        ("🔍", "Repository\\nValidated"),
        ("🐍", "FastAPI App\\nDetected"),
        ("📦", "Dependencies\\nResolved"),
        ("🔐", "Environment\\nConfigured"),
        ("📓", "Notebook\\nGenerated")
    ]
    
    for i, (icon, step) in enumerate(steps):
        with progress_cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: #e8f5e8; border-radius: 8px; margin: 5px;">
                <div style="font-size: 2em;">{icon}</div>
                <div style="font-size: 0.8em; color: #2e7d32;">{step}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main deployment section
    st.markdown("---")
    st.markdown("## 🚀 Deploy to Google Colab")
    
    # Detailed step-by-step instructions
    st.markdown("## 📋 Deployment Instructions")
    
    # Create tabs for different instruction formats  
    tab1, tab2, tab3 = st.tabs(["⚡ One-Click Deploy", "📝 Detailed Guide", "🎥 Video Guide"])
    
    with tab1:
        st.markdown("### ⚡ One-Click Deploy (Fastest Method)")
        st.markdown("**Copy the code below and paste it into a single Google Colab cell, then run it!**")
        
        # Single cell deployment
        if 'single_cell_code' in result and 'single_cell_path' in result:
            # Two column layout for buttons
            download_col1, download_col2 = st.columns([1, 1])
            
            with download_col1:
                # Download single cell code as TXT file
                if os.path.exists(result['single_cell_path']):
                    with open(result['single_cell_path'], 'r', encoding='utf-8') as f:
                        single_cell_txt = f.read()
                    
                    st.download_button(
                        label="📥 Download Code (TXT)",
                        data=single_cell_txt,
                        file_name=result['single_cell_filename'],
                        mime="text/plain",
                        type="primary",
                        use_container_width=True,
                        help="Download the complete code as a text file"
                    )
            
            with download_col2:
                if st.button("🚀 Open Google Colab", type="secondary", use_container_width=True):
                    st.markdown("🌐 **Opening Google Colab...**")
                    st.markdown("[👆 Click here if it didn't open automatically](https://colab.research.google.com/)")
                    # Try to open in new tab using JavaScript
                    st.markdown("""
                    <script>
                    window.open('https://colab.research.google.com/', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
            
            # Instructions
            st.markdown("#### 💡 How to Use:")
            st.info("""
            **Method 1: Download & Copy (Recommended)**
            1. 📥 Click "Download Code (TXT)" button above
            2. 🌐 Open Google Colab in new tab  
            3. 📁 Create a new notebook
            4. 📄 Open the downloaded TXT file on your computer
            5. 📋 Copy all the code from the TXT file
            6. 📝 Paste it into a Colab code cell
            7. ▶️ Run the cell (Shift + Enter)
            8. ⏳ Wait 2-3 minutes for deployment!
            
            **Method 2: Copy from Below**
            1. Select all code below and copy it
            2. Paste into Google Colab cell and run
            """)
            
            # Code display with copy button
            st.markdown("#### 📋 Complete Deployment Code:")
            
            # Enhanced code display
            with st.expander("👀 View/Copy Code (Click to expand)", expanded=False):
                st.code(result['single_cell_code'], language='python')
                
                st.markdown("""
                **📝 Copy Instructions:**
                1. **Expand** this section fully
                2. **Select All** code (Ctrl+A or Cmd+A)  
                3. **Copy** (Ctrl+C or Cmd+C)
                4. **Paste** in Google Colab cell
                5. **Run** the cell
                """)
            
            # Success metrics
            st.markdown("---")
            st.markdown("#### 🎯 Why One-Click Deploy?")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("⏱️ Time", "2-3 min", help="Total deployment time")
            
            with metrics_col2:
                st.metric("🔧 Steps", "1 Cell", help="Just paste and run one cell")
            
            with metrics_col3:
                st.metric("💰 Cost", "Free", help="Completely free using Google Colab")
            
            st.success("""
            **🎉 Everything is automated in this single code!**
            - ✅ Package installation (fastapi, uvicorn, ngrok, etc.)
            - ✅ Repository cloning from GitHub (Public/Private both supported)
            - ✅ Environment variables setup  
            - ✅ FastAPI server startup
            - ✅ Public URL creation with ngrok
            - ✅ API testing and health check
            - ✅ Live monitoring dashboard
            
            **🔑 Pre-configured with ngrok auth token for unlimited usage!**
            """)
        else:
            st.error("Single cell code not available. Please try regenerating the deployment.")
    
    with tab2:
        st.markdown("""
        ### 📝 Complete Step-by-Step Guide for TXT File Deployment
        
        #### 🎯 **STEP 1: Download Code File**
        - Click the "📥 Download Code (TXT)" button above
        - Save the `.txt` file to your computer  
        - Remember the download location
        
        #### 🌐 **STEP 2: Open Google Colab**
        - Go to [colab.research.google.com](https://colab.research.google.com)
        - Sign in with your Google account (free)
        - You'll see the Colab homepage
        
        #### 📁 **STEP 3: Create New Notebook**
        - Click **"File"** in the top menu
        - Select **"New notebook"**
        - A new empty notebook will open
        
        #### 📋 **STEP 4: Copy the Code**
        - Open the downloaded `.txt` file on your computer
        - **Select All** code (Ctrl+A or Cmd+A)
        - **Copy** the code (Ctrl+C or Cmd+C)
        
        #### 📝 **STEP 5: Paste in Colab**
        - In the Colab notebook, click on the empty code cell
        - **Paste** the code (Ctrl+V or Cmd+V)
        - The entire deployment code will be in one cell
        
        #### ▶️ **STEP 6: Run the Code**
        - Click the **Play button** (▶️) next to the cell
        - OR press **Shift + Enter**
        - Watch the automatic deployment process
        - Wait 2-3 minutes for completion
        
        #### 🔗 **STEP 7: Get Your API URL**
        - Look for the "🎉 DEPLOYMENT SUCCESSFUL!" message
        - Copy the **Public API URL** from the output
        - Test it by clicking the Swagger UI link
        
        #### 🚀 **STEP 8: Use Your API**
        - Your API is now live and globally accessible
        - Use the URL in your frontend applications
        - Access API documentation at `your-url/docs`
        - Keep the Colab tab open to maintain the API
        
        **💡 Pro Tips:**
        - The code includes a pre-configured ngrok auth token
        - All packages install automatically
        - Environment variables are set automatically
        - No manual configuration needed!
        - Works with both Public and Private repositories!
        """)
    
    with tab3:
        st.markdown("""
        ### 🎥 Video Instructions for TXT File Deployment
        
        **🎬 Step-by-Step Video Walkthrough:**
        
        #### 📺 What you'll see in this process:
        
        **🔽 1. Download Phase (0-30 seconds)**
        - Click download button → TXT file downloads instantly
        - File contains complete deployment code
        - No need to unzip or extract
        
        **🌐 2. Google Colab Setup (30-60 seconds)**  
        - Open colab.research.google.com
        - Create new notebook
        - One empty code cell appears
        
        **📋 3. Code Copy Process (60-90 seconds)**
        - Open downloaded TXT file
        - Select all code (Ctrl+A)
        - Copy code (Ctrl+C)
        - Paste in Colab cell (Ctrl+V)
        
        **▶️ 4. Execution Phase (90 seconds - 4 minutes)**
        - Click Run button or Shift+Enter
        - Watch automated installation:
          - Package installation progress bars
          - GitHub repo cloning messages
          - FastAPI server startup logs
          - ngrok tunnel creation
        
        **🎉 5. Success Output (4-5 minutes)**
        - "DEPLOYMENT SUCCESSFUL!" message appears
        - Public API URL displayed
        - Swagger UI link provided
        - Testing endpoints shown
        
        #### 📱 **Expected Console Output Example:**
        ```bash
        📦 Installing packages...
        ✅ fastapi==0.104.1 installed
        ✅ uvicorn==0.24.0 installed  
        ✅ pyngrok==5.1.0 installed
        
        🔄 Cloning repository...
        🔄 Attempt 1/3...
        ✅ Repository cloned successfully
        
        🔧 Setting up environment...
        ✅ Environment variables configured
        
        🚀 Starting FastAPI server...
        ✅ Server running on http://127.0.0.1:8000
        
        🌐 Creating public tunnel...
        ✅ ngrok tunnel established
        
        🎉 DEPLOYMENT SUCCESSFUL!
        📡 Public API URL: https://abc123.ngrok.io
        📖 API Docs: https://abc123.ngrok.io/docs
        🧪 Health Check: https://abc123.ngrok.io/health
        ```
        
        #### ⚠️ **Common Issues & Quick Fixes:**
        
        **🔧 Package Installation Issues:**
        - **Problem:** `No module named 'pyngrok'`
        - **Solution:** ✅ Fixed in new version - proper comma separation
        - **Action:** Download fresh TXT file and try again
        
        **🔧 Repository Clone Issues:**
        - **Problem:** Git clone fails (Error 128)
        - **Solution:** ✅ Multi-attempt clone with different methods
        - **Supports:** Both public and private repositories
        - **Action:** Code automatically retries 3 times with different approaches
        
        **🔧 Network Issues:**
        - **Problem:** Connection timeouts
        - **Solution:** ✅ Built-in retry mechanisms
        - **Action:** Code waits and retries automatically
        
        **🔧 FastAPI Detection:**
        - **Problem:** App not found
        - **Solution:** ✅ Smart detection of app.py, main.py, server.py
        - **Action:** Ensure your FastAPI app follows standard patterns
        
        #### 🎯 **Video Timeline (Expected):**
        - **0:00-0:30** - Download TXT file
        - **0:30-1:00** - Open Google Colab & create notebook  
        - **1:00-1:30** - Copy-paste code from TXT file
        - **1:30-4:00** - Run cell & watch automated deployment
        - **4:00-4:30** - Get public URL & test API
        
        **⏱️ Total Time: 4-5 minutes**
        **🎥 Recommended: Record your own walkthrough for team reference!**
        """)
    
    # Advanced Features Section
    st.markdown("---")
    st.markdown("## 🔥 Advanced Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        ### 🚀 **Enhanced Capabilities**
        - ✅ **Multi-Repository Support** (Public/Private)
        - ✅ **Smart FastAPI Detection** 
        - ✅ **Auto Environment Variables**
        - ✅ **Multi-Attempt Git Clone**
        - ✅ **Pre-configured ngrok Token**
        - ✅ **Error Recovery & Retry**
        - ✅ **Live Health Monitoring**
        - ✅ **Auto Swagger UI Generation**
        """)
    
    with feature_col2:
        st.markdown("""
        ### 🛡️ **Reliability Features**
        - ✅ **3-Attempt Clone Strategy**
        - ✅ **Network Error Handling**
        - ✅ **Package Installation Retry**
        - ✅ **Graceful Error Messages**
        - ✅ **Auto-Recovery Mechanisms**
        - ✅ **Comprehensive Logging**
        - ✅ **Real-time Status Updates**
        - ✅ **Fallback Methods**
        """)
    
    # Colab Notebook Alternative
    st.markdown("---")
    st.markdown("## 📓 Alternative: Jupyter Notebook")
    
    if 'notebook_path' in result:
        notebook_col1, notebook_col2 = st.columns([2, 1])
        
        with notebook_col1:
            st.markdown("""
            **Prefer traditional notebook approach?**
            
            Download the complete Jupyter notebook with all cells pre-configured:
            - Individual cells for each step
            - Detailed comments and explanations
            - Step-by-step execution
            - Educational value for learning
            """)
        
        with notebook_col2:
            if os.path.exists(result['notebook_path']):
                with open(result['notebook_path'], 'rb') as f:
                    notebook_data = f.read()
                
                st.download_button(
                    label="📓 Download Notebook",
                    data=notebook_data,
                    file_name=result.get('notebook_filename', 'deployment.ipynb'),
                    mime="application/x-ipynb+json",
                    use_container_width=True
                )
    
    # Final call-to-action
    st.markdown("---")
    st.markdown("### 🎯 Ready to Deploy?")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📥 Download TXT & Deploy Now", type="primary", use_container_width=True):
            st.balloons()
            st.success("TXT file downloaded! Follow the guide above to deploy in Colab.")
    
    with action_col2:
        st.markdown("**🌐 [Open Google Colab](https://colab.research.google.com/)**")
    
    with action_col3:
        if st.button("🔄 Generate New Deployment", use_container_width=True):
            st.rerun()
    
    # Technical Details Section
    st.markdown("---")
    st.markdown("## 📊 Technical Details")
    
    with st.expander("📋 Deployment Configuration", expanded=False):
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown(f"""
            **📁 Repository Information:**
            - Owner: {result['repository_info']['owner']}
            - Repository: {result['repository_info']['repo']}
            - Language: {result['repository_info'].get('language', 'Python')}
            - Description: {result['repository_info'].get('description', 'No description')}
            
            **🐍 FastAPI Detection:**
            - App File: {result['fastapi_info']['app_file']}
            - App Variable: {result['fastapi_info']['app_variable']}
            - Detection Confidence: {result['fastapi_info']['confidence']}%
            - Total Apps Found: {result['fastapi_info']['total_apps_found']}
            """)
        
        with detail_col2:
            st.markdown(f"""
            **🔐 Environment Configuration:**
            - Variables Count: {result['environment']['vars_count']}
            - Has Sensitive Vars: {'Yes' if result['environment']['has_sensitive_vars'] else 'No'}
            - Validation Warnings: {len(result['environment']['validation_warnings'])}
            
            **📦 Dependencies:**
            - Has Custom Requirements: {'Yes' if result['requirements']['has_custom'] else 'No'}
            - Source: {result['requirements']['source']}
            - Estimated Deploy Time: {result['estimated_deployment_time']}
            """)
    
    # Show raw result for debugging
    with st.expander("🔧 Debug Information", expanded=False):
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
        - Ensure your repository is accessible (public or private with proper access)
        - Check that it contains FastAPI code
        - Verify the GitHub URL is correct
        - Repository can be public OR private (both supported)
        
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
        
        ### Network Issues:
        - Try again - temporary connectivity issues are common
        - Check your internet connection
        - Colab sometimes has temporary restrictions
        """)
    
    # Retry option
    if st.button("🔄 Try Again", type="primary"):
        st.rerun()


def display_success_response(result):
    """Legacy function - calls show_success_response for compatibility"""
    return show_success_response(result)


def display_error_response(result):
    """Legacy function - calls show_error_response for compatibility"""
    return show_error_response(result)
