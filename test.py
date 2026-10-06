import pandas as pd
import pytest

def load_data():
    return pd.read_csv("language_learning_data.csv")

def test_data_loading_and_record_count():
    """Ensure the dataset contains at least 200 records as required."""
    df = load_data()
    assert len(df) >= 200

def test_required_columns_exist():
    """Verify that all essential columns are present in the dataset."""
    df = load_data()
    expected_cols = ['nom_langue', 'code', 'territoire', 'statut', 'description', 'localisation', 'latitude', 'longitude']
    for col in expected_cols:
        assert col in df.columns

def test_region_filtering():
    """Test filtering by Australian region/territory (e.g., WA)."""
    df = load_data()
    wa_df = df[df['territoire'] == 'WA']
    assert len(wa_df) > 0
    assert all(wa_df['territoire'] == 'WA')

def test_status_filtering():
    """Test filtering by documentation status."""
    df = load_data()
    confirmed_df = df[df['statut'] == 'Confirmed']
    assert len(confirmed_df) > 0
    assert all(confirmed_df['statut'] == 'Confirmed')

def test_text_search_by_name():
    """Test text search functionality using language name."""
    df = load_data()
    sample_name = df.iloc[0]['nom_langue']
    result = df[df['nom_langue'].str.contains(sample_name, case=False, na=False)]
    assert len(result) >= 1

def test_text_search_by_code():
    """Test text search functionality using AUSTLANG code."""
    df = load_data()
    sample_code = df.iloc[0]['code']
    result = df[df['code'].str.contains(str(sample_code), case=False, na=False)]
    assert len(result) >= 1

def test_coordinate_bounds():
    """Verify that geographic coordinates fall within Australia's bounding box (including Torres Strait Islands)."""
    df = load_data()
    valid_coords = df.dropna(subset=['latitude', 'longitude'])
    # Adjusted latitude range to safely cover northern islands like TSI (-9.35)
    assert all(valid_coords['latitude'].between(-45, -8))
    assert all(valid_coords['longitude'].between(110, 155))

def test_empty_search_result_edge_case():
    """Test edge case for a non-existent search term (should return 0 rows without crashing)."""
    df = load_data()
    non_existent = df[df['nom_langue'].str.contains("XYZNONEXISTENT999", case=False, na=False)]
    assert len(non_existent) == 0