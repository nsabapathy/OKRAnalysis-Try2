"""
LLM-based OKR Analysis Engine with Map-Reduce Pattern
Supports parallel processing of large OKR datasets
"""

from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json
from pathlib import Path

from src.utils.llm_client import LLMClient, PromptTemplates
from src.data.okr_loader import OKREntry


class OKRAnalyzer:
    """Main analyzer class with map-reduce pattern supporting multiple LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, provider: Optional[str] = None):
        self.llm = LLMClient(api_key=api_key, model_name=model_name, provider=provider)
        self.prompt_templates = PromptTemplates()
    
    def analyze_chunk_map(self, chunk: List[OKREntry], chunk_id: int) -> Dict:
        """
        MAP phase: Analyze a single chunk of OKRs
        
        Args:
            chunk: List of OKR entries to analyze
            chunk_id: Identifier for this chunk
        
        Returns:
            Dictionary with themes, quality scores, and insights for this chunk
        """
        print(f"Processing chunk {chunk_id} with {len(chunk)} OKRs...")
        
        okr_texts = [entry.to_text() for entry in chunk]
        
        try:
            themes_result = self.llm.generate_json(
                self.prompt_templates.theme_extraction_prompt(okr_texts[:30])
            )
            
            return {
                'chunk_id': chunk_id,
                'okr_count': len(chunk),
                'themes': themes_result.get('themes', []),
                'status': 'success'
            }
        except Exception as e:
            print(f"Error processing chunk {chunk_id}: {str(e)}")
            return {
                'chunk_id': chunk_id,
                'okr_count': len(chunk),
                'themes': [],
                'status': 'error',
                'error': str(e)
            }
    
    def aggregate_results_reduce(self, chunk_results: List[Dict]) -> Dict:
        """
        REDUCE phase: Merge and deduplicate results from all chunks
        
        Args:
            chunk_results: List of results from map phase
        
        Returns:
            Consolidated analysis results
        """
        print("Aggregating results from all chunks...")
        
        all_themes = []
        for result in chunk_results:
            if result['status'] == 'success':
                all_themes.extend(result.get('themes', []))
        
        if not all_themes:
            return {
                'themes': [],
                'total_okrs_analyzed': sum(r['okr_count'] for r in chunk_results),
                'status': 'no_themes_found'
            }
        
        try:
            consolidated = self.llm.generate_json(
                self.prompt_templates.reduce_themes_prompt(all_themes)
            )
            
            return {
                'themes': consolidated.get('themes', []),
                'total_okrs_analyzed': sum(r['okr_count'] for r in chunk_results),
                'chunks_processed': len(chunk_results),
                'status': 'success'
            }
        except Exception as e:
            print(f"Error in reduce phase: {str(e)}")
            return {
                'themes': all_themes[:20],
                'total_okrs_analyzed': sum(r['okr_count'] for r in chunk_results),
                'status': 'reduce_error',
                'error': str(e)
            }
    
    def extract_themes_parallel(self, chunks: List[List[OKREntry]], max_workers: int = 4) -> Dict:
        """
        Process all chunks in parallel and aggregate results
        
        Args:
            chunks: List of OKR chunks
            max_workers: Number of parallel workers
        
        Returns:
            Consolidated theme analysis
        """
        print(f"Starting parallel theme extraction with {max_workers} workers...")
        
        chunk_results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {
                executor.submit(self.analyze_chunk_map, chunk, i): i 
                for i, chunk in enumerate(chunks)
            }
            
            for future in tqdm(as_completed(future_to_chunk), total=len(chunks), desc="Processing chunks"):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    chunk_results.append(result)
                except Exception as e:
                    print(f"Chunk {chunk_id} failed: {str(e)}")
                    chunk_results.append({
                        'chunk_id': chunk_id,
                        'okr_count': len(chunks[chunk_id]),
                        'themes': [],
                        'status': 'error',
                        'error': str(e)
                    })
        
        chunk_results.sort(key=lambda x: x['chunk_id'])
        
        final_results = self.aggregate_results_reduce(chunk_results)
        final_results['chunk_results'] = chunk_results
        
        return final_results
    
    def assess_quality_single(self, okr: OKREntry) -> Dict:
        """
        Assess quality of a single OKR
        
        Args:
            okr: OKR entry to assess
        
        Returns:
            Quality assessment with scores and suggestions
        """
        try:
            result = self.llm.generate_json(
                self.prompt_templates.quality_assessment_prompt(okr.to_text())
            )
            result['entry_id'] = okr.entry_id
            result['team'] = okr.team
            result['quarter'] = okr.quarter
            return result
        except Exception as e:
            print(f"Error assessing OKR {okr.entry_id}: {str(e)}")
            return {
                'entry_id': okr.entry_id,
                'team': okr.team,
                'quarter': okr.quarter,
                'scores': {},
                'overall_score': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def assess_quality_batch(self, okrs: List[OKREntry], max_workers: int = 4) -> List[Dict]:
        """
        Assess quality of multiple OKRs in parallel
        
        Args:
            okrs: List of OKR entries
            max_workers: Number of parallel workers
        
        Returns:
            List of quality assessments
        """
        print(f"Assessing quality for {len(okrs)} OKRs...")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_okr = {
                executor.submit(self.assess_quality_single, okr): okr 
                for okr in okrs
            }
            
            for future in tqdm(as_completed(future_to_okr), total=len(okrs), desc="Quality assessment"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    okr = future_to_okr[future]
                    print(f"Failed to assess OKR {okr.entry_id}: {str(e)}")
        
        return results
    
    def analyze_team_alignment(self, team_okrs: Dict[str, List[OKREntry]]) -> Dict:
        """
        Analyze alignment across teams
        
        Args:
            team_okrs: Dictionary mapping team names to their OKRs
        
        Returns:
            Alignment analysis with gaps and opportunities
        """
        print("Analyzing cross-team alignment...")
        
        team_objectives = {}
        for team, okrs in team_okrs.items():
            team_objectives[team] = [okr.objective for okr in okrs[:10]]
        
        try:
            result = self.llm.generate_json(
                self.prompt_templates.alignment_analysis_prompt(team_objectives)
            )
            return result
        except Exception as e:
            print(f"Error in alignment analysis: {str(e)}")
            return {
                'alignments': [],
                'gaps': [],
                'conflicts': [],
                'collaboration_opportunities': [],
                'status': 'error',
                'error': str(e)
            }
    
    def generate_summary_report(self, theme_results: Dict, quality_results: List[Dict], 
                               alignment_results: Dict) -> str:
        """
        Generate executive summary report
        
        Args:
            theme_results: Results from theme extraction
            quality_results: Results from quality assessment
            alignment_results: Results from alignment analysis
        
        Returns:
            Formatted summary report
        """
        avg_quality = sum(r.get('overall_score', 0) for r in quality_results) / len(quality_results) if quality_results else 0
        
        prompt = f"""Generate an executive summary report for OKR analysis:

**Theme Analysis:**
- Total themes identified: {len(theme_results.get('themes', []))}
- Top 5 themes: {', '.join([t['name'] for t in theme_results.get('themes', [])[:5]])}

**Quality Assessment:**
- Total OKRs assessed: {len(quality_results)}
- Average quality score: {avg_quality:.1f}/10
- High quality OKRs (8+): {sum(1 for r in quality_results if r.get('overall_score', 0) >= 8)}
- Needs improvement (<6): {sum(1 for r in quality_results if r.get('overall_score', 0) < 6)}

**Alignment Analysis:**
- Strong alignments found: {len(alignment_results.get('alignments', []))}
- Strategic gaps identified: {len(alignment_results.get('gaps', []))}
- Potential conflicts: {len(alignment_results.get('conflicts', []))}

Create a concise executive summary (300-400 words) highlighting:
1. Key strategic themes across the organization
2. Overall OKR quality assessment
3. Critical alignment insights
4. Top 3 recommendations for improvement
"""
        
        try:
            summary = self.llm.generate(prompt, temperature=0.5)
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"
