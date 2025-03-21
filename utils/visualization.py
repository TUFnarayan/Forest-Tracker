import plotly.graph_objects as go
import plotly.express as px
import folium
from folium import plugins
import streamlit as st
from typing import Tuple
import branca.colormap as cm
import numpy as np

def create_trend_chart(data, title: str) -> go.Figure:
    """Create an interactive trend chart using Plotly"""
    fig = go.Figure()

    # Add forest cover trend
    fig.add_trace(go.Scatter(
        x=data['year'],
        y=data['forest_cover_percentage'],
        name='Forest Cover (%)',
        line=dict(color='#2E7D32', width=3),
        fill='tozeroy',
        fillcolor='rgba(46, 125, 50, 0.2)',
        hovertemplate='Year: %{x}<br>Forest Cover: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=24)
        ),
        xaxis_title='Year',
        yaxis_title='Forest Cover (%)',
        template='simple_white',
        hovermode='x unified',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_map(location: str, coordinates: Tuple[float, float], forest_cover: float) -> folium.Map:
    """Create an enhanced Folium map with forest cover visualization"""
    lat, lon = coordinates

    # Create base map with satellite imagery
    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        control_scale=True
    )

    # Add CartoDB positron as an optional layer
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)

    # Create forest density visualization
    radius = 20000  # 20km radius
    num_points = 20
    grid_size = radius / num_points

    # Generate grid of points for density visualization
    for i in range(-num_points, num_points + 1):
        for j in range(-num_points, num_points + 1):
            point_lat = lat + (i * grid_size / 111111)  # Convert meters to degrees
            point_lon = lon + (j * grid_size / (111111 * np.cos(np.radians(lat))))

            # Skip points in the sea (basic land check based on distance from coast)
            distance_from_coast = abs(point_lon - lon)  # Simple distance from coastline
            if distance_from_coast > 0.1:  # Skip if too far into sea
                continue

            # Calculate distance from center with reduced radius
            distance = np.sqrt((lat - point_lat)**2 + (lon - point_lon)**2)
            max_distance = grid_size * (num_points/2) / 111111  # Reduced radius

            # Enhanced local forest cover calculation with urban-aware patterns
            distance_factor = 1 - (distance / max_distance)**1.5  # Smoother falloff
            elevation = np.sin(point_lat * 15) * np.cos(point_lon * 15) * 0.3  # Gentler elevation
            moisture = np.cos(point_lat * 10 - point_lon * 10) * 0.2  # Urban moisture patterns

            # Urban-aware terrain influence
            terrain_factor = (
                np.sin(point_lat * 15 + point_lon * 15) * 0.2 +  # Urban features
                np.cos(point_lat * 25 - point_lon * 25) * 0.15 +  # Parks and green spaces
                np.sin((point_lat * 35 + point_lon * 35)) * 0.1  # Small urban forests
            )

            # Combine environmental factors with higher base values for rainforests
            environmental_factor = 1.5 + elevation + moisture + terrain_factor
            random_variation = np.random.normal(1, 0.1)  # Subtle natural variation

            # Enhanced forest density for rainforest areas
            if "rainforest" in location.lower():
                base_density = 0.8  # Higher base density for rainforests
            else:
                base_density = 0.6

            # Gradual falloff from center with higher minimum
            local_cover = forest_cover * max(base_density, distance_factor) * random_variation * environmental_factor

            # Add subtle noise based on position
            noise = np.sin(point_lat * 25) * np.cos(point_lon * 25) * 0.1
            local_cover *= (1 + noise)
            local_cover = max(0, min(100, local_cover))  # Clamp values

            if local_cover > 2:  # Lower threshold for urban areas
                # Create organic shapes with varied patterns
                pattern_scale = 60
                noise_val = (np.sin(point_lat * pattern_scale) * np.cos(point_lon * pattern_scale) + 
                           np.sin((point_lat + point_lon) * pattern_scale * 0.5)) * 0.5

                # More natural color gradients
                base_green = int(70 + (local_cover/100) * 120)
                color = f'#{int(30 + noise_val * 20):02x}{base_green:02x}{int(30):02x}'

                # Varied cluster sizes
                base_radius = 6 + (noise_val + 1) * 4
                cluster_size = np.random.randint(3, 6)

                # Create organic forest clusters with natural distribution
                for _ in range(cluster_size):
                    # Use polar coordinates for more natural spread
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = np.random.exponential(0.0002)

                    # Convert to lat/lon offsets
                    offset_lat = distance * np.cos(angle)
                    offset_lon = distance * np.sin(angle)

                    # Add some terrain-based variation
                    terrain_influence = np.sin(point_lat * 30 + point_lon * 30) * 0.00005
                    offset_lat += terrain_influence
                    offset_lon += terrain_influence

                    # Vary marker size based on position and terrain
                    size_variation = (1 + np.sin(point_lat * 20 + point_lon * 20) * 0.3)
                    radius_var = base_radius * size_variation * (0.7 + np.random.beta(2, 2) * 0.6)

                    # Natural opacity variation
                    opacity = min(local_cover/100 * 0.65 * (0.5 + np.random.beta(2, 2) * 0.5), 0.75)

                    folium.CircleMarker(
                        location=[point_lat + offset_lat, point_lon + offset_lon],
                        radius=radius_var,
                        color=color,
                        fill=True,
                        fill_opacity=opacity,
                        weight=1,
                        stroke=False
                    ).add_to(m)

    # Add central marker
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        popup=f'<strong>{location}</strong><br>Forest Cover: {forest_cover:.1f}%',
        color='#2E7D32',
        fill=True,
        fill_color='#2E7D32'
    ).add_to(m)

    # Add legend
    colormap = cm.LinearColormap(
        colors=['#C62828', '#FDD835', '#2E7D32'],
        vmin=0,
        vmax=100,
        caption='Forest Cover Density (%)'
    )
    colormap.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add fullscreen option
    plugins.Fullscreen().add_to(m)

    # Add minimap
    minimap = plugins.MiniMap()
    m.add_child(minimap)

    # Convert to HTML string
    map_html = m._repr_html_()

    # Add necessary height style
    map_html = map_html.replace('<div style="', '<div style="height:600px;')

    return map_html

def create_deforestation_rate_chart(data) -> go.Figure:
    """Create an enhanced bar chart showing deforestation rates"""
    fig = go.Figure()

    # Calculate cumulative deforestation
    cumulative_deforestation = data['deforestation_rate'].cumsum()

    # Add bar chart for annual rate
    fig.add_trace(go.Bar(
        x=data['year'],
        y=data['deforestation_rate'],
        name='Annual Rate',
        marker_color='#C62828',
        opacity=0.7,
        hovertemplate='Year: %{x}<br>Rate: %{y:.2f} ha/year<extra></extra>'
    ))

    # Add line for cumulative deforestation
    fig.add_trace(go.Scatter(
        x=data['year'],
        y=cumulative_deforestation,
        name='Cumulative Loss',
        line=dict(color='#FF5252', width=2),
        hovertemplate='Year: %{x}<br>Total Loss: %{y:.2f} ha<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text='Deforestation Analysis',
            font=dict(size=24)
        ),
        xaxis_title='Year',
        yaxis_title='Hectares',
        template='simple_white',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig