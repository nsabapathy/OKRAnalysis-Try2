"""
OKR Text File Loader with Streaming and Chunking Support
Handles large text files efficiently with memory-conscious processing
"""

from typing import List, Dict, Iterator, Optional
from dataclasses import dataclass, asdict
import re
from pathlib import Path
import json


@dataclass
class OKREntry:
    """Represents a single OKR entry"""
    team: str
    quarter: str
    objective: str
    key_result_1: str
    key_result_2: str
    key_result_3: str
    quality_level: str
    raw_text: str
    entry_id: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_text(self) -> str:
        """Format OKR as readable text for LLM analysis"""
        return f"""Team: {self.team}
Quarter: {self.quarter}
Objective: {self.objective}
Key Results:
  1. {self.key_result_1}
  2. {self.key_result_2}
  3. {self.key_result_3}
Quality Level: {self.quality_level}"""


class OKRTextLoader:
    """Loads and parses OKR entries from large text files"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"OKR file not found: {file_path}")
    
    def parse_okr_file(self) -> List[OKREntry]:
        """Parse entire OKR file into structured entries"""
        entries = []
        current_entry = {}
        entry_id = 0
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line == "=== OKR ENTRY ===":
                    if current_entry:
                        entries.append(self._create_okr_entry(current_entry, entry_id))
                        entry_id += 1
                    current_entry = {}
                
                elif line.startswith("Team:"):
                    current_entry['team'] = line.replace("Team:", "").strip()
                
                elif line.startswith("Quarter:"):
                    current_entry['quarter'] = line.replace("Quarter:", "").strip()
                
                elif line.startswith("Objective:"):
                    current_entry['objective'] = line.replace("Objective:", "").strip()
                
                elif line.startswith("Key Result 1:"):
                    current_entry['key_result_1'] = line.replace("Key Result 1:", "").strip()
                
                elif line.startswith("Key Result 2:"):
                    current_entry['key_result_2'] = line.replace("Key Result 2:", "").strip()
                
                elif line.startswith("Key Result 3:"):
                    current_entry['key_result_3'] = line.replace("Key Result 3:", "").strip()
                
                elif line.startswith("Quality Level:"):
                    current_entry['quality_level'] = line.replace("Quality Level:", "").strip()
                
                elif line.startswith("Raw Text:"):
                    current_entry['raw_text'] = line.replace("Raw Text:", "").strip()
            
            if current_entry:
                entries.append(self._create_okr_entry(current_entry, entry_id))
        
        return entries
    
    def _create_okr_entry(self, entry_dict: Dict, entry_id: int) -> OKREntry:
        """Create OKREntry from parsed dictionary"""
        return OKREntry(
            team=entry_dict.get('team', 'Unknown'),
            quarter=entry_dict.get('quarter', 'Unknown'),
            objective=entry_dict.get('objective', ''),
            key_result_1=entry_dict.get('key_result_1', ''),
            key_result_2=entry_dict.get('key_result_2', ''),
            key_result_3=entry_dict.get('key_result_3', ''),
            quality_level=entry_dict.get('quality_level', 'Unknown'),
            raw_text=entry_dict.get('raw_text', ''),
            entry_id=entry_id
        )
    
    def chunk_for_parallel_processing(self, num_chunks: int = 4) -> List[List[OKREntry]]:
        """
        Split OKRs into equal chunks for parallel processing
        
        Args:
            num_chunks: Number of chunks to create (default: 4)
        
        Returns:
            List of OKR entry chunks
        """
        all_entries = self.parse_okr_file()
        total_entries = len(all_entries)
        chunk_size = (total_entries + num_chunks - 1) // num_chunks
        
        chunks = []
        for i in range(0, total_entries, chunk_size):
            chunk = all_entries[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def chunk_by_team(self) -> Dict[str, List[OKREntry]]:
        """Group OKRs by team for team-based analysis"""
        all_entries = self.parse_okr_file()
        team_groups = {}
        
        for entry in all_entries:
            if entry.team not in team_groups:
                team_groups[entry.team] = []
            team_groups[entry.team].append(entry)
        
        return team_groups
    
    def get_statistics(self) -> Dict:
        """Get basic statistics about the OKR dataset"""
        all_entries = self.parse_okr_file()
        teams = set(entry.team for entry in all_entries)
        quarters = set(entry.quarter for entry in all_entries)
        quality_levels = {}
        
        for entry in all_entries:
            quality_levels[entry.quality_level] = quality_levels.get(entry.quality_level, 0) + 1
        
        return {
            'total_entries': len(all_entries),
            'unique_teams': len(teams),
            'teams': sorted(list(teams)),
            'unique_quarters': len(quarters),
            'quarters': sorted(list(quarters)),
            'quality_distribution': quality_levels
        }
    
    def save_processed_data(self, output_path: str):
        """Save parsed OKRs to JSON for caching"""
        all_entries = self.parse_okr_file()
        data = [entry.to_dict() for entry in all_entries]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(data)} OKR entries to {output_path}")


class SmartChunker:
    """Advanced chunking strategies for LLM processing"""
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def chunk_by_token_limit(self, entries: List[OKREntry]) -> List[List[OKREntry]]:
        """Create chunks that fit within token limit"""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for entry in entries:
            entry_text = entry.to_text()
            entry_tokens = self.estimate_tokens(entry_text)
            
            if current_tokens + entry_tokens > self.max_tokens and current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(entry)
            current_tokens += entry_tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def create_overlapping_chunks(self, entries: List[OKREntry], overlap_ratio: float = 0.1) -> List[List[OKREntry]]:
        """Create chunks with overlap for context preservation"""
        base_chunks = self.chunk_by_token_limit(entries)
        overlapping_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            if i > 0:
                overlap_size = int(len(base_chunks[i-1]) * overlap_ratio)
                overlap_entries = base_chunks[i-1][-overlap_size:] if overlap_size > 0 else []
                overlapping_chunks.append(overlap_entries + chunk)
            else:
                overlapping_chunks.append(chunk)
        
        return overlapping_chunks
