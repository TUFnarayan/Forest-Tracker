import streamlit as st
import pandas as pd
from utils import (
    generate_deforestation_data,
    get_location_coordinates,
    create_trend_chart,
    create_map,
    create_deforestation_rate_chart,
    get_location_suggestions
)
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Background image and overlay
st.markdown("""
    <div class="bg-image"></div>
    <div class="content-overlay">
""", unsafe_allow_html=True)

# Sidebar with forest theme
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2>🌳 Forest Watch</h2>
            <p>Monitoring Earth's Forests</p>
        </div>
    """, unsafe_allow_html=True)

    # Home button
    if st.button("🏠 Home", key="home_button"):
        st.session_state.location = ""
        st.rerun()

    # Search input with suggestions
    st.markdown("### 🔍 Search Location")
    location = st.text_input(
        "",
        placeholder="e.g., Amazon Rainforest, Noida, Western Ghats",
        help="Enter the name of a forest, region, or country",
        value=st.session_state.get('location', '')
    ).strip()

    # Show suggestions as the user types
    if location:
        suggestions = get_location_suggestions(location)
        if suggestions and location.lower() not in [s.lower() for s in suggestions]:
            st.markdown("### Suggestions:")
            for suggestion in suggestions:
                if st.button(f"📍 {suggestion}", key=f"suggestion_{suggestion}"):
                    st.session_state.location = suggestion
                    st.experimental_rerun()

    # Time range selector
    start_year = st.slider(
        "Select Start Year",
        min_value=2000,
        max_value=2024,
        value=2000,
        help="Choose the starting year for the analysis"
    )

    # Add filters
    st.markdown("### 📊 Display Options")
    show_map = st.checkbox("Show Interactive Map", value=True)
    show_trends = st.checkbox("Show Trend Analysis", value=True)
    show_rates = st.checkbox("Show Deforestation Rates", value=True)

    # Add environmental impact section
    st.markdown("""
        <div class="sidebar-info">
            <h3>🌿 Why It Matters</h3>
            <ul>
                <li>Carbon Storage</li>
                <li>Biodiversity</li>
                <li>Climate Regulation</li>
                <li>Water Cycle</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Store location in session state
if location:
    st.session_state.location = location

# Main content
if location:
    try:
        with st.spinner('Analyzing forest data...'):
            # Generate data for the location
            data = generate_deforestation_data(location)
            data = data[data['year'] >= start_year]
            coordinates = get_location_coordinates(location)
            latest_data = data.iloc[-1]

            # Create tabs with environmental styling
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "🗺️ Forest Map", "📈 Detailed Analysis"])

            with tab1:
                st.markdown("""
                    <div class="overview-header">
                        <h2>Forest Health Overview</h2>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(
                        f"""
                        <div class="stat-box">
                            <h3>Current Forest Cover</h3>
                            <h2>{latest_data['forest_cover_percentage']:.1f}%</h2>
                            <p>of total area</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f"""
                        <div class="stat-box">
                            <h3>Total Area</h3>
                            <h2>{latest_data['total_area']:,} ha</h2>
                            <p>monitored region</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    total_loss = data['forest_cover_percentage'].iloc[0] - data['forest_cover_percentage'].iloc[-1]
                    st.markdown(
                        f"""
                        <div class="stat-box warning">
                            <h3>Total Loss Since {start_year}</h3>
                            <h2>{total_loss:.1f}%</h2>
                            <p>forest cover reduction</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if show_trends:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    trend_chart = create_trend_chart(data, f'Forest Cover Trends in {location}')
                    st.plotly_chart(trend_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                if show_map:
                    st.markdown('<div class="map-container">', unsafe_allow_html=True)
                    st.markdown("""
                        <div class="map-header">
                            <h2>Interactive Forest Cover Map</h2>
                            <p>Green areas indicate higher forest density</p>
                        </div>
                    """, unsafe_allow_html=True)
                    map_html = create_map(location, coordinates, latest_data['forest_cover_percentage'])
                    components.html(map_html, height=600, scrolling=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                if show_rates:
                    st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                    rate_chart = create_deforestation_rate_chart(data)
                    st.plotly_chart(rate_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("### 📊 Detailed Statistics")
                st.dataframe(
                    data.style.format({
                        'forest_cover_percentage': '{:.1f}%',
                        'deforestation_rate': '{:.2f}',
                        'total_area': '{:,.0f}'
                    }).background_gradient(subset=['forest_cover_percentage'], cmap='RdYlGn'),
                    use_container_width=True
                )

            # Export options with styled button
            st.download_button(
                label="📥 Download Complete Dataset (CSV)",
                data=data.to_csv(index=False).encode('utf-8'),
                file_name=f'forest_data_{location.lower().replace(" ", "_")}.csv',
                mime='text/csv'
            )

    except Exception as e:
        st.error(f"An error occurred while processing your request: {str(e)}")

else:
    st.markdown("""
        <div class="main-header">
            <div class="header-content">
                <h1>🌳 Global Forest Monitor</h1>
                <p>Track and Analyze Deforestation Trends Worldwide</p>
            </div>
        </div>
        <div class="landing-content">
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🔍 Global Coverage</h3>
                    <p>Monitor forests worldwide with detailed analytics</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Real-time Analysis</h3>
                    <p>Track changes and trends over time</p>
                </div>
                <div class="feature-card">
                    <h3>🗺️ Interactive Maps</h3>
                    <p>Visualize forest density and changes</p>
                </div>
                <div class="feature-card">
                    <h3>📱 Mobile Ready</h3>
                    <p>Access data anywhere, anytime</p>
                </div>
            </div>
            <div class="cta-section">
                <h2>Start Monitoring Forest Changes</h2>
                <p>Enter a location in the sidebar to begin your analysis</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # Close content-overlay div