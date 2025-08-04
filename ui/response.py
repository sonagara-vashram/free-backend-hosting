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
        ("🔍", "Repository\nValidated"),
        ("🐍", "FastAPI App\nDetected"),
        ("📦", "Dependencies\nResolved"),
        ("🔐", "Environment\nConfigured"),
        ("📓", "Notebook\nGenerated")
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
    
    # Create two-column layout for deployment
    deploy_col1, deploy_col2 = st.columns([1, 1])
    
    with deploy_col1:
        st.markdown("### 📥 Step 1: Download Notebook")
        
        if os.path.exists(result['notebook_path']):
            # Enhanced download section
            with open(result['notebook_path'], 'rb') as f:
                notebook_data = f.read()
            
            st.download_button(
                label="📥 Download Deployment Notebook",
                data=notebook_data,
                file_name=f"fastapi_deploy_{result['deployment_id']}.ipynb",
                mime="application/json",
                type="primary",
                use_container_width=True,
                help="Download the auto-configured notebook for your FastAPI deployment"
            )
            
            st.success("✅ Notebook ready for download!")
            st.info(f"📊 File size: {len(notebook_data) // 1024} KB")
        else:
            st.error("❌ Notebook file not found. Please try again.")
    
    with deploy_col2:
        st.markdown("### 🌐 Step 2: Open Google Colab")
        
        # Enhanced Colab section
        colab_button_clicked = st.button(
            "🚀 Open Google Colab",
            type="secondary",
            use_container_width=True,
            help="Opens Google Colab in a new tab"
        )
        
        if colab_button_clicked:
            st.markdown("""
            <script>
            window.open('https://colab.research.google.com', '_blank');
            </script>
            """, unsafe_allow_html=True)
            st.success("✅ Google Colab opened! Upload your notebook there.")
        
        st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin-top: 10px;">
            <strong>🔗 Direct Link:</strong><br>
            <a href="https://colab.research.google.com" target="_blank">
                colab.research.google.com
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed step-by-step instructions
    st.markdown("---")
    st.markdown("## 📋 Detailed Deployment Instructions")
    
    # Create tabs for different instruction formats
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Quick Steps", "⚡ One-Click Deploy", "📝 Detailed Guide", "🎥 Video Guide"])
    
    with tab1:
        st.markdown("""
        ### ⚡ Quick Deployment (2-3 minutes)
        
        1. **📥 Download** the notebook using the button above
        2. **🌐 Open** Google Colab (colab.research.google.com)
        3. **📁 Upload** the notebook file (File → Upload notebook)
        4. **▶️ Run All** cells (Runtime → Run all)
        5. **🔗 Copy** your public API URL from the output
        6. **✅ Use** the URL in your applications!
        
        **⏱️ Total Time:** 2-3 minutes  
        **💰 Cost:** Completely Free  
        **🌐 Access:** Global Public URL
        """)
    
    with tab2:
        st.markdown("### ⚡ One-Click Deploy (Fastest Method)")
        st.markdown("**Copy the code below and paste it into a single Google Colab cell, then run it!**")
        
        # Single cell deployment
        if 'single_cell_code' in result:
            # Open Google Colab button
            colab_col1, colab_col2 = st.columns([1, 1])
            
            with colab_col1:
                if st.button("🚀 Open Google Colab", type="primary", use_container_width=True):
                    st.markdown("🌐 **Opening Google Colab...**")
                    st.markdown("[👆 Click here if it didn't open automatically](https://colab.research.google.com/)")
                    # Try to open in new tab using JavaScript
                    st.markdown("""
                    <script>
                    window.open('https://colab.research.google.com/', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
            
            with colab_col2:
                st.info("💡 **Instructions:**\n1. Open Google Colab (button above)\n2. Create new notebook\n3. Copy code below\n4. Paste and run!")
            
            # Code display with copy button
            st.markdown("#### 📋 Copy This Code:")
            
            # Enhanced code display
            code_container = st.container()
            with code_container:
                st.code(result['single_cell_code'], language='python')
                
                # Copy helper text
                st.markdown("""
                **💡 How to use:**
                1. **Select All** the code above (Ctrl+A or Cmd+A)
                2. **Copy** (Ctrl+C or Cmd+C)  
                3. **Open Google Colab** and create a new notebook
                4. **Paste** into a code cell (Ctrl+V or Cmd+V)
                5. **Run the cell** (Shift+Enter)
                6. **Wait 2-3 minutes** for your API to be live!
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
            **🎉 Everything is automated!**
            - Package installation ✅
            - Repository cloning ✅  
            - Environment setup ✅
            - FastAPI server start ✅
            - Public URL creation ✅
            - API testing ✅
            """)
        else:
            st.error("Single cell code not available. Please try regenerating the deployment.")
    
    with tab3:
        st.markdown("""
        ### 📝 Step-by-Step Detailed Guide
        
        #### 🎯 **STEP 1: Download Notebook**
        - Click the "📥 Download Deployment Notebook" button above
        - Save the `.ipynb` file to your computer
        - Remember the download location
        
        #### 🌐 **STEP 2: Open Google Colab**
        - Go to [colab.research.google.com](https://colab.research.google.com)
        - Sign in with your Google account (free)
        - You'll see the Colab homepage
        
        #### 📁 **STEP 3: Upload Notebook**
        - Click **"File"** in the top menu
        - Select **"Upload notebook"**
        - Choose the downloaded `.ipynb` file
        - Wait for upload to complete
        
        #### ⚙️ **STEP 4: Configure ngrok (Optional)**
        - For unlimited sessions, get free ngrok auth token:
          1. Go to [ngrok.com](https://ngrok.com) and sign up (free)
          2. Copy your auth token from dashboard
          3. In Colab: click 🔑 (secrets) in left sidebar
          4. Add secret: Name = `NGROK_AUTH_TOKEN`, Value = your token
        
        #### ▶️ **STEP 5: Run Deployment**
        - Click **"Runtime"** in the top menu
        - Select **"Run all"** 
        - Watch the automatic deployment process
        - Each cell will execute in sequence
        
        #### 🔗 **STEP 6: Get Your API URL**
        - Wait for all cells to complete (2-3 minutes)
        - Look for the "🎉 DEPLOYMENT SUCCESSFUL!" message
        - Copy the **Public API URL** 
        - Test it by clicking the Swagger UI link
        
        #### 🚀 **STEP 7: Use Your API**
        - Your API is now live and globally accessible
        - Use the URL in your frontend applications
        - Access API documentation at `your-url/docs`
        - Keep the Colab tab open to maintain the API
        """)
    
    with tab4:
        st.markdown("""
        ### 🎥 Video Instructions
        
        **🎬 Complete Deployment Walkthrough:**
        
        1. **Watch this process in action:**
           - Download notebook ✅
           - Upload to Colab ✅  
           - Run all cells ✅
           - Get public URL ✅
        
        2. **Key Points to Remember:**
           - Keep Colab tab open for API uptime
           - Sessions last 8-12 hours automatically
           - Get ngrok token for unlimited usage
           - Test API with Swagger UI
        
        3. **Common Mistakes to Avoid:**
           - Don't close Colab tab while using API
           - Ensure all cells complete before copying URL
           - Check for any error messages in output
        
        **📱 Mobile Friendly:** This works on phones and tablets too!
        """)
    
    # Important notes and tips
    st.markdown("---")
    st.markdown("## 💡 Important Notes & Tips")
    
    note_col1, note_col2 = st.columns(2)
    
    with note_col1:
        st.markdown("""
        ### ✅ **What You Get:**
        - 🌐 **Public HTTPS URL** (globally accessible)
        - 📚 **Automatic Swagger UI** (API documentation)
        - 📋 **ReDoc documentation** (alternative docs)
        - 🔒 **CORS enabled** (frontend integration ready)
        - 💓 **Health monitoring** (automatic checks)
        - 🔄 **Auto-restart** (if session timeouts)
        """)
    
    with note_col2:
        st.markdown("""
        ### ⚠️ **Keep in Mind:**
        - 🕐 **Session Duration:** 8-12 hours continuous
        - 🔄 **Auto-Restart:** Available for reconnection
        - 💰 **Cost:** Completely free with Google Colab
        - 📱 **Access:** Works on all devices
        - 🌍 **Global:** Accessible from anywhere
        - 🛡️ **Security:** HTTPS encryption included
        """)
    
    # Ngrok setup guide
    with st.expander("🔧 Optional: Setup Unlimited ngrok Sessions"):
        st.markdown("""
        ### 🚀 Get Unlimited ngrok Sessions (Free)
        
        **Why do this?**
        - 🔄 Unlimited tunnel sessions
        - 🎯 Custom subdomain options
        - 📊 Better performance
        - 📈 Usage analytics
        
        **How to setup:**
        1. 🌐 Go to [ngrok.com](https://ngrok.com) and create free account
        2. 📋 Copy your auth token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
        3. 🔑 In Google Colab, click the 🔑 (secrets) icon in left sidebar
        4. ➕ Add new secret:
           - **Name:** `NGROK_AUTH_TOKEN`
           - **Value:** paste your auth token
        5. ✅ The notebook will automatically use it!
        
        **📱 Pro Tip:** The notebook works fine without this too, but auth token gives you unlimited usage!
        """)
    
    # Troubleshooting section
    show_enhanced_troubleshooting()
    
    # Success metrics
    st.markdown("---")
    st.markdown("## 📊 Deployment Package Details")
    
    with st.expander("📋 Technical Details", expanded=False):
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
            **� Environment Configuration:**
            - Variables Count: {result['environment']['vars_count']}
            - Has Sensitive Vars: {'Yes' if result['environment']['has_sensitive_vars'] else 'No'}
            - Validation Warnings: {len(result['environment']['validation_warnings'])}
            
            **📦 Dependencies:**
            - Has Custom Requirements: {'Yes' if result['requirements']['has_custom'] else 'No'}
            - Source: {result['requirements']['source']}
            - Estimated Deploy Time: {result['estimated_deployment_time']}
            """)
        
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


# Legacy functions for compatibility
def handle_dict_response(result):
    show_response(result)

def handle_string_response(result):
    st.info(result)
    """Handle dictionary responses from enhanced deployment"""
    
    status = result.get("status", "unknown")
    message = result.get("message", "No message provided")
    
    if status == "api_ready":
        # Live API is ready - Render-style deployment complete!
        show_api_ready_response(result)
        
    elif status == "auto_deploy_ready":
        # Enhanced notebook created - will auto-deploy when opened
        show_auto_deploy_ready_response(result)
        
    elif status == "notebook_ready":
        # Standard notebook created - user needs to run manually
        show_notebook_ready_response(result)
        
    elif status == "manual_upload":
        # Notebook created but needs manual upload
        show_manual_upload_response(result)
        
    elif status == "error":
        # Error occurred
        show_error_response(result)
        
    else:
        st.warning(f"⚠️ Unknown status: {status}")
        st.info(message)

def show_api_ready_response(result):
    """Show response for live API deployment (Render-style)"""
    
    api_url = result.get("api_url", "")
    swagger_url = result.get("swagger_url", f"{api_url}/docs")
    redoc_url = result.get("redoc_url", f"{api_url}/redoc")
    
    st.success("🎉 **YOUR BACKEND IS LIVE!**")
    st.balloons()
    
    # Main API info
    st.markdown("### 🚀 **Live API URL**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.code(api_url, language="text")
        st.markdown(f"**📚 Swagger UI:** [Open Documentation]({swagger_url})")
        st.markdown(f"**📋 ReDoc:** [Alternative Docs]({redoc_url})")
    
    with col2:
        if st.button("📋 **COPY URL**", type="primary", use_container_width=True):
            st.success("URL copied!")
            
        if st.button("📚 **OPEN DOCS**", use_container_width=True):
            webbrowser.open(swagger_url)
            st.success("✅ Documentation opened!")
    
    # API metrics
    st.markdown("---")
    st.markdown("### 📊 **API Status**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚀 Status", "LIVE", "✅ Active")
    with col2:
        st.metric("⏰ Session Time", "8-12 hours", "🔄 Active")
    with col3:
        st.metric("🌐 Access", "Global", "🌍 Public")
    
    # Quick test section
    show_api_testing_section(api_url)
    
    # Integration guide
    show_integration_guide(api_url)
    
    # Important notes
    st.markdown("---")
    st.info("""
    **⚠️ Important Notes:**
    - Your API is live and accessible worldwide
    - Keep the Colab session running to maintain uptime
    - Session will auto-restart if it times out
    - Perfect for development, testing, and demos
    """)

def show_auto_deploy_ready_response(result):
    """Show response for auto-deployment notebook"""
    
    notebook_url = result.get("notebook_url", "")
    message = result.get("message", "")
    
    st.success("🚀 **Auto-Deploy Notebook Ready!**")
    st.info(message)
    
    st.markdown("### 📝 **Enhanced Colab Notebook**")
    
    # Big prominent button for Colab
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **OPEN & AUTO-DEPLOY IN COLAB**", type="primary", use_container_width=True):
            webbrowser.open(notebook_url)
            st.success("✅ Colab notebook opened!")
    
    st.markdown("---")
    
    # Instructions
    st.markdown("### 📋 **Automatic Deployment Process**")
    
    step_col1, step_col2 = st.columns(2)
    
    with step_col1:
        st.markdown("""
        **🎯 What happens next:**
        1. 📝 Notebook opens in Google Colab
        2. 🔄 Click "Run all" to start deployment
        3. ⚙️ Automatic setup (2-3 minutes)
        4. 🌐 Live API URL appears
        5. ✅ Ready to use in your apps!
        """)
    
    with step_col2:
        st.markdown("""
        **⚡ Features included:**
        - 🚀 Instant deployment
        - 📚 Auto-generated Swagger UI  
        - 🌐 Public ngrok tunnel
        - 💓 Health monitoring
        - 🔄 Auto-restart on errors
        """)
    
    # Colab info
    with st.expander("📖 **About Google Colab**"):
        st.markdown("""
        **Google Colab** is a free cloud platform that runs your code:
        
        - ✅ **No signup required** (uses your Google account)
        - ✅ **Free GPU/CPU resources** for 8-12 hours
        - ✅ **Auto-saves your work** in Google Drive
        - ✅ **Perfect for backends** and API hosting
        - ✅ **Global accessibility** via ngrok tunnels
        
        **📱 Mobile friendly:** Works on phones and tablets too!
        """)
    
    st.markdown("---")
    st.warning("""
    **📋 Next Steps:**
    1. Click the "Open & Auto-Deploy" button above
    2. In Colab: Click Runtime → Run all
    3. Wait 2-3 minutes for your live API URL
    4. Use the URL in your frontend applications
    """)

def show_notebook_ready_response(result):
    """Show response for standard notebook deployment"""
    
    notebook_url = result.get("notebook_url", "")
    message = result.get("message", "")
    
    st.success("📝 **Colab Notebook Created!**")
    st.info(message)
    
    # Colab button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 **OPEN COLAB NOTEBOOK**", type="primary", use_container_width=True):
            webbrowser.open(notebook_url)
            st.success("✅ Colab opened!")
    
    # Instructions
    st.markdown("### 📋 **Deployment Instructions**")
    st.markdown("""
    **Steps to deploy your backend:**
    
    1. 📝 **Open the notebook** in Google Colab (button above)
    2. 🔄 **Click "Runtime → Run all"** to execute all cells
    3. ⏳ **Wait 2-3 minutes** for deployment to complete
    4. 🌐 **Copy the API URL** that appears at the end
    5. ✅ **Use the URL** in your frontend applications
    """)
    
    show_troubleshooting_tips()

def show_manual_upload_response(result):
    """Show response for manual upload requirement"""
    
    notebook_path = result.get("notebook_path", "")
    message = result.get("message", "")
    
    st.warning("📤 **Manual Upload Required**")
    st.info(message)
    
    st.markdown("### 📁 **Download & Upload Instructions**")
    
    # Download button
    if notebook_path and os.path.exists(notebook_path):
        with open(notebook_path, 'rb') as file:
            st.download_button(
                label="📥 **Download Notebook**",
                data=file.read(),
                file_name="deploy_backend.ipynb",
                mime="application/x-ipynb+json",
                type="primary",
                use_container_width=True
            )
    
    # Upload instructions
    st.markdown("### 📋 **Upload to Google Colab**")
    st.markdown("""
    **Follow these steps:**
    
    1. 📥 **Download the notebook** (button above)
    2. 🌐 **Go to [Google Colab](https://colab.research.google.com/)**
    3. 📁 **Click "Upload"** and select the downloaded notebook
    4. 🔄 **Click "Runtime → Run all"** to deploy
    5. 🌐 **Get your live API URL** in 2-3 minutes
    """)
    
    # Quick link to Colab
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌐 **OPEN GOOGLE COLAB**", use_container_width=True):
            webbrowser.open("https://colab.research.google.com/")
            st.success("✅ Colab opened in new tab!")

def show_error_response(result):
    """Show error response with helpful guidance"""
    
    message = result.get("message", "Unknown error occurred")
    
    st.error("❌ **Deployment Failed**")
    st.error(message)
    
    # Common solutions
    st.markdown("### 🔧 **Troubleshooting**")
    
    with st.expander("💡 **Common Solutions**", expanded=True):
        st.markdown("""
        **Check your repository:**
        - ✅ Contains `main.py`, `app.py`, or `server.py`
        - ✅ Has a FastAPI/Flask app instance (e.g., `app = FastAPI()`)
        - ✅ Requirements.txt includes all dependencies
        - ✅ Repository is public on GitHub
        
        **Try these fixes:**
        - 🔄 Check the GitHub URL format
        - 📦 Verify your requirements.txt
        - 🔍 Ensure your app has proper entry point
        - ⏳ Try again (sometimes GitHub is temporarily unavailable)
        """)
    
    # Support links
    st.markdown("### 🆘 **Need Help?**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📖 **View Documentation**", use_container_width=True):
            st.info("Check the troubleshooting guide in the sidebar")
    
    with col2:
        if st.button("🔄 **Try Again**", use_container_width=True):
            st.experimental_rerun()

def handle_string_response(result):
    """Handle legacy string responses"""
    
    if result.startswith("api_ready:"):
        # Extract API URL from string
        parts = result.split(":")
        api_url = parts[1] if len(parts) > 1 else ""
        
        # Convert to dict format and handle
        dict_result = {
            "status": "api_ready",
            "api_url": api_url,
            "swagger_url": f"{api_url}/docs",
            "message": "🎉 API deployed successfully!"
        }
        handle_dict_response(dict_result)
        
    elif result.startswith("auto_deploy_ready:"):
        # Auto-deploy notebook ready
        parts = result.split(":")
        notebook_url = parts[1] if len(parts) > 1 else ""
        
        dict_result = {
            "status": "auto_deploy_ready",
            "notebook_url": notebook_url,
            "message": "🚀 Auto-deployment notebook ready!"
        }
        handle_dict_response(dict_result)
        
    elif result.startswith("manual_upload:"):
        # Manual upload required
        parts = result.split(":")
        notebook_path = parts[1] if len(parts) > 1 else ""
        
        dict_result = {
            "status": "manual_upload",
            "notebook_path": notebook_path,
            "message": "📤 Manual upload required"
        }
        handle_dict_response(dict_result)
        
    elif result.startswith("https://colab.research.google.com"):
        # Direct Colab URL
        dict_result = {
            "status": "notebook_ready",
            "notebook_url": result,
            "message": "📝 Colab notebook created successfully!"
        }
        handle_dict_response(dict_result)
        
    else:
        # Legacy or unknown string response
        st.info(f"📝 Response: {result}")
        
        if "colab" in result.lower():
            st.markdown("### 📝 **Colab Notebook**")
            if st.button("🌐 **Open Colab**", type="primary"):
                webbrowser.open("https://colab.research.google.com/")

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

def show_troubleshooting_tips():
    """Show troubleshooting tips"""
    
    with st.expander("🔧 **Troubleshooting Tips**"):
        st.markdown("""
        **If deployment fails:**
        
        **🔍 Check Repository Structure:**
        - Ensure `main.py` or `app.py` exists
        - Verify FastAPI/Flask app instance: `app = FastAPI()`
        - Check that all imports are correct
        
        **📦 Requirements Issues:**
        - Include all necessary packages in requirements.txt
        - Add version numbers for stability: `fastapi==0.104.1`
        - Common packages needed: `fastapi`, `uvicorn`, `python-dotenv`
        
        **🔄 Colab Issues:**
        - If cells fail, try running them individually
        - Restart runtime if needed: Runtime → Restart runtime
        - Check for error messages in the output
        
        **🌐 ngrok Issues:**
        - If tunnel fails, re-run the deployment cell
        - ngrok URLs change each time you restart
        - Free tier has some limitations but works great for development
        """)

def show_deployment_success_animation():
    """Show success animation and celebration"""
    
    st.balloons()
    
    # Success message with animation
    success_html = """
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #4CAF50; font-size: 3em; animation: bounce 1s;">🎉</h1>
        <h2 style="color: #2E7D32;">Deployment Successful!</h2>
        <p style="color: #666; font-size: 1.2em;">Your backend is now live and ready to use!</p>
    </div>
    
    <style>
    @keyframes bounce {
        0%, 20%, 60%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-20px);
        }
        80% {
            transform: translateY(-10px);
        }
    }
    </style>
    """
    
    st.markdown(success_html, unsafe_allow_html=True)

def show_enhanced_troubleshooting():
    """Enhanced troubleshooting section"""
    
    with st.expander("🔧 Troubleshooting & Common Issues"):
        trouble_tab1, trouble_tab2, trouble_tab3 = st.tabs(["🚨 Common Errors", "💡 Quick Fixes", "🆘 Support"])
        
        with trouble_tab1:
            st.markdown("""
            ### 🚨 Most Common Issues & Solutions
            
            **❌ "Notebook upload failed"**
            - ✅ Ensure file ends with `.ipynb`
            - ✅ File size should be under 25MB
            - ✅ Try refreshing Colab and uploading again
            
            **❌ "FastAPI app not starting"**
            - ✅ Check your `main.py` or `app.py` has `app = FastAPI()`
            - ✅ Verify all imports are correct
            - ✅ Ensure requirements.txt includes all dependencies
            
            **❌ "ngrok tunnel failed"**
            - ✅ Wait for FastAPI server to start completely (30-60 seconds)
            - ✅ Try running the ngrok cell again
            - ✅ Add ngrok auth token for unlimited usage
            
            **❌ "API not responding"**
            - ✅ Ensure port 8000 is not blocked
            - ✅ Check FastAPI app is running in previous cells
            - ✅ Wait 2-3 minutes for complete deployment
            
            **❌ "Environment variables not working"**
            - ✅ Check .env format: `KEY=value` (no spaces around =)
            - ✅ Use quotes for values with spaces: `KEY="value with spaces"`
            - ✅ Verify variables are set in environment cell output
            """)
        
        with trouble_tab2:
            st.markdown("""
            ### 💡 Quick Fix Commands
            
            **🔄 Restart Everything:**
            ```
            Runtime → Restart and run all
            ```
            
            **🧹 Clear Output:**
            ```
            Edit → Clear all outputs
            ```
            
            **📊 Check FastAPI Status:**
            ```python
            import requests
            response = requests.get("http://localhost:8000/")
            print(response.status_code)
            ```
            
            **🔍 Debug ngrok:**
            ```python
            from pyngrok import ngrok
            tunnels = ngrok.get_tunnels()
            print(tunnels)
            ```
            
            **🔐 Verify Environment Variables:**
            ```python
            import os
            for key, value in os.environ.items():
                if not key.startswith('_'):
                    print(f"{key}: {'*' * len(value)}")
            ```
            """)
        
        with trouble_tab3:
            st.markdown("""
            ### 🆘 Need More Help?
            
            **📖 Documentation:**
            - [FastAPI Documentation](https://fastapi.tiangolo.com/)
            - [Google Colab Guide](https://colab.research.google.com/notebooks/intro.ipynb)
            - [ngrok Documentation](https://ngrok.com/docs)
            
            **🎥 Video Tutorials:**
            - FastAPI Deployment Basics
            - Google Colab for Beginners
            - ngrok Setup and Usage
            
            **💬 Community Support:**
            - Stack Overflow (tag: fastapi, google-colab)
            - GitHub Issues
            - FastAPI Discord Community
            
            **🐛 Report Issues:**
            If you found a bug in our deployment system, please report it with:
            - Your repository URL
            - Error message screenshot
            - Steps to reproduce
            """)
