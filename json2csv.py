"""
JSON to CSV Converter

This utility was conceptualized, reviewed, and directed by a human.
But the code implementation collaboratively built by several advanced AI.

Attribution:
----------------------------------------------------------------
AIs Contributed:
- Deepseek Chat v2.68.5b (Engine Build 2024-07-25)
- ChatGPT-4o (May 2024)
- Grok 3 (2025.06.10.1137)
- Google Gemini 1.5 Pro (Interaction: 2025-06-10)

Human Vibecode Developer:
- AnatolyRyzhakov

Repository:
- https://github.com/AnatolyRyzhakov/json2cs
----------------------------------------------------------------

License: MIT

Copyright (c) 2025 Anatoly Ryzhakov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.1.0"

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple, Union

# CONSTANTS

JSON_EXTENSION = ".json"
CSV_EXTENSION = ".csv"
PARENT_KEY = ""
KEY_SEPARATOR = "_"
INDEX_FORMAT = "{:04d}"
CSV_HEADERS = ["key", "value"]
MAX_KEY_LENGTH = 256


# ARGUMENT PARSER


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the JSON to CSV converter"""
    parser = argparse.ArgumentParser(
        description="Convert JSON file(s) to a CSV",
        epilog="Example: python json2csv.py -i ./data/ -o output.csv",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path.cwd(),
        help="Path to a JSON file or directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Path for output CSV file (default: output_YYYYMMDD_HHMMSS.csv)",
    )
    parser.add_argument(
        "--separator",
        "-s",
        type=str,
        default=KEY_SEPARATOR,
        help=f"Separator for nested keys (default: '{KEY_SEPARATOR}')",
    )
    parser.add_argument(
        "--index-format",
        type=str,
        default=INDEX_FORMAT,
        help="Format string for array indices (default: '{:04d}')",
    )
    parser.add_argument(
        "--validate-keys",
        action="store_true",
        default=False,
        help="Validate keys for CSV compatibility",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s v{__version__}",
        help="Show program version",
    )
    args = parser.parse_args()

    # Validate separator
    if any(c in args.separator for c in {",", "\n", "\r"}):
        raise ValueError("Separator cannot be empty, a comma, or a newline!")

    # Validate index format
    try:
        args.index_format.format(0)
    except ValueError as error:
        raise ValueError(f"Invalid index format: {error}")

    return args


# FILE HANDLING


def get_json_files(path: Path) -> List[Path]:
    """Collect all JSON files from the specified path"""
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path.is_file():
        if path.suffix.lower() == JSON_EXTENSION:
            return [path]
        raise FileNotFoundError(f"Not a {JSON_EXTENSION} file: {path}")

    if path.is_dir():
        files = list(path.glob(f"*{JSON_EXTENSION}"))
        if not files:
            raise FileNotFoundError(f"No JSON files found in: {path}")
        return files

    raise ValueError(f"Invalid path: {path}")


def load_json_data(path: Path) -> Union[Dict, List]:
    """Load and parse JSON data from a file"""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

            if not isinstance(data, (dict, list)):
                raise ValueError(
                    f"JSON must be object or array, got {type(data).__name__}"
                )
            return data
    except json.JSONDecodeError as error:
        raise json.JSONDecodeError(
            f"Invalid JSON in {path}: {error}", error.doc, error.pos
        )
    except UnicodeDecodeError as error:
        raise ValueError(f"Encoding error in {path}: {error}")


# JSON PROCESSING


def flatten_json(
    data: Union[Dict, List, Any],
    parent_key: str = PARENT_KEY,
    separator: str = KEY_SEPARATOR,
    index_format: str = INDEX_FORMAT,
    validate_keys: bool = False,
) -> Generator[Tuple[str, Any], None, None]:
    """Recursively flattens nested JSON structures"""

    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(key, str):
                raise ValueError(f"Keys must be str, got {type(key).__name__}")
            new_key = f"{parent_key}{separator}{key}" if parent_key else key

            if validate_keys:
                if len(new_key) > MAX_KEY_LENGTH:
                    raise ValueError(
                        f"Key too long (max {MAX_KEY_LENGTH} chars): {new_key}"
                    )
                if any(c in new_key for c in {",", "\n", "\r"}):
                    raise ValueError(f"Key has invalid characters: {new_key}")
            yield from flatten_json(
                value, new_key, separator, index_format, validate_keys
            )

    elif isinstance(data, list):
        for index, item in enumerate(data):
            try:
                idx = index_format.format(index)
            except ValueError:
                idx = str(index)
            idx_key = f"{parent_key}{separator}{idx}" if parent_key else idx
            yield from flatten_json(
                item, idx_key, separator, index_format, validate_keys
            )
    elif isinstance(data, (str, int, float, bool)) or data is None:
        yield parent_key, data
    else:
        raise ValueError(f"Unsupported data type: {type(data).__name__}")


def process_json_data(
    data: Union[Dict, List],
    file_prefix: str,
    separator: str = KEY_SEPARATOR,
    index_format: str = INDEX_FORMAT,
    validate_keys: bool = False,
) -> Generator[Tuple[str, Any], None, None]:
    """Process JSON data into a list of flattened dictionaries"""
    if isinstance(data, dict):
        yield from flatten_json(
            data, file_prefix, separator, index_format, validate_keys
        )
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(f"Must be dicts, got {type(item).__name__}")
            yield from flatten_json(
                item, file_prefix, separator, index_format, validate_keys
            )
    else:
        raise ValueError("JSON must be an object or array of objects!")


# CSV WRITER


def write_csv(data: Generator[Tuple[str, Any], None, None], path: Path) -> int:
    """Writes flattened JSON data to a CSV file"""
    row_count = 0
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)

            for key, value in data:
                sanitized_key = key.replace(",", "_")
                writer.writerow([sanitized_key, value])
                row_count += 1

        if row_count == 0:
            raise ValueError("No valid data to write!")

    except IOError as error:
        raise IOError(f"Failed to write to {path}: {error}")

    return row_count


# UTILITIES


def generate_output_filename() -> Path:
    """Generate default output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path.cwd() / f"output_{timestamp}{CSV_EXTENSION}"


# MAIN LOGIC


def run() -> None:
    """Main execution flow for JSON to CSV conversion"""
    try:
        args = parse_arguments()
        json_files = get_json_files(args.input)
        output_path = args.output or Path.cwd() / generate_output_filename()

    except (FileNotFoundError, ValueError) as error:
        print(f"Initialization failed! {error}")
        sys.exit(1)

    all_data = []
    for json_file in json_files:
        try:
            data = load_json_data(json_file)
            rows = process_json_data(
                data,
                json_file.stem,
                args.separator,
                args.index_format,
                args.validate_keys,
            )
            all_data.extend(rows)
        except ValueError as error:
            print(f"Skipping {json_files}: {error}")
            continue

    if not all_data:
        print("No valid data found. Exiting...")
        sys.exit(1)

    try:
        row_count = write_csv(all_data, output_path)
        print(f"Successfully wrote {row_count} rows to {output_path}")

    except (FileNotFoundError, ValueError, IOError) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    run()
