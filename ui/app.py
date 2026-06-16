from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px

from services.receiver_launcher import start_receiver
from services.receiver_service import (
    receiver_running,
    stop_receiver,
    restart_receiver,
)
from services.ros2_service import ros2_connected
from services.zenoh_service import zenoh_running
from services.zenoh_launcher import (
    start_zenoh,
    stop_zenoh,
)
from services.robot_service import (
    robot_status,
    execute_trajectory,
)

st.set_page_config(
    page_title="Fairino Edge Operator",
    layout="wide"
)

st.title("Fairino Edge Operator")

# SESSION STATE

if "execution_status" not in st.session_state:
    st.session_state.execution_status = "Idle"


# REFRESH

if st.button("Refresh Dashboard"):
    st.rerun()

# ZENOH CONTROL

st.subheader("Zenoh Control")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Start Zenoh",
        use_container_width=True
    ):

        start_zenoh()
        st.rerun()

with col2:

    if st.button(
        "Stop Zenoh",
        use_container_width=True
    ):

        stop_zenoh()
        st.rerun()

st.divider()

# SYSTEM STATUS


st.subheader("System Status")

robot_info = robot_status()

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Zenoh",
        "Running" if zenoh_running() else "Stopped"
    )

with col2:

    st.metric(
        "ROS2",
        "Connected" if ros2_connected() else "Disconnected"
    )

with col3:

    st.metric(
        "Receiver",
        "Running" if receiver_running() else "Stopped"
    )

with col4:

    st.metric(
        "Robot",
        "Connected" if robot_info["connected"] else "Disconnected"
    )

st.divider()


# RECEIVER CONTROL


st.subheader("Receiver Control")

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "Start Receiver",
        use_container_width=True
    ):

        if not receiver_running():
            start_receiver()

        st.rerun()

with col2:

    if st.button(
        "Restart Receiver",
        use_container_width=True
    ):

        restart_receiver()
        st.rerun()

with col3:

    if st.button(
        "Stop Receiver",
        use_container_width=True
    ):

        stop_receiver()
        st.rerun()

with col4:

    st.metric(
        "Receiver State",
        "Running"
        if receiver_running()
        else "Stopped"
    )

st.divider()


# ROBOT STATUS


st.subheader("Robot Status")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Controller IP",
        robot_info["controller_ip"]
    )

with col2:

    st.metric(
        "Robot State",
        "Connected"
        if robot_info["connected"]
        else "Disconnected"
    )

if st.button(
    "Test Robot Connection",
    use_container_width=True
):

    robot_info = robot_status()

    if robot_info["connected"]:

        st.success(
            f"Connected to {robot_info['controller_ip']}"
        )

    else:

        st.error(
            "Robot not reachable"
        )

st.divider()


# TRAJECTORY SOURCE


st.subheader("Trajectory Source")

source = st.radio(
    "Select Source",
    [
        "Received CSV",
        "Test CSV"
    ],
    horizontal=True
)

if source == "Received CSV":

    trajectory_file = (
        ROOT
        / "data"
        / "trajectories"
        / "received_trajectory.csv"
    )

    if st.button(
        "Clear Received Trajectory",
        use_container_width=True
    ):

        if trajectory_file.exists():
            trajectory_file.unlink()

        st.rerun()

else:

    trajectory_file = (
        ROOT
        / "skill_reuse_live_screwdriver_1_events_mm.csv"
    )


# FILE CHECK


if not trajectory_file.exists():

    st.warning(
        f"Trajectory file not found:\n{trajectory_file}"
    )

    st.stop()

try:

    df = pd.read_csv(trajectory_file)

except Exception as e:

    st.error(
        f"Failed to load trajectory:\n{e}"
    )

    st.stop()


# FILE INFO


modified_time = trajectory_file.stat().st_mtime

st.subheader("Trajectory File")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "File",
        trajectory_file.name
    )

with col2:

    st.metric(
        "Last Update",
        datetime.fromtimestamp(
            modified_time
        ).strftime("%H:%M:%S")
    )

st.divider()


# STATISTICS


st.subheader("Trajectory Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Points",
        len(df)
    )

with col2:

    event_count = 0

    if "event" in df.columns:

        event_count = len(
            df["event"]
            .fillna("")
            .astype(str)
            .replace("nan", "")
            .loc[lambda x: x != ""]
        )

    st.metric(
        "Events",
        event_count
    )

with col3:

    z_col = None

    if "z_mm" in df.columns:
        z_col = "z_mm"

    elif "z" in df.columns:
        z_col = "z"

    if z_col:

        st.metric(
            "Min Z",
            round(df[z_col].min(), 2)
        )

with col4:

    if z_col:

        st.metric(
            "Max Z",
            round(df[z_col].max(), 2)
        )

st.divider()


# TABLE PREVIEW


st.subheader("Trajectory Preview")

st.dataframe(
    df,
    width="stretch",
    height=350
)

st.divider()


# 3D VISUALIZATION


x_col = None
y_col = None
z_col = None

if {"x_mm", "y_mm", "z_mm"}.issubset(df.columns):

    x_col = "x_mm"
    y_col = "y_mm"
    z_col = "z_mm"

elif {"x", "y", "z"}.issubset(df.columns):

    x_col = "x"
    y_col = "y"
    z_col = "z"

if x_col:

    st.subheader("3D Trajectory")

    fig = px.line_3d(
        df,
        x=x_col,
        y=y_col,
        z=z_col
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

st.divider()


# EXECUTION


st.subheader("Execution")

st.metric(
    "Execution Status",
    st.session_state.execution_status
)

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Execute Trajectory",
        type="primary",
        use_container_width=True
    ):

        try:

            st.session_state.execution_status = "Running"

            execute_trajectory(
                str(trajectory_file)
            )

            st.session_state.execution_status = "Completed"

            st.success(
                "Trajectory execution completed."
            )

        except Exception as e:

            st.session_state.execution_status = "Failed"

            st.error(
                f"Execution failed:\n{e}"
            )

with col2:

    if st.button(
        "Reload Dashboard",
        use_container_width=True
    ):

        st.rerun()

st.divider()

st.info(
    "Workflow: Zenoh → ROS2 Receiver → Received Trajectory → Trajectory Executor → Fairino Robot"
)