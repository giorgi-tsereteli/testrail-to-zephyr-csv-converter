# TestRail to Zephyr CSV Converter

🔄 Convert TestRail exports to Zephyr test format with structured multi-section descriptions.

## What This Tool Does

This transformer converts TestRail CSV exports into Jira-compatible import files with:

- **9 Jira Columns**: Issue Type, Summary, Product(s) Affected, Parent, Engineering Team, Description, and 3 Labels columns
- **Structured Descriptions**: Multi-section format with Overview, Preconditions, Steps, and Expected Result
- **Data Integration**: Extracts actual test case data from TestRail export columns
- **Static Values**: Pre-configured editable values for Product, Parent, and Engineering Team

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pandas library (included in setup script)
- TestRail CSV export with all required columns

### Quick Setup

1. **Clone and enter the directory:**
   ```bash
   git clone <your-repo-url>
   cd testrail-zephyr-csv-converter
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This creates a virtual environment and installs all dependencies.

3. **Test with sample data:**
   ```bash
   ./test.sh
   ```
   This transforms the sample TestRail export and shows the results.

## 📋 How to Use

### Step 1: Export from TestRail
Export your test cases from TestRail as CSV Ensuring following columns are included:

- `ID` - Test case ID
- `Title` - Test case title  
- `Type` - Test type (Functional, etc.)
- `Manual/Automated` - Automation status
- `Overview` - Test overview/description
- `Preconditions` - Prerequisites 
- `Steps` - Test steps
- `Expected Result` - Expected outcome

**💡** You don't need to change any code or paths. Just replace the `sample_testrail_export.csv` file with your data and keep the same filename.

### Step 2: Transform the File
```bash
python3 run.py
```

This will:
- Read `examples/sample_testrail_export.csv`
- Transform it to Jira format
- Save as `examples/jira_import.csv`
- Show transformation statistics

### Step 3: Customize Static Values (Optional)
Edit the hardcoded values in `src/transformer.py`:

```python
# Search for "CHANGE THIS VALUE HERE" to find all editable values:

"Product(s) Affected": "Platform",     # ← Change to "Dossier", "RPT", etc.
"Parent": "3074219",                   # ← Change to different Parent ID  
"Engineering Team": "Team Platinum",   # ← Change to different team
```

### Step 4: Import to Jira
- Upload the generated `jira_import.csv` to your Jira instance
- Use Jira's CSV import feature
- Map the columns as needed

## � Output Format

The transformer creates a Jira import CSV with these columns:

| Column | Source | Description |
|--------|--------|-------------|
| **Issue Type** | Static: "Test" | Fixed value for all rows |
| **Summary** | TestRail: Title + ID | Format: "Test Title - C12345" |
| **Product(s) Affected** | Static: "Platform" | ⚠️ **Editable** - Change in transformer.py |
| **Parent** | Static: "3074219" | ⚠️ **Editable** - Change to your Parent ID |
| **Engineering Team** | Static: "Team Platinum" | ⚠️ **Editable** - Change to your team |
| **Description** | Multi-section format | Combined from Overview, Preconditions, Steps, Expected Result |
| **Labels** (3 columns) | TestRail: Type + Manual/Automated | 3rd Labels column is empty for manual entry |

### Description Format
Each test case description includes:

```
C12345

*Overview*
[Content from TestRail Overview column]
----

*Preconditions*  
[Content from TestRail Preconditions column]
----

*Steps*
[Content from TestRail Steps column]  
----

*Expected Result*
[Content from TestRail Expected Result column]
```

## 🔧 Customization

### Editing Static Values
1. Open `src/transformer.py`
2. Search for `CHANGE THIS VALUE HERE` 
3. Update these values:
   ```python
   "Product(s) Affected": "Platform",      # Change to "Dossier", "RPT", etc.
   "Parent": "3074219",                    # Your Jira Parent ID
   "Engineering Team": "Team Platinum",    # Your team name or just Team Platinum bcz we are best ;)
   ```

### Processing Your Own Files
1. Replace `examples/sample_testrail_export.csv` with your export
2. Run `python3 run.py`
3. Check the generated `examples/jira_import.csv`

### Advanced Usage
For custom file paths or different configurations, modify `run.py`:
```python
transformer = CSVTransformer()
result = transformer.transform(
    "path/to/your/testrail_export.csv", 
    "path/to/output/jira_import.csv"
)
```

## 📂 Project Structure

```
testrail-zephyr-csv-converter/
├── src/
│   ├── transformer.py      # Main transformation logic
│   └── __init__.py
├── examples/
│   ├── sample_testrail_export.csv    # Sample TestRail export
│   └── jira_import.csv              # Generated Jira import file
├── run.py                  # Simple runner script
├── test.sh                # Quick test script  
├── setup.sh               # Environment setup
├── requirements.txt       # Python dependencies
└── README.md             # This documentation
```
---

**Ready to migrate your test cases!** 🚀 This tool handles the complex multi-section Description formatting so you can focus on your testing workflow.