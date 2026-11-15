
import streamlit as st


def render_3d_lunar_visualization(scenario=None):

    st.header("🌕 3D Lunar Visualization")

    st.write(
        "Interactive three-dimensional exploration "
        "of the lunar surface."
    )

    if scenario is not None:
        st.subheader("Selected Lunar Site")

        st.metric("Site", scenario.site_name)

        st.metric(
            "Latitude",
            f"{scenario.latitude:.2f}°"
        )

        st.metric(
            "Longitude",
            f"{scenario.longitude:.2f}°"
        )

    # Your 3D Moon visualization code goes here.
    st.info(
        "Your interactive 3D Moon globe will appear here."
    )
