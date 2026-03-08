"""
Chart Components for Streamlit Dashboard
Reusable visualization components using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict
import numpy as np


def create_theme_bar_chart(themes: List[Dict]) -> go.Figure:
    """Create horizontal bar chart for themes"""
    df = pd.DataFrame(themes)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No themes data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df = df.nlargest(15, 'count')
    
    fig = px.bar(
        df,
        y='theme_name' if 'theme_name' in df.columns else 'name',
        x='count',
        orientation='h',
        title='Top Themes Across Organization',
        labels={'count': 'Number of OKRs', 'theme_name': 'Theme'},
        color='count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def create_theme_sunburst(themes: List[Dict]) -> go.Figure:
    """Create sunburst chart for hierarchical theme visualization"""
    if not themes:
        fig = go.Figure()
        fig.add_annotation(
            text="No themes data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    labels = ['All Themes'] + [t.get('theme_name', t.get('name', 'Unknown')) for t in themes[:15]]
    parents = [''] + ['All Themes'] * min(15, len(themes))
    values = [sum(t.get('count', 0) for t in themes[:15])] + [t.get('count', 1) for t in themes[:15]]
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
    ))
    
    fig.update_layout(
        title='Theme Distribution Across Organization',
        height=600
    )
    
    return fig


def create_quality_distribution(quality_scores: List[Dict]) -> go.Figure:
    """Create histogram of quality score distribution"""
    if not quality_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No quality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    scores = [q['overall_score'] for q in quality_scores if 'overall_score' in q]
    
    fig = go.Figure(data=[go.Histogram(
        x=scores,
        nbinsx=20,
        marker_color='rgb(55, 83, 109)'
    )])
    
    fig.update_layout(
        title='OKR Quality Score Distribution',
        xaxis_title='Quality Score',
        yaxis_title='Number of OKRs',
        height=400
    )
    
    return fig


def create_quality_by_team(quality_scores: List[Dict]) -> go.Figure:
    """Create box plot of quality scores by team"""
    if not quality_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No quality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df = pd.DataFrame(quality_scores)
    
    teams = df['team'].unique()
    
    fig = go.Figure()
    
    for team in teams:
        team_scores = df[df['team'] == team]['overall_score']
        fig.add_trace(go.Box(
            y=team_scores,
            name=team,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title='Quality Score Distribution by Team',
        yaxis_title='Quality Score',
        xaxis_title='Team',
        height=500,
        showlegend=False
    )
    
    return fig


def create_quality_radar(avg_scores: Dict) -> go.Figure:
    """Create radar chart for average quality dimensions"""
    if not avg_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No quality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    categories = ['Clarity', 'Measurability', 'Ambition', 'Alignment', 'Actionability']
    values = [
        avg_scores.get('clarity', 0),
        avg_scores.get('measurability', 0),
        avg_scores.get('ambition', 0),
        avg_scores.get('alignment', 0),
        avg_scores.get('actionability', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Average Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title='Average Quality Scores by Dimension',
        height=500
    )
    
    return fig


def create_alignment_heatmap(alignment_matrix: Dict) -> go.Figure:
    """Create heatmap for team alignment scores"""
    if not alignment_matrix or 'matrix' not in alignment_matrix:
        fig = go.Figure()
        fig.add_annotation(
            text="No alignment data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    teams = alignment_matrix['teams']
    matrix = alignment_matrix['matrix']
    
    z_values = []
    for team_a in teams:
        row = []
        for team_b in teams:
            row.append(matrix.get(team_a, {}).get(team_b, 0))
        z_values.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=teams,
        y=teams,
        colorscale='RdYlGn',
        zmid=0.5,
        text=np.round(z_values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Alignment Score")
    ))
    
    fig.update_layout(
        title='Cross-Team Alignment Heatmap',
        xaxis_title='Team',
        yaxis_title='Team',
        height=600,
        width=800
    )
    
    return fig


def create_quality_trends(quality_scores: List[Dict]) -> go.Figure:
    """Create line chart showing quality trends by quarter"""
    if not quality_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No quality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df = pd.DataFrame(quality_scores)
    
    quarter_stats = df.groupby('quarter')['overall_score'].agg(['mean', 'count']).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=quarter_stats['quarter'],
        y=quarter_stats['mean'],
        mode='lines+markers',
        name='Average Quality Score',
        line=dict(color='rgb(55, 83, 109)', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Quality Score Trends by Quarter',
        xaxis_title='Quarter',
        yaxis_title='Average Quality Score',
        yaxis_range=[0, 10],
        height=400
    )
    
    return fig


def create_team_comparison(quality_scores: List[Dict], top_n: int = 10) -> go.Figure:
    """Create grouped bar chart comparing teams across quality dimensions"""
    if not quality_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No quality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df = pd.DataFrame(quality_scores)
    
    team_avg = df.groupby('team').agg({
        'clarity_score': 'mean',
        'measurability_score': 'mean',
        'ambition_score': 'mean',
        'alignment_score': 'mean',
        'actionability_score': 'mean',
        'overall_score': 'mean'
    }).reset_index()
    
    team_avg = team_avg.nlargest(top_n, 'overall_score')
    
    fig = go.Figure()
    
    dimensions = ['clarity_score', 'measurability_score', 'ambition_score', 
                 'alignment_score', 'actionability_score']
    dimension_names = ['Clarity', 'Measurability', 'Ambition', 'Alignment', 'Actionability']
    
    for dim, name in zip(dimensions, dimension_names):
        fig.add_trace(go.Bar(
            name=name,
            x=team_avg['team'],
            y=team_avg[dim]
        ))
    
    fig.update_layout(
        title=f'Top {top_n} Teams - Quality Dimension Comparison',
        xaxis_title='Team',
        yaxis_title='Score',
        barmode='group',
        height=500,
        yaxis_range=[0, 10]
    )
    
    return fig
