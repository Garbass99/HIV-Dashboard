# HIV_PMTCT_Dashboard.py - Complete Professional Dashboard with Enhanced Font Sizes
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from datetime import datetime
import io

warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="Gombe State HIV/PMTCT Situation Room",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with BOLD and ENLARGED fonts for better visibility
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 3rem !important;
        font-weight: bold !important;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 0.8rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #2a5298;
        font-weight: bold;
        font-size: 1.5rem !important;
    }
    
    /* KPI Box Styling with LARGER NUMBERS */
    .kpi-box {
        background: white;
        border-radius: 10px;
        padding: 1.5rem 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #2a5298;
        transition: transform 0.2s;
    }
    .kpi-box:hover {
        transform: scale(1.02);
    }
    .kpi-value {
        font-size: 3.2rem !important;
        font-weight: bold !important;
        color: #1e3c72;
        line-height: 1.2;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Reporting rate colors */
    .reporting-rate-good {
        color: #27ae60 !important;
        font-weight: bold !important;
        font-size: 3.2rem !important;
    }
    .reporting-rate-warning {
        color: #f39c12 !important;
        font-weight: bold !important;
        font-size: 3.2rem !important;
    }
    .reporting-rate-critical {
        color: #e74c3c !important;
        font-weight: bold !important;
        font-size: 3.2rem !important;
    }
    .positive-value {
        color: #e74c3c;
        font-weight: bold;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Metric styling for streamlit metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric label {
        font-weight: bold !important;
        font-size: 1.1rem !important;
        color: #666;
    }
    .stMetric .metric-value {
        font-weight: bold !important;
        font-size: 2.5rem !important;
        color: #1e3c72;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-weight: bold !important;
    }
    h1 {
        font-size: 2.5rem !important;
    }
    h2 {
        font-size: 2rem !important;
    }
    h3 {
        font-size: 1.75rem !important;
    }
    h4 {
        font-size: 1.5rem !important;
    }
    
    /* General text */
    .stMarkdown, p, li, div {
        font-size: 1rem;
    }
    
    /* Dataframe tables */
    .dataframe {
        font-size: 1rem !important;
    }
    .dataframe th {
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    .dataframe td {
        font-size: 1rem !important;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    
    /* Sidebar text */
    .css-1d391kg, .css-163ttbj, .css-1v0mbdj {
        font-size: 1rem !important;
    }
    
    /* Success and info messages */
    .stAlert {
        font-size: 1rem !important;
    }
    
    /* Button text */
    .stButton button {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA PROCESSING FUNCTIONS
# ============================================

def load_data(uploaded_file):
    """Load and process uploaded Excel file - Supports both .xlsx and .xls formats"""
    try:
        # Check file extension to use appropriate engine
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        else:
            # Try openpyxl first, then fallback to xlrd
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            except:
                df = pd.read_excel(uploaded_file, engine='xlrd')
        
        df.columns = df.columns.str.strip()
        
        # Convert Period to datetime
        if 'Period' in df.columns:
            df['Period'] = pd.to_datetime(df['Period'], errors='coerce')
            df['Year'] = df['Period'].dt.year
            df['Month'] = df['Period'].dt.month
            df['Month_Name'] = df['Period'].dt.strftime('%b %Y')
            # Add Quarter
            df['Quarter'] = df['Period'].dt.quarter
            df['Quarter_Year'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)
        
        # Convert numeric columns
        for col in df.columns:
            if col not in ['Period', 'State', 'LGA', 'Facility', 'organisationunitname', 'Year', 'Month', 'Month_Name', 'Quarter', 'Quarter_Year']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Filter out facilities with "delete" or "Delete" in name
        if 'Facility' in df.columns:
            df = df[~df['Facility'].astype(str).str.contains('delete|Delete', case=False, na=False)]
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def calculate_form_reporting_rate(df, form_indicators, form_name, facility_col='Facility', period_col='Period'):
    """Calculate reporting rate for specific forms based on presence of key indicators"""
    try:
        if facility_col not in df.columns or period_col not in df.columns:
            return None
        
        existing_indicators = [col for col in form_indicators if col in df.columns]
        if not existing_indicators:
            return None
        
        has_form = df[existing_indicators].notna().any(axis=1)
        df_submission = df[has_form].copy()
        df_submission['Submitted'] = 1
        
        all_periods = df[period_col].dropna().unique()
        all_facilities = df[facility_col].dropna().unique()
        
        if len(all_periods) == 0 or len(all_facilities) == 0:
            return None
        
        all_combinations = []
        for period in all_periods:
            for facility in all_facilities:
                all_combinations.append({period_col: period, facility_col: facility})
        
        all_combinations_df = pd.DataFrame(all_combinations)
        submission_status = df_submission.groupby([period_col, facility_col]).size().reset_index(name='Submitted')
        submission_status['Submitted'] = 1
        
        reporting_data = all_combinations_df.merge(submission_status, on=[period_col, facility_col], how='left')
        reporting_data['Submitted'] = reporting_data['Submitted'].fillna(0)
        
        reporting_rate = reporting_data.groupby(period_col).agg({
            'Submitted': ['mean', 'sum', 'count']
        }).reset_index()
        
        reporting_rate.columns = [period_col, 'Reporting_Rate', 'Actual_Reporting', 'Expected_Reporting']
        reporting_rate['Reporting_Rate'] = reporting_rate['Reporting_Rate'] * 100
        reporting_rate = reporting_rate.sort_values(period_col)
        
        return reporting_rate
    except Exception as e:
        return None

def get_reporting_status_color(rate):
    if rate >= 90:
        return "reporting-rate-good"
    elif rate >= 70:
        return "reporting-rate-warning"
    else:
        return "reporting-rate-critical"

def get_reporting_rate_from_column(df, column_name):
    """Extract reporting rate from column with proper handling of decimal vs percentage values"""
    if column_name in df.columns and 'Period' in df.columns:
        # Get data grouped by period
        reporting_data = df.groupby('Period')[column_name].mean().reset_index()
        reporting_data.columns = ['Period', 'Reporting_Rate']
        
        # Check if values are already percentages (0-100) or decimals (0-1)
        # If max value is <= 1, it's likely decimal format, convert to percentage
        if reporting_data['Reporting_Rate'].max() <= 1:
            reporting_data['Reporting_Rate'] = reporting_data['Reporting_Rate'] * 100
        
        reporting_data = reporting_data.sort_values('Period')
        return reporting_data
    return None

def find_column(df, possible_names):
    """Find which column name exists in dataframe"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def plot_grouped_bar_comparison(df, metrics_dict, title, period_col='Period', color_palette=None):
    """Plot grouped bar chart comparing multiple metrics side by side"""
    if period_col not in df.columns:
        return None
    
    valid_metrics = {name: col for name, col in metrics_dict.items() if col in df.columns}
    if not valid_metrics:
        return None
    
    trend_data = df.groupby(period_col)[list(valid_metrics.values())].sum().reset_index()
    trend_data = trend_data.sort_values(period_col)
    
    fig = go.Figure()
    
    if color_palette is None:
        color_palette = ['#1e3c72', '#2a5298', '#3b6cb0', '#4c86c8', '#5da0e0', '#6ebaf8', '#e74c3c']
    
    for idx, (name, col) in enumerate(valid_metrics.items()):
        # Use red color for positive indicators
        if 'Positive' in name or 'HIV positive' in name or 'positive' in name.lower():
            marker_color = '#e74c3c'
        else:
            marker_color = color_palette[idx % len(color_palette)]
        
        fig.add_trace(go.Bar(
            x=trend_data[period_col],
            y=trend_data[col],
            name=name,
            marker_color=marker_color,
            text=trend_data[col].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            textfont=dict(size=16, weight='bold', family='Arial Black'),  # Increased to 16px and bold
            textangle=0,
            insidetextanchor='middle'
        ))
    
    # Format x-axis dates to be bold
    period_labels = trend_data[period_col].dt.strftime('%b %Y') if pd.api.types.is_datetime64_any_dtype(trend_data[period_col]) else trend_data[period_col].astype(str)
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, weight='bold', family='Arial Black')),
        xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
        yaxis_title=dict(text="Count", font=dict(size=16, weight='bold', family='Arial Black')),
        barmode='group',
        height=500,
        hovermode='x unified',
        legend=dict(font=dict(size=14, weight='bold', family='Arial Black')),
        xaxis=dict(
            tickfont=dict(size=14, weight='bold', family='Arial Black'),
            ticktext=period_labels,
            tickvals=trend_data[period_col]
        ),
        yaxis=dict(
            tickfont=dict(size=13, weight='bold', family='Arial Black'),
            tickformat=',d'  # Format numbers with commas
        ),
        plot_bgcolor='white',
        bargap=0.2
    )
    
    return fig

def plot_trend(df, column, title, y_label="Count"):
    """Plot trend line chart with bold numbers and periods"""
    if column not in df.columns or 'Period' not in df.columns:
        return None
    
    trend_data = df.groupby('Period')[column].sum().reset_index()
    trend_data = trend_data.sort_values('Period')
    
    # Format x-axis dates
    period_labels = trend_data['Period'].dt.strftime('%b %Y')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trend_data['Period'],
        y=trend_data[column],
        mode='lines+markers',
        marker=dict(size=12, color='#2a5298'),
        line=dict(color='#1e3c72', width=3),
        text=trend_data[column].apply(lambda x: f'{x:,.0f}'),
        textposition='top center',
        textfont=dict(size=14, weight='bold', family='Arial Black'),
        hovertemplate='Period: %{x}<br>Value: %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, weight='bold', family='Arial Black')),
        xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
        yaxis_title=dict(text=y_label, font=dict(size=16, weight='bold', family='Arial Black')),
        legend=dict(font=dict(size=14, weight='bold', family='Arial Black')),
        xaxis=dict(
            tickfont=dict(size=14, weight='bold', family='Arial Black'),
            ticktext=period_labels,
            tickvals=trend_data['Period']
        ),
        yaxis=dict(
            tickfont=dict(size=13, weight='bold', family='Arial Black'),
            tickformat=',d'  # Format numbers with commas
        ),
        hovermode='x unified',
        height=450,
        plot_bgcolor='white'
    )
    
    return fig

def plot_pmtct_cascade_bar(df, period_col='Period'):
    """Plot PMTCT cascade as grouped bar chart"""
    metrics = {
        "ANC Clients": 'PMTCT_ANC_1 Number of New ANC clients',
        "HIV Tested": None,  # Will calculate
        "HIV Positive": 'PMTCT_HTS_ Number of pregnant women tested HIV positive',
        "New on ART": 'PMTCT_ART_15b-e. Number of HIV positive pregnant women newly started on ART'
    }
    
    valid_metrics = {}
    for name, col in metrics.items():
        if name == "HIV Tested":
            if 'PMTCT_HTS_ Number of pregnant women tested HIV Negative' in df.columns and 'PMTCT_HTS_ Number of pregnant women tested HIV positive' in df.columns:
                df['HIV_Tested'] = df['PMTCT_HTS_ Number of pregnant women tested HIV Negative'] + df['PMTCT_HTS_ Number of pregnant women tested HIV positive']
                valid_metrics[name] = 'HIV_Tested'
        elif col and col in df.columns:
            valid_metrics[name] = col
    
    if valid_metrics:
        return plot_grouped_bar_comparison(df, valid_metrics, "PMTCT Cascade: ANC → HIV Testing → ART", period_col)
    return None

# ============================================
# MAIN DASHBOARD
# ============================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Gombe State HIV/PMTCT Situation Room Dashboard</h1>
        <p>Comprehensive Program Monitoring & Evaluation | Real-time Performance Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # Sidebar - File Upload and Filters
    with st.sidebar:
        st.markdown("## 📂 Data Upload")
        uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.success(f"✅ Loaded {len(df)} records")
                
                # Filter Section
                st.markdown("---")
                st.markdown("## 🔍 Filters")
                
                filtered_df = df.copy()
                
                # State Filter
                if 'State' in filtered_df.columns:
                    states = ['All'] + sorted(filtered_df['State'].dropna().unique().tolist())
                    selected_state = st.selectbox("State", states)
                    if selected_state != 'All':
                        filtered_df = filtered_df[filtered_df['State'] == selected_state]
                
                # LGA Filter
                if 'LGA' in filtered_df.columns and selected_state != 'All':
                    lgas = ['All'] + sorted(filtered_df['LGA'].dropna().unique().tolist())
                    selected_lga = st.selectbox("LGA", lgas)
                    if selected_lga != 'All':
                        filtered_df = filtered_df[filtered_df['LGA'] == selected_lga]
                
                # Facility Filter
                if 'Facility' in filtered_df.columns:
                    facilities = ['All'] + sorted(filtered_df['Facility'].dropna().unique().tolist())
                    selected_facility = st.selectbox("Facility", facilities)
                    if selected_facility != 'All':
                        filtered_df = filtered_df[filtered_df['Facility'] == selected_facility]
                
                # Year Filter
                if 'Year' in filtered_df.columns:
                    years = ['All'] + sorted(filtered_df['Year'].dropna().unique().tolist())
                    selected_year = st.selectbox("Year", years)
                    if selected_year != 'All':
                        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
                
                # Month Filter
                if 'Month' in filtered_df.columns and selected_year != 'All':
                    months = ['All'] + sorted(filtered_df['Month'].dropna().unique().tolist())
                    selected_month = st.selectbox("Month", months)
                    if selected_month != 'All':
                        filtered_df = filtered_df[filtered_df['Month'] == selected_month]
                
                # Quarter Filter
                if 'Quarter_Year' in filtered_df.columns:
                    quarters = ['All'] + sorted(filtered_df['Quarter_Year'].dropna().unique().tolist())
                    selected_quarter = st.selectbox("Quarter (3-Month Period)", quarters)
                    if selected_quarter != 'All':
                        filtered_df = filtered_df[filtered_df['Quarter_Year'] == selected_quarter]
                
                st.session_state.filtered_df = filtered_df
                
                st.markdown("---")
                st.markdown("## 📥 Export")
                if st.button("Export Data"):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, sheet_name='Filtered_Data', index=False)
                    st.download_button(
                        label="Download Excel",
                        data=output.getvalue(),
                        file_name=f"hiv_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    # Main Content
    if st.session_state.df is None:
        st.info("👈 **Please upload your Excel file to begin**")
        st.markdown("""
        ### 📊 Dashboard Capabilities
        
        This dashboard provides comprehensive monitoring of:
        - **PMTCT Cascade**: ANC → HIV Testing → ART
        - **Previously Known HIV vs Already on ART**
        - **Delivery Outcomes**: Booked/Unbooked , Live Births Vs  HEI Prophylaxis
        - **HEI Prophylaxis**: Within 72hrs vs After 72hrs
        - **EID Cascade**: Samples vs Results Total, Negative vs Positive, Final Outcome at 18 Months
        - **HTS & PrEP**: Testing services and prevention
        - **ART & Viral Load**: Treatment outcomes
        - **TB/HIV Integration**: Screening and treatment
        - **Advanced HIV Disease**: CrAg screening and management
        - **📋 Form Reporting Rates**: ART, HTS, PMTCT Spoke, PMTCT Comprehensive, PrEP forms
        """)
        return
    
    # Get filtered data
    df = st.session_state.get('filtered_df', st.session_state.df)
    
    # Display Filter Summary with LARGER numbers
    st.markdown('<div class="section-header">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(df):,}</div><div class="kpi-label">Total Records</div></div>', unsafe_allow_html=True)
    with col2:
        if 'State' in df.columns:
            st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(df["State"].unique())}</div><div class="kpi-label">States</div></div>', unsafe_allow_html=True)
    with col3:
        if 'Facility' in df.columns:
            st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(df["Facility"].unique())}</div><div class="kpi-label">Facilities</div></div>', unsafe_allow_html=True)
    with col4:
        if 'Period' in df.columns:
            st.markdown(f'<div class="kpi-box"><div class="kpi-value">{df["Period"].min().strftime("%b %Y")} - {df["Period"].max().strftime("%b %Y")}</div><div class="kpi-label">Period</div></div>', unsafe_allow_html=True)
    
    # ============================================
    # REPORTING RATES SECTION
    # ============================================
    st.markdown('<div class="section-header">📋 Form Reporting Rates & Data Completeness</div>', unsafe_allow_html=True)
    
    # Define reporting rate columns with alternative names
    reporting_columns_config = {
        'ART MONTHLY SUMMARY FORM - Reporting rate': ['ART MONTHLY SUMMARY FORM - Reporting rate', 'ART Reporting Rate', 'ART_Rate', 'ART Monthly Summary Form - Reporting rate'],
        'HTS Forms - Reporting rate': ['HTS Forms - Reporting rate', 'HTS Reporting Rate', 'HTS_Rate'],
        'PMTCT MSF FOR SPOKE SITES   - Reporting rate': ['PMTCT MSF FOR SPOKE SITES   - Reporting rate', 'PMTCT Spoke Reporting Rate', 'Spoke_Rate', 'PMTCT MSF FOR SPOKE SITES - Reporting rate'],
        'PMTCT MSF Comprehensive - Reporting rate': ['PMTCT MSF Comprehensive - Reporting rate', 'PMTCT Comp Reporting Rate', 'Comp_Rate'],
        'PrEP Monthly Summary Form - Reporting rate': ['PrEP Monthly Summary Form - Reporting rate', 'PrEP Reporting Rate', 'PrEP_Rate']
    }
    
    reporting_data_dict = {}
    
    for display_name, possible_names in reporting_columns_config.items():
        found_col = find_column(df, possible_names)
        if found_col:
            reporting_data = get_reporting_rate_from_column(df, found_col)
            if reporting_data is not None and len(reporting_data) > 0:
                clean_name = display_name.replace(' - Reporting rate', '').replace('   ', ' ')
                reporting_data_dict[clean_name] = reporting_data
    
    if reporting_data_dict:
        # Display KPI cards for latest reporting rates with LARGER numbers
        cols = st.columns(min(len(reporting_data_dict), 5))
        for idx, (form_name, data) in enumerate(reporting_data_dict.items()):
            latest_rate = data['Reporting_Rate'].iloc[-1] if len(data) > 0 else 0
            color_class = get_reporting_status_color(latest_rate)
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="kpi-box">
                    <div class="kpi-label">{form_name}</div>
                    <div class="kpi-value {color_class}">{latest_rate:.1f}%</div>
                    <div class="kpi-label">Latest Reporting Rate</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.subheader("📈 Form Reporting Rate Trends")
        
        # Create separate line charts for each reporting rate
        for form_name, data in reporting_data_dict.items():
            if len(data) > 0:
                fig = go.Figure()
                
                # Format period labels
                period_labels = data['Period'].dt.strftime('%b %Y')
                
                fig.add_trace(go.Scatter(
                    x=data['Period'],
                    y=data['Reporting_Rate'],
                    mode='lines+markers',
                    name=form_name,
                    line=dict(color='#1e3c72', width=3),
                    marker=dict(size=10, color='#2a5298'),
                    text=data['Reporting_Rate'].round(1),
                    textposition='top center',
                    textfont=dict(size=14, weight='bold', family='Arial Black'),
                    hovertemplate='Period: %{x}<br>Rate: %{y:.1f}%<extra></extra>'
                ))
                
                fig.add_hline(
                    y=90, 
                    line_dash="dash", 
                    line_color="green",
                    annotation_text="Target (90%)",
                    annotation_font=dict(size=14, weight='bold'),
                    annotation_position="bottom right"
                )
                
                fig.add_hrect(y0=0, y1=70, line_width=0, fillcolor="red", opacity=0.1)
                fig.add_hrect(y0=70, y1=90, line_width=0, fillcolor="orange", opacity=0.1)
                fig.add_hrect(y0=90, y1=100, line_width=0, fillcolor="green", opacity=0.1)
                
                fig.update_layout(
                    title=dict(text=f"{form_name} - Reporting Rate Trend", font=dict(size=20, weight='bold', family='Arial Black')),
                    xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                    yaxis_title=dict(text="Reporting Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                    yaxis_range=[0, 100],
                    height=500,
                    hovermode='x unified',
                    showlegend=False,
                    xaxis=dict(
                        tickfont=dict(size=14, weight='bold', family='Arial Black'),
                        ticktext=period_labels,
                        tickvals=data['Period']
                    ),
                    yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"reporting_rate_{form_name.replace(' ', '_')}")
        
        # Create a combined view
        with st.expander("📊 View All Reporting Rates Combined"):
            combined_fig = go.Figure()
            colors = ['#1e3c72', '#2a5298', '#3b6cb0', '#4c86c8', '#5da0e0']
            
            for idx, (form_name, data) in enumerate(reporting_data_dict.items()):
                if len(data) > 0:
                    combined_fig.add_trace(go.Scatter(
                        x=data['Period'],
                        y=data['Reporting_Rate'],
                        mode='lines+markers',
                        name=form_name,
                        line=dict(color=colors[idx % len(colors)], width=2),
                        marker=dict(size=8)
                    ))
            
            combined_fig.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Target (90%)")
            combined_fig.update_layout(
                title=dict(text="All Form Reporting Rates Comparison", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Reporting Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_range=[0, 100],
                height=550,
                hovermode='x unified',
                legend=dict(font=dict(size=12, weight='bold')),
                xaxis=dict(tickfont=dict(size=12, weight='bold')),
                yaxis=dict(tickfont=dict(size=12, weight='bold'))
            )
            st.plotly_chart(combined_fig, use_container_width=True, key="combined_reporting_rates")
    
    # Tabs for different program areas
    tabs = st.tabs(["🤰 PMTCT", "🩸 Syphilis & HBV", "👶 EID", "🔬 HTS & PrEP", "💊 ART & VL", "🫁 TB/HIV", "🧠 AHD"])
    
    # ============================================
    # TAB 1: PMTCT
    # ============================================
    with tabs[0]:
        st.header("🤰 PMTCT Program Performance")
        
        # 1. PMTCT Cascade (includes ANC Clients)
        st.subheader("📊 PMTCT Cascade")
        pmtct_cascade = plot_pmtct_cascade_bar(df)
        if pmtct_cascade:
            st.plotly_chart(pmtct_cascade, use_container_width=True, key="pmtct_cascade_chart")
        
        # 2. Previously Known HIV vs Already on ART
        st.subheader("📊 Previously Known HIV Positive vs Already on ART")
        known_art_metrics = {
            "Previously Known HIV+": 'PMTCT_HTS. Number of pregnant women with previously known HIV positive infection',
            "Already on ART": 'PMTCT_ART_15a. Number of HIV positive pregnant women already on ART prior to this pregnancy'
        }
        known_art_comparison = plot_grouped_bar_comparison(df, known_art_metrics, "Previously Known HIV vs Already on ART")
        if known_art_comparison:
            st.plotly_chart(known_art_comparison, use_container_width=True, key="known_art_comparison_chart")
        
        # 3. Delivery Outcomes: Booked/Unbooked vs Livebirths
        st.subheader("📊 Delivery Outcomes: Booked/Unbooked vs Livebirths")
        delivery_metrics = {
            "Booked & Unbooked Deliveries": 'PMTCT_L&D_21. Number of booked and unbooked HIV positive pregnant women who delivered at facility',
            "Livebirths": 'PMTCT_L&D_Number of HIV positive pregnant women who delivered at facility - Livebirth'
        }
        delivery_comparison = plot_grouped_bar_comparison(df, delivery_metrics, "Delivery Outcomes Among HIV+ Women")
        if delivery_comparison:
            st.plotly_chart(delivery_comparison, use_container_width=True, key="delivery_comparison_chart")
        
        # 4. HEI Prophylaxis: Within 72hrs vs After 72hrs
        st.subheader("📊 HEI Prophylaxis: Within 72hrs vs After 72hrs")
        hei_metrics = {
            "Prophylaxis Within 72hrs": 'PMTCT_HEI_ Number of HIV-exposed infants born to HIV positive women who received ARV prophylaxis within 72 hrs of delivery',
            "Prophylaxis After 72hrs": 'PMTCT_HEI Number of HIV-exposed infants born to HIV positive women who received ARV prophylaxis after 72 hrs of delivery'
        }
        hei_comparison = plot_grouped_bar_comparison(df, hei_metrics, "HEI Prophylaxis Timing Comparison")
        if hei_comparison:
            st.plotly_chart(hei_comparison, use_container_width=True, key="hei_comparison_chart")
        
        # 5. Stillbirths
        if 'PMTCT_L&D_Number of HIV positive pregnant women who delivered at facility - Stillbirth' in df.columns:
            fig = plot_trend(df, 'PMTCT_L&D_Number of HIV positive pregnant women who delivered at facility - Stillbirth',
                            "Stillbirths Among HIV+ Women")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="stillbirths_trend_chart")
    
    # ============================================
    # TAB 2: Syphilis & HEI
    # ============================================
    with tabs[1]:
        st.header("🩸 Syphilis Testing, Treatment & Hepatitis B")
        
        # 1. Syphilis Cascade (includes Tested for Syphilis)
        st.subheader("📊 Syphilis Testing and Treatment Cascade")
        syphilis_metrics = {
            "Tested for Syphilis": 'PMTCT_Syphilis- Number of new ANC Clients tested for syphilis total',
            "Tested Positive": 'PMTCT_ANC_3. Number of new ANC Clients tested positive for syphilis Total',
            "Treated": 'PMTCT_Syph_Tx. Number of the ANC Clients treated for Syphilis total'
        }
        syphilis_comparison = plot_grouped_bar_comparison(df, syphilis_metrics, "Syphilis Testing and Treatment Cascade")
        if syphilis_comparison:
            st.plotly_chart(syphilis_comparison, use_container_width=True, key="syphilis_comparison_chart")
        
        # 2. HBV Known Status vs New ANC Clients
        st.subheader("📊 Hepatitis B Testing Coverage: Known HBV Status vs New ANC Clients")
        hbv_anc_metrics = {
            "New ANC Clients": 'PMTCT_ANC_1 Number of New ANC clients',
            "Known HBV Status": 'PMTCT_HBV. Number of pregnant and breastfeeding women with known HBV Status'
        }
        hbv_anc_comparison = plot_grouped_bar_comparison(df, hbv_anc_metrics, "HBV Testing Coverage: Known Status vs ANC Clients")
        if hbv_anc_comparison:
            st.plotly_chart(hbv_anc_comparison, use_container_width=True, key="hbv_anc_comparison_chart")
        
        # 3. HBV Testing Trend
        if 'PMTCT_HBV. Number of pregnant and breastfeeding women with known HBV Status' in df.columns:
            fig = plot_trend(df, 'PMTCT_HBV. Number of pregnant and breastfeeding women with known HBV Status',
                            "Hepatitis B Status Known Trend")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="hbv_trend_chart")
    
    # ============================================
    # TAB 3: EID (Early Infant Diagnosis) - UPDATED
    # ============================================
    with tabs[2]:
        st.header("👶 Early Infant Diagnosis (EID) Cascade")
        
        # 1. EID Samples vs Results (Within 72hrs)
        st.subheader("📊 EID Within 72hrs: Samples Taken vs Results Received")
        eid_72hr_metrics = {
            "EID Samples Taken (Within 72hrs)": 'PMTCT_EID_30. Number of Infants born to HIV positive women whose blood samples were taken for DNA PCR test within 72 hrs of birth',
            "EID Results Received (≤72hrs)": 'PMTCT_EID_33. Number of HIV PCR results received for babies whose samples were taken within 72 hrs of birth'
        }
        eid_72hr_comparison = plot_grouped_bar_comparison(df, eid_72hr_metrics, "EID Within 72hrs: Samples Taken vs Results Received")
        if eid_72hr_comparison:
            st.plotly_chart(eid_72hr_comparison, use_container_width=True, key="eid_72hr_comparison_chart")
        
        # 2. EID Samples vs Results (>72hrs - 2 months)
        st.subheader("📊 EID Samples vs Results (>72hrs - 2 months)")
        eid_2month_metrics = {
            "Samples Taken (>72hrs - 2mo)": 'PMTCT_EID_31. Number of Infants born to HIV positive women whose blood samples were taken for DNA PCR test between >72 hrs - < 2 months of birth',
            "Results Received (>72hrs - 2mo)": 'PMTCT_EID_34. Number of HIV PCR results received for babies whose samples were taken between >72 hrs - < 2 months of birth'
        }
        eid_2month_comparison = plot_grouped_bar_comparison(df, eid_2month_metrics, "EID Samples vs Results (>72hrs - 2 months)")
        if eid_2month_comparison:
            st.plotly_chart(eid_2month_comparison, use_container_width=True, key="eid_2month_comparison_chart")
        
        # 3. EID Within 1 Year: Total vs Negative vs Positive
        st.subheader("📊 EID Within 1 Year: Total Samples vs Negative vs Positive Results")
        eid_1year_metrics = {
            "Total Samples Taken": 'PMTCT_EID_33. No. of of HEI whose samples were taken for DNA PCR_Total',
            "Negative Results": 'PMTCT_EID_33. No. of HIV PCR results received for babies whose samples were taken for DNA PCR_Negative',
            "Positive Results": 'PMTCT_EID_33. No. of HIV PCR results received for babies whose samples were taken for DNA PCR_Positive'
        }
        eid_1year_comparison = plot_grouped_bar_comparison(df, eid_1year_metrics, "EID Results: Total vs Negative vs Positive", 
                                                           color_palette=['#1e3c72', '#27ae60', '#e74c3c'])
        if eid_1year_comparison:
            st.plotly_chart(eid_1year_comparison, use_container_width=True, key="eid_1year_comparison_chart")
        
        # 4. Final Outcome at 18 Months
        if 'PMTCT_Final Outcome_Number of HIV-Exposed Children Aged 18 Months with Documented Final outcome Status' in df.columns:
            fig = plot_trend(df, 'PMTCT_Final Outcome_Number of HIV-Exposed Children Aged 18 Months with Documented Final outcome Status',
                            "HEI with Documented Final Outcome at 18 Months")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="final_outcome_trend_chart")
    
    # ============================================
    # TAB 4: HTS & PrEP
    # ============================================
    with tabs[3]:
        st.header("🔬 HTS & PrEP Program Performance")
        
        # 1. HTS Negative vs Positive
        st.subheader("📊 HTS Testing Results: Negative vs Positive")
        hts_metrics = {
            "HTS Negative": 'HTS Monthly_1_HTS_TST_NEG',
            "HTS Positive": 'HTS Monthly_2_HTS_TST_POS'
        }
        hts_comparison = plot_grouped_bar_comparison(df, hts_metrics, "HTS Testing Results Comparison")
        if hts_comparison:
            st.plotly_chart(hts_comparison, use_container_width=True, key="hts_comparison_chart")
        
        # 2. HTS Positivity Rate
        if 'HTS Monthly_1_HTS_TST_NEG' in df.columns and 'HTS Monthly_2_HTS_TST_POS' in df.columns:
            positivity_data = df.groupby('Period').apply(
                lambda x: (x['HTS Monthly_2_HTS_TST_POS'].sum() / x['HTS Monthly_1_HTS_TST_NEG'].sum() * 100) if x['HTS Monthly_1_HTS_TST_NEG'].sum() > 0 else 0
            ).reset_index()
            positivity_data.columns = ['Period', 'Positivity_Rate']
            
            period_labels = positivity_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=positivity_data['Period'],
                y=positivity_data['Positivity_Rate'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=positivity_data['Positivity_Rate'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="HTS Positivity Rate Trend", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Positivity Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=positivity_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="hts_positivity_rate_chart")
        
        # 3. PrEP Screened vs Initiated
        st.subheader("📊 PrEP: Screened vs Initiated")
        prep_metrics = {
            "PrEP Screened": 'HTS Monthly_15_HTS_TST_clients Screened for PrEp',
            "PrEP Initiated": 'No. of individuals who were eligible and started PrEP in the reporting month'
        }
        prep_comparison = plot_grouped_bar_comparison(df, prep_metrics, "PrEP Cascade: Screened vs Initiated")
        if prep_comparison:
            st.plotly_chart(prep_comparison, use_container_width=True, key="prep_comparison_chart")
        
        # 4. PrEP Initiation Rate
        if 'HTS Monthly_15_HTS_TST_clients Screened for PrEp' in df.columns and 'No. of individuals who were eligible and started PrEP in the reporting month' in df.columns:
            prep_rate_data = df.groupby('Period').apply(
                lambda x: (x['No. of individuals who were eligible and started PrEP in the reporting month'].sum() / 
                          x['HTS Monthly_15_HTS_TST_clients Screened for PrEp'].sum() * 100) if x['HTS Monthly_15_HTS_TST_clients Screened for PrEp'].sum() > 0 else 0
            ).reset_index()
            prep_rate_data.columns = ['Period', 'Initiation_Rate']
            
            period_labels = prep_rate_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=prep_rate_data['Period'],
                y=prep_rate_data['Initiation_Rate'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=prep_rate_data['Initiation_Rate'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="PrEP Initiation Rate Trend", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Initiation Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=prep_rate_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="prep_initiation_rate_chart")
        
        # 5. TB Screening in HTS
        if 'HTS Monthly_9_HTS_TST_TB Screened' in df.columns:
            fig = plot_trend(df, 'HTS Monthly_9_HTS_TST_TB Screened', "TB Screened in HTS")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="hts_tb_screening_chart")
        
        # 6. STI Screening
        if 'Number of HTS clients clinically screened for STI' in df.columns:
            fig = plot_trend(df, 'Number of HTS clients clinically screened for STI', "STI Screening in HTS")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="sti_screening_chart")
    
    # ============================================
    # TAB 5: ART & Viral Load
    # ============================================
    with tabs[4]:
        st.header("💊 ART & Viral Load Performance")
        
        # 1. Currently on ART vs Newly Initiated
        st.subheader("📊 ART: Currently on ART vs Newly Initiated")
        art_metrics = {
            "Currently on ART": 'ART Monthly_2_Currently on ART',
            "Newly Initiated": 'ART Monthly_1_Newly Initiated'
        }
        art_comparison = plot_grouped_bar_comparison(df, art_metrics, "ART Patient Population")
        if art_comparison:
            st.plotly_chart(art_comparison, use_container_width=True, key="art_comparison_chart")
        
        # 2. Viral Load: With Results vs Suppressed
        st.subheader("📊 Viral Load: With Results vs Suppressed")
        vl_metrics = {
            "With VL Results": 'ART Monthly_3_Currently on ART with VL result',
            "Virally Suppressed": 'ART Monthly_4_PLHIV on ART virologic suppression'
        }
        vl_comparison = plot_grouped_bar_comparison(df, vl_metrics, "Viral Load Testing and Suppression")
        if vl_comparison:
            st.plotly_chart(vl_comparison, use_container_width=True, key="vl_comparison_chart")
        
        # 3. VL Testing Coverage
        if 'ART Monthly_2_Currently on ART' in df.columns and 'ART Monthly_3_Currently on ART with VL result' in df.columns:
            vl_coverage_data = df.groupby('Period').apply(
                lambda x: (x['ART Monthly_3_Currently on ART with VL result'].sum() / 
                          x['ART Monthly_2_Currently on ART'].sum() * 100) if x['ART Monthly_2_Currently on ART'].sum() > 0 else 0
            ).reset_index()
            vl_coverage_data.columns = ['Period', 'VL_Coverage']
            
            period_labels = vl_coverage_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=vl_coverage_data['Period'],
                y=vl_coverage_data['VL_Coverage'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=vl_coverage_data['VL_Coverage'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="Viral Load Testing Coverage Trend", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Coverage (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=vl_coverage_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="vl_coverage_chart")
        
        # 4. VL Suppression Rate
        if 'ART Monthly_3_Currently on ART with VL result' in df.columns and 'ART Monthly_4_PLHIV on ART virologic suppression' in df.columns:
            vl_suppression_data = df.groupby('Period').apply(
                lambda x: (x['ART Monthly_4_PLHIV on ART virologic suppression'].sum() / 
                          x['ART Monthly_3_Currently on ART with VL result'].sum() * 100) if x['ART Monthly_3_Currently on ART with VL result'].sum() > 0 else 0
            ).reset_index()
            vl_suppression_data.columns = ['Period', 'Suppression_Rate']
            
            period_labels = vl_suppression_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=vl_suppression_data['Period'],
                y=vl_suppression_data['Suppression_Rate'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=vl_suppression_data['Suppression_Rate'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="Viral Load Suppression Rate Trend", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Suppression Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=vl_suppression_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="vl_suppression_chart")
        
        # 5. New ART Initiations vs TB Screened (includes TB Screened)
        st.subheader("📊 New ART Initiations vs TB Screened")
        art_tb_metrics = {
            "New ART Initiations": 'ART Monthly_1_Newly Initiated',
            "TB Screened (New)": 'ART Monthly_10a_PLHIV TB Screened(newly initiated)'
        }
        art_tb_comparison = plot_grouped_bar_comparison(df, art_tb_metrics, "TB Screening Among New ART Initiations")
        if art_tb_comparison:
            st.plotly_chart(art_tb_comparison, use_container_width=True, key="art_tb_comparison_chart")
    
    # ============================================
    # TAB 6: TB/HIV Integration
    # ============================================
    with tabs[5]:
        st.header("🫁 TB/HIV Integration Cascade")
        
        # Full TB Cascade (includes Screened for TB)
        st.subheader("📊 TB/HIV Cascade: Screening to Treatment")
        tb_metrics = {
            "Screened for TB": 'ART Monthly_10_PLHIV on ART (Including PMTCT) who were Clinically Screened for TB in HIV Treatment Settings',
            "Presumptive TB": 'ART Monthly_11_PLHIV Presumptive TB during the month',
            "Tested for TB": 'ART Monthly_12_PLHIV Presumptive TB and Tested for TB during the month',
            "Confirmed TB": 'ART Monthly_13_PLHIV confirmed TB',
            "Initiated TB Treatment": 'ART Monthly_14_PLHIV on ART with active TB disease who initiated TB treatment'
        }
        tb_comparison = plot_grouped_bar_comparison(df, tb_metrics, "TB/HIV Cascade")
        if tb_comparison:
            st.plotly_chart(tb_comparison, use_container_width=True, key="tb_comparison_chart")
        
        # TB Treatment Rate
        if 'ART Monthly_13_PLHIV confirmed TB' in df.columns and 'ART Monthly_14_PLHIV on ART with active TB disease who initiated TB treatment' in df.columns:
            tb_tx_data = df.groupby('Period').apply(
                lambda x: (x['ART Monthly_14_PLHIV on ART with active TB disease who initiated TB treatment'].sum() / 
                          x['ART Monthly_13_PLHIV confirmed TB'].sum() * 100) if x['ART Monthly_13_PLHIV confirmed TB'].sum() > 0 else 0
            ).reset_index()
            tb_tx_data.columns = ['Period', 'Treatment_Rate']
            
            period_labels = tb_tx_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tb_tx_data['Period'],
                y=tb_tx_data['Treatment_Rate'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=tb_tx_data['Treatment_Rate'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="TB Treatment Initiation Rate", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Treatment Rate (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=tb_tx_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="tb_treatment_rate_chart")
    
    # ============================================
    # TAB 7: Advanced HIV Disease (AHD)
    # ============================================
    with tabs[6]:
        st.header("🧠 Advanced HIV Disease (AHD) Management")
        
        # 1. AHD Patients Trend
        if 'ART Monthly_19_PLHIV with WHO clinical stages 3 and 4 and/or CD4 <200c/mm3 and children  ≤ 5 years (Advanced HIV Disease) (Total)' in df.columns:
            fig = plot_trend(df, 'ART Monthly_19_PLHIV with WHO clinical stages 3 and 4 and/or CD4 <200c/mm3 and children  ≤ 5 years (Advanced HIV Disease) (Total)',
                            "AHD Patients")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="ahd_trend_chart")
        
        # 2. CrAg Screening: Negative vs Positive
        st.subheader("📊 CrAg Screening Results: Negative vs Positive")
        crag_metrics = {
            "CrAg Negative": 'ART Monthly_20a_PLHIV with AHD screened for serum Cryptococcal Antigen (Serum CrAg)  (Neg)',
            "CrAg Positive": 'ART Monthly_20b_PLHIV with AHD screened for serum Cryptococcal Antigen (Serum CrAg) (POS)'
        }
        crag_comparison = plot_grouped_bar_comparison(df, crag_metrics, "CrAg Screening Results")
        if crag_comparison:
            st.plotly_chart(crag_comparison, use_container_width=True, key="crag_comparison_chart")
        
        # 3. CrAg Screening Coverage
        if 'ART Monthly_19_PLHIV with WHO clinical stages 3 and 4 and/or CD4 <200c/mm3 and children  ≤ 5 years (Advanced HIV Disease) (Total)' in df.columns:
            crag_coverage_data = df.groupby('Period').apply(
                lambda x: ((x['ART Monthly_20a_PLHIV with AHD screened for serum Cryptococcal Antigen (Serum CrAg)  (Neg)'].sum() +
                           x['ART Monthly_20b_PLHIV with AHD screened for serum Cryptococcal Antigen (Serum CrAg) (POS)'].sum()) / 
                          x['ART Monthly_19_PLHIV with WHO clinical stages 3 and 4 and/or CD4 <200c/mm3 and children  ≤ 5 years (Advanced HIV Disease) (Total)'].sum() * 100) 
                          if x['ART Monthly_19_PLHIV with WHO clinical stages 3 and 4 and/or CD4 <200c/mm3 and children  ≤ 5 years (Advanced HIV Disease) (Total)'].sum() > 0 else 0
            ).reset_index()
            crag_coverage_data.columns = ['Period', 'CrAg_Coverage']
            
            period_labels = crag_coverage_data['Period'].dt.strftime('%b %Y')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=crag_coverage_data['Period'],
                y=crag_coverage_data['CrAg_Coverage'],
                mode='lines+markers',
                marker=dict(size=10, color='#2a5298'),
                line=dict(color='#1e3c72', width=3),
                text=crag_coverage_data['CrAg_Coverage'].round(1),
                textposition='top center',
                textfont=dict(size=14, weight='bold', family='Arial Black')
            ))
            fig.update_layout(
                title=dict(text="CrAg Screening Coverage", font=dict(size=20, weight='bold', family='Arial Black')),
                xaxis_title=dict(text="Period", font=dict(size=16, weight='bold', family='Arial Black')),
                yaxis_title=dict(text="Coverage (%)", font=dict(size=16, weight='bold', family='Arial Black')),
                xaxis=dict(
                    tickfont=dict(size=14, weight='bold', family='Arial Black'),
                    ticktext=period_labels,
                    tickvals=crag_coverage_data['Period']
                ),
                yaxis=dict(tickfont=dict(size=13, weight='bold', family='Arial Black'))
            )
            st.plotly_chart(fig, use_container_width=True, key="crag_coverage_chart")
        
        # 4. Cryptococcal Meningitis Screening
        st.subheader("📊 Cryptococcal Meningitis Screening Results")
        cm_metrics = {
            "CM Positive": 'ART Monthly_21a_PLHIV with AHD and positive CrAg result screened for Cryptococcal meningitis(lumbar puncture) - Positive',
            "CM Negative": 'ART Monthly_21b_PLHIV with AHD and positive CrAg result screened for Cryptococcal meningitis(lumbar puncture) - Negative'
        }
        cm_comparison = plot_grouped_bar_comparison(df, cm_metrics, "Cryptococcal Meningitis Screening Results")
        if cm_comparison:
            st.plotly_chart(cm_comparison, use_container_width=True, key="cm_comparison_chart")
        
        # 5. CM Treatment
        if 'ART Monthly_22_newly enrolled PLHIV for Serum CrAg POS with meningitis started on treatment' in df.columns:
            fig = plot_trend(df, 'ART Monthly_22_newly enrolled PLHIV for Serum CrAg POS with meningitis started on treatment',
                            "CM Treatment Initiated")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="cm_treatment_chart")

if __name__ == "__main__":
    main()