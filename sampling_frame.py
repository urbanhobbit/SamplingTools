import pandas as pd
import streamlit as st

def eval_condition(condition, df, config):
    try:
        col_map = {v: k for k, v in config['columns'].items()}
        parts = condition.split(' and ')
        mask = pd.Series(True, index=df.index)
        for part in parts:
            field, value = part.split('==')
            field = col_map.get(field.strip(), field.strip())
            value = value.strip().strip("'").strip('"')
            mask &= df[field] == value
        return mask
    except Exception as e:
        st.error(f"Error evaluating condition '{condition}': {str(e)}")
        return pd.Series(False, index=df.index)

def create_population_distribution(df, config):
    try:
        adjustments = {}
        for adj in config['special_adjustments']:
            stratum = adj['stratum']
            condition = adj['condition']
            if adj['action'] == 'add_population':
                pop = df[eval_condition(condition, df, config)]['population'].sum()
                adjustments[stratum] = pop

        table = pd.pivot_table(
            df,
            values='population',
            index='Group',
            columns='STATU_CAT',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        if 'M&D' not in table.columns:
            table['M&D'] = 0
        if 'BŞ' not in table.columns:
            table['BŞ'] = 0

        for stratum, pop in adjustments.items():
            if stratum in table['Group'].values:
                table.loc[table['Group'] == stratum, 'M&D'] += pop

        table['Total_Pop'] = table['BŞ'] + table['M&D']
        return table.sort_values('Group').reset_index(drop=True)

    except Exception as e:
        st.error(f"Error creating population distribution: {str(e)}")
        st.stop()

def compute_sampling_frame(population_distribution, total_sample_size, interviews_per_neighborhood):
    import numpy as np
    try:
        frame = population_distribution.copy()

        total_pop = frame['Total_Pop'].sum()
        if total_pop == 0:
            st.error("Total population is zero.")
            st.stop()

        frame['Sample_Size'] = (frame['Total_Pop'] / total_pop * total_sample_size).round().astype(int)
        diff = total_sample_size - frame['Sample_Size'].sum()
        if diff != 0:
            frame.loc[frame['Sample_Size'].idxmax(), 'Sample_Size'] += diff

        frame['Neighborhood_Count'] = (frame['Sample_Size'] / interviews_per_neighborhood).apply(np.ceil).astype(int)
        frame['Neighborhood_BŞ'] = ((frame.get('BŞ', 0) / frame['Total_Pop']) * frame['Neighborhood_Count']).round().astype(int)
        frame['Neighborhood_M&D'] = frame['Neighborhood_Count'] - frame['Neighborhood_BŞ']

        return frame
    except Exception as e:
        st.error(f"Error computing sampling frame: {str(e)}")
        st.stop()
