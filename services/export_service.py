import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64


def export_csv(df, filename=None):
    """Export dataframe to CSV"""
    if filename is None:
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{filename}.csv",
        mime="text/csv"
    )


def export_excel(df, filename=None, sheet_name="Sheet1"):
    """Export dataframe to Excel (requires openpyxl)"""
    try:
        import openpyxl
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if isinstance(df, dict):
                for sheet, data in df.items():
                    data.to_excel(writer, sheet_name=sheet[:31], index=False)
            else:
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        
        output.seek(0)
        
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ImportError:
        st.warning("⚠️ Excel export requires openpyxl. Install with: pip install openpyxl")
        # Fallback to CSV
        export_csv(df, filename)


def export_multi_sheet_excel(dataframes, filename=None):
    """Export multiple dataframes to Excel with sheets"""
    try:
        import openpyxl
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        
        output.seek(0)
        
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        st.download_button(
            label="📥 Download Excel (Multi-Sheet)",
            data=output,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ImportError:
        st.warning("⚠️ Excel export requires openpyxl. Install with: pip install openpyxl")