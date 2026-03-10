"""
Storage Module for Analysis Results
Handles SQLite database and JSON caching
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


class ResultsStorage:
    """Manages storage of analysis results in SQLite"""
    
    def __init__(self, db_path: str = "./data/okr_results.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS okrs (
                entry_id INTEGER PRIMARY KEY,
                team TEXT,
                quarter TEXT,
                objective TEXT,
                key_result_1 TEXT,
                key_result_2 TEXT,
                key_result_3 TEXT,
                quality_level TEXT,
                raw_text TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_scores (
                entry_id INTEGER PRIMARY KEY,
                team TEXT,
                quarter TEXT,
                clarity_score REAL,
                measurability_score REAL,
                ambition_score REAL,
                alignment_score REAL,
                actionability_score REAL,
                overall_score REAL,
                strengths TEXT,
                weaknesses TEXT,
                suggestions TEXT,
                FOREIGN KEY (entry_id) REFERENCES okrs(entry_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS themes (
                theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_name TEXT,
                description TEXT,
                count INTEGER,
                examples TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alignment_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_a TEXT,
                team_b TEXT,
                alignment_score REAL,
                analysis_date TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT,
                total_okrs INTEGER,
                total_themes INTEGER,
                avg_quality_score REAL,
                status TEXT
            )
        """)
        
        self.conn.commit()
    
    def store_okrs(self, okrs: List[Dict]):
        """Store OKR entries in database"""
        cursor = self.conn.cursor()
        
        for okr in okrs:
            cursor.execute("""
                INSERT OR REPLACE INTO okrs 
                (entry_id, team, quarter, objective, key_result_1, key_result_2, 
                 key_result_3, quality_level, raw_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                okr['entry_id'],
                okr['team'],
                okr['quarter'],
                okr['objective'],
                okr['key_result_1'],
                okr['key_result_2'],
                okr['key_result_3'],
                okr['quality_level'],
                okr['raw_text']
            ))
        
        self.conn.commit()
        print(f"Stored {len(okrs)} OKRs in database")
    
    def store_quality_scores(self, quality_results: List[Dict]):
        """Store quality assessment results"""
        cursor = self.conn.cursor()
        
        for result in quality_results:
            scores = result.get('scores', {})
            cursor.execute("""
                INSERT OR REPLACE INTO quality_scores
                (entry_id, team, quarter, clarity_score, measurability_score, 
                 ambition_score, alignment_score, actionability_score, overall_score,
                 strengths, weaknesses, suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.get('entry_id'),
                result.get('team'),
                result.get('quarter'),
                scores.get('clarity', 0),
                scores.get('measurability', 0),
                scores.get('ambition', 0),
                scores.get('alignment', 0),
                scores.get('actionability', 0),
                result.get('overall_score', 0),
                json.dumps(result.get('strengths', [])),
                json.dumps(result.get('weaknesses', [])),
                json.dumps(result.get('improvement_suggestions', []))
            ))
        
        self.conn.commit()
        print(f"Stored {len(quality_results)} quality scores in database")
    
    def store_themes(self, themes: List[Dict]):
        """Store theme analysis results"""
        cursor = self.conn.cursor()
        
        cursor.execute("DELETE FROM themes")
        
        for theme in themes:
            cursor.execute("""
                INSERT INTO themes (theme_name, description, count, examples)
                VALUES (?, ?, ?, ?)
            """, (
                theme['name'],
                theme['description'],
                theme.get('total_count', theme.get('count', 0)),
                json.dumps(theme.get('example_objectives', []))
            ))
        
        self.conn.commit()
        print(f"Stored {len(themes)} themes in database")
    
    def store_alignment_scores(self, alignments: List[Dict]):
        """Store team alignment scores"""
        cursor = self.conn.cursor()
        
        analysis_date = datetime.now().isoformat()
        
        for alignment in alignments:
            cursor.execute("""
                INSERT INTO alignment_scores (team_a, team_b, alignment_score, analysis_date)
                VALUES (?, ?, ?, ?)
            """, (
                alignment['team_a'],
                alignment['team_b'],
                alignment['alignment_score'],
                analysis_date
            ))
        
        self.conn.commit()
        print(f"Stored {len(alignments)} alignment scores in database")
    
    def record_analysis_run(self, total_okrs: int, total_themes: int, 
                           avg_quality: float, status: str = "completed"):
        """Record an analysis run"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_runs (run_date, total_okrs, total_themes, 
                                      avg_quality_score, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            total_okrs,
            total_themes,
            avg_quality,
            status
        ))
        
        self.conn.commit()
    
    def get_all_okrs(self) -> List[Dict]:
        """Retrieve all OKRs from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM okrs")
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_quality_scores(self, team: Optional[str] = None) -> List[Dict]:
        """Retrieve quality scores, optionally filtered by team"""
        cursor = self.conn.cursor()
        
        if team:
            cursor.execute("SELECT * FROM quality_scores WHERE team = ?", (team,))
        else:
            cursor.execute("SELECT * FROM quality_scores")
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            result['strengths'] = json.loads(result['strengths']) if result['strengths'] else []
            result['weaknesses'] = json.loads(result['weaknesses']) if result['weaknesses'] else []
            result['suggestions'] = json.loads(result['suggestions']) if result['suggestions'] else []
            results.append(result)
        
        return results
    
    def get_themes(self) -> List[Dict]:
        """Retrieve all themes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM themes ORDER BY count DESC")
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            result['examples'] = json.loads(result['examples']) if result['examples'] else []
            results.append(result)
        
        return results
    
    def get_alignment_matrix(self) -> Dict:
        """Retrieve latest alignment scores"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT team_a, team_b, alignment_score 
            FROM alignment_scores 
            ORDER BY analysis_date DESC
        """)
        
        rows = cursor.fetchall()
        
        teams = set()
        for row in rows:
            teams.add(row[0])
            teams.add(row[1])
        
        teams = sorted(list(teams))
        matrix = {team: {} for team in teams}
        
        for team_a, team_b, score in rows:
            matrix[team_a][team_b] = score
            matrix[team_b][team_a] = score
        
        for team in teams:
            matrix[team][team] = 1.0
        
        return {
            'matrix': matrix,
            'teams': teams
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()
