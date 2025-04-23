# main.py
import streamlit as st
import pandas as pd
import pickle
import hashlib
from pathlib import Path

from data_loader import load_data
from sampling_frame import create_population_distribution, compute_sampling_frame
from sample_allocator import allocate_sample
from output_generator import generate_outputs
from utils import load_config
from phase2_neighborhood_selection import neighborhood_selection_ui
from phase3_sampler import sample_metropol_neighborhoods, sample_other_neighborhoods

st.set_page_config(page_title="Stratified Sampling Tool", layout="wide")
st.title("📊 Stratified Sampling Framework")

with st.expander("📘 How to Use This App (Click to Expand)", expanded=False):
    st.markdown("""
### Welcome to the Stratified Sampling Framework!

This app consists of **four structured phases**:

#### **Phase 1: Sampling Frame**
- Automatically loads ADNKS 2023 dataset.
- Define total interviews and number per neighborhood.
- View and download population distribution and sampling frame.

#### **Phase 2: Neighborhood Selection**
- Upload Metropol and Other province lists.
- App filters and summarizes neighborhoods from ADNKS dataset.
- Download `metropol.txt` and `other.txt`.

#### **Phase 3: Stratified Sampling**
- Use sampling frame to select neighborhoods:
  - **Metropol** groups: PPS sampling by population.
  - **Other** groups: Stratified by neighborhood status and district.

#### **Phase 4: Final Validation**
- Merges both samples.
- Compares final sample to the planned allocation.
- Download final sample and comparison sheet.

All data is cached unless reset. You can rerun each section independently.
""")

# Load configuration
config = load_config()

# Constants
DEFAULT_DATA_PATH = "ADNKS_2023.xlsx"
CACHE_PATH = Path("population_distribution.pkl")
HASH_PATH = Path("data_hash.txt")

# Compute file hash
def compute_hash(df, config):
    return hashlib.sha256((df.to_csv(index=False) + str(config)).encode()).hexdigest()

# Load dataset
@st.cache_data
def cached_load_data():
    return load_data(DEFAULT_DATA_PATH, config, is_csv=False)

try:
    df = cached_load_data()
    # Optional debug output
    if st.checkbox("🔍 Show raw column names (debug)"):
        st.write(df.columns.tolist())
except Exception as e:
    st.error(f"Failed to load default dataset: {e}")
    st.stop()

# Cache population distribution
current_hash = compute_hash(df, config)
if HASH_PATH.exists() and HASH_PATH.read_text() == current_hash and CACHE_PATH.exists():
    population_distribution = pickle.load(open(CACHE_PATH, "rb"))
    st.info("Using cached population distribution.")
else:
    population_distribution = create_population_distribution(df, config)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(population_distribution, f)
    HASH_PATH.write_text(current_hash)
    st.success("Population distribution calculated and cached.")

# Tabs for each phase
tabs = st.tabs(["Phase 1: Sampling Frame", "Phase 2: Neighborhood Selection", "Phase 3 & 4: Final Sampling"])

with tabs[0]:
    st.header("📌 Phase 1: Sampling Frame")
    col1, col2 = st.columns(2)
    with col1:
        total_sample_size = st.number_input("Total Sample Size", min_value=1, value=1000)
    with col2:
        interviews_per_neighborhood = st.number_input("Interviews per Neighborhood", min_value=1, value=10)

    sampling_frame = compute_sampling_frame(population_distribution, total_sample_size, interviews_per_neighborhood)

    st.subheader("Population Distribution")
    st.dataframe(population_distribution)

    st.subheader("Sampling Frame")
    with st.expander("Preview: Sampling Frame (first 5 rows)"):
        st.dataframe(sampling_frame.head())

    outputs, zip_buffer = generate_outputs({
        "population_distribution.xlsx": population_distribution,
        "sampling_frame.xlsx": sampling_frame
    })

    st.download_button(
        label="📥 Download All Outputs (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="sampling_outputs.zip",
        mime="application/zip"
    )

    if st.button("🔄 Reset Cache"):
        if CACHE_PATH.exists():
            CACHE_PATH.unlink()
        if HASH_PATH.exists():
            HASH_PATH.unlink()
        st.experimental_rerun()

with tabs[1]:
    neighborhood_selection_ui(df)
    if 'df_filtered' in st.session_state:
        df = st.session_state['df_filtered']

with tabs[2]:
    st.header("🎯 Phase 3 & 4: Final Sampling and Validation")
    if st.button("Run Final Sampling"):
        metropol_sample = sample_metropol_neighborhoods(df, sampling_frame)
        other_sample = sample_other_neighborhoods(df, sampling_frame)

        final_sample = pd.concat([metropol_sample, other_sample], ignore_index=True)

        st.subheader("📋 Final Sample vs Plan")
        comparison = final_sample.groupby('Group').size().reset_index(name='Sampled_Neighborhoods')
        merged_plan = sampling_frame[['Group', 'Neighborhood_Count']].merge(comparison, on='Group', how='left').fillna(0)
        merged_plan['Sampled_Neighborhoods'] = merged_plan['Sampled_Neighborhoods'].astype(int)
        with st.expander("Preview: Final Sample Plan Comparison (first 5 rows)"):
            st.dataframe(merged_plan.head())

        outputs_final, zip_final = generate_outputs({
            "final_sample.xlsx": final_sample,
            "sample_plan_vs_actual.xlsx": merged_plan
        })

        st.download_button(
            label="📥 Download Final Sampling Outputs (ZIP)",
            data=zip_final.getvalue(),
            file_name="final_sampling_outputs.zip",
            mime="application/zip"
        )
