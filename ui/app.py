import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px

from services.receiver_launcher import start_receiver

st.set_page_config(
    page_title="Fairino Edge",
    layout="wide"
)

st.title("Fairino Edge Receiver")

csv_file = ROOT / "data" / "received_trajectory.csv"

# --------------------------------------------------
# STATUS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Zenoh", "Running")

with col2:
    st.metric("ROS2", "Connected")

with col3:
    st.metric(
        "Trajectory",
        "Found" if csv_file.exists() else "Missing"
    )

st.divider()

# --------------------------------------------------
# RECEIVER CONTROL
# --------------------------------------------------

st.subheader("ROS2 Receiver")

if st.button("Start Receiver"):
    start_receiver()
    st.success("Receiver Started")

st.divider()

# --------------------------------------------------
# TRAJECTORY DATA
# --------------------------------------------------

if csv_file.exists():

    try:

        df = pd.read_csv(csv_file)

        st.subheader("Trajectory Information")

        st.write(f"Points: {len(df)}")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        st.divider()

        st.subheader("3D Trajectory Preview")

        required_columns = ["x", "y", "z"]

        if all(col in df.columns for col in required_columns):

            fig = px.line_3d(
                df,
                x="x",
                y="y",
                z="z",
                title="Received Trajectory"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.error(
                f"CSV must contain columns: {required_columns}"
            )

            st.write("Detected columns:")
            st.write(list(df.columns))

    except Exception as e:

        st.error(f"Failed to read CSV: {e}")

else:

    st.warning(
        "No trajectory received yet.\n\n"
        "Start the ROS2 receiver and publish a trajectory from the server."
    )