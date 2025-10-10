# TestRail to Zephyr CSV Converter

🔄 Convert TestRail cases to Zephyr test format with structured, multi-section descriptions

## What This Tool Does

This transformer converts TestRail CSV export file into Jira compatible import file with:

- **Current Jira columns**: Issue Type, Summary, Product(s) Affected, Parent, Engineering Team, etc..
- **Structured Descriptions**: Multi-section format with Overview, Preconditions, Steps, and Expected Results
- **Static Values**: Pre-configured editable values for users to provide their team specific data

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pandas library (included in setup script)
- TestRail CSV export file

### Quick Setup

1. **Clone and enter the directory:**
   ```bash
   git clone git@github.com:giorgi-tsereteli/testrail-to-zephyr-csv-converter.git
   cd testrail-to-zephyr-csv-converter
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This creates a virtual env and installs all dependencies

3. **Test with sample data:**
   ```bash
   ./test.sh
   ```
   This transforms the sample TestRail export and shows the results

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

**💡** You don't need to change any code or paths. Just replace the `sample_testrail_export.csv` file with your data but keep the same filename

### Step 2: Transform the File
```bash
./test.sh
```

This will:
- Read `examples/sample_testrail_export.csv`
- Transform it to Jira format
- Save as `examples/jira_import.csv`
- Show transformation log in terminal

### Step 3: Customize Static Values (Required for real data)
Edit the hardcoded values in `src/transformer.py`:

```python
# Search for "CHANGE THIS VALUE HERE" to find all editable values:

"Product(s) Affected": "Platform",     # ← Change to your product like "Dossier", "RPT", etc.
"Parent": "3074219",                   # ← Change to necessary parent ID (epic) 
"Engineering Team": "Team Platinum",   # ← Change to necessary team name
```

### Step 4: Import to Jira
- Use Zephyr's `Import Issues` feature when clicking Create Test
- Upload the generated `jira_import.csv` and click next
- Select Interfolio Engineering from project dropdown and click next
- Map Jira fields to import file fields
- ⚠️ **Important**: When mapping fields, select the checkbox for all fields **except** the Description field
- Finish the import and review your test cases in Zephyr or parent epic

## Output Format

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


## 📂 Project Structure

```
testrail-zephyr-csv-converter/
├── src/
│   ├── transformer.py      # Main transformation logic
│   └── __init__.py
├── examples/
│   ├── sample_testrail_export.csv    # Sample TestRail export
│   └── jira_import.csv               # Generated Jira import file
├── run.py                  # Simple runner script
├── test.sh                 # Quick test script  
├── setup.sh                # Environment setup
├── requirements.txt        # Python dependencies
└── README.md               # This documentation
```
---

**Ready to migrate your test cases?** 🚀 If you have questions, text me on slack `@Giorgi Tsereteli `