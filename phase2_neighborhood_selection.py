# phase_neighborhood_selection.py
import pandas as pd
import streamlit as st

def filter_by_nuts3(df, metropol_file, other_file):
    try:
        metropol_nuts3 = pd.read_csv(metropol_file)['NUTS3KODU'].dropna().unique().tolist()
        other_nuts3 = pd.read_csv(other_file)['NUTS3KODU'].dropna().unique().tolist()
        all_selected = set(metropol_nuts3 + other_nuts3)

        filtered = df[df['nuts3'].isin(all_selected)].copy()
        filtered['GroupLabel'] = filtered['nuts3'].apply(
            lambda x: 'Metropol' if x in metropol_nuts3 else 'Other'
        )

        st.session_state['df_filtered'] = filtered  # Used in Phase 3

        df_metropol = filtered[filtered['STATU_CAT'] == 'BŞ']
        df_other = filtered[filtered['STATU_CAT'] == 'M&D']

        provinces = filtered['province'].nunique()
        districts = filtered['district'].nunique()
        population = filtered['population'].sum()
        st.info(f"Filtered data covers {provinces} provinces, {districts} districts, total population: {population:,}")

        return df_metropol, df_other

    except Exception as e:
        st.error(f"Error during NUTS3 filtering: {str(e)}")
        return None, None

def export_neighborhood_codes(df, filename):
    try:
        codes = df['neighborhood_code'].dropna().astype(str).drop_duplicates().sort_values()
        codes.to_csv(filename, index=False, header=False, encoding='utf-8')
        st.success(f"Exported: {filename} ({len(codes)} records)")
    except Exception as e:
        st.error(f"Failed to export {filename}: {str(e)}")

def check_status_distribution(df):
    if df is None or df.empty:
        return
    status1_counts = df[(df['STATU_CAT'] == 'M&D') & (df['status'] == 1)].groupby('Group').size()
    if status1_counts.empty:
        st.warning("⚠️ No neighborhoods with status=1 (Central) found in 'Other' strata for some groups.")

# ---- UI Integration ----
def neighborhood_selection_ui(df):
    st.header("📍 Phase 2: Neighborhood Selection")

    col1, col2 = st.columns(2)
    with col1:
        metropol_file = st.file_uploader("Upload Metropol Provinces (CSV)", type="csv", key="metropol")
    with col2:
        other_file = st.file_uploader("Upload Other Provinces (CSV)", type="csv", key="other")

    if metropol_file and other_file:
        if st.button("Generate Neighborhood Lists"):
            df_metropol, df_other = filter_by_nuts3(df, metropol_file, other_file)
            if df_metropol is not None and df_other is not None:
                export_neighborhood_codes(df_metropol, "metropol.txt")
                export_neighborhood_codes(df_other, "other.txt")
                check_status_distribution(st.session_state['df_filtered'])
