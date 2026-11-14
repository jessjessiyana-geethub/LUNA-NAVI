
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from datetime import timedelta


def build_demo_solar_data(scenario):

    start = scenario.datetime_utc

    times = [
        start + timedelta(hours=i)
        for i in range(25)
    ]

    hours = np.arange(25)

    elevation = 8 * np.sin(
        2 * np.pi * hours / 24
    )

    azimuth = (hours * 15) % 360

    return pd.DataFrame({
        "Time (UTC)": times,
        "Sun Elevation (°)": elevation,
        "Sun Azimuth (°)": azimuth
    })


def render_solar_analysis(scenario):

    st.header("☀️ Solar Position Analysis")

    st.warning(
        "DEMO MODE: Artificial data, "
        "not actual lunar solar measurements."
    )

    st.write("Landing Site:", scenario.site_name)

    data = build_demo_solar_data(scenario)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["Time (UTC)"],
        y=data["Sun Elevation (°)"],
        mode="lines+markers",
        name="Solar Elevation"
    ))

    fig.update_layout(
        title="Solar Elevation Chart",
        xaxis_title="Time (UTC)",
        yaxis_title="Elevation (degrees)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Solar Data")

    st.dataframe(data)
