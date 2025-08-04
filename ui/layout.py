import streamlit as st
from ui.styles import apply_custom_css
import os

def main_layout():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .stats-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .deployment-flow {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with gradient
    st.markdown('<h1 class="main-header">🚀 Free Python Backend Hosting</h1>', unsafe_allow_html=True)
    
    # Logo (only if exists)
    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(logo_path, width=150)
    
    # Enhanced subtitle
    st.markdown(
        '<p class="subtitle">Deploy your FastAPI/Flask backend to Google Colab in minutes - completely free with live public URLs!</p>', 
        unsafe_allow_html=True
    )
    
    # Key stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🆓 Cost", "Free", "Always")
    with col2:
        st.metric("⚡ Deploy Time", "2 min", "avg")
    with col3:
        st.metric("🌐 Global Access", "Yes", "ngrok tunnel")
    with col4:
        st.metric("📚 Swagger UI", "Included", "auto-generated")
    
    # Enhanced deployment flow
    st.markdown("""
    <div class="deployment-flow">
        <h3>🔄 How It Works:</h3>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="text-align: center; margin: 0.5rem;">
                <div style="font-size: 2rem;">📤</div>
                <div>Upload Repo</div>
            </div>
            <div style="font-size: 1.5rem;">→</div>
            <div style="text-align: center; margin: 0.5rem;">
                <div style="font-size: 2rem;">⚙️</div>
                <div>Auto Configure</div>
            </div>
            <div style="font-size: 1.5rem;">→</div>
            <div style="text-align: center; margin: 0.5rem;">
                <div style="font-size: 2rem;">📓</div>
                <div>Generate Colab</div>
            </div>
            <div style="font-size: 1.5rem;">→</div>
            <div style="text-align: center; margin: 0.5rem;">
                <div style="font-size: 2rem;">🚀</div>
                <div>Live Deployment</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced features overview
    st.markdown("### ✨ Platform Features:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🆓</div>
            <h4>Completely Free</h4>
            <ul>
                <li>No credit card required</li>
                <li>Uses Google Colab infrastructure</li>
                <li>Zero setup costs</li>
                <li>No hidden fees</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">⚡</div>
            <h4>Real Deployment</h4>
            <ul>
                <li>Creates actual Google Colab notebook</li>
                <li>One-click deployment in Colab</li>
                <li>FastAPI with full Swagger UI</li>
                <li>Smart app detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔗</div>
            <h4>Live API URLs</h4>
            <ul>
                <li>Real ngrok tunnel via Colab</li>
                <li>Global accessibility</li>
                <li>CORS enabled</li>
                <li>SSL secured (HTTPS)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # What's supported
    st.markdown("""
    <div class="stats-container">
        <h4>🎯 What's Supported:</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div><strong>🐍 Frameworks:</strong> FastAPI, Flask</div>
            <div><strong>📦 Dependencies:</strong> Any pip package</div>
            <div><strong>🔐 Environment:</strong> .env files supported</div>
            <div><strong>🌐 Endpoints:</strong> All HTTP methods</div>
            <div><strong>📊 Features:</strong> CORS, JSON, WebSockets</div>
            <div><strong>📚 Documentation:</strong> Auto Swagger UI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Important notice with better styling
    st.info("⚡ **Real Deployment:** This tool creates a Google Colab notebook that actually deploys your backend with Swagger UI and provides a live public API URL that works worldwide!")
    
    # Success stories / testimonials (placeholder)
    with st.expander("🌟 Success Stories & Use Cases"):
        st.markdown("""
        **Perfect for:**
        - 🎓 **Students**: Deploy class projects instantly
        - 👨‍💻 **Developers**: Test APIs quickly  
        - 🏢 **Startups**: MVP development
        - 📚 **Learning**: Practice deployment skills
        - 🎯 **Demos**: Show your work to clients
        - 🔬 **Research**: Share academic APIs
        
        **Real Usage Examples:**
        - REST APIs for mobile apps
        - Data processing endpoints
        - Machine learning model servers
        - Webhook receivers
        - Microservices prototypes
        """)
    
    st.markdown("---")
    apply_custom_css()
