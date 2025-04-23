import pandas as pd
import streamlit as st
import numpy as np

def allocate_sample(frame, total_sample_size, interviews_per_neighborhood):
    try:
        # Validate inputs
        if total_sample_size <= 0:
            st.error("Total sample size must be positive.")
            st.stop()
        if interviews_per_neighborhood <= 0:
            st.error("Interviews per neighborhood must be positive.")
            st.stop()
        if frame.empty:
            st.error("Sampling frame is empty.")
            st.stop()

        # Calculate total population
        total_pop = frame['Total_Pop'].sum()
        if total_pop == 0:
            st.error("Total population is zero.")
            st.stop()

        # Allocate sample size proportionally
        frame['Sample_Size'] = (
            frame['Total_Pop'] / total_pop * total_sample_size
        ).round().astype(int)

        # Adjust to ensure sum equals total_sample_size
        diff = total_sample_size - frame['Sample_Size'].sum()
        if diff != 0:
            largest_stratum = frame['Sample_Size'].idxmax()
            frame.loc[largest_stratum, 'Sample_Size'] += diff

        # Calculate number of neighborhoods
        frame['Neighborhood_Count'] = (
            frame['Sample_Size'] / interviews_per_neighborhood
        ).apply(np.ceil).astype(int)

        # Allocate neighborhoods to BŞ and M&D
        frame['Neighborhood_BŞ'] = (
            (frame.get('BŞ', 0) / frame['Total_Pop']) * frame['Neighborhood_Count']
        ).round().astype(int)
        frame['Neighborhood_M&D'] = frame['Neighborhood_Count'] - frame['Neighborhood_BŞ']

        # Handle edge cases where Total_Pop is zero
        frame.loc[frame['Total_Pop'] == 0, ['Sample_Size', 'Neighborhood_Count', 'Neighborhood_BŞ', 'Neighborhood_M&D']] = 0

        # Check for zero allocations
        zero_allocation = frame[
            (frame['Neighborhood_BŞ'] == 0) &
            (frame['Neighborhood_M&D'] == 0) &
            (frame['Sample_Size'] > 0)
        ]
        if not zero_allocation.empty:
            st.warning(f"Zero neighborhood allocation for groups: {zero_allocation['Group'].tolist()}")

        return frame

    except Exception as e:
        st.error(f"Error allocating sample: {str(e)}")
        st.stop()