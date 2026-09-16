import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from ml_engine import detect_anomalies, generate_forecast
import json

# Try importing GenAI SDK for the mock/real implementation
try:
    import google.generativeai as genai
    # Configure with the user-provided API key (loaded securely from environment or set placeholder)
    import os
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Digital Shram Sankalp Dashboard (Advanced)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium UI
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    .stMetric {
        background-color: #1E232E;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stMetric:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_analyze_data():
    if not os.path.exists('workers_data.csv'):
        import data_pipeline
        df = data_pipeline.generate_mock_data(10000)
    else:
        df = pd.read_csv('workers_data.csv')
    
    # Run Tri-Modal ML Engine
    df_analyzed = detect_anomalies(df)
    forecast_df = generate_forecast(df_analyzed)
    return df_analyzed, forecast_df

def main():
    st.sidebar.title("Next-Gen Command Center")
    st.sidebar.markdown("---")
    
    view = st.sidebar.radio(
        "Navigation",
        [
            "Migration & Forecasting", 
            "Skill & Wage Analytics", 
            "Data Integrity Radar",
            "DPI API Gateway",
            "GenAI Data Chat"
        ]
    )
    
    # Load Data
    with st.spinner("Loading Tri-Modal AI pipelines..."):
        df, forecast_df = load_and_analyze_data()
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"Total Records: {len(df):,}")
    st.sidebar.warning(f"Anomalies Detected: {df['Is_Anomaly'].sum():,}")

    if view == "Migration & Forecasting":
        show_migration_forecasting(df, forecast_df)
    elif view == "Skill & Wage Analytics":
        show_skill_wage_analytics(df)
    elif view == "Data Integrity Radar":
        show_data_integrity(df)
    elif view == "DPI API Gateway":
        show_api_gateway(df)
    elif view == "GenAI Data Chat":
        show_genai_chat(df)

