# TestRail to Jira CSV Converter

🔄 A flexible, Python-based tool for transforming TestRail manual test CSV exports into Jira-compatible import format.

## ✨ Features

- **Flexible Column Mapping**: Easily configure which TestRail fields map to Jira fields
- **Data Validation**: Comprehensive validation for both input and output data
- **Preview Mode**: See transformation results before saving
- **Batch Processing**: Process multiple CSV files at once
- **Custom Transformations**: Add your own data transformation logic
- **CLI Interface**: User-friendly command-line interface
- **Configuration Templates**: Pre-built configs for common scenarios

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Basic familiarity with CSV files and command line

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd testrail-zephyr-csv-converter
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation:**
   ```bash
   python examples/run_examples.py
   ```

### Basic Usage

1. **Transform a TestRail CSV to Jira format:**
   ```bash
   python cli.py transform input.csv output.csv
   ```

2. **Preview transformation without saving:**
   ```bash
   python cli.py preview input.csv
   ```

3. **Validate your input file:**
   ```bash
   python cli.py validate input.csv
   ```

## 📋 Detailed Usage

### Command Line Interface

The CLI provides several commands for different use cases:

#### Transform Command
Convert TestRail CSV to Jira format:
```bash
python cli.py transform input.csv output.csv [options]

Options:
  --config, -c     Use custom configuration file
  --validate, -v   Validate input before transformation
```

**Examples:**
```bash
# Basic transformation
python cli.py transform testrail_export.csv jira_import.csv

# With validation
python cli.py transform input.csv output.csv --validate

# Using custom config
python cli.py transform input.csv output.csv --config config/zephyr_config.json
```

#### Preview Command
See what the transformation will look like:
```bash
python cli.py preview input.csv [options]

Options:
  --config, -c    Use custom configuration file
  --rows, -r      Number of rows to preview (default: 5)
```

#### Validate Command
Check your input file for issues:
```bash
python cli.py validate input.csv [options]

Options:
  --config, -c    Use custom configuration file
  --report        Save validation report to file
```

#### Batch Processing
Process multiple files at once:
```bash
python cli.py batch input_folder/ output_folder/ [options]

Options:
  --config, -c    Use custom configuration file
  --pattern, -p   File pattern to match (default: *.csv)
```

#### Generate Configuration
Create a custom configuration file:
```bash
python cli.py init-config my_config.json [options]

Options:
  --template     Configuration template (default, zephyr)
```

### Configuration

The tool uses JSON configuration files to define how data should be transformed. 

#### Default Configuration Structure

```json
{
  "column_mappings": {
    "Summary": "Title",
    "Description": "Preconditions", 
    "Priority": "Priority",
    "Component": "Section"
  },
  "static_values": {
    "Issue Type": "Test",
    "Project Key": "PROJ"
  },
  "transformations": {
    "Priority": "priority_mapping",
    "Component": "extract_component"
  },
  "required_fields": ["Summary", "Issue Type"],
  "jira_fields": [
    "Project Key", "Summary", "Issue Type", 
    "Priority", "Component", "Description", "Labels"
  ]
}
```

#### Configuration Sections

- **column_mappings**: Direct field mappings from TestRail to Jira
- **static_values**: Fixed values for all rows
- **transformations**: Custom functions to transform data
- **required_fields**: Fields that must have values
- **jira_fields**: Final output columns in order

#### Creating Custom Configurations

1. **Generate a template:**
   ```bash
   python cli.py init-config my_config.json --template default
   ```

2. **Edit the file** to match your needs:
   - Update column mappings for your TestRail export format
   - Set your project key and other static values
   - Define required fields based on your Jira setup

3. **Use your custom config:**
   ```bash
   python cli.py transform input.csv output.csv --config my_config.json
   ```

### Data Transformation Functions

The tool includes several built-in transformation functions:

#### Priority Mapping
Converts TestRail priorities to Jira format:
```python
"1" → "Low"
"2" → "Medium"  
"3" → "High"
"4" → "Highest"
```

#### Component Extraction
Extracts component from hierarchical sections:
```python
"Authentication > Login > Positive" → "Authentication"
```

#### Label Generation
Creates labels based on multiple fields:
```python
# Generates: "authentication,manual-test,priority-high"
```

### Custom Transformations

You can extend the transformer with your own functions:

```python
from src.transformer import CSVTransformer

class MyCustomTransformer(CSVTransformer):
    def my_custom_function(self, value):
        # Your transformation logic here
        return transformed_value
        
    def combine_fields(self, row):
        # Access multiple fields from the row
        return f"{row['Field1']} - {row['Field2']}"
```

## 📂 Project Structure

```
testrail-zephyr-csv-converter/
├── src/                    # Core source code
│   ├── transformer.py      # Main transformation logic
│   ├── validator.py        # Data validation
│   └── __init__.py
├── config/                 # Configuration files
│   ├── default_config.json # Default settings
│   └── zephyr_config.json  # Zephyr-specific config
├── examples/               # Sample files and usage
│   ├── sample_testrail_export.csv
│   ├── expected_jira_output.csv
│   └── run_examples.py
├── tests/                  # Unit tests (future)
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Common Use Cases

### Scenario 1: Basic TestRail to Jira Migration

```bash
# 1. Get your TestRail CSV export
# 2. Preview the transformation
python cli.py preview testrail_export.csv

# 3. Transform with validation
python cli.py transform testrail_export.csv jira_import.csv --validate

# 4. Import the result into Jira
```

### Scenario 2: Custom Field Mapping

```bash
# 1. Create custom configuration
python cli.py init-config my_project_config.json

# 2. Edit config file to match your fields
# 3. Test with preview
python cli.py preview input.csv --config my_project_config.json

# 4. Transform
python cli.py transform input.csv output.csv --config my_project_config.json
```

### Scenario 3: Batch Processing

```bash
# Process all CSV files in a directory
python cli.py batch input_exports/ processed_outputs/

# With custom configuration
python cli.py batch input_exports/ processed_outputs/ --config my_config.json
```

## 🔍 Troubleshooting

### Common Issues

**"Column not found" errors:**
- Check your TestRail export format
- Update the `column_mappings` in your config file
- Use `python cli.py validate input.csv` to see what columns are available

**"Required field missing" errors:**
- Ensure your TestRail export has all necessary fields
- Update `required_fields` in config if some fields are optional for your use case

**Import fails in Jira:**
- Use `python cli.py validate output.csv` to check Jira compatibility
- Verify your Project Key is correct
- Check field length limits (Summary: 255 chars, Description: 32KB)

### Getting Help

1. **Run the examples:** `python examples/run_examples.py`
2. **Check validation:** `python cli.py validate your_file.csv --report report.txt`
3. **Preview first:** Always preview before transforming large files
4. **Check logs:** Look for `transformer.log` for detailed error information

## 🧪 Testing

Run the example scripts to test functionality:

```bash
python examples/run_examples.py
```

This will run through various scenarios and show you how the tool works.

## 🤝 Contributing

This tool is designed to be easily extensible:

1. **Add transformation functions** in `src/transformer.py`
2. **Extend validation rules** in `src/validator.py`  
3. **Create configuration templates** in `config/`
4. **Add examples** in `examples/`

## 📝 License

[Your License Here]

## 🙋‍♂️ Support

- Create an issue for bugs or feature requests
- Check the examples for usage patterns
- Review the configuration files for customization options

---

**Happy Testing!** 🎉 Transform your TestRail data to Jira format with confidence.