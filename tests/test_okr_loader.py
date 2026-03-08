"""
Unit tests for OKR Loader
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.okr_loader import OKRTextLoader, OKREntry, SmartChunker


def test_okr_loader_initialization():
    """Test loader initialization"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    assert loader.file_path.exists()


def test_parse_okr_file():
    """Test parsing OKR file"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    entries = loader.parse_okr_file()
    
    assert len(entries) > 0
    assert all(isinstance(entry, OKREntry) for entry in entries)
    assert all(entry.team for entry in entries)
    assert all(entry.objective for entry in entries)


def test_chunk_for_parallel_processing():
    """Test chunking for parallel processing"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    chunks = loader.chunk_for_parallel_processing(num_chunks=4)
    
    assert len(chunks) == 4
    assert all(isinstance(chunk, list) for chunk in chunks)
    
    total_okrs = sum(len(chunk) for chunk in chunks)
    all_okrs = loader.parse_okr_file()
    assert total_okrs == len(all_okrs)


def test_chunk_by_team():
    """Test grouping by team"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    team_okrs = loader.chunk_by_team()
    
    assert isinstance(team_okrs, dict)
    assert len(team_okrs) > 0
    
    for team, okrs in team_okrs.items():
        assert all(okr.team == team for okr in okrs)


def test_get_statistics():
    """Test statistics generation"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    stats = loader.get_statistics()
    
    assert 'total_entries' in stats
    assert 'unique_teams' in stats
    assert 'teams' in stats
    assert 'unique_quarters' in stats
    assert 'quality_distribution' in stats
    
    assert stats['total_entries'] > 0
    assert stats['unique_teams'] > 0


def test_smart_chunker():
    """Test smart chunker"""
    loader = OKRTextLoader("./data/okr_samples_500.txt")
    okrs = loader.parse_okr_file()[:50]
    
    chunker = SmartChunker(max_tokens=2000)
    chunks = chunker.chunk_by_token_limit(okrs)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, list) for chunk in chunks)
    
    for chunk in chunks:
        total_tokens = sum(chunker.estimate_tokens(okr.to_text()) for okr in chunk)
        assert total_tokens <= 2500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