def show_migration_forecasting(df, forecast_df):
    st.title("Migration & Forecasting (LSTM)")
    st.markdown("Analyze current movement corridors and view 6-month predictive forecasts.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Historical vs LSTM Forecast Volume")
        fig_line = px.line(
            forecast_df, 
            x='Month_Year_Ts', 
            y='Predicted_Volume', 
            color='Type',
            title="Workforce Migration Volume Over Time",
            color_discrete_map={'Historical': '#1E90FF', 'Forecast': '#00FA9A'}
        )
        # Add dashed line for forecast
        fig_line.update_traces(patch={"line": {"dash": "dash"}}, selector={"legendgroup": "Forecast"})
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#FAFAFA")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("Top Migration Corridors")
        mig_df = df[df['State_Origin'] != df['State_Current']]
        mig_counts = mig_df.groupby(['State_Origin', 'State_Current']).size().reset_index(name='Count')
        top_mig = mig_counts.sort_values('Count', ascending=False).head(10)
        
        fig_bar = px.bar(
            top_mig, 
            x='Count', 
            y='State_Current', 
            color='State_Origin',
            orientation='h',
            title="Destination States vs Origin",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#FAFAFA")
        st.plotly_chart(fig_bar, use_container_width=True)

def show_skill_wage_analytics(df):
    st.title("Skill & Wage Analytics")
    # Filter ML-flagged anomalies, and forcefully drop extreme visual outliers for the chart
    normal_df = df[(~df['Is_Anomaly']) & (df['Daily_Wage'] <= 1500)]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Average Wage by Skill Level")
        wage_skill = normal_df.groupby('Skill_Level')['Daily_Wage'].mean().reset_index()
        skill_order = ["Unskilled", "Semi-skilled", "Skilled", "Highly-skilled"]
        wage_skill['Skill_Level'] = pd.Categorical(wage_skill['Skill_Level'], categories=skill_order, ordered=True)
        wage_skill = wage_skill.sort_values('Skill_Level')
        
        fig_wage = px.line(
            wage_skill, 
            x='Skill_Level', 
            y='Daily_Wage',
            markers=True,
            title="Wage Progression Matrix",
            color_discrete_sequence=['#00BFFF']
        )
        fig_wage.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#FAFAFA")
        st.plotly_chart(fig_wage, use_container_width=True)
        
    with col2:
        st.subheader("Wage Distribution by Sector")
        fig_box = px.box(
            normal_df, 
            x='Occupation_Sector', 
            y='Daily_Wage', 
            color='Occupation_Sector',
            title="Sectoral Wage Disparities",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#FAFAFA", showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

def show_data_integrity(df):
    st.title("Data Integrity Radar (Tri-Modal)")
    st.markdown("Features Statistical (Isolation Forest) and Deep Learning (Autoencoder) layers.")
    
    anomalies = df[df['Is_Anomaly']].copy()
    if 'DL_Reconstruction_Error' in anomalies.columns:
        anomalies = anomalies.sort_values(by='DL_Reconstruction_Error', ascending=False)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Stat Anomalies", f"{df['Is_Anomaly_Stat'].sum():,}", delta_color="inverse")
    col3.metric("DL Anomalies", f"{df['Is_Anomaly_DL'].sum():,}", delta_color="inverse")
    col4.metric("Data Health", f"{(1 - len(anomalies)/len(df))*100:.1f}%")
    
    st.subheader("Top 'At-Risk' Data Entries (Explainable AI)")
    
    # Download Button for Clean Data
    clean_df = df[~df['Is_Anomaly']].copy()
    csv = clean_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Cleaned Dataset (CSV)",
        data=csv,
        file_name='cleansed_eshram_data.csv',
        mime='text/csv',
        help="Download the verified, ML-cleared dataset for downstream processing."
    )
    
    st.dataframe(
        anomalies[['UAN', 'Age', 'Skill_Level', 'Daily_Wage', 'Occupation_Sector', 'Anomaly_Reason']].head(50),
        use_container_width=True,
        hide_index=True
    )
    
    colA, colB = st.columns(2)
    with colA:
        fig_scatter2 = px.scatter(
            df, x='Age', y='Daily_Wage', color='Is_Anomaly_DL',
            title="Age vs Wage (Autoencoder Outliers)",
            color_discrete_map={True: '#FF4B4B', False: '#1E90FF'}
        )
        fig_scatter2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#FAFAFA")
        st.plotly_chart(fig_scatter2, use_container_width=True)

def show_api_gateway(df):
    st.title("DPI API Gateway")
    st.markdown("Simulates how external platforms (e.g. Shram Suvidha) can securely query cleansed eShram data via REST endpoints.")
    
    st.subheader("Endpoint: `GET /api/v1/workers/cleansed`")
    st.text("Returns the top 5 cleansed (non-anomalous) worker profiles as a JSON response.")
    
    clean_df = df[~df['Is_Anomaly']].head(5)
    # Mask UAN slightly more for API output simulation
    clean_df['UAN_Masked'] = clean_df['UAN'].apply(lambda x: x[:-4] + "****")
    
    api_response = {
        "status": "success",
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_returned": len(clean_df),
        "data": clean_df[['UAN_Masked', 'Age', 'State_Current', 'Occupation_Sector', 'Skill_Level']].to_dict(orient='records')
    }
    
    st.json(api_response)

def show_genai_chat(df):
    st.title("GenAI Data Chat (Live/Resilient)")
    st.markdown("Query your data using natural language powered by Google Gemini, with a robust offline fallback.")
    
    # Initialize session state for chat history
    if 'chat_response' not in st.session_state:
        st.session_state['chat_response'] = None
    
    user_query = st.text_input("Ask a question about the dataset (e.g., 'Which states have the most anomalies?'):")
    
    if st.button("Generate Insight"):
        if not user_query:
            st.warning("Please enter a question.")
            return
            
        if not GENAI_AVAILABLE:
            st.error("Google Generative AI SDK is not installed.")
            return
            
        with st.spinner("Analyzing data with Gemini..."):
            try:
                total_records = len(df)
                total_anomalies = df['Is_Anomaly'].sum()
                
                mig_anomalies = df[df['Is_Anomaly'] & (df['State_Origin'] != df['State_Current'])]
                top_states = mig_anomalies['State_Current'].value_counts().head(3).to_dict()
                
                context = f"""
                You are an AI assistant analyzing a workforce dataset for the Ministry of Labour & Employment.
                Dataset Overview:
                - Total Records: {total_records}
                - Total Anomalies Flagged: {total_anomalies}
                - Top states where migrating anomalous workers are located: {top_states}
                
                User Query: {user_query}
                
                Please provide a concise, professional answer based ONLY on the data overview provided above. 
                If the query asks for something outside this context, politely state that you can only analyze the provided dataset summary.
                """
                
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(context)
                
                st.session_state['chat_response'] = f"**Gemini AI Insight:**\n\n{response.text}"
                
            except Exception as e:
                # Intelligent Offline Fallback
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower() or "connection" in error_msg.lower() or "closed" in error_msg.lower():
                    # Compute offline insight
                    worst_state = df[df['Is_Anomaly']]['State_Current'].value_counts().index[0]
                    worst_sector = df[df['Is_Anomaly']]['Occupation_Sector'].value_counts().index[0]
                    
                    fallback_text = f"**Analysis (Edge-Compute Mode Active):** Cloud uplink unavailable. Synthesizing insights directly from local verified records... The data reveals that **{worst_state}** currently accounts for the highest volume of flagged anomalies. The most anomalous sector overall is **{worst_sector}**."
                    st.session_state['chat_response'] = fallback_text
                else:
                    st.session_state['chat_response'] = f"**Error:** Failed to generate insight: {e}"
    
    # Display the cached response
    if st.session_state['chat_response']:
        st.success("Query processed.")
        st.markdown(st.session_state['chat_response'])

if __name__ == "__main__":
    main()
