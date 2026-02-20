"""
Haystack pipeline for patent search.

This module provides document store, preprocessing, and search pipelines
for patent document retrieval using BM25 and embedding-based search.
"""

from typing import List, Dict, Any, Optional
from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever, InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter


class PatentSearchPipeline:
    """
    Patent search pipeline using Haystack.

    Provides BM25 keyword search and semantic embedding search
    for patent documents stored in-memory.
    """

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the patent search pipeline.

        Args:
            embedding_model: Sentence transformers model for embeddings
        """
        self.embedding_model = embedding_model
        self.document_store = InMemoryDocumentStore()
        self._setup_preprocessing_pipeline()
        self._setup_search_pipeline()

    def _setup_preprocessing_pipeline(self) -> None:
        """Set up the document preprocessing pipeline."""
        self.preprocessing_pipeline = Pipeline()

        # Clean documents
        cleaner = DocumentCleaner(
            remove_empty_lines=True,
            remove_extra_whitespaces=True
        )

        # Split documents into chunks
        splitter = DocumentSplitter(
            split_by="word",
            split_length=200,
            split_overlap=20
        )

        # Create embeddings
        embedder = SentenceTransformersDocumentEmbedder(
            model=self.embedding_model
        )

        # Write to document store
        writer = DocumentWriter(document_store=self.document_store)

        self.preprocessing_pipeline.add_component("cleaner", cleaner)
        self.preprocessing_pipeline.add_component("splitter", splitter)
        self.preprocessing_pipeline.add_component("embedder", embedder)
        self.preprocessing_pipeline.add_component("writer", writer)

        # Connect components
        self.preprocessing_pipeline.connect("cleaner", "splitter")
        self.preprocessing_pipeline.connect("splitter", "embedder")
        self.preprocessing_pipeline.connect("embedder", "writer")

    def _setup_search_pipeline(self) -> None:
        """Set up the search pipeline with BM25 and embedding retrievers."""
        self.search_pipeline = Pipeline()

        # BM25 retriever for keyword search
        bm25_retriever = InMemoryBM25Retriever(
            document_store=self.document_store,
            top_k=10
        )

        # Embedding retriever for semantic search
        text_embedder = SentenceTransformersTextEmbedder(
            model=self.embedding_model
        )
        embedding_retriever = InMemoryEmbeddingRetriever(
            document_store=self.document_store,
            top_k=10
        )

        self.search_pipeline.add_component("text_embedder", text_embedder)
        self.search_pipeline.add_component("embedding_retriever", embedding_retriever)
        self.search_pipeline.add_component("bm25_retriever", bm25_retriever)

        # Connect embedder to retriever
        self.search_pipeline.connect("text_embedder.embedding", "embedding_retriever.query_embedding")

    def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Add documents to the search index.

        Args:
            documents: List of Haystack Document objects

        Returns:
            Pipeline run result
        """
        return self.preprocessing_pipeline.run({"cleaner": {"documents": documents}})

    def search(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Search for patents using both BM25 and embedding retrieval.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            Dictionary with bm25_results and embedding_results
        """
        # Run embedding search
        embedding_results = self.search_pipeline.run({
            "text_embedder": {"text": query},
            "embedding_retriever": {"top_k": top_k}
        })

        # Run BM25 search
        bm25_results = self.search_pipeline.run({
            "bm25_retriever": {"query": query, "top_k": top_k}
        })

        return {
            "bm25_results": bm25_results.get("bm25_retriever", {}).get("documents", []),
            "embedding_results": embedding_results.get("embedding_retriever", {}).get("documents", [])
        }

    def hybrid_search(self, query: str, top_k: int = 10) -> List[Document]:
        """
        Perform hybrid search combining BM25 and embedding results.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            Merged and ranked list of documents
        """
        results = self.search(query, top_k=top_k * 2)

        bm25_docs = results["bm25_results"]
        embedding_docs = results["embedding_results"]

        # Merge results with simple reciprocal rank fusion
        doc_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        # Score BM25 results by rank
        for rank, doc in enumerate(bm25_docs):
            doc_id = doc.id
            doc_map[doc_id] = doc
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0 / (rank + 1)

        # Score embedding results by rank
        for rank, doc in enumerate(embedding_docs):
            doc_id = doc.id
            doc_map[doc_id] = doc
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0 / (rank + 1)

        # Sort by combined score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top_k unique documents
        return [doc_map[doc_id] for doc_id, _ in sorted_docs[:top_k]]

    def get_document_count(self) -> int:
        """Return the number of documents in the store."""
        return self.document_store.count_documents()


# Global pipeline instance
_patent_pipeline: Optional[PatentSearchPipeline] = None


def get_pipeline() -> PatentSearchPipeline:
    """Get or create the global patent search pipeline."""
    global _patent_pipeline
    if _patent_pipeline is None:
        _patent_pipeline = PatentSearchPipeline()
    return _patent_pipeline


def initialize_sample_patents() -> None:
    """Initialize the pipeline with sample patent documents."""
    pipeline = get_pipeline()

    sample_patents = [
        Document(
            id="patent-001",
            content="A method for training neural networks using distributed computing. "
                    "The invention relates to machine learning systems that utilize "
                    "multiple processing units to accelerate model training.",
            meta={
                "title": "Distributed Neural Network Training",
                "inventor": "John Smith",
                "filing_date": "2023-01-15",
                "patent_number": "US12345678"
            }
        ),
        Document(
            id="patent-002",
            content="A system for natural language processing using transformer architectures. "
                    "The invention provides improved attention mechanisms for understanding "
                    "context in text data.",
            meta={
                "title": "Transformer-based NLP System",
                "inventor": "Jane Doe",
                "filing_date": "2023-03-22",
                "patent_number": "US12345679"
            }
        ),
        Document(
            id="patent-003",
            content="An apparatus for quantum computing with superconducting qubits. "
                    "The invention includes novel error correction techniques for "
                    "maintaining quantum coherence.",
            meta={
                "title": "Superconducting Quantum Processor",
                "inventor": "Bob Johnson",
                "filing_date": "2023-05-10",
                "patent_number": "US12345680"
            }
        ),
        Document(
            id="patent-004",
            content="A blockchain-based system for secure medical record storage. "
                    "The invention ensures patient privacy while enabling authorized "
                    "access to healthcare providers.",
            meta={
                "title": "Secure Medical Records on Blockchain",
                "inventor": "Alice Williams",
                "filing_date": "2023-07-08",
                "patent_number": "US12345681"
            }
        ),
        Document(
            id="patent-005",
            content="A computer-implemented method for image recognition using convolutional "
                    "neural networks. The system achieves high accuracy in object detection "
                    "with reduced computational requirements.",
            meta={
                "title": "Efficient CNN for Image Recognition",
                "inventor": "Charlie Brown",
                "filing_date": "2023-09-14",
                "patent_number": "US12345682"
            }
        )
    ]

    pipeline.add_documents(sample_patents)
