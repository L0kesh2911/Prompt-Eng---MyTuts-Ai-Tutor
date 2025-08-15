"""
Basic functionality tests for MYTUTS RAG system
Tests core components without requiring actual PDF files
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine import RAGEngine
import tempfile

def test_rag_engine_initialization():
    """Test if RAG engine initializes properly"""
    try:
        # Set up test environment variable
        os.environ['GOOGLE_AI_API_KEY'] = 'test_key_for_initialization'
        
        engine = RAGEngine()
        
        print("PASS: RAG Engine initialization successful")
        return True
    except Exception as e:
        print(f"FAIL: RAG Engine initialization failed - {e}")
        return False

def test_text_preprocessing():
    """Test text cleaning and preprocessing functionality"""
    try:
        engine = RAGEngine()
        
        # Test with messy text that needs cleaning
        messy_text = "This    is   a  test!!!   With    weird   spacing\n\n\nand multiple\tlines."
        cleaned = engine.preprocess_text(messy_text)
        
        # Check if important words are preserved
        expected_keywords = ["test", "weird", "spacing", "multiple", "lines"]
        found_keywords = [word for word in expected_keywords if word in cleaned.lower()]
        
        if len(found_keywords) >= 4:
            print("PASS: Text preprocessing maintains content integrity")
            return True
        else:
            print("FAIL: Text preprocessing lost important keywords")
            return False
    except Exception as e:
        print(f"FAIL: Text preprocessing error - {e}")
        return False

def test_chunking_functionality():
    """Test document chunking logic"""
    try:
        engine = RAGEngine()
        
        # Sample text that should be split into multiple chunks
        sample_text = """This is the first sentence about physics concepts. Newton's laws are fundamental principles that govern motion. 
        The first law states that objects at rest stay at rest unless acted upon by an external force. The second law relates force to acceleration through the equation F equals ma. 
        These concepts are essential for understanding classical mechanics in physics courses. Students often struggle with these ideas initially when learning physics.
        Practice problems help reinforce the concepts and improve understanding. Real-world applications make physics more interesting and relevant to daily life."""
        
        chunks = engine.create_chunks(sample_text, chunk_size=100)
        
        # Verify chunking worked correctly
        if len(chunks) > 1 and all('text' in chunk for chunk in chunks):
            print(f"PASS: Text chunking created {len(chunks)} valid chunks")
            return True
        else:
            print("FAIL: Text chunking produced invalid results")
            return False
    except Exception as e:
        print(f"FAIL: Text chunking error - {e}")
        return False

def test_search_functionality():
    """Test content search capabilities"""
    try:
        engine = RAGEngine()
        
        # Create mock content chunks for testing search
        mock_chunks = [
            {
                'id': 'test_chunk_1',
                'text': 'Newton\'s first law states that objects at rest stay at rest unless acted upon by an external force',
                'text_lower': 'newton\'s first law states that objects at rest stay at rest unless acted upon by an external force',
                'filename': 'physics_textbook.pdf',
                'doc_id': 'test_document',
                'chunk_index': 0
            },
            {
                'id': 'test_chunk_2', 
                'text': 'Energy can be converted from one form to another but cannot be created or destroyed according to conservation laws',
                'text_lower': 'energy can be converted from one form to another but cannot be created or destroyed according to conservation laws',
                'filename': 'physics_textbook.pdf',
                'doc_id': 'test_document',
                'chunk_index': 1
            }
        ]
        
        # Add mock data to engine
        engine.chunks = mock_chunks
        
        # Test search functionality
        results = engine.search_relevant_content("Newton first law")
        
        # Verify search returns relevant results
        if len(results) > 0 and 'Newton' in results[0]['text']:
            print("PASS: Content search returns relevant results")
            return True
        else:
            print("FAIL: Content search did not find relevant material")
            return False
    except Exception as e:
        print(f"FAIL: Content search error - {e}")
        return False

def test_document_statistics():
    """Test document statistics and metadata tracking"""
    try:
        engine = RAGEngine()
        
        # Add mock document data
        engine.documents['test_document_id'] = {
            'filename': 'sample_textbook.pdf',
            'chunks': 5,
            'total_chars': 1000
        }
        
        # Test statistics generation
        stats = engine.get_document_stats()
        
        # Verify statistics are calculated correctly
        if stats['total_documents'] == 1:
            print("PASS: Document statistics calculated correctly")
            return True
        else:
            print("FAIL: Document statistics calculation error")
            return False
    except Exception as e:
        print(f"FAIL: Document statistics error - {e}")
        return False

def test_chunk_quality():
    """Test quality of generated text chunks"""
    try:
        engine = RAGEngine()
        
        # Test with academic content
        academic_text = """The fundamental principles of thermodynamics govern energy transfer in physical systems. The first law establishes energy conservation. The second law introduces entropy and the direction of spontaneous processes. These principles apply to everything from steam engines to biological systems."""
        
        chunks = engine.create_chunks(academic_text, chunk_size=150)
        
        # Check chunk quality
        valid_chunks = 0
        for chunk in chunks:
            if len(chunk['text']) > 20 and chunk['text'].count('.') > 0:
                valid_chunks += 1
        
        if valid_chunks == len(chunks) and len(chunks) > 0:
            print("PASS: Generated chunks maintain content quality")
            return True
        else:
            print("FAIL: Generated chunks have quality issues")
            return False
    except Exception as e:
        print(f"FAIL: Chunk quality test error - {e}")
        return False

def run_comprehensive_tests():
    """Execute all test cases and report results"""
    print("MYTUTS System Testing Suite")
    print("=" * 40)
    print()
    
    # Define all test functions
    test_functions = [
        ("RAG Engine Initialization", test_rag_engine_initialization),
        ("Text Preprocessing", test_text_preprocessing),
        ("Document Chunking", test_chunking_functionality),
        ("Content Search", test_search_functionality),
        ("Document Statistics", test_document_statistics),
        ("Chunk Quality", test_chunk_quality)
    ]
    
    passed_tests = 0
    total_tests = len(test_functions)
    
    # Run each test
    for test_name, test_function in test_functions:
        print(f"Testing {test_name}...")
        if test_function():
            passed_tests += 1
        print()
    
    # Print final results
    print("=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    print(f"Tests Passed: {passed_tests} out of {total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if passed_tests == total_tests:
        print("All tests completed successfully. System is ready for production demo.")
    elif passed_tests >= total_tests * 0.8:
        print("Most tests passed. System is functional with minor issues.")
    else:
        print("Several tests failed. System needs debugging before demo.")
    
    return passed_tests, total_tests

def test_system_integration():
    """Integration test simulating real usage"""
    try:
        engine = RAGEngine()
        
        # Simulate document addition
        engine.documents['integration_test'] = {
            'filename': 'test_physics.pdf',
            'chunks': 10,
            'total_chars': 5000
        }
        
        # Add sample chunks
        for i in range(3):
            engine.chunks.append({
                'id': f'integration_{i}',
                'text': f'This is test content chunk {i} about physics concepts and scientific principles.',
                'text_lower': f'this is test content chunk {i} about physics concepts and scientific principles.',
                'filename': 'test_physics.pdf',
                'doc_id': 'integration_test',
                'chunk_index': i
            })
        
        # Test end-to-end workflow
        stats = engine.get_document_stats()
        search_results = engine.search_relevant_content("physics concepts")
        
        if stats['total_documents'] > 0 and len(search_results) > 0:
            print("PASS: System integration test successful")
            return True
        else:
            print("FAIL: System integration test failed")
            return False
    except Exception as e:
        print(f"FAIL: System integration error - {e}")
        return False

if __name__ == "__main__":
    # Run all tests
    passed, total = run_comprehensive_tests()
    
    # Run integration test
    print("Running Integration Test...")
    test_system_integration()
    
    print("\nTesting complete. Check results above for any issues.")