# phase3_sampler.py
import pandas as pd
import numpy as np
import streamlit as st
from numpy.random import choice

def sample_metropol_neighborhoods(df, sampling_frame):
    st.subheader("📍 Road 1: Metropolitan Sampling")
    metropol_strata = sampling_frame[sampling_frame['Neighborhood_BŞ'] > 0]
    results = []

    for _, row in metropol_strata.iterrows():
        group = row['Group']
        n = int(row['Neighborhood_BŞ'])
        group_df = df[(df['Group'] == group) & (df['STATU_CAT'] == 'BŞ')]

        if not group_df.empty:
            sampled = group_df.sample(n=min(n, len(group_df)), weights=group_df['population'], random_state=42)
            results.append(sampled)

    sampled_df = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
    st.write("Sampled Metropolitan Neighborhoods:")
    st.dataframe(sampled_df[['province', 'district', 'neighborhood_code', 'population']])
    return sampled_df

def simple_rounding_allocation(pop_matrix, total_neigh):
    flat_pop = np.nan_to_num(pop_matrix.flatten().astype(float))
    pop_total = flat_pop.sum()
    if pop_total == 0:
        return np.zeros_like(pop_matrix, dtype=int)

    fractional_neigh = total_neigh * (flat_pop / pop_total)
    floored = np.floor(fractional_neigh).astype(int)
    remainders = fractional_neigh - floored
    remaining = total_neigh - floored.sum()

    if remaining > 0:
        indices = np.argsort(-remainders)
        for i in indices[:remaining]:
            floored[i] += 1

    return floored.reshape(pop_matrix.shape)

def sample_other_neighborhoods(df, sampling_frame):
    st.subheader("📍 Road 2: Other Sampling")
    other_strata = sampling_frame[sampling_frame['Neighborhood_M&D'] > 0]
    all_results = []

    for _, row in other_strata.iterrows():
        
        group = row['Group']
        total_interviews = int(row['Neighborhood_M&D']) * 2
        group_df = df[(df['Group'] == group) & (df['STATU_CAT'] == 'M&D')]
        

        if group_df.empty:
            continue

        matrix = np.zeros((2, 1))
        for i, ilce_status in enumerate([1, 2]):
            subset = group_df[group_df['status'] == ilce_status]
            matrix[i, 0] = subset['population'].sum() if not subset.empty else 0

        total_neigh = int(row['Neighborhood_M&D'])
        neigh_alloc = simple_rounding_allocation(matrix, total_neigh)
        sample_parts = []

        for i, ilce_status in enumerate([1, 2]):
            sub_df = group_df[group_df['status'] == ilce_status]
            districts = sub_df['district'].unique()

            if len(districts) == 0:
                continue

            if ilce_status == 1:
                selected_district = districts[0]
            else:
                pop_by_district = sub_df.groupby('district')['population'].sum()
                probs = pop_by_district / pop_by_district.sum()
                selected_district = choice(pop_by_district.index, p=probs)

            needed = neigh_alloc[i, 0]
            if needed == 0:
                continue
            cell_df = group_df[(group_df['status'] == ilce_status) &
                        (group_df['district'] == selected_district)]
            
            if cell_df.empty:
                cell_df = group_df[group_df['status'] == ilce_status]
                st.warning(f"⚠️ No neighborhoods matched district {selected_district}. Fallback to group-wide sampling for ILCE_STATU={ilce_status}")
            if not cell_df.empty:
                    selected = cell_df.sample(n=min(needed, len(cell_df)), weights=cell_df['population'], random_state=42)
                    sample_parts.append(selected)

        if sample_parts:
            all_results.append(pd.concat(sample_parts, ignore_index=True))

    final_other = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    
    st.write("Sampled Other Neighborhoods:")
    if not final_other.empty and all(col in final_other.columns for col in ['province', 'district', 'neighborhood_code', 'neighborhood_status', 'population']):
        st.dataframe(final_other[['province', 'district', 'neighborhood_code', 'neighborhood_status', 'population']])
    else:
        st.warning("⚠️ No valid neighborhoods were selected or expected columns are missing.")

    if not final_other.empty:
        st.subheader("📊 Neighborhoods by ILCE_STATU")
        ilce_summary = final_other.groupby('status').size().reset_index(name='count')
        ilce_summary['status'] = ilce_summary['status'].map({1: "Central", 2: "Outer"})
        import plotly.express as px
        fig = px.bar(ilce_summary, x='status', y='count', title='Allocated Neighborhoods by ILCE_STATU')
        st.plotly_chart(fig, use_container_width=True)
    return final_other
