import importlib.util
import json
import logging
from pathlib import Path

import pytest


def _load_etl_module():
    """Load etl.py from the repository without relying on PYTHONPATH."""
    etl_path = Path(__file__).resolve().parents[1] / "src" / "etl.py"
    assert etl_path.is_file(), f"Expected ETL module at {etl_path}"

    spec = importlib.util.spec_from_file_location("etl", etl_path)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def etl():
    """Load the ETL module for a test."""
    return _load_etl_module()


def test_etl_module_imports(etl):
    """The ETL module should import without raising an exception."""
    assert etl is not None


@pytest.mark.parametrize(
    "record",
    [
        {"id": 1, "product": "Laptop", "price": 1200, "quantity": 2},
        {"id": 1, "product": "Laptop", "price": 12.5, "quantity": 0.5},
    ],
)
def test_valid_record(etl, record):
    """Records with required fields and positive numeric values are valid."""
    assert etl.is_valid_record(record) is True


@pytest.mark.parametrize(
    "record",
    [
        None,
        [],
        {},
        {"product": "Laptop", "price": 10, "quantity": 1},
        {"id": None, "product": "Laptop", "price": 10, "quantity": 1},
        {"id": 1, "price": 10, "quantity": 1},
        {"id": 1, "product": "", "price": 10, "quantity": 1},
        {"id": 1, "product": "Laptop", "quantity": 1},
        {"id": 1, "product": "Laptop", "price": 0, "quantity": 1},
        {"id": 1, "product": "Laptop", "price": -1, "quantity": 1},
        {"id": 1, "product": "Laptop", "price": "10", "quantity": 1},
        {"id": 1, "product": "Laptop", "price": True, "quantity": 1},
        {"id": 1, "product": "Laptop", "price": 10, "quantity": 0},
        {"id": 1, "product": "Laptop", "price": 10, "quantity": -1},
        {"id": 1, "product": "Laptop", "price": 10, "quantity": "1"},
        {"id": 1, "product": "Laptop", "price": 10, "quantity": False},
    ],
)
def test_invalid_records(etl, record):
    """Records missing required fields or with invalid values are rejected."""
    assert etl.is_valid_record(record) is False


def test_invalid_record_logs_warning(etl, caplog):
    record = {"id": 1, "product": "Laptop", "price": -1, "quantity": 1}

    with caplog.at_level(logging.WARNING):
        assert etl.is_valid_record(record) is False

    assert "Invalid price" in caplog.text


def test_transform_valid_record_adds_total_without_mutating_input(etl):
    record = {"id": 1, "product": "Laptop", "price": 1200, "quantity": 2}
    original_record = record.copy()

    result = etl.transform_records([record])

    assert result == [{**original_record, "total": 2400}]
    assert record == original_record


def test_transform_records_skips_invalid_records(etl):
    records = [
        {"id": 1, "product": "Laptop", "price": 100, "quantity": 2},
        {"id": 2, "product": "Mouse", "price": -1, "quantity": 3},
        {"id": 3, "product": "Keyboard", "price": 50, "quantity": 1},
    ]

    assert etl.transform_records(records) == [
        {"id": 1, "product": "Laptop", "price": 100, "quantity": 2, "total": 200},
        {"id": 3, "product": "Keyboard", "price": 50, "quantity": 1, "total": 50},
    ]


@pytest.mark.parametrize("records", [[], [{"invalid": "record"}]])
def test_transform_records_returns_empty_list_when_no_records_are_valid(etl, records):
    assert etl.transform_records(records) == []


def test_load_records_reads_json_list(etl, tmp_path):
    input_path = tmp_path / "input.json"
    records = [{"id": 1, "product": "Laptop", "price": 100, "quantity": 2}]
    input_path.write_text(json.dumps(records), encoding="utf-8")

    assert etl.load_records(input_path) == records


def test_load_records_rejects_json_object(etl, tmp_path):
    input_path = tmp_path / "input.json"
    input_path.write_text('{"id": 1}', encoding="utf-8")

    with pytest.raises(ValueError, match="list of records"):
        etl.load_records(input_path)


def test_load_records_rejects_malformed_json(etl, tmp_path):
    input_path = tmp_path / "input.json"
    input_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        etl.load_records(input_path)


def test_save_records_writes_json_that_can_be_loaded(etl, tmp_path):
    output_path = tmp_path / "output.json"
    records = [
        {"id": 1, "product": "Laptop", "price": 100, "quantity": 2, "total": 200}
    ]

    etl.save_records(records, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == records

def test_full_etl_pipeline(etl, tmp_path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    records = [
        {"id": 1, "product": "Laptop", "price": 100, "quantity": 2},
        {"id": 2, "product": "Mouse", "price": -1, "quantity": 3},
        {"id": 3, "product": "Keyboard", "price": 50, "quantity": 1},
    ]
    input_path.write_text(json.dumps(records), encoding="utf-8")

    loaded_records = etl.load_records(input_path)
    transformed_records = etl.transform_records(loaded_records)
    etl.save_records(transformed_records, output_path)

    expected_output = [
        {"id": 1, "product": "Laptop", "price": 100, "quantity": 2, "total": 200},
        {"id": 3, "product": "Keyboard", "price": 50, "quantity": 1, "total": 50},
    ]
    assert json.loads(output_path.read_text(encoding="utf-8")) == expected_output

