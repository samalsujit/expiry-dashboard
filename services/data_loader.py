# services/data_loader.py
from pathlib import Path

import pandas as pd
import streamlit as st


RAW_FOLDER = Path("data/raw")


def save_uploaded_file(uploaded_file):
    """Save uploaded file to data/raw"""

    # Check that data/raw is actually a folder
    if RAW_FOLDER.exists() and not RAW_FOLDER.is_dir():
        raise RuntimeError(
            "'data/raw' exists as a file. Delete it and create a folder named 'raw'."
        )

    # Create folder if it doesn't exist
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)

    file_path = RAW_FOLDER / uploaded_file.name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def load_dataframe(file_path):
    """Load uploaded file into a DataFrame"""

    suffix = Path(file_path).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)

    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    else:
        raise ValueError("Unsupported file type")


def get_latest_dataframe():
    """Return uploaded DataFrame from session"""
    # ✅ Check both possible session state variables
    df = st.session_state.get("uploaded_dataframe")
    if df is None:
        df = st.session_state.get("original_dataframe")
    return df