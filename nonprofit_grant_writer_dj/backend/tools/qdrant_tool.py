import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct,
    VectorParams,
    Distance,
    CollectionStatus,
    Filter,
    FieldCondition,
    MatchValue,
)

logger = logging.getLogger(__name__)

class QdrantTool:
    """
    Tool for storing and retrieving vector data from Qdrant.
    Used for semantic search and retrieval of grant-related information.
    """
    
    def __init__(self):
        """Initialize the Qdrant tool."""
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not all([self.qdrant_url, self.qdrant_api_key]):
            logger.warning("Qdrant credentials not properly configured. Vector operations will be unavailable.")
            self.client = None
        else:
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key
            )
    
    def create_collection(self, collection_name: str, vector_size: int = 1536) -> bool:
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name (str): Name of the collection
            vector_size (int): Size of the vector embeddings (default: 1536 for OpenAI embeddings)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Qdrant client not initialized")
            return False
        
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def store_embeddings(
        self, collection_name: str, vectors: List[List[float]], 
        metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None
    ) -> bool:
        """
        Store embeddings in a Qdrant collection.
        
        Args:
            collection_name (str): Name of the collection
            vectors (List[List[float]]): List of vector embeddings
            metadata (List[Dict[str, Any]]): List of metadata for each vector
            ids (Optional[List[str]]): Optional list of IDs for the vectors
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Qdrant client not initialized")
            return False
        
        try:
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            # Create points
            points = [
                PointStruct(
                    id=id_,
                    vector=vector,
                    payload=metadata_
                )
                for id_, vector, metadata_ in zip(ids, vectors, metadata)
            ]
            
            # Upsert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            return True
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return False
    
    def search_similar(
        self, collection_name: str, query_vector: List[float], 
        limit: int = 5, filter_condition: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in a Qdrant collection.
        
        Args:
            collection_name (str): Name of the collection
            query_vector (List[float]): Query vector embedding
            limit (int): Maximum number of results to return
            filter_condition (Optional[Dict[str, Any]]): Optional filter condition
            
        Returns:
            List[Dict[str, Any]]: List of search results with metadata
        """
        if not self.client:
            logger.error("Qdrant client not initialized")
            return []
        
        try:
            # Convert the filter condition to a Qdrant filter if provided
            filter_obj = None
            if filter_condition:
                conditions = []
                for key, value in filter_condition.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                filter_obj = Filter(must=conditions)
            
            # Search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_obj
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from Qdrant.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Qdrant client not initialized")
            return False
        
        try:
            self.client.delete_collection(collection_name=collection_name)
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False 