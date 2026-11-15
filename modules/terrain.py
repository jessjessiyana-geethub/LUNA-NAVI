import streamlit as st
import plotly.graph_objects as go
import numpy as np

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="LUNA NAV - 3D Lunar Navigation",
    layout="wide"
)

st.title("🌙 LUNA NAV - Lunar South Pole Imaging & Navigation System")

# =====================================================
# 2. TOP 3 RECOMMENDED SITES
# =====================================================

def get_top_three_recommended_sites():

    """
    Reserved Interface:
    Team members can integrate the landing site
    filtering algorithm here in the future.
    """

    return [

        {
            "name": "Connecting Ridge (Rank 1)",
            "lat": -89.4632,
            "lon": -137.49,
            "slope": "Gentle (<5°)",
            "illumination": "Peak of Eternal Light (PEA)",
            "recommend_level": "⭐⭐⭐⭐⭐",
            "comment": "Optimal illumination and slope conditions."
        },

        {
            "name": "Shackleton Rim (Rank 2)",
            "lat": -89.7668,
            "lon": -171.87,
            "slope": "Moderate (5°-15°)",
            "illumination": "Peak of Eternal Light (PEA)",
            "recommend_level": "⭐⭐⭐⭐",
            "comment": "Close to PSR regions for water-ice exploration."
        },

        {
            "name": "Leibnitz Beta Plateau (Rank 3)",
            "lat": -85.4266,
            "lon": 31.74276,
            "slope": "Gentle (<5°)",
            "illumination": "Peak of Eternal Light (PEA)",
            "recommend_level": "⭐⭐⭐",
            "comment": "Flat terrain with excellent solar power support."
        }

    ]


# =====================================================
# 3. SESSION STATE
# =====================================================

if "markers" not in st.session_state:

    st.session_state.markers = get_top_three_recommended_sites()


if "selected_marker" not in st.session_state:

    st.session_state.selected_marker = 0


# =====================================================
# 4. GENERATE 3D MOON SURFACE
# =====================================================

def generate_moon_surface():

    resolution = 150

    theta = np.linspace(0, 2 * np.pi, resolution)

    phi = np.linspace(0, np.pi, resolution)

    theta, phi = np.meshgrid(theta, phi)

    # Spherical coordinates

    x = np.sin(phi) * np.cos(theta)

    y = np.sin(phi) * np.sin(theta)

    z = np.cos(phi)

    # Generate procedural lunar surface texture

    texture = (
        np.sin(theta * 12) * 0.08
        + np.cos(phi * 20) * 0.08
        + np.sin(theta * 25 + phi * 10) * 0.04
        + np.cos(theta * 35) * 0.03
    )

    # Crater-like surface patterns

    for i in range(35):

        cx = np.random.uniform(-1, 1)

        cy = np.random.uniform(-1, 1)

        cz = np.random.uniform(-1, 1)

        crater_radius = np.random.uniform(0.015, 0.07)

        distance = np.sqrt(
            (x - cx)**2 +
            (y - cy)**2 +
            (z - cz)**2
        )

        texture -= np.exp(
            -(distance**2) / (crater_radius**2)
        ) * 0.15

    return x, y, z, texture


# =====================================================
# 5. CONVERT LATITUDE AND LONGITUDE TO 3D
# =====================================================

def latlon_to_xyz(lat, lon, radius=1.015):

    lat_rad = np.radians(lat)

    lon_rad = np.radians(lon)

    x = radius * np.cos(lat_rad) * np.cos(lon_rad)

    y = radius * np.cos(lat_rad) * np.sin(lon_rad)

    z = radius * np.sin(lat_rad)

    return x, y, z


# =====================================================
# 6. CREATE 3D MOON MODEL
# =====================================================

