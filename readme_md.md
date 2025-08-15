# MYTUTS - Personal Study Assistant

An AI-powered study companion that transforms static textbooks into interactive learning experiences. Upload your PDFs and get instant, personalized explanations with source citations.

## What It Does

Ever wished your textbooks could answer questions? MYTUTS makes that happen. Students can upload their course materials and ask questions in plain English, getting explanations tailored to their learning level.

The system analyzes uploaded documents, breaks them into searchable chunks, and uses AI to provide contextual answers with proper citations. Whether you need simple analogies or technical deep-dives, MYTUTS adapts to your learning style.

## Key Features

- **Smart Document Processing**: Uploads and analyzes PDF textbooks automatically
- **Adaptive Learning**: Switches between beginner-friendly explanations and advanced technical details
- **Source Citations**: Every answer includes references to specific parts of your materials
- **Quiz Generation**: Creates practice questions from your uploaded content
- **Multi-Document Support**: Search across multiple textbooks and materials simultaneously

## How It Works

1. **Upload**: Drop your PDF textbooks into the system
2. **Process**: The system breaks documents into searchable chunks
3. **Ask**: Type questions in natural language
4. **Learn**: Get personalized explanations with source references

## Technical Overview

MYTUTS uses Retrieval-Augmented Generation (RAG) to combine document search with AI generation. The system processes uploaded PDFs, creates a searchable knowledge base, and uses Google's Gemini AI to generate contextual responses.

**Core Technologies:**
- **Frontend**: Streamlit for the web interface
- **Document Processing**: PyPDF2 for text extraction
- **AI Integration**: Google AI Studio (Gemini 1.5 Flash)
- **Search**: Custom keyword matching with similarity scoring
- **Deployment**: Streamlit Cloud

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google AI Studio API key (free)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Lokesh2911/Prompt-Eng---MyTuts---Ai-Tutor.git
cd Prompt-Eng---MyTuts---Ai-Tutor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Get a free API key from [Google AI Studio](https://aistudio.google.com/)
   - Create a `.env` file in the project root
   - Add your key: `GOOGLE_AI_API_KEY=your_api_key_here`

4. Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Usage Guide

**Basic Workflow:**
1. Use the sidebar to upload PDF documents
2. Click "Process All Documents" to analyze your materials
3. Enter questions in the main interface
4. Choose your preferred explanation level (Beginner/Advanced)
5. Click "Generate Answer" to get personalized responses

**Question Examples:**
- "What is Newton's first law?"
- "Explain photosynthesis in simple terms"
- "Create a quiz on momentum"
- "What are the main concepts in chapter 3?"

## Project Structure

```
mytuts-ai-tutor/
├── app.py                    # Main Streamlit application
├── rag_engine.py            # RAG implementation with Google AI
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not in git)
├── docs/                    # Documentation files
├── examples/                # Example outputs and screenshots
└── tests/                   # Test scripts
```

## Example Outputs

The system generates comprehensive responses for various question types:

- **Concept Explanations**: Detailed breakdowns of physics principles
- **Quiz Generation**: Multiple choice, true/false, and short answer questions
- **Document Analysis**: Overview of textbook structure and key topics
- **Adaptive Responses**: Same concept explained at different complexity levels

## Testing

Run basic tests to verify functionality:

```bash
python tests/test_basic_functionality.py
```

Tests cover:
- PDF text extraction
- Document chunking
- Search functionality
- API integration
- Error handling

## Performance

**Processing Capabilities:**
- Large documents: Successfully processed 40MB+ physics textbook
- Text extraction: 1.5M+ characters processed efficiently
- Chunking: Created 2,196 searchable text segments
- Response time: Typically 3-5 seconds for complex questions

## Known Issues

- Very large PDFs (>100MB) may take longer to process
- Scanned PDFs without OCR won't extract text properly
- Mathematical equations in images aren't processed
- Search accuracy depends on keyword overlap

## Future Improvements

- Integration with vector embeddings for better semantic search
- Support for additional document formats (Word, PowerPoint)
- Advanced quiz formats with images and diagrams
- Study progress tracking and personalized recommendations
- Multi-language support for international textbooks

## Contributing

This project was developed as part of a Generative AI course assignment. Feel free to fork and extend the functionality.

## License

MIT License - see LICENSE file for details

## Contact

Lokesh Kumar Thodkar - thodkar.l@northeastern.edu

Project Link: [https://github.com/Lokesh2911/Prompt-Eng---MyTuts---Ai-Tutor](https://github.com/Lokesh2911/Prompt-Eng---MyTuts---Ai-Tutor)