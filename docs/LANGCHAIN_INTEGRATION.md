# LangChain Integration Guide

## When to Integrate LangChain

LangChain should be integrated when you want to enhance your RAG (Retrieval Augmented Generation) system with:

1. **Advanced Document Processing**
   - Better text splitting strategies
   - Document loaders for various formats
   - Pre-processing pipelines

2. **Improved Retrieval**
   - Advanced vector store integrations
   - Hybrid search (vector + keyword)
   - Re-ranking capabilities

3. **Chain Orchestration**
   - Complex RAG chains
   - Multi-step reasoning
   - Agent-based workflows

4. **Prompt Management**
   - Prompt templates
   - Prompt versioning
   - Prompt optimization

## Current State vs. LangChain Integration

### Current Implementation (Custom)
- ✅ Basic document loaders (Excel, CSV)
- ✅ Custom chunking
- ✅ OpenAI embeddings
- ✅ PostgreSQL with pgvector
- ✅ Basic RAG service structure

### With LangChain Integration
- 🔄 LangChain document loaders (more formats)
- 🔄 LangChain text splitters (better chunking strategies)
- 🔄 LangChain vector stores (abstraction layer)
- 🔄 LangChain chains (RAG, QA chains)
- 🔄 LangChain agents (complex workflows)

## Integration Points

### 1. Document Loaders (Priority: Medium)

**When**: You need to support more file formats (PDF, Word, HTML, etc.)

**Current**: Custom loaders in `src/loaders/`

**With LangChain**:
```python
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.document_loaders import UnstructuredExcelLoader

# Replace or enhance current loaders
```

**Recommendation**: Keep custom Excel Q&A loader, add LangChain for other formats.

### 2. Text Splitters (Priority: High)

**When**: You want better chunking strategies (semantic, recursive, etc.)

**Current**: Basic chunker in `src/embeddings/chunker.py`

**With LangChain**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import SemanticChunker

# Better chunking for Q&A and content
```

**Recommendation**: Integrate now for better chunk quality.

### 3. Vector Stores (Priority: Low)

**When**: You want to support multiple vector databases or need abstraction

**Current**: Direct PostgreSQL/pgvector implementation

**With LangChain**:
```python
from langchain.vectorstores import PGVector
from langchain.embeddings import OpenAIEmbeddings

# Abstraction layer, but you lose direct control
```

**Recommendation**: Keep current implementation for performance, consider LangChain if you need multi-DB support.

### 4. RAG Chains (Priority: High)

**When**: You want to implement complex RAG workflows

**Current**: Basic RAG service in `src/services/rag_service.py`

**With LangChain**:
```python
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain

# Better chain orchestration
```

**Recommendation**: Integrate for query processing and answer generation.

### 5. Prompt Templates (Priority: Medium)

**When**: You want better prompt management

**Current**: Basic prompt template in `src/llm/prompt_template.py`

**With LangChain**:
```python
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate

# Better prompt management
```

**Recommendation**: Integrate for better prompt handling.

## Recommended Integration Plan

### Phase 1: Text Splitting (Now)
- Replace custom chunker with LangChain's `RecursiveCharacterTextSplitter`
- Better handling of Q&A pairs
- Improved chunk boundaries

### Phase 2: RAG Chains (Next)
- Implement LangChain's `RetrievalQA` chain
- Better query processing
- Enhanced answer generation

### Phase 3: Document Loaders (Later)
- Add LangChain loaders for PDF, Word, etc.
- Keep custom Excel Q&A loader
- Unified loader interface

### Phase 4: Advanced Features (Future)
- LangChain agents for complex queries
- Multi-step reasoning
- Tool integration

## Installation

Add to `requirements.txt`:
```txt
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
```

## Example: Integrating Text Splitter

```python
# src/embeddings/chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Chunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        documents = self.splitter.create_documents([text])
        return [
            {
                "text": doc.page_content,
                "start": 0,  # LangChain doesn't track positions
                "end": len(doc.page_content)
            }
            for doc in documents
        ]
```

## Example: Integrating RAG Chain

```python
# src/services/rag_service.py
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import PGVector

class RAGService:
    def __init__(self):
        # Initialize LangChain components
        self.vectorstore = PGVector(
            connection_string=settings.database_url,
            embedding_function=OpenAIEmbeddings()
        )
        self.llm = OpenAI()
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        result = self.qa_chain.run(request.query)
        return QueryResponse(answer=result, ...)
```

## Benefits of LangChain Integration

1. **Ecosystem**: Access to many pre-built components
2. **Best Practices**: Implements RAG best practices
3. **Flexibility**: Easy to swap components
4. **Community**: Large community and examples

## Drawbacks

1. **Abstraction**: Less control over low-level operations
2. **Performance**: May have overhead compared to direct implementation
3. **Dependencies**: Additional dependencies to manage
4. **Learning Curve**: Team needs to learn LangChain patterns

## Decision Matrix

| Feature | Current | LangChain | Recommendation |
|---------|---------|-----------|----------------|
| Excel Q&A Loader | ✅ Custom | ⚠️ Generic | Keep custom |
| Text Splitting | ⚠️ Basic | ✅ Advanced | **Integrate** |
| Vector Store | ✅ Direct | ⚠️ Abstraction | Keep current |
| RAG Chains | ⚠️ Basic | ✅ Advanced | **Integrate** |
| Embeddings | ✅ Direct | ✅ Wrapper | Optional |
| Prompt Management | ⚠️ Basic | ✅ Advanced | **Integrate** |

## Conclusion

**Start with**: Text Splitters and RAG Chains (high value, low risk)
**Keep custom**: Excel Q&A loader and direct pgvector (performance)
**Add later**: Document loaders for other formats

The current implementation is solid for basic RAG. LangChain will add value primarily in:
- Better text splitting strategies
- Chain orchestration for complex queries
- Prompt template management

