# views/upload.py
import streamlit as st
import pandas as pd
from services.processor import process_dataframe


def show_upload():
    st.title("📤 Upload Data")
    
    st.markdown("""
    Upload your inventory data file to start the dashboard.
    
    Supported formats: **CSV**, **Excel** (.xlsx, .xls)
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        help="Upload your inventory report"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # ✅ FIX 3: Store in both session state variables
            st.session_state.uploaded_dataframe = df  # For data_loader.py
            st.session_state.original_dataframe = df  # For upload view
            
            # Display preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            st.info(f"📊 Total rows: {len(df)}")
            st.info(f"📂 Total columns: {len(df.columns)}")
            
            # Process data with default filter
            with st.spinner("Processing data..."):
                dashboard_data = process_dataframe(df, expiry_window="All Inventory")
                st.session_state.dashboard_data = dashboard_data
            
            st.success("✅ Data processed successfully!")
            
            # Show column info
            with st.expander("📊 Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    else:
        st.info("👆 Please upload a file to get started")