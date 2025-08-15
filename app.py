import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO
from rag_engine import RAGEngine

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MYTUTS - Personal Study Assistant",
    page_icon="books",
    layout="wide"
)

# Initialize RAG engine with caching
@st.cache_resource
def initialize_rag_engine():
    return RAGEngine()

# Main title and description
st.title("MYTUTS - Personal Study Assistant")
st.markdown("Transform your textbooks into an interactive AI tutor. Upload PDFs and get instant, personalized answers with source citations.")

# Initialize session state variables
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = initialize_rag_engine()

if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = 0

if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Sidebar for document management
with st.sidebar:
    st.header("Document Upload")
    
    uploaded_files = st.file_uploader(
        "Select your study materials (PDF format)",
        type="pdf",
        accept_multiple_files=True,
        help="Upload textbooks, lecture notes, or any study materials"
    )
    
    if uploaded_files:
        st.write(f"Selected files: {len(uploaded_files)}")
        
        for file in uploaded_files:
            st.write(f"• {file.name}")
        
        # Process documents button
        if st.button("Process All Documents", type="primary"):
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            successful_uploads = 0
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    status_container.text(f"Processing: {uploaded_file.name}")
                    
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Add document to knowledge base
                    document_id, chunk_count = st.session_state.rag_engine.add_document(
                        uploaded_file, uploaded_file.name
                    )
                    
                    successful_uploads += 1
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                except Exception as error:
                    st.error(f"Failed to process {uploaded_file.name}: {str(error)}")
            
            st.session_state.documents_loaded = successful_uploads
            st.session_state.processing_complete = True
            status_container.text("Document processing completed successfully")
            st.rerun()
    
    # Display document statistics
    if st.session_state.documents_loaded > 0:
        st.header("Knowledge Base Status")
        
        stats = st.session_state.rag_engine.get_document_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", stats['total_documents'])
        with col2:
            st.metric("Text Segments", stats['total_chunks'])
        
        # Document details
        with st.expander("View Loaded Documents"):
            for document in stats['documents']:
                st.write(f"**{document['filename']}**")
                st.caption(f"Text chunks: {document['chunks']} | Characters: {document.get('total_chars', 'N/A')}")

# Main content area
main_col, sidebar_col = st.columns([3, 1])

with main_col:
    st.header("Ask Questions")
    
    # Check if documents are loaded
    if st.session_state.documents_loaded == 0:
        st.info("Please upload and process your study materials to begin asking questions.")
        st.markdown("""
        **Getting Started:**
        1. Upload PDF files using the sidebar
        2. Click "Process All Documents"  
        3. Ask questions about your materials
        4. Get personalized explanations with citations
        """)
    else:
        # Question input section
        user_question = st.text_input(
            "Enter your question:",
            placeholder="What would you like to understand better?",
            help="Ask specific questions about concepts, definitions, processes, or request summaries"
        )
        
        # Learning level selection
        explanation_level = st.selectbox(
            "Select explanation complexity:",
            ["Beginner - Simple explanations with analogies", 
             "Advanced - Technical details and comprehensive coverage"],
            help="Choose how detailed you want the explanation to be"
        )
        
        # Generate answer button
        col_btn, col_space = st.columns([1, 2])
        with col_btn:
            generate_answer = st.button("Generate Answer", type="primary")
        
        # Process the question
        if generate_answer and user_question:
            with st.spinner("Analyzing documents and generating response..."):
                try:
                    # Get answer from RAG system
                    answer_result = st.session_state.rag_engine.generate_answer(
                        user_question, explanation_level
                    )
                    
                    # Display the generated answer
                    st.markdown("---")
                    st.subheader("Answer")
                    st.markdown(answer_result['answer'])
                    
                    # Display source information
                    if answer_result['sources']:
                        st.markdown("---")
                        st.subheader("Source References")
                        
                        for idx, source in enumerate(answer_result['sources'], 1):
                            relevance_score = int(source['confidence'] * 100)
                            st.write(f"**{idx}.** {source['filename']} (Relevance: {relevance_score}%)")
                    
                    # Additional information
                    st.caption(f"Answer generated from {answer_result['context_used']} relevant text sections")
                    
                except Exception as error:
                    st.error(f"An error occurred while generating the answer: {str(error)}")
                    st.info("Please try rephrasing your question or check that your documents were processed correctly.")
        
        elif generate_answer and not user_question:
            st.warning("Please enter a question before generating an answer.")

with sidebar_col:
    st.header("System Features")
    
    # Feature status indicators
    feature_list = [
        ("PDF Document Processing", st.session_state.documents_loaded > 0),
        ("Question Answering", st.session_state.documents_loaded > 0),
        ("Adaptive Explanations", True),
        ("Source Citations", True),
        ("Multi-Document Search", st.session_state.documents_loaded > 1)
    ]
    
    for feature_name, is_active in feature_list:
        status_icon = "✓" if is_active else "○"
        st.write(f"{status_icon} {feature_name}")
    
    st.markdown("---")
    
    # Usage tips
    st.subheader("Usage Tips")
    st.markdown("""
    **For Better Results:**
    - Ask specific, focused questions
    - Upload relevant course materials
    - Try both beginner and advanced modes
    - Use follow-up questions for clarity
    
    **Question Examples:**
    - "Explain the main concept in chapter 3"
    - "What are the key formulas for this topic?"
    - "Summarize the important points"
    - "How does this process work?"
    """)
    
    # Quick question suggestions
    if st.session_state.documents_loaded > 0:
        st.subheader("Quick Questions")
        
        sample_questions = [
            "What are the main topics covered?",
            "Explain this concept simply",
            "What are the key formulas?",
            "Give me a summary",
            "What are practical applications?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"quick_{hash(question)}", use_container_width=True):
                # This would ideally populate the question input field
                st.session_state.suggested_question = question

# Footer section
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>MYTUTS Personal Study Assistant</p>
    <p>Powered by Claude AI, ChromaDB, and Streamlit</p>
    <p><em>Making your textbooks interactive and accessible</em></p>
</div>
""", unsafe_allow_html=True)