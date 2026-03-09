"""
Main Streamlit Dashboard for OKR Analysis
Interactive web interface for exploring OKR insights
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.storage import ResultsStorage
from src.app.components.charts import (
    create_theme_bar_chart,
    create_theme_sunburst,
    create_quality_distribution,
    create_quality_by_team,
    create_quality_radar,
    create_alignment_heatmap,
    create_quality_trends,
    create_team_comparison
)
from src.search.vector_search import OKRVectorSearch


st.set_page_config(
    page_title="OKR Analysis Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_storage():
    """Load database connection"""
    return ResultsStorage()


@st.cache_resource
def load_vector_search():
    """Load vector search engine"""
    try:
        return OKRVectorSearch()
    except Exception as e:
        st.warning(f"Vector search not available: {str(e)}")
        return None


def main():
    st.title("🎯 Enterprise OKR Analysis Dashboard")
    st.markdown("---")
    
    storage = load_storage()
    vector_search = load_vector_search()
    
    all_okrs = storage.get_all_okrs()
    
    if not all_okrs:
        st.warning("⚠️ No OKR data found. Please run the analysis script first.")
        st.code("python scripts/run_analysis.py", language="bash")
        return
    
    all_quality_scores = storage.get_quality_scores()
    all_themes = storage.get_themes()
    alignment_matrix = storage.get_alignment_matrix()
    
    teams = sorted(list(set(okr['team'] for okr in all_okrs)))
    quarters = sorted(list(set(okr['quarter'] for okr in all_okrs)))
    
    with st.sidebar:
        st.header("🔍 Filters")
        
        selected_teams = st.multiselect(
            "Select Teams",
            options=teams,
            default=teams[:5] if len(teams) > 5 else teams
        )
        
        selected_quarter = st.selectbox(
            "Quarter",
            options=["All"] + quarters
        )
        
        st.markdown("---")
        st.markdown("### 📊 Dataset Info")
        st.metric("Total OKRs", len(all_okrs))
        st.metric("Teams", len(teams))
        st.metric("Quarters", len(quarters))
    
    filtered_okrs = [
        okr for okr in all_okrs
        if (not selected_teams or okr['team'] in selected_teams) and
           (selected_quarter == "All" or okr['quarter'] == selected_quarter)
    ]
    
    filtered_quality = [
        q for q in all_quality_scores
        if (not selected_teams or q['team'] in selected_teams) and
           (selected_quarter == "All" or q['quarter'] == selected_quarter)
    ]
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "🎨 Theme Analysis",
        "⭐ Quality Metrics",
        "🔗 Alignment & Gaps",
        "🔍 Search"
    ])
    
    with tab1:
        st.header("Executive Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total OKRs", len(filtered_okrs))
        
        with col2:
            st.metric("Teams Analyzed", len(selected_teams) if selected_teams else len(teams))
        
        with col3:
            if filtered_quality:
                avg_quality = sum(q['overall_score'] for q in filtered_quality) / len(filtered_quality)
                st.metric("Avg Quality Score", f"{avg_quality:.1f}/10")
            else:
                st.metric("Avg Quality Score", "N/A")
        
        with col4:
            st.metric("Themes Identified", len(all_themes))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Quality Distribution")
            if filtered_quality:
                fig = create_quality_distribution(filtered_quality)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No quality data available")
        
        with col2:
            st.subheader("Top Themes")
            if all_themes:
                fig = create_theme_bar_chart(all_themes[:10])
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No theme data available")
    
    with tab2:
        st.header("Theme Analysis")
        
        if all_themes:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Theme Distribution")
                fig = create_theme_sunburst(all_themes)
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.subheader("Theme Statistics")
                st.metric("Total Themes", len(all_themes))
                
                if all_themes:
                    top_theme = all_themes[0]
                    st.metric(
                        "Most Common Theme",
                        top_theme.get('theme_name', top_theme.get('name', 'N/A')),
                        f"{top_theme.get('count', 0)} OKRs"
                    )
            
            st.markdown("---")
            st.subheader("Theme Details")
            
            theme_df = pd.DataFrame([
                {
                    'Theme': t.get('theme_name', t.get('name', 'Unknown')),
                    'Description': t.get('description', 'N/A'),
                    'Count': t.get('count', 0)
                }
                for t in all_themes[:20]
            ])
            
            st.dataframe(theme_df, width="stretch", height=400)
            
            with st.expander("View Example Objectives"):
                selected_theme = st.selectbox(
                    "Select Theme",
                    options=[t.get('theme_name', t.get('name', 'Unknown')) for t in all_themes[:20]]
                )
                
                theme_data = next(
                    (t for t in all_themes if t.get('theme_name', t.get('name')) == selected_theme),
                    None
                )
                
                if theme_data and 'example_objectives' in theme_data:
                    for i, example in enumerate(theme_data['example_objectives'][:5], 1):
                        st.markdown(f"{i}. {example}")
        else:
            st.info("No theme data available. Run analysis first.")
    
    with tab3:
        st.header("Quality Metrics")
        
        if filtered_quality:
            col1, col2, col3 = st.columns(3)
            
            avg_quality = sum(q['overall_score'] for q in filtered_quality) / len(filtered_quality)
            high_quality = sum(1 for q in filtered_quality if q['overall_score'] >= 8)
            needs_improvement = sum(1 for q in filtered_quality if q['overall_score'] < 6)
            
            with col1:
                st.metric("Average Score", f"{avg_quality:.1f}/10")
            
            with col2:
                st.metric("High Quality (8+)", high_quality)
            
            with col3:
                st.metric("Needs Improvement (<6)", needs_improvement)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Quality by Team")
                fig = create_quality_by_team(filtered_quality)
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.subheader("Quality Dimensions")
                avg_scores = {
                    'clarity': sum(q['clarity_score'] for q in filtered_quality) / len(filtered_quality),
                    'measurability': sum(q['measurability_score'] for q in filtered_quality) / len(filtered_quality),
                    'ambition': sum(q['ambition_score'] for q in filtered_quality) / len(filtered_quality),
                    'alignment': sum(q['alignment_score'] for q in filtered_quality) / len(filtered_quality),
                    'actionability': sum(q['actionability_score'] for q in filtered_quality) / len(filtered_quality)
                }
                fig = create_quality_radar(avg_scores)
                st.plotly_chart(fig, width="stretch")
            
            st.markdown("---")
            st.subheader("Team Comparison")
            fig = create_team_comparison(filtered_quality, top_n=10)
            st.plotly_chart(fig, width="stretch")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top Quality OKRs")
                top_okrs = sorted(filtered_quality, key=lambda x: x['overall_score'], reverse=True)[:5]
                
                for i, okr in enumerate(top_okrs, 1):
                    with st.expander(f"#{i} - {okr['team']} (Score: {okr['overall_score']:.1f})"):
                        okr_data = next((o for o in all_okrs if o['entry_id'] == okr['entry_id']), None)
                        if okr_data:
                            st.markdown(f"**Objective:** {okr_data['objective']}")
                            st.markdown(f"**Quarter:** {okr_data['quarter']}")
                            strengths = okr.get('strengths', [])
                            if isinstance(strengths, str):
                                import json
                                try:
                                    strengths = json.loads(strengths)
                                except:
                                    strengths = []
                            if strengths:
                                st.markdown("**Strengths:**")
                                for strength in strengths:
                                    st.markdown(f"- {strength}")
            
            with col2:
                st.subheader("⚠️ Needs Improvement")
                low_okrs = sorted(filtered_quality, key=lambda x: x['overall_score'])[:5]
                
                for i, okr in enumerate(low_okrs, 1):
                    with st.expander(f"#{i} - {okr['team']} (Score: {okr['overall_score']:.1f})"):
                        okr_data = next((o for o in all_okrs if o['entry_id'] == okr['entry_id']), None)
                        if okr_data:
                            st.markdown(f"**Objective:** {okr_data['objective']}")
                            st.markdown(f"**Quarter:** {okr_data['quarter']}")
                            suggestions = okr.get('suggestions', [])
                            if isinstance(suggestions, str):
                                import json
                                try:
                                    suggestions = json.loads(suggestions)
                                except:
                                    suggestions = []
                            if suggestions:
                                st.markdown("**Suggestions:**")
                                for suggestion in suggestions:
                                    st.markdown(f"- {suggestion}")
        else:
            st.info("No quality data available. Run analysis first.")
    
    with tab4:
        st.header("Alignment & Collaboration")
        
        if alignment_matrix and alignment_matrix.get('teams'):
            st.subheader("Cross-Team Alignment Heatmap")
            fig = create_alignment_heatmap(alignment_matrix)
            st.plotly_chart(fig, width="stretch")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🤝 Strongest Alignments")
                
                matrix = alignment_matrix['matrix']
                teams_list = alignment_matrix['teams']
                
                alignments = []
                for i, team_a in enumerate(teams_list):
                    for j, team_b in enumerate(teams_list):
                        if i < j:
                            score = matrix[team_a][team_b]
                            alignments.append((team_a, team_b, score))
                
                alignments.sort(key=lambda x: x[2], reverse=True)
                
                for team_a, team_b, score in alignments[:10]:
                    st.markdown(f"**{team_a}** ↔️ **{team_b}**: {score:.2f}")
            
            with col2:
                st.subheader("⚠️ Weakest Alignments")
                
                for team_a, team_b, score in alignments[-10:]:
                    st.markdown(f"**{team_a}** ↔️ **{team_b}**: {score:.2f}")
        else:
            st.info("No alignment data available. Run analysis first.")
    
    with tab5:
        st.header("🔍 Semantic Search")
        
        if vector_search:
            search_query = st.text_input(
                "Search OKRs by meaning (e.g., 'improve customer satisfaction', 'reduce costs')",
                placeholder="Enter your search query..."
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search_team = st.selectbox("Filter by Team", ["All"] + teams)
            
            with col2:
                top_k = st.slider("Number of results", 5, 20, 10)
            
            if search_query:
                with st.spinner("Searching..."):
                    try:
                        results = vector_search.find_similar_okrs(
                            query=search_query,
                            top_k=top_k,
                            filter_team=None if search_team == "All" else search_team
                        )
                        
                        st.subheader(f"Found {len(results)} similar OKRs")
                        
                        for i, result in enumerate(results, 1):
                            metadata = result['metadata']
                            with st.expander(f"#{i} - {metadata['team']} | {metadata['quarter']} (Distance: {result.get('distance', 0):.3f})"):
                                st.markdown(f"**Objective:** {metadata['objective']}")
                                st.markdown("**Full OKR:**")
                                st.text(result['text'])
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
        else:
            st.info("Vector search is not initialized. Please run the analysis script to index OKRs.")
    
    st.markdown("---")
    st.caption("OKR Analysis System | Powered by Google Gemini Flash & ChromaDB")


if __name__ == "__main__":
    main()
