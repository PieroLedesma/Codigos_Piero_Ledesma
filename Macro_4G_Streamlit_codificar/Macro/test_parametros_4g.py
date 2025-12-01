
import sys
import os
import pandas as pd
from io import BytesIO

# Add Macro directory to path
sys.path.append(os.path.abspath("Macro"))

from functions.parametros_generator import generate_parametros_mos

# Mock data_reader functions to avoid dependency on actual Excel files
import functions.data_reader as dr

def mock_read_node_mos_grouped(x):
    return {
        'AnrFunctionNR': [{'AnrFunctionNRId': '1', 'attr1': 'val1'}],
        'EndcProfile': [{'EndcProfileId': '1', 'attr1': 'val1'}],
        'SubscriberGroupProfile': [{'SubscriberGroupProfileId': '1', 'profilePriority': '10'}],
        'QciProfileOperatorDefined': [
            {'qci': '1', 'priority': '1'},
            {'qci': '254', 'priority': '10', 'dscp': '18', 'caOffloadingEnabled': 'True'}
        ],
        'NbIotCell': [{'NbIotCellId': '1', 'cellId': '10', 'eutranCellRef': 'EUtranCellFDD=1'}]
    }

def mock_read_equipment_all_mos(x):
    return {}

def mock_read_features_sheet(x):
    return {'Feature1': '1'}

def mock_read_equipment_profiles(x):
    return ({}, {})

def mock_read_cell_carrier_full(x):
    return {'1': {'ReportConfigB1GUtra': {'attr1': 'val1'}}}

# Patch the functions in the module
dr._read_node_mos_grouped = mock_read_node_mos_grouped
dr._read_equipment_all_mos = mock_read_equipment_all_mos
dr._read_features_sheet = mock_read_features_sheet
dr._read_equipment_profiles = mock_read_equipment_profiles

# Also patch the local imports in parametros_generator if they were imported directly
import functions.parametros_generator as pg
pg._read_node_mos_grouped = mock_read_node_mos_grouped
pg._read_equipment_all_mos = mock_read_equipment_all_mos
pg._read_features_sheet = mock_read_features_sheet
pg._read_equipment_profiles = mock_read_equipment_profiles
pg._read_cell_carrier_full = mock_read_cell_carrier_full

def test_generation():
    print("Testing generate_parametros_mos...")
    try:
        # Pass a dummy object as rnd_file since we mocked the readers
        output = generate_parametros_mos("GLA781", "dummy_file")
        print("Generation successful!")
        print("Output preview (first 20 lines):")
        print("\n".join(output.split("\n")[:20]))
        
        # Check for specific sections
        if "AnrFunctionNR" in output: print("[OK] AnrFunctionNR section found")
        if "SubscriberGroupProfile" in output: print("[OK] SubscriberGroupProfile section found")
        if "QciProfileOperatorDefined" in output: print("[OK] QciProfileOperatorDefined section found")
        if "NbIotCell" in output: print("[OK] NbIotCell section found")
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
