# MYTUTS System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   STUDENT       │───▶│   STREAMLIT UI   │───▶│   RAG ENGINE    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │                 │
                                │               │ DOCUMENT        │
                                │               │ PROCESSING      │
                                │               │                 │
                                │               └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │                 │
                                │               │ KNOWLEDGE BASE  │
                                │               │ (In-Memory)     │
                                │               │                 │
                                │               └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │                 │
                                │               │ SEARCH &        │
                                │               │ RETRIEVAL       │
                                │               │                 │
                                │               └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │                 │
                                └──────────────▶│ GOOGLE AI API   │
                                                │ (Gemini 1.5)    │
                                                │                 │
                                                └─────────────────┘
```

## Data Flow Process:

**1. Document Upload:**
```
PDF File → PyPDF2 → Text Extraction → Text Cleaning → Chunk Generation → Storage
```

**2. Question Processing:**
```
User Query → Keyword Analysis → Document Search → Context Assembly → AI Prompt → Response
```

**3. Response Generation:**
```
Retrieved Context + User Question + Complexity Level → Prompt Engineering → Google AI → Formatted Answer + Citations
```

## Component Details:

**Frontend Layer:**
- Streamlit web interface
- File upload handling
- Real-time user feedback
- Response display and formatting

**Processing Layer:**
- PDF text extraction (PyPDF2)
- Intelligent text chunking
- Metadata management
- Error handling and validation

**Storage Layer:**
- In-memory document storage
- Chunk-based knowledge organization
- Source tracking for citations
- Performance statistics

**AI Integration Layer:**
- Google AI Studio API
- Prompt engineering templates
- Response parsing and formatting
- Error recovery and retry logic
