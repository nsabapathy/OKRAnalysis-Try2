"""
Theme Extraction Module
Identifies recurring strategic themes across OKRs
"""

from typing import List, Dict
from collections import Counter
import json
from pathlib import Path

from src.data.okr_loader import OKREntry
from src.analysis.llm_analyzer import OKRAnalyzer


class ThemeExtractor:
    """Extracts and analyzes themes from OKR data"""
    
    def __init__(self, analyzer: OKRAnalyzer):
        self.analyzer = analyzer
    
    def extract_themes_from_chunks(self, chunks: List[List[OKREntry]], 
                                   max_workers: int = 4) -> Dict:
        """
        Extract themes using parallel map-reduce
        
        Args:
            chunks: List of OKR chunks
            max_workers: Number of parallel workers
        
        Returns:
            Consolidated theme analysis
        """
        return self.analyzer.extract_themes_parallel(chunks, max_workers)
    
    def get_theme_by_team(self, okrs: List[OKREntry]) -> Dict[str, List[str]]:
        """
        Extract simple keyword-based themes by team
        
        Args:
            okrs: List of OKR entries
        
        Returns:
            Dictionary mapping teams to their theme keywords
        """
        team_themes = {}
        
        for okr in okrs:
            if okr.team not in team_themes:
                team_themes[okr.team] = []
            
            keywords = self._extract_keywords(okr.objective)
            team_themes[okr.team].extend(keywords)
        
        for team in team_themes:
            counter = Counter(team_themes[team])
            team_themes[team] = [word for word, count in counter.most_common(10)]
        
        return team_themes
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                    'can', 'could', 'may', 'might', 'must', 'our', 'their', 'this', 'that'}
        
        words = text.lower().split()
        keywords = [w.strip('.,!?;:()[]{}') for w in words if len(w) > 3 and w.lower() not in stopwords]
        
        return keywords
    
    def save_themes(self, themes: Dict, output_path: str):
        """Save theme analysis to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(themes, f, indent=2)
        
        print(f"Themes saved to {output_path}")
    
    def load_themes(self, input_path: str) -> Dict:
        """Load previously saved themes"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
