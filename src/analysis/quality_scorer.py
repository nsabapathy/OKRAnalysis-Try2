"""
Quality Scoring Module
Assesses OKR quality based on best practices
"""

from typing import List, Dict
import statistics
from pathlib import Path
import json

from src.data.okr_loader import OKREntry
from src.analysis.llm_analyzer import OKRAnalyzer


class QualityScorer:
    """Assesses OKR quality and provides improvement suggestions"""
    
    def __init__(self, analyzer: OKRAnalyzer):
        self.analyzer = analyzer
    
    def score_okrs(self, okrs: List[OKREntry], max_workers: int = 4) -> List[Dict]:
        """
        Score quality for all OKRs
        
        Args:
            okrs: List of OKR entries to score
            max_workers: Number of parallel workers
        
        Returns:
            List of quality assessments
        """
        return self.analyzer.assess_quality_batch(okrs, max_workers)
    
    def get_quality_statistics(self, quality_results: List[Dict]) -> Dict:
        """
        Calculate quality statistics across all OKRs
        
        Args:
            quality_results: List of quality assessment results
        
        Returns:
            Statistical summary of quality scores
        """
        overall_scores = [r['overall_score'] for r in quality_results if 'overall_score' in r]
        
        if not overall_scores:
            return {'status': 'no_data'}
        
        dimension_scores = {
            'clarity': [],
            'measurability': [],
            'ambition': [],
            'alignment': [],
            'actionability': []
        }
        
        for result in quality_results:
            scores = result.get('scores', {})
            for dimension in dimension_scores:
                if dimension in scores:
                    dimension_scores[dimension].append(scores[dimension])
        
        stats = {
            'overall': {
                'mean': statistics.mean(overall_scores),
                'median': statistics.median(overall_scores),
                'stdev': statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
                'min': min(overall_scores),
                'max': max(overall_scores)
            },
            'by_dimension': {}
        }
        
        for dimension, scores in dimension_scores.items():
            if scores:
                stats['by_dimension'][dimension] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores)
                }
        
        stats['distribution'] = {
            'high_quality_8_plus': sum(1 for s in overall_scores if s >= 8),
            'good_quality_6_to_8': sum(1 for s in overall_scores if 6 <= s < 8),
            'needs_improvement_below_6': sum(1 for s in overall_scores if s < 6)
        }
        
        return stats
    
    def get_quality_by_team(self, quality_results: List[Dict]) -> Dict[str, Dict]:
        """
        Calculate quality statistics by team
        
        Args:
            quality_results: List of quality assessment results
        
        Returns:
            Dictionary mapping teams to their quality statistics
        """
        team_scores = {}
        
        for result in quality_results:
            team = result.get('team', 'Unknown')
            score = result.get('overall_score', 0)
            
            if team not in team_scores:
                team_scores[team] = []
            
            team_scores[team].append(score)
        
        team_stats = {}
        for team, scores in team_scores.items():
            if scores:
                team_stats[team] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'count': len(scores),
                    'high_quality_count': sum(1 for s in scores if s >= 8)
                }
        
        return team_stats
    
    def get_top_quality_okrs(self, quality_results: List[Dict], top_n: int = 10) -> List[Dict]:
        """Get the highest quality OKRs"""
        sorted_results = sorted(
            quality_results, 
            key=lambda x: x.get('overall_score', 0), 
            reverse=True
        )
        return sorted_results[:top_n]
    
    def get_improvement_needed_okrs(self, quality_results: List[Dict], 
                                   threshold: float = 6.0) -> List[Dict]:
        """Get OKRs that need improvement"""
        return [
            r for r in quality_results 
            if r.get('overall_score', 10) < threshold
        ]
    
    def save_quality_results(self, results: List[Dict], output_path: str):
        """Save quality assessment results to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"Quality results saved to {output_path}")
    
    def load_quality_results(self, input_path: str) -> List[Dict]:
        """Load previously saved quality results"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
