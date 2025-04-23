import pandas as pd
import yaml
import streamlit as st

def load_config(config_path='config.yaml'):
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        if not config:
            st.error("Configuration file is empty or invalid.")
            st.stop()
        return config
    except FileNotFoundError:
        st.error(f"Configuration file not found: {config_path}")
        st.stop()
    except yaml.YAMLError as e:
        st.error(f"Error parsing configuration file: {str(e)}")
        st.stop()

def assign_group(row):
    try:
        nuts3 = row['nuts3']
        nuts2 = row['nuts2']
        nuts1 = row['nuts1']

        if nuts3 in ['TR100', 'TR310', 'TR510']:
            return nuts3
        if nuts2.startswith('TR61'):
            return 'TR61'
        if nuts2.startswith('TR62') or nuts2.startswith('TR63'):
            return 'TR62&TR63'
        if nuts2.startswith('TRC1'):
            return 'TRC1'
        if nuts2.startswith('TRC2') or (nuts2.startswith('TRC3')):
            return 'TRC2&TRC3'
        if nuts1 == 'TR3' and nuts3 != 'TR310':
            return 'TR3-dışı'
        if nuts1 == 'TR5' and nuts3 != 'TR510':
            return 'TR5-dışı'
        return nuts1

    except Exception as e:
        st.error(f"Error assigning group for row: {str(e)}")
        return None

def classify_statut(stat):
    try:
        if stat == 0:
            return 'BŞ'
        elif stat in [1, 2]:
            return 'M&D'
        return 'Other'
    except Exception as e:
        st.error(f"Error classifying status: {str(e)}")
        return 'Other'