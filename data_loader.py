import pandas as pd
import streamlit as st
from utils import load_config, assign_group, classify_statut

def load_data(file, config, is_csv=False):
    try:
        if is_csv:
            df = pd.read_csv(file, low_memory=False)
        else:
            df = pd.read_excel(file, engine='openpyxl')

        st.write("Original dataset columns:", df.columns.tolist())

        df.columns = df.columns.str.strip().str.replace('\u00a0', ' ').str.replace(' ', '_').str.upper()

        column_mapping = {v: k for k, v in config['columns'].items()}
        df = df.rename(columns=column_mapping)

        required_columns = list(config['columns'].keys())
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing columns in dataset: {missing_cols}")
            st.stop()

        nuts_cols = ['nuts1', 'nuts2', 'nuts3']
        for col in nuts_cols:
            if df[col].isna().any():
                st.warning(f"Missing values found in {col}. Dropping affected rows.")
                df = df.dropna(subset=[col])

        df = df.dropna(subset=required_columns)

        df['STATU_CAT'] = df['status'].apply(classify_statut)
        df = df[df['STATU_CAT'].isin(['BŞ', 'M&D'])]

        df['Group'] = df.apply(assign_group, axis=1)

        if df['Group'].isna().any():
            st.error("Some rows have missing Group assignments. Check NUTS codes.")
            st.write("Rows with missing groups:", df[df['Group'].isna()][nuts_cols].head())
            st.stop()

        st.success(f"Dataset loaded successfully with {len(df)} rows.")
        return df

    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.stop()
