"""
Vector Search Engine using ChromaDB
Enables semantic search and similarity detection across OKRs
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import numpy as np
from tqdm import tqdm
from pathlib import Path

from src.data.okr_loader import OKREntry


class OKRVectorSearch:
    """Vector search engine for OKR semantic search and analysis"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db", 
                 embedding_model: str = "intfloat/multilingual-e5-large"):
        """
        Initialize vector search engine
        
        Args:
            persist_directory: Path to persist ChromaDB data
            embedding_model: Sentence transformer model name
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        self.collection = self.client.get_or_create_collection(
            name="okrs",
            metadata={"description": "OKR embeddings for semantic search"}
        )
        
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print("Embedding model loaded successfully")
    
    def index_okrs_batch(self, okrs: List[OKREntry], batch_size: int = 100):
        """
        Batch embed and store all OKRs in vector database
        
        Args:
            okrs: List of OKR entries to index
            batch_size: Number of OKRs to process per batch
        """
        print(f"Indexing {len(okrs)} OKRs in batches of {batch_size}...")
        
        for i in tqdm(range(0, len(okrs), batch_size), desc="Indexing OKRs"):
            batch = okrs[i:i + batch_size]
            
            texts = [okr.to_text() for okr in batch]
            ids = [f"okr_{okr.entry_id}" for okr in batch]
            
            metadatas = [
                {
                    'team': okr.team,
                    'quarter': okr.quarter,
                    'quality_level': okr.quality_level,
                    'objective': okr.objective,
                    'entry_id': okr.entry_id
                }
                for okr in batch
            ]
            
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
        
        print(f"Successfully indexed {len(okrs)} OKRs")
    
    def find_similar_okrs(self, query: str, top_k: int = 10, 
                         filter_team: Optional[str] = None,
                         filter_quarter: Optional[str] = None) -> List[Dict]:
        """
        Semantic search for similar OKRs
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_team: Optional team filter
            filter_quarter: Optional quarter filter
        
        Returns:
            List of similar OKRs with metadata and similarity scores
        """
        query_embedding = self.embedding_model.encode([query])[0]
        
        where_filter = {}
        if filter_team:
            where_filter['team'] = filter_team
        if filter_quarter:
            where_filter['quarter'] = filter_quarter
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        similar_okrs = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                similar_okrs.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return similar_okrs
    
    def find_duplicates(self, threshold: float = 0.85) -> List[Tuple[Dict, Dict, float]]:
        """
        Detect duplicate or highly similar OKRs across teams
        
        Args:
            threshold: Similarity threshold (0-1, higher = more similar)
        
        Returns:
            List of (okr1, okr2, similarity_score) tuples
        """
        print("Searching for duplicate OKRs...")
        
        all_results = self.collection.get(include=['embeddings', 'documents', 'metadatas'])
        
        if not all_results['ids']:
            return []
        
        embeddings = np.array(all_results['embeddings'])
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(embeddings)
        
        duplicates = []
        n = len(similarity_matrix)
        
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] >= threshold:
                    duplicates.append((
                        {
                            'id': all_results['ids'][i],
                            'text': all_results['documents'][i],
                            'metadata': all_results['metadatas'][i]
                        },
                        {
                            'id': all_results['ids'][j],
                            'text': all_results['documents'][j],
                            'metadata': all_results['metadatas'][j]
                        },
                        float(similarity_matrix[i][j])
                    ))
        
        duplicates.sort(key=lambda x: x[2], reverse=True)
        
        print(f"Found {len(duplicates)} potential duplicates")
        return duplicates
    
    def compute_team_alignment(self, team_a: str, team_b: str) -> Dict:
        """
        Calculate semantic similarity between two teams' OKRs
        
        Args:
            team_a: First team name
            team_b: Second team name
        
        Returns:
            Alignment score and details
        """
        team_a_results = self.collection.get(
            where={'team': team_a},
            include=['embeddings', 'documents']
        )
        
        team_b_results = self.collection.get(
            where={'team': team_b},
            include=['embeddings', 'documents']
        )
        
        if len(team_a_results['embeddings']) == 0 or len(team_b_results['embeddings']) == 0:
            return {
                'team_a': team_a,
                'team_b': team_b,
                'alignment_score': 0.0,
                'status': 'insufficient_data'
            }
        
        embeddings_a = np.array(team_a_results['embeddings'])
        embeddings_b = np.array(team_b_results['embeddings'])
        
        avg_embedding_a = embeddings_a.mean(axis=0)
        avg_embedding_b = embeddings_b.mean(axis=0)
        
        from sklearn.metrics.pairwise import cosine_similarity
        alignment_score = cosine_similarity([avg_embedding_a], [avg_embedding_b])[0][0]
        
        return {
            'team_a': team_a,
            'team_b': team_b,
            'alignment_score': float(alignment_score),
            'team_a_okr_count': len(team_a_results['ids']),
            'team_b_okr_count': len(team_b_results['ids']),
            'status': 'success'
        }
    
    def compute_all_team_alignments(self, teams: List[str]) -> List[Dict]:
        """
        Compute alignment scores for all team pairs
        
        Args:
            teams: List of team names
        
        Returns:
            List of alignment scores for all pairs
        """
        print(f"Computing alignment for {len(teams)} teams...")
        
        alignments = []
        
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                alignment = self.compute_team_alignment(teams[i], teams[j])
                alignments.append(alignment)
        
        return alignments
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about indexed OKRs"""
        count = self.collection.count()
        
        all_data = self.collection.get(include=['metadatas'])
        
        teams = set()
        quarters = set()
        
        if all_data['metadatas']:
            for metadata in all_data['metadatas']:
                teams.add(metadata.get('team', 'Unknown'))
                quarters.add(metadata.get('quarter', 'Unknown'))
        
        return {
            'total_okrs': count,
            'unique_teams': len(teams),
            'teams': sorted(list(teams)),
            'unique_quarters': len(quarters),
            'quarters': sorted(list(quarters))
        }
