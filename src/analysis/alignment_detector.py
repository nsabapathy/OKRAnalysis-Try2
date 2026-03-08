"""
Alignment Detection Module
Analyzes cross-team alignment, gaps, and collaboration opportunities
"""

from typing import List, Dict
import json
from pathlib import Path
import numpy as np

from src.data.okr_loader import OKREntry
from src.analysis.llm_analyzer import OKRAnalyzer
from src.search.vector_search import OKRVectorSearch


class AlignmentDetector:
    """Detects alignment patterns and gaps across teams"""
    
    def __init__(self, analyzer: OKRAnalyzer, vector_search: OKRVectorSearch):
        self.analyzer = analyzer
        self.vector_search = vector_search
    
    def analyze_team_alignment(self, team_okrs: Dict[str, List[OKREntry]]) -> Dict:
        """
        Analyze alignment across all teams using LLM
        
        Args:
            team_okrs: Dictionary mapping team names to their OKRs
        
        Returns:
            Alignment analysis with gaps and opportunities
        """
        return self.analyzer.analyze_team_alignment(team_okrs)
    
    def compute_alignment_matrix(self, teams: List[str]) -> Dict:
        """
        Compute pairwise alignment scores between all teams
        
        Args:
            teams: List of team names
        
        Returns:
            Alignment matrix and statistics
        """
        alignments = self.vector_search.compute_all_team_alignments(teams)
        
        matrix = {}
        for team_a in teams:
            matrix[team_a] = {}
            for team_b in teams:
                if team_a == team_b:
                    matrix[team_a][team_b] = 1.0
                else:
                    alignment = next(
                        (a for a in alignments 
                         if (a['team_a'] == team_a and a['team_b'] == team_b) or
                            (a['team_a'] == team_b and a['team_b'] == team_a)),
                        None
                    )
                    matrix[team_a][team_b] = alignment['alignment_score'] if alignment else 0.0
        
        avg_alignment = np.mean([a['alignment_score'] for a in alignments])
        
        return {
            'matrix': matrix,
            'teams': teams,
            'average_alignment': float(avg_alignment),
            'pairwise_alignments': alignments
        }
    
    def identify_alignment_clusters(self, alignment_matrix: Dict) -> List[List[str]]:
        """
        Identify clusters of highly aligned teams
        
        Args:
            alignment_matrix: Output from compute_alignment_matrix
        
        Returns:
            List of team clusters
        """
        teams = alignment_matrix['teams']
        matrix = alignment_matrix['matrix']
        
        clusters = []
        visited = set()
        
        for team_a in teams:
            if team_a in visited:
                continue
            
            cluster = [team_a]
            visited.add(team_a)
            
            for team_b in teams:
                if team_b not in visited and matrix[team_a][team_b] >= 0.7:
                    cluster.append(team_b)
                    visited.add(team_b)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    def find_isolated_teams(self, alignment_matrix: Dict, threshold: float = 0.5) -> List[str]:
        """
        Find teams with low alignment to others
        
        Args:
            alignment_matrix: Output from compute_alignment_matrix
            threshold: Alignment threshold
        
        Returns:
            List of isolated team names
        """
        teams = alignment_matrix['teams']
        matrix = alignment_matrix['matrix']
        
        isolated = []
        
        for team in teams:
            avg_alignment = np.mean([
                matrix[team][other] 
                for other in teams 
                if other != team
            ])
            
            if avg_alignment < threshold:
                isolated.append(team)
        
        return isolated
    
    def detect_duplicate_efforts(self, similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Find potential duplicate efforts across teams
        
        Args:
            similarity_threshold: Similarity threshold for duplicates
        
        Returns:
            List of potential duplicate OKRs
        """
        duplicates = self.vector_search.find_duplicates(threshold=similarity_threshold)
        
        duplicate_list = []
        for okr1, okr2, score in duplicates:
            if okr1['metadata']['team'] != okr2['metadata']['team']:
                duplicate_list.append({
                    'team_a': okr1['metadata']['team'],
                    'team_b': okr2['metadata']['team'],
                    'objective_a': okr1['metadata']['objective'],
                    'objective_b': okr2['metadata']['objective'],
                    'similarity_score': score,
                    'quarter': okr1['metadata']['quarter']
                })
        
        return duplicate_list
    
    def save_alignment_results(self, results: Dict, output_path: str):
        """Save alignment analysis results"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"Alignment results saved to {output_path}")
    
    def load_alignment_results(self, input_path: str) -> Dict:
        """Load previously saved alignment results"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
