# output_generator.py
import pandas as pd
import streamlit as st
from io import BytesIO
import zipfile

def generate_outputs(output_dict):
    try:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for filename, df in output_dict.items():
                if df is None or df.empty:
                    st.warning(f"{filename} is empty, skipping.")
                    continue
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                z.writestr(filename, excel_buffer.getvalue())

        buffer.seek(0)
        st.success("Outputs generated successfully.")
        return output_dict, buffer

    except Exception as e:
        st.error(f"Error generating outputs: {str(e)}")
        st.stop()
