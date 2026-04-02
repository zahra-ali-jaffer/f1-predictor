import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="F1 Predictor Pro",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e10600, #ff4b2b);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .card {
        background: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #e10600;
        margin-bottom: 1rem;
    }
    
    /* Metric boxes */
    .metric-box {
        background: #0e0e0e;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #333;
    }
    
    /* Table styling */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Position badges */
    .pos-1 { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 20px; font-weight: bold; }
    .pos-2 { background: #C0C0C0; color: #000; padding: 2px 8px; border-radius: 20px; font-weight: bold; }
    .pos-3 { background: #CD7F32; color: #000; padding: 2px 8px; border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Title with animation effect
st.markdown('<div class="main-title"><h1 style="color: white;">🏎️ F1 Leaderboard Predictor Pro</h1><p style="color: white;">Powered by Real-Time Data & AI</p></div>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/200px-F1.svg.png", use_container_width=True)
    st.markdown("## ⚙️ Settings")
    
    # Year selection with icons
    year = st.selectbox(
        "📅 Select Season", 
        [2022, 2023, 2024, 2025], 
        index=2,
        help="Choose the F1 season"
    )
    
    # Model settings
    st.markdown("### 🧮 Prediction Model")
    grid_weight = st.slider(
        "Grid Position Weight", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.05,
        help="Higher weight = grid position matters more"
    )
    
    points_weight = st.slider(
        "Points History Weight", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.3, 
        step=0.05,
        help="Higher weight = past performance matters more"
    )
    
    # Advanced features
    use_circuit_factor = st.checkbox("🏁 Enable Circuit Factor", value=True, help="Adjust predictions based on track characteristics")
    show_confidence = st.checkbox("📊 Show Confidence Score", value=True, help="Display prediction confidence")
    
    st.markdown("---")
    st.caption("Data source: Ergast API")

# Cache data fetching for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_f1_data(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/last/results.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# Fetch data with loading spinner
with st.spinner("🏎️ Fetching latest race data..."):
    data = fetch_f1_data(year)

# Error handling
if not data:
    st.error("❌ Failed to fetch data. Please try again later.")
    st.stop()

# Extract race data
try:
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        st.warning("⚠️ No race data found for this season")
        st.stop()
    
    race = races[0]
    results = race["Results"]
    
    # Circuit information (simplified - would need actual circuit data)
    circuit_name = race.get("Circuit", {}).get("circuitName", "Unknown")
    
except Exception as e:
    st.error(f"❌ Error parsing data: {str(e)}")
    st.stop()

# Build dataframe with enhanced data
drivers = []
for r in results:
    driver_data = {
        "name": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
        "code": r['Driver'].get('code', 'N/A'),
        "grid": int(r['grid']),
        "position": int(r['position']),
        "points": float(r['points']),
        "constructor": r['Constructor']['name'],
        "laps": int(r.get('laps', 0)),
        "status": r.get('status', 'Finished')
    }
    drivers.append(driver_data)

df = pd.DataFrame(drivers)

# Display race info banner
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏁 Grand Prix", race['raceName'])
with col2:
    st.metric("📍 Circuit", circuit_name)
with col3:
    st.metric("📅 Date", race['date'])

# Advanced prediction logic
def calculate_prediction_score(row, grid_weight, points_weight, circuit_name, use_circuit_factor):
    # Base score
    score = -grid_weight * row['grid'] - points_weight * row['points']
    
    # Circuit-specific adjustments
    if use_circuit_factor:
        # Hard to overtake circuits (grid position matters MORE)
        hard_overtake = ["Monaco", "Singapore", "Hungary", "Imola"]
        # Easy overtake circuits (car performance matters MORE)
        easy_overtake = ["Monza", "Baku", "Spa", "Bahrain"]
        
        for circuit in hard_overtake:
            if circuit in circuit_name:
                score = -0.9 * row['grid'] - 0.1 * row['points']  # Grid matters even more
                break
        for circuit in easy_overtake:
            if circuit in circuit_name:
                score = -0.5 * row['grid'] - 0.5 * row['points']  # Performance matters more
                break
    
    return score

# Apply prediction
df['score'] = df.apply(
    lambda row: calculate_prediction_score(row, grid_weight, points_weight, circuit_name, use_circuit_factor), 
    axis=1
)

# Sort predictions
predicted = df.sort_values('score', ascending=False).copy()
predicted['predicted_position'] = range(1, len(predicted) + 1)

# Calculate confidence (based on grid position variance)
if show_confidence:
    grid_variance = df['grid'].std()
    confidence = max(0, min(100, 100 - (grid_variance * 5)))
    st.info(f"🎯 Prediction Confidence: {confidence:.1f}% - {'High' if confidence > 70 else 'Medium' if confidence > 40 else 'Low'}")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🔮 Predictions", "📊 Actual Results", "📈 Comparison", "📉 Analysis"])

with tab1:
    st.subheader("🏆 Predicted Race Results")
    
    # Format predicted results with position badges
    predicted_display = predicted[['predicted_position', 'name', 'constructor', 'grid']].head(10).copy()
    
    # Add position badges
    def add_position_badge(pos):
        if pos == 1:
            return "🥇 P1"
        elif pos == 2:
            return "🥈 P2"
        elif pos == 3:
            return "🥉 P3"
        else:
            return f"📍 P{pos}"
    
    predicted_display['position'] = predicted_display['predicted_position'].apply(add_position_badge)
    predicted_display = predicted_display[['position', 'name', 'constructor', 'grid']]
    predicted_display.columns = ['Position', 'Driver', 'Team', 'Starting Grid']
    
    st.dataframe(predicted_display, use_container_width=True, hide_index=True)
    
    # Visual prediction chart
    st.subheader("📊 Prediction Visualisation")
    fig = px.bar(
        predicted.head(10),
        x='name',
        y='score',
        color='constructor',
        title='Prediction Scores (Higher = Better)',
        labels={'score': 'Prediction Score', 'name': 'Driver'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🏁 Official Race Results")
    
    # Format actual results
    actual_display = df[['position', 'name', 'constructor', 'grid', 'points']].copy()
    actual_display['position_label'] = actual_display['position'].apply(add_position_badge)
    actual_display = actual_display[['position_label', 'name', 'constructor', 'grid', 'points']]
    actual_display.columns = ['Position', 'Driver', 'Team', 'Starting Grid', 'Points']
    
    st.dataframe(actual_display, use_container_width=True, hide_index=True)
    
    # Points distribution chart
    st.subheader("📊 Points Distribution")
    fig = px.pie(
        df.head(10),
        values='points',
        names='name',
        title='Top 10 Points Distribution',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("📈 Prediction vs Reality")
    
    # Create comparison table
    comparison = predicted[['name', 'predicted_position', 'constructor']].merge(
        df[['name', 'position']],
        on='name'
    )
    comparison['difference'] = comparison['predicted_position'] - comparison['position']
    comparison['accuracy'] = comparison['difference'].abs()
    
    # Color code the differences
    def color_diff(val):
        if val == 0:
            return '✅'
        elif val > 0:
            return f'⬆️ +{val}'
        else:
            return f'⬇️ {val}'
    
    comparison['diff_label'] = comparison['difference'].apply(color_diff)
    comparison_display = comparison[['name', 'constructor', 'predicted_position', 'position', 'diff_label', 'accuracy']]
    comparison_display.columns = ['Driver', 'Team', 'Predicted', 'Actual', 'Difference', 'Error']
    
    st.dataframe(comparison_display, use_container_width=True, hide_index=True)
    
    # Accuracy metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        top3_actual = set(df.nsmallest(3, 'position')['name'].values)
        top3_predicted = set(predicted.head(3)['name'].values)
        top3_correct = len(top3_actual & top3_predicted)
        st.metric("Top 3 Accuracy", f"{top3_correct}/3", f"{top3_correct*33.3:.0f}%")
    
    with col2:
        mean_error = comparison['accuracy'].mean()
        st.metric("Mean Position Error", f"{mean_error:.1f}", "Lower is better")
    
    with col3:
        exact_matches = len(comparison[comparison['difference'] == 0])
        st.metric("Exact Matches", f"{exact_matches}/{len(comparison)}", f"{exact_matches/len(comparison)*100:.0f}%")

with tab4:
    st.subheader("📊 Performance Analysis")
    
    # Grid vs Position scatter plot
    fig = px.scatter(
        df,
        x='grid',
        y='position',
        text='name',
        title='Starting Grid vs Final Position',
        labels={'grid': 'Starting Grid Position', 'position': 'Final Position'},
        trendline='ols',
        color='constructor'
    )
    fig.update_traces(textposition='top center', marker=dict(size=12))
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.subheader("🏎️ Driver Performance Metrics")
    
    # Calculate performance gain/loss
    df['position_change'] = df['grid'] - df['position']
    
    col1, col2 = st.columns(2)
    with col1:
        best_overtaker = df.nlargest(1, 'position_change')[['name', 'grid', 'position', 'position_change']]
        st.info(f"🏆 **Best Overtaker**\n\n{best_overtaker['name'].iloc[0]}\nGained {best_overtaker['position_change'].iloc[0]} positions")
    
    with col2:
        worst_overtaker = df.nsmallest(1, 'position_change')[['name', 'grid', 'position', 'position_change']]
        st.error(f"⚠️ **Biggest Loser**\n\n{worst_overtaker['name'].iloc[0]}\nLost {abs(worst_overtaker['position_change'].iloc[0])} positions")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.caption(f"🏎️ F1 Predictor Pro | Data from Ergast API | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("⚡ Prediction model uses grid position and points history with circuit-specific adjustments")
