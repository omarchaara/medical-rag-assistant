"""
Streamlit Frontend for Medical RAG Assistant
Placeholder for Day 1 - Basic structure
"""

import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Medical RAG Assistant",
    page_icon="🏥",
    layout="wide"
)

# API configuration
API_BASE_URL = "http://api:8000"


def main():
    """Main Streamlit application"""
    
    st.title("🏥 Medical RAG Assistant")
    st.markdown("---")
    
    # Placeholder message for Day 1
    st.info("""
    **🚧 Day 1 Status: Infrastructure Setup Complete**
    
    This interface is a placeholder. Full implementation planned for:
    - **Day 2**: Document ingestion system
    - **Day 3**: RAG retrieval pipeline  
    - **Day 4**: LLM integration & API
    - **Day 5**: Complete frontend with monitoring
    
    Current services running:
    - ✅ ChromaDB Vector Database
    - ✅ PostgreSQL Database
    - ✅ Ollama LLM Service
    - ✅ FastAPI Backend
    - ✅ MLflow Monitoring
    """)
    
    # Test API connection placeholder
    st.markdown("### 🧪 API Connection Test")
    if st.button("Test API Health"):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is healthy!")
                st.json(response.json())
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    # Placeholder for query interface
    st.markdown("### 💬 Ask a Medical Question")
    st.text_input(
        "Your question (placeholder - implementation Day 4):",
        placeholder="e.g., What are the symptoms of myocardial infarction?",
        disabled=True
    )
    st.button("Get Answer", disabled=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Medical RAG Assistant - M1 Innovation Week Project*")


if __name__ == "__main__":
    main()
