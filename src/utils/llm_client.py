"""
LLM Client Abstraction Layer
Provides unified interface for Gemini (can be swapped for Azure OpenAI later)
"""

import os
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Abstraction layer for LLM interactions"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 8000) -> str:
        """
        Generate text using Gemini with retry logic
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_json(self, prompt: str, temperature: float = 0.3) -> Dict:
        """
        Generate structured JSON response
        
        Args:
            prompt: Input prompt (should request JSON output)
            temperature: Sampling temperature
        
        Returns:
            Parsed JSON response
        """
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        import json
        return json.loads(response.text)
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return self.model.count_tokens(text).total_tokens


class PromptTemplates:
    """Centralized prompt templates for OKR analysis"""
    
    @staticmethod
    def theme_extraction_prompt(okr_texts: List[str]) -> str:
        """Prompt for extracting themes from OKRs"""
        okr_list = "\n\n".join(okr_texts)
        return f"""You are an expert business analyst specializing in OKR (Objectives and Key Results) analysis.

Analyze the following OKRs and identify the main strategic themes and focus areas:

{okr_list}

Extract the top recurring themes across these OKRs. For each theme:
1. Provide a clear theme name (2-4 words)
2. Brief description (1 sentence)
3. Count how many OKRs relate to this theme
4. List example OKRs that exemplify this theme

Return your analysis as a JSON array with this structure:
{{
  "themes": [
    {{
      "name": "Theme name",
      "description": "Brief description",
      "count": 5,
      "example_objectives": ["objective 1", "objective 2"]
    }}
  ]
}}

Focus on strategic business themes, not implementation details."""
    
    @staticmethod
    def quality_assessment_prompt(okr_text: str) -> str:
        """Prompt for assessing OKR quality"""
        return f"""You are an OKR quality expert. Evaluate this OKR against best practices:

{okr_text}

Rate the OKR on these dimensions (1-10 scale):

1. **Clarity**: Is the objective clear and easy to understand?
2. **Measurability**: Are the key results specific, measurable, and quantifiable?
3. **Ambition**: Is it challenging yet achievable (not too easy, not impossible)?
4. **Alignment**: Does it appear to support broader organizational goals?
5. **Actionability**: Can teams clearly understand what actions to take?

Return your assessment as JSON:
{{
  "scores": {{
    "clarity": 8,
    "measurability": 9,
    "ambition": 7,
    "alignment": 8,
    "actionability": 8
  }},
  "overall_score": 8.0,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "improvement_suggestions": ["suggestion 1", "suggestion 2"]
}}"""
    
    @staticmethod
    def alignment_analysis_prompt(team_okrs: Dict[str, List[str]]) -> str:
        """Prompt for analyzing cross-team alignment"""
        teams_text = ""
        for team, okrs in team_okrs.items():
            teams_text += f"\n\n**{team} Team:**\n"
            teams_text += "\n".join(f"- {okr}" for okr in okrs[:5])
        
        return f"""You are a strategic alignment expert. Analyze the alignment between these teams' OKRs:

{teams_text}

Identify:
1. **Strong Alignments**: Where teams are working toward complementary goals
2. **Gaps**: Strategic areas that appear under-resourced or missing
3. **Conflicts**: Where teams might have competing priorities
4. **Opportunities**: Where teams could collaborate more effectively

Return your analysis as JSON:
{{
  "alignments": [
    {{
      "teams": ["Team A", "Team B"],
      "description": "How they align",
      "strength": "high/medium/low"
    }}
  ],
  "gaps": [
    {{
      "area": "Strategic area",
      "description": "What's missing",
      "impact": "high/medium/low"
    }}
  ],
  "conflicts": [
    {{
      "teams": ["Team A", "Team B"],
      "description": "Nature of conflict",
      "severity": "high/medium/low"
    }}
  ],
  "collaboration_opportunities": [
    {{
      "teams": ["Team A", "Team B"],
      "opportunity": "Description",
      "potential_impact": "Expected benefit"
    }}
  ]
}}"""
    
    @staticmethod
    def reduce_themes_prompt(chunk_themes: List[Dict]) -> str:
        """Prompt for aggregating themes from multiple chunks"""
        themes_json = json.dumps(chunk_themes, indent=2)
        return f"""You are synthesizing theme analysis results from multiple chunks of OKRs.

Here are the themes identified in each chunk:

{themes_json}

Your task:
1. Merge similar/duplicate themes across chunks
2. Consolidate counts and examples
3. Rank themes by prevalence
4. Return the top 15-20 most significant themes

Return consolidated themes as JSON:
{{
  "themes": [
    {{
      "name": "Consolidated theme name",
      "description": "Merged description",
      "total_count": 25,
      "example_objectives": ["example 1", "example 2", "example 3"]
    }}
  ]
}}

Sort themes by total_count in descending order."""