def create_3d_moon():

    x, y, z, texture = generate_moon_surface()

    fig = go.Figure()

    # Moon surface

    fig.add_trace(

        go.Surface(

            x=x,

            y=y,

            z=z,

            surfacecolor=texture,

            colorscale=[

                [0.0, "#292929"],

                [0.2, "#555555"],

                [0.5, "#929292"],

                [0.8, "#BDBDBD"],

                [1.0, "#E0E0E0"]

            ],

            showscale=False,

            lighting=dict(

                ambient=0.35,

                diffuse=0.8,

                specular=0.3,

                roughness=0.9,

                fresnel=0.1

            ),

            lightposition=dict(

                x=100,

                y=100,

                z=200

            ),

            hoverinfo="skip"

        )

    )

    # =================================================
    # ADD LANDING SITE MARKERS
    # =================================================

    markers = st.session_state.markers

    marker_x = []

    marker_y = []

    marker_z = []

    marker_names = []

    marker_colors = []

    marker_customdata = []

    colors = [

        "#00FF99",

        "#FFD700",

        "#FF8C42"

    ]

    for idx, marker in enumerate(markers):

        px, py, pz = latlon_to_xyz(

            marker["lat"],

            marker["lon"]

        )

        marker_x.append(px)

        marker_y.append(py)

        marker_z.append(pz)

        marker_names.append(marker["name"])

        marker_colors.append(colors[idx])

        marker_customdata.append(idx)

    # Landing site points

    fig.add_trace(

        go.Scatter3d(

            x=marker_x,

            y=marker_y,

            z=marker_z,

            mode="markers+text",

            marker=dict(

                size=8,

                color=marker_colors,

                symbol="circle",

                line=dict(

                    color="white",

                    width=2

                )

            ),

            text=marker_names,

            textposition="top center",

            textfont=dict(

                color="white",

                size=10

            ),

            customdata=marker_customdata,

            hovertemplate=(

                "<b>%{text}</b><br>"

                "Click to inspect location"

                "<extra></extra>"

            )

        )

    )

    # =================================================
    # 3D SCENE SETTINGS
    # =================================================

    fig.update_layout(

        height=650,

        margin=dict(

            l=0,

            r=0,

            t=0,

            b=0

        ),

        paper_bgcolor="#080B12",

        plot_bgcolor="#080B12",

        scene=dict(

            bgcolor="#080B12",

            xaxis=dict(

                visible=False

            ),

            yaxis=dict(

                visible=False

            ),

            zaxis=dict(

                visible=False

            ),

            aspectmode="cube",

            camera=dict(

                eye=dict(

                    x=0.1,

                    y=-2.5,

                    z=1.8

                ),

                center=dict(

                    x=0,

                    y=0,

                    z=0

                )

            )

        ),

        showlegend=False

    )

    return fig


# =====================================================
# 7. DISPLAY 3D INTERACTIVE MOON
# =====================================================

st.markdown("### 🌍 3D Lunar South Pole Interactive Model")

st.caption(

    "Rotate, zoom and explore the Moon. "

    "Select a landing site using the markers or site buttons below."

)

fig = create_3d_moon()

# Display 3D model

event = st.plotly_chart(

    fig,

    use_container_width=True,

    on_select="rerun",

    selection_mode="points",

    key="moon_3d_map"

)


# =====================================================
# 8. HANDLE MARKER SELECTION
# =====================================================

if event and event.selection and event.selection.points:

    selected_point = event.selection.points[0]

    selected_index = selected_point.get("customdata")

    if selected_index is not None:

        st.session_state.selected_marker = int(selected_index)


# =====================================================
# 9. SELECTED LOCATION INFORMATION
# =====================================================

st.markdown("---")

st.subheader("📍 Currently Selected Landing Site Details")

current_selected = st.session_state.markers[

    st.session_state.selected_marker

]

col1, col2, col3, col4 = st.columns(4)

col1.metric(

    "Selected Site",

    current_selected["name"]

)

col2.metric(

    "Recommendation",

    current_selected["recommend_level"]

)

col3.metric(

    "Latitude",

    f"{current_selected['lat']}°"

)

col4.metric(

    "Longitude",

    f"{current_selected['lon']}°"

)

st.info(

    f"""

    **Slope Condition:** {current_selected['slope']}

    **Illumination:** {current_selected['illumination']}

    **Comment:** {current_selected['comment']}

    """

)


# =====================================================
# 10. TOP 3 RECOMMENDED SITES OVERVIEW
# =====================================================

st.markdown("---")

st.subheader("🌟 Top 3 Recommended Landing Sites Overview")

cols = st.columns(3)

for idx, marker in enumerate(st.session_state.markers):

    with cols[idx]:

        with st.container(border=True):

            st.markdown(f"### Rank #{idx+1}")

            st.markdown(f"**{marker['name']}**")

            st.write(

                f"⭐ Recommendation: {marker['recommend_level']}"

            )

            st.write(

                f"Latitude: {marker['lat']}°"

            )

            st.write(

                f"Longitude: {marker['lon']}°"

            )

            st.write(

                f"Slope: {marker['slope']}"

            )

            st.write(

                f"Illumination: {marker['illumination']}"

            )

            if st.button(

                f"Inspect Rank #{idx+1}",

                key=f"inspect_{idx}"

            ):

                st.session_state.selected_marker = idx

                st.rerun()


# =====================================================
# 11. FOOTER
# =====================================================

st.markdown("---")

st.caption(

    "LUNA NAV | Lunar Navigation & Landing Assessment Tool"

)
