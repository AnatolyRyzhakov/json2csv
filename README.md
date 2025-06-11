# JSON to CSV Converter
A Python utility to convert JSON files into CSV format. 

This project was collaboratively vibecoded by advanced AI models under human guidance.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AnatolyRyzhakov/json2csv.git
   cd json2csv
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. The project has no external dependencies beyond the Python standard library, so no additional packages are required.

3. **Run the Script**:
   ```bash
   python src/main.py --help
   ```

## Usage

Run the converter from the command line with the following options:
  ```bash
  python src/main.py [options]
  ```

### Options

- `--input, -i <path>`: Path to a JSON file or directory containing JSON files (default: current directory).
- `--output, -o <path>`: Path for the output CSV file (default: `output_YYYYMMDD_HHMMSS.csv`).
- `--separator, -s <str>`: Separator for nested keys (default: `_`).
- `--index-format <str>`: Format string for array indices (default: `{:04d}`).
- `--validate-keys`: Enable validation of keys for CSV compatibility (default: disabled).
- `--version, -v`: Display the program version (`0.1.0`).

### Examples

1. **Convert a Single JSON File**:
   ```bash
   python json2csv.py -i data/sample.json -o output.csv
   ```

2. **Convert All JSON Files in a Directory**:
   ```bash
   python json2csv.py -i data/ -o combined.csv
   ```

3. **Use Custom Separator and Key Validation**:
   ```bash
   python json2csv.py -i data/sample.json -o output.csv --separator . --validate-keys
   ```

4. **Custom Index Format**:
   ```bash
   python json2csv.py -i data/sample.json -o output.csv --index-format {:03d}
   ```

### Example Input and Output

**Input JSON** (`sample.json`):
```json
{
  "name": "John",
  "skills": [
    {"type": "coding", "level": 8},
    {"type": "design", "level": 5}
  ]
}
```

**Output CSV (`key,value` format)**:
```csv
key,value
sample.name,John
sample.skills_0000_type,coding
sample.skills_0000_level,8
sample.skills_0001_type,design
sample.skills_0001_level,5
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details (recommended to create).

## Attribution

This project was developed collaboratively by:

- **AI Contributors**:
  - Deepseek Chat v2.68.5b (Engine Build 2024-07-25)
  - ChatGPT-4o (2024-05)
  - Grok 3 (2025-06-10.1137)
  - Google Gemini 1.5 Pro (Interaction: 2025-06-10)
- **Human Developer**: Anatoly Ryzhakov

## Contact

For issues or questions, please open an issue on the [GitHub repository](https://github.com/AnatolyRyzhakov/json2csv/issues).
