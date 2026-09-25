import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


# Extract: read the input records from a JSON file.
def load_records(input_path: Path) -> list[dict[str, Any]]:
	"""Read records from a JSON file."""
	with input_path.open("r", encoding="utf-8") as input_file:
		records = json.load(input_file)

	if not isinstance(records, list):
		raise ValueError("Input JSON must contain a list of records")
	return records


# Validate: check required fields and positive values.
def is_valid_record(record: Any) -> bool:
	"""Validate one record and log a warning when it is invalid."""
	if not isinstance(record, dict):
		logger.warning("Invalid record: expected an object")
		return False

	product = record.get("product", "unknown")
	if "id" not in record or record["id"] is None:
		logger.warning("Invalid id for product %s", product)
		return False
	if not record.get("product"):
		logger.warning("Invalid product for id %s", record["id"])
		return False

	try:
		price = record["price"]
	except KeyError:
		logger.warning("Invalid price for product %s", product)
		return False
	if not isinstance(price, (int, float)) or isinstance(price, bool) or price <= 0:
		logger.warning("Invalid price for product %s", product)
		return False

	try:
		quantity = record["quantity"]
	except KeyError:
		logger.warning("Invalid quantity for product %s", product)
		return False
	if not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or quantity <= 0:
		logger.warning("Invalid quantity for product %s", product)
		return False

	return True


# Transform: add the calculated total field to valid records.
def transform_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
	"""Validate records and add the calculated total to valid records."""
	transformed_records = []
	for record in records:
		# Skip invalid records so the pipeline can continue.
		if not is_valid_record(record):
			continue

		# Copy the record so the original input data is not modified.
		transformed_record = dict(record)
		transformed_record["total"] = record["price"] * record["quantity"]
		transformed_records.append(transformed_record)
	return transformed_records


# Load: write the processed records to an output JSON file.
def save_records(records: list[dict[str, Any]], output_path: Path) -> None:
	"""Write processed records to a JSON file."""
	with output_path.open("w", encoding="utf-8") as output_file:
		json.dump(records, output_file, indent=2)
		output_file.write("\n")


def main() -> None:
	# Build paths relative to the project's root directory.
	project_root = Path(__file__).resolve().parent.parent
	input_path = project_root / "data" / "input.json"
	output_path = project_root / "data" / "output.json"

	records = load_records(input_path)
	logger.info("Processing %d records", len(records))
	processed_records = transform_records(records)
	save_records(processed_records, output_path)
	logger.info("Successfully processed %d records", len(processed_records))


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
	main()
