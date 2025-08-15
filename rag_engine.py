import PyPDF2
import os
from typing import List, Dict, Tuple
import uuid
import re
from io import BytesIO
import requests
import json

class RAGEngine:
    """
    RAG engine using free Google AI Studio API
    Processes documents and generates answers using retrieval-augmented generation
    """
    
    def __init__(self):
        """Initialize the RAG system with Google AI integration"""
        self.documents = {}
        self.chunks = []
        
        # Get Google AI API key from environment
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required. Get your free key from https://aistudio.google.com/")
        
        # Google AI API endpoint
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
        
        print("RAG Engine initialized with Google AI integration")
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extract text content from uploaded PDF file
        
        Args:
            pdf_file: Uploaded PDF file object
            
        Returns:
            str: Extracted text with page markers
        """
        try:
            # Reset file pointer to beginning
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            
            extracted_text = ""
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        extracted_text += f"\n--- Page {page_num + 1} of {total_pages} ---\n"
                        extracted_text += page_text.strip() + "\n"
                except Exception as page_error:
                    # Skip pages that can't be processed
                    continue
            
            if not extracted_text.strip():
                raise ValueError("No readable text found in the PDF file")
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove unusual characters while preserving punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-\'""]', ' ', text)
        # Clean up multiple spaces
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def create_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """
        Divide text into manageable chunks for processing
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        # Clean the text first
        processed_text = self.preprocess_text(text)
        
        # Split into sentences for better context preservation
        sentences = re.split(r'(?<=[.!?])\s+', processed_text)
        
        chunks = []
        current_chunk = ""
        sentence_buffer = []
        
        for sentence in sentences:
            projected_length = len(current_chunk) + len(sentence) + 1
            
            if projected_length > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'text': current_chunk.strip(),
                    'length': len(current_chunk),
                    'sentence_count': len(sentence_buffer)
                })
                
                # Start new chunk with overlap
                if len(sentence_buffer) > 2:
                    overlap_sentences = sentence_buffer[-2:]
                    current_chunk = ' '.join(overlap_sentences) + ' ' + sentence
                    sentence_buffer = overlap_sentences + [sentence]
                else:
                    current_chunk = sentence
                    sentence_buffer = [sentence]
            else:
                current_chunk += ' ' + sentence if current_chunk else sentence
                sentence_buffer.append(sentence)
        
        # Add final chunk if it exists
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'length': len(current_chunk),
                'sentence_count': len(sentence_buffer)
            })
        
        return chunks
    
    def add_document(self, pdf_file, filename: str) -> Tuple[str, int]:
        """
        Process and add a document to the knowledge base
        
        Args:
            pdf_file: PDF file to process
            filename: Name of the uploaded file
            
        Returns:
            Tuple of (document_id, number_of_chunks)
        """
        try:
            print(f"Processing document: {filename}")
            
            # Extract text from PDF
            document_text = self.extract_text_from_pdf(pdf_file)
            print(f"Extracted {len(document_text)} characters from {filename}")
            
            # Create text chunks
            doc_chunks = self.create_chunks(document_text)
            print(f"Created {len(doc_chunks)} chunks from {filename}")
            
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            # Process and store each chunk
            for i, chunk in enumerate(doc_chunks):
                chunk_data = {
                    'id': f"{doc_id}_{i}",
                    'text': chunk['text'],
                    'text_lower': chunk['text'].lower(),  # For case-insensitive search
                    'filename': filename,
                    'doc_id': doc_id,
                    'chunk_index': i,
                    'length': chunk['length'],
                    'sentence_count': chunk['sentence_count']
                }
                self.chunks.append(chunk_data)
            
            # Store document metadata
            self.documents[doc_id] = {
                'filename': filename,
                'chunks': len(doc_chunks),
                'total_chars': len(document_text),
                'preview': document_text[:300] + "..." if len(document_text) > 300 else document_text
            }
            
            print(f"Successfully processed {filename}: {len(doc_chunks)} chunks created")
            return doc_id, len(doc_chunks)
            
        except Exception as e:
            print(f"Error processing document {filename}: {str(e)}")
            raise Exception(f"Failed to add document {filename}: {str(e)}")
    
    def search_relevant_content(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search for content relevant to the given query using keyword matching
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant content chunks with similarity scores
        """
        if not self.chunks:
            return []
        
        try:
            query_lower = query.lower()
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            
            if not query_words:
                return []
            
            scored_chunks = []
            
            for chunk in self.chunks:
                chunk_words = set(re.findall(r'\b\w+\b', chunk['text_lower']))
                
                # Calculate similarity based on common words
                common_words = query_words.intersection(chunk_words)
                
                if common_words:
                    # Basic similarity score: ratio of matching words
                    base_score = len(common_words) / len(query_words)
                    
                    # Bonus for exact phrase matches
                    phrase_bonus = 0.3 if query_lower in chunk['text_lower'] else 0
                    
                    # Bonus for multiple word matches in sequence
                    sequence_bonus = 0.2 if len(common_words) > 1 else 0
                    
                    final_score = base_score + phrase_bonus + sequence_bonus
                    
                    scored_chunks.append({
                        'text': chunk['text'],
                        'filename': chunk['filename'],
                        'similarity_score': min(final_score, 1.0),  # Cap at 1.0
                        'chunk_index': chunk['chunk_index'],
                        'matching_words': list(common_words)
                    })
            
            # Sort by similarity score in descending order
            scored_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top results
            return scored_chunks[:max_results]
            
        except Exception as e:
            print(f"Error in content search: {str(e)}")
            return []
    
    def call_google_ai(self, prompt: str) -> str:
        """
        Make API call to Google AI Studio
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            str: AI-generated response
        """
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("No response generated from Google AI")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google AI API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from Google AI: {str(e)}")
        except Exception as e:
            raise Exception(f"Google AI API call failed: {str(e)}")
    
    def generate_answer(self, question: str, complexity_level: str = "beginner") -> Dict:
        """
        Generate an answer to the question using retrieved content and AI
        
        Args:
            question: User's question
            complexity_level: Desired explanation complexity
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            print(f"Generating answer for: {question}")
            
            # Search for relevant content
            relevant_chunks = self.search_relevant_content(question, max_results=3)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information in your uploaded documents to answer this question. Please make sure you've uploaded materials that cover this topic, or try rephrasing your question with different keywords.",
                    "sources": [],
                    "context_used": 0
                }
            
            # Prepare context from retrieved chunks
            context_parts = []
            for i, chunk in enumerate(relevant_chunks):
                source_info = f"Source {i+1} from {chunk['filename']}"
                context_parts.append(f"[{source_info}]\n{chunk['text']}")
            
            context = "\n\n".join(context_parts)
            
            # Determine explanation approach based on complexity level
            if "advanced" in complexity_level.lower():
                style_instruction = """Provide a comprehensive, technical explanation that includes:
- Detailed technical terminology and precise definitions
- In-depth analysis of processes and mechanisms
- Mathematical formulations, equations, or formulas when applicable
- Advanced conceptual relationships and theoretical implications
- References to established principles and theories"""
            else:
                style_instruction = """Provide a clear, beginner-friendly explanation that includes:
- Simple, accessible language with helpful analogies
- Step-by-step breakdown of complex concepts
- Real-world examples and practical applications
- Minimal technical jargon, with explanations when necessary
- Easy-to-understand comparisons and metaphors"""
            
            # Construct comprehensive prompt
            prompt = f"""You are MYTUTS, an intelligent AI study assistant helping students understand their course materials. Your role is to provide clear, accurate explanations based on the uploaded study documents.

CONTEXT FROM STUDENT'S UPLOADED MATERIALS:
{context}

STUDENT'S QUESTION: {question}

EXPLANATION APPROACH: {style_instruction}

RESPONSE GUIDELINES:
1. Answer the question directly and comprehensively using the provided context
2. Apply the specified complexity level consistently throughout your response
3. Include specific details, examples, and explanations from the context
4. Structure your response clearly with appropriate headings or organization
5. If the context doesn't fully address the question, mention what additional information would be helpful
6. Always ground your response in the provided materials
7. Be engaging and educational while maintaining accuracy

Please provide your detailed response:"""

            # Generate response using Google AI
            ai_response = self.call_google_ai(prompt)
            
            # Prepare source information
            sources = []
            for chunk in relevant_chunks:
                sources.append({
                    "filename": chunk['filename'],
                    "confidence": chunk['similarity_score'],
                    "matching_terms": chunk.get('matching_words', [])[:5]  # Top 5 matching words
                })
            
            result = {
                "answer": ai_response,
                "sources": sources,
                "context_used": len(relevant_chunks)
            }
            
            print(f"Answer generated successfully using {len(relevant_chunks)} relevant chunks")
            return result
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            raise Exception(f"Answer generation failed: {str(e)}")
    
    def get_document_stats(self) -> Dict:
        """
        Get current statistics about the document knowledge base
        
        Returns:
            Dictionary containing system statistics
        """
        try:
            return {
                "total_documents": len(self.documents),
                "total_chunks": len(self.chunks),
                "documents": list(self.documents.values())
            }
        except Exception:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "documents": []
            }
    
    def generate_study_quiz(self, topic: str = None, question_count: int = 5) -> Dict:
        """
        Generate quiz questions based on uploaded study materials
        
        Args:
            topic: Specific topic to focus on (optional)
            question_count: Number of questions to generate
            
        Returns:
            Dictionary containing quiz questions and metadata
        """
        try:
            # Search for relevant content
            if topic:
                relevant_chunks = self.search_relevant_content(topic, max_results=5)
            else:
                # Use general search terms for broad quiz
                relevant_chunks = self.search_relevant_content("main concepts key points important", max_results=5)
            
            if not relevant_chunks:
                return {"error": "Insufficient content available for quiz generation. Please upload more study materials."}
            
            # Prepare content for quiz generation
            quiz_content = "\n\n".join([chunk['text'] for chunk in relevant_chunks[:3]])
            
            quiz_prompt = f"""Based on the following study material, create {question_count} educational quiz questions to test student understanding:

STUDY MATERIAL:
{quiz_content}

Please create a variety of question types:
- Multiple choice questions with 4 options each (label A, B, C, D)
- Short answer questions
- True/false questions

For each question:
1. Clearly state the question
2. Provide all answer options (for multiple choice)
3. Indicate the correct answer
4. Give a brief explanation of why the answer is correct

Format the quiz clearly with numbered questions."""

            quiz_response = self.call_google_ai(quiz_prompt)
            
            return {
                "quiz_content": quiz_response,
                "source_documents": list(set([chunk['filename'] for chunk in relevant_chunks[:3]])),
                "questions_generated": question_count
            }
            
        except Exception as e:
            return {"error": f"Quiz generation failed: {str(e)}"}