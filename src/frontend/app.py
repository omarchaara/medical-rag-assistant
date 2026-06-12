"""
Streamlit Frontend Professionnel pour Medical RAG Assistant
Interface utilisateur avec navbar, couleurs professionnelles et affichage clair
"""

import streamlit as st
import requests
import time
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="Medical RAG Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS avec navbar et couleurs professionnelles
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #ffffff;
    }
    
    /* Navbar styles */
    .navbar {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 1.5rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Button styles */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }
    
    /* Input styles */
    .stTextInput>div>div>input {
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        font-size: 16px;
        background-color: #f9fafb;
        transition: border-color 0.3s;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6;
        background-color: white;
    }
    
    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: none;
    }
    
    /* Metric styles */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #3b82f6;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Response box */
    .response-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 6px solid #3b82f6;
        padding: 24px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
    }
    
    /* Chunk styles */
    .chunk-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: all 0.3s;
    }
    
    .chunk-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.2);
    }
    
    .chunk-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-weight: 600;
    }
    
    /* Success banner */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* Info box */
    .info-box {
        background: #f3f4f6;
        border-left: 4px solid #6b7280;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
    }
    
    /* Section headers */
    .section-header {
        color: #1e3a8a;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application with navbar and professional design"""
    
    # Navbar
    st.markdown("""
    <div class="navbar">
        <div style="text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: 700;">🏥 Medical RAG Assistant</h1>
            <p style="color: rgba(255,255,255,0.95); margin: 10px 0 0 0; font-size: 1.2em; font-weight: 500;">
                Système d'Assistance Médical IA Avancé
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with professional styling
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px; background: rgba(255,255,255,0.1); border-radius: 16px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0 0 16px 0;">📊 Statistiques Système</h3>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                
                st.metric("📄 Documents", stats.get("total_documents", 0), delta_color="normal")
                st.metric("📚 Chunks", stats.get("total_chunks", 0), delta_color="normal")
                st.metric("👥 Sessions", stats.get("active_sessions", 0), delta_color="normal")
                st.metric("🔄 Requêtes", stats.get("total_requests", 0), delta_color="normal")
            else:
                st.warning("⚠️ Statistiques non disponibles")
        except:
            st.warning("⚠️ API non connectée")
        
        st.markdown("---")
        
        st.markdown("""
        <div style="padding: 20px; background: rgba(255,255,255,0.1); border-radius: 16px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0 0 16px 0;">📚 Fonctionnalités</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        - ✅ Recherche sémantique avancée
        - ✅ Réponses médicales sourcées
        - ✅ Métriques en temps réel
        - ✅ Tracking MLflow complet
        - ✅ Interface professionnelle
        """)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="padding: 20px; background: rgba(255,255,255,0.1); border-radius: 16px;">
            <h3 style="color: white; margin: 0 0 16px 0;">🔧 Services Actifs</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        - 🟢 API FastAPI (port 8000)
        - 🟢 Streamlit UI (port 8502)
        - 🟢 Monitoring Prometheus
        - 🟢 MLflow Tracking
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="padding: 20px; background: rgba(255,255,255,0.1); border-radius: 16px;">
            <h3 style="color: white; margin: 0 0 16px 0;">🎨 À Propos</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        Assistant IA basé sur **RAG (Retrieval-Augmented Generation)** développé pour aider les professionnels de santé.
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div class="section-header">💬 Question Médicale</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_input(
            "Posez votre question médicale:",
            placeholder="Ex: Quels sont les symptômes du diabète de type 2 ?",
            key="query_input",
            label_visibility="visible"
        )
        
        col_a, col_b = st.columns([2, 1])
        with col_a:
            send_button = st.button("🔍 Rechercher", key="search_button", use_container_width=True)
        with col_b:
            clear_button = st.button("🧹 Effacer", key="clear_button", use_container_width=True)
        
        guide_button = st.button("📖 Guide", key="guide_button", use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header" style="font-size: 1.2em;">⚡ Actions</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Tester API", key="test_api", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API en ligne")
                    st.json(response.json())
                else:
                    st.error(f"❌ Status: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
        
        if st.button("📊 Métriques", key="metrics_button", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Métriques chargées")
                    with st.expander("Voir métriques brutes"):
                        st.text(response.text[:1500])
                else:
                    st.error("❌ Erreur métriques")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # Clear input
    if clear_button:
        user_query = ""
    
    # Guide
    if guide_button:
        with st.expander("📖 Guide d'utilisation"):
            st.markdown("""
            ### Comment utiliser l'assistant
            
            1. **Entrez votre question** dans la zone de texte
            2. **Cliquez sur "Rechercher"** pour traiter la requête
            3. **Visualisez les résultats** avec les chunks pertinents
            4. **Consultez les métriques** pour la performance
            
            ### Exemples de questions
            
            - Quels sont les symptômes du diabète de type 2 ?
            - Comment traiter l'hypertension artérielle ?
            - Quels sont les facteurs de risque cardiovasculaires ?
            - Quels médicaments pour le diabète ?
            - Comment diagnostiquer l'infarctus du myocarde ?
            
            ### Système
            
            - **Architecture**: RAG (Retrieval-Augmented Generation)
            - **Vector DB**: ChromaDB
            - **Embeddings**: Sentence-Transformers
            - **Monitoring**: Prometheus + Grafana
            - **Tracking**: MLflow
            """)
    
    # Query processing with clear display
    if send_button and user_query:
        with st.spinner("⏳ Traitement en cours..."):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE_URL}/api/query",
                    json={"text": user_query, "top_k": 5, "use_embeddings": True},
                    timeout=15
                )
                total_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Success banner
                    st.markdown(f"""
                    <div class="success-banner">
                        <h3 style="margin: 0 0 10px 0;">✅ Requête traitée avec succès !</h3>
                        <p style="margin: 0;">⏱️ Temps de traitement: {total_time:.2f} secondes</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Response section with clear display
                    st.markdown('<div class="section-header">📝 Réponse</div>', unsafe_allow_html=True)
                    
                    response_text = result.get('response', 'Réponse non disponible')
                    
                    # Make response text more visible
                    st.markdown(f"""
                    <div class="response-box">
                        <p style="font-size: 1.1em; line-height: 1.6; margin: 0; color: #1f2937;">
                            <strong>{response_text}</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Metrics section
                    if "metrics" in result and result["metrics"]:
                        st.markdown('<div class="section-header">📊 Performance</div>', unsafe_allow_html=True)
                        
                        metrics = result["metrics"]
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        
                        with col_m1:
                            st.metric("Embedding", f"{metrics.get('embedding_time', 0):.4f}s")
                        with col_m2:
                            st.metric("Retrieval", f"{metrics.get('retrieval_time', 0):.4f}s")
                        with col_m3:
                            st.metric("Total", f"{metrics.get('total_time', 0):.4f}s")
                        with col_m4:
                            st.metric("Documents", f"{metrics.get('documents_loaded', 0)}")
                    
                    # Chunks section with clear display
                    if "chunks" in result and result["chunks"]:
                        st.markdown(f'<div class="section-header">📚 Chunks Récupérés ({len(result["chunks"])})</div>', unsafe_allow_html=True)
                        
                        for i, chunk in enumerate(result["chunks"], 1):
                            score = chunk.get('score', 0)
                            text = chunk.get('text', 'Contenu non disponible')
                            source = chunk.get('source', 'Source inconnue')
                            
                            # Use expander with styled content
                            with st.expander(f"📄 Chunk {i} - Similarité: {score:.3f}", expanded=(i==1)):
                                st.markdown(f"""
                                <div class="chunk-card">
                                    <div class="chunk-header">
                                        📊 Score: {score:.3f} | 📄 Source: {source}
                                    </div>
                                    <p style="font-size: 1em; line-height: 1.7; margin: 16px 0; color: #374151;">
                                        {text}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Erreur API: Status {response.status_code}")
                    st.json(response.text if response.text else "Détails non disponibles")
                    
            except Exception as e:
                st.error(f"❌ Erreur de traitement: {str(e)}")
                st.markdown(f"""
                <div class="info-box">
                    <strong>Conseil:</strong> Vérifiez que l'API est démarrée sur le port 8000
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()