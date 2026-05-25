import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from pipeline.connectors.npi_connector import parse_npi_record


def test_parse_valid_npi_record():
    mock_record = {
        "number": "1234567890",
        "basic": {
            "first_name": "Jane",
            "last_name": "Doe",
            "credential": "PharmD",
        },
        "addresses": [{"address_purpose": "LOCATION", "state": "TX", "city": "Houston", "postal_code": "77001"}],
        "taxonomies": [{"primary": True, "desc": "Pharmacist"}],
    }
    result = parse_npi_record(mock_record)
    assert result is not None
    assert result["first_name"] == "Jane"
    assert result["state"] == "TX"
    assert result["license_type"] == "pharmacist"


def test_parse_record_missing_name_returns_none():
    result = parse_npi_record({"number": "111", "basic": {}, "addresses": [], "taxonomies": []})
    assert result is None
