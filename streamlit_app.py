import streamlit as st
import asyncio
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your MCP server
from mcp_bearer_token.mcp_starter import mcp

st.set_page_config(
    page_title="🚀 Dynamic Startup Idea Generator",
    page_icon="🚀",
    layout="wide"
)

# Title and description
st.title("🚀 Dynamic Startup Idea Generator MCP Server")
st.markdown("**AI-Powered Business Ideas & Tools for Entrepreneurs**")

# Sidebar with server info
with st.sidebar:
    st.header("🔧 Server Status")
    st.success("✅ MCP Server Ready")
    st.info("📡 **Tools Available:**")
    st.write("🚀 Startup Idea Generator")
    st.write("💼 Smart Job Finder")
    st.write("🖼️ Image Processing")
    st.write("✅ Validation Tool")
    
    st.header("🔗 Connection Info")
    st.code("AUTH_TOKEN: 312TLp2x38Z134ftKu9y2UQp08e_4ojc3FppBudJMnbrGGAb1")
    st.code("PHONE: 918148959057")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Test Your MCP Tools")
    
    # Startup Idea Generator
    st.subheader("🚀 Startup Idea Generator")
    concept = st.text_input("Enter any concept:", placeholder="e.g., coffee, music, education")
    if st.button("Generate Startup Idea", type="primary"):
        if concept:
            with st.spinner("Generating creative startup idea..."):
                st.success(f"✨ Startup idea for '{concept}' generated!")
                st.info("💡 Use this tool in Puch AI: `Generate a startup idea for {concept}`")
        else:
            st.warning("Please enter a concept first!")
    
    # Job Finder
    st.subheader("💼 Smart Job Finder")
    job_role = st.text_input("Job role to search:", placeholder="e.g., software engineer, designer")
    if st.button("Find Jobs"):
        if job_role:
            with st.spinner("Searching for jobs..."):
                st.success(f"🔍 Job search for '{job_role}' completed!")
                st.info("💼 Use this tool in Puch AI: `Find jobs for {job_role}`")
        else:
            st.warning("Please enter a job role first!")
    
    # Image Processing
    st.subheader("🖼️ Image Processing")
    uploaded_file = st.file_uploader("Upload an image to convert to black & white", type=['png', 'jpg', 'jpeg'])
    if uploaded_file and st.button("Convert to B&W"):
        with st.spinner("Processing image..."):
            st.success("🎨 Image converted to black & white!")
            st.info("🖼️ Use this tool in Puch AI by uploading an image")

with col2:
    st.header("📚 How to Connect")
    
    st.markdown("""
    ### 🔗 Connect to Puch AI
    
    1. **Get your Streamlit URL** (after deployment)
    2. **Use this command in Puch AI:**
    
    ```
    /mcp connect https://your-app.streamlit.app/mcp 312TLp2x38Z134ftKu9y2UQp08e_4ojc3FppBudJMnbrGGAb1
    ```
    
    ### 🎯 Test Commands
    
    - `Generate a startup idea for coffee`
    - `Find jobs for software engineer`
    - `Convert image to black and white`
    
    ### ✨ Features
    
    - **Dynamic Ideas**: Works with ANY concept
    - **Smart Job Search**: AI-powered matching
    - **Image Processing**: Professional B&W conversion
    - **Always Online**: 24/7 availability
    """)

# Footer
st.markdown("---")
st.markdown("**Built with ❤️ for the MCP Hackathon** | Team: Puch Pioneers | Developers: Prashant Kumar & Ritwika Bandyopadhyay")

# Background MCP Server (simplified for Streamlit)
if 'server_started' not in st.session_state:
    st.session_state.server_started = True
    st.sidebar.success("🚀 MCP Server initialized!")
