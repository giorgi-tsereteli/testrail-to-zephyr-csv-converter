"""
CSV Transformer Module - Converts TestRail CSV to Jira import format.

🔧 QA ENGINEERS: To change hardcoded values:
   1. Search for "CHANGE THIS VALUE HERE" to find all editable values
   2. Edit these static values as needed:
      - "Product(s) Affected": "Platform" (change to "Dossier", "RPT", etc.)
      - "Parent": "3074219" (change to different Parent ID)
      - "Engineering Team": "Team Platinum" (change to different team)
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional, Any


class CSVTransformer:
    """Transform CSV files from TestRail format to Jira format."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "column_mappings": {
                "Summary": "Title",
                "Description": "ID",
                "Labels_1": "Type",
                "Labels_2": "Manual/Automated"
            },
            "static_values": {
                "Issue Type": "Test",
                # ⚠️  EDIT HERE: Change "Platform" to "Dossier", "RPT" or other products as needed
                # 3rd column in the Jira import file
                "Product(s) Affected": "Platform",  # <-- CHANGE THIS VALUE HERE
                # ⚠️  EDIT HERE: Change "3074219" to different Parent ID as needed
                # 4th column in the Jira import file
                "Parent": "3074219",  # <-- CHANGE THIS VALUE HERE
                # ⚠️  EDIT HERE: Change "Team Platinum" to different engineering team as needed
                # 5th column in the Jira import file
                "Engineering Team": "Team Platinum",  # <-- CHANGE THIS VALUE HERE
                # Labels_3 is empty for QA engineers to manually fill if needed
                # ⚠️ Added label MUST exist in the Jira instance beforehand. Example: "automation"
                "Labels_3": ""
            },
            "transformations": {
                "Summary": "format_summary",
                "Description": "format_description"
            },
            "jira_fields": [
                "Issue Type", "Summary", "Product(s) Affected", "Parent", "Engineering Team",
                "Description", "Labels_1", "Labels_2", "Labels_3"
            ]
        }
    
    def transform(self, input_file: str, output_file: str, preview: bool = False, show_columns: bool = False) -> Dict:
        try:
            # Try different encodings to handle various CSV exports
            try:
                df = pd.read_csv(input_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(input_file, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(input_file, encoding='cp1252')
            
            # Filter out empty rows - rows where both ID and Title are NaN/empty
            original_count = len(df)
            df = df.dropna(subset=['ID', 'Title'], how='all')
            filtered_count = len(df)
            
            if show_columns:
                self._show_available_columns(df)
            
            transformed_df = self._apply_transformations(df)
            
            if preview:
                self._show_preview(transformed_df)
            else:
                # Custom CSV writing to handle duplicate column names
                self._write_csv_with_duplicate_columns(transformed_df, output_file)
                print(f"✅ Transformation complete: {output_file}")
            
            return {
                "success": True,
                "original_rows": original_count,
                "filtered_rows": filtered_count,
                "transformed_rows": len(transformed_df)
            }
            
        except Exception as e:
            print(f"❌ Transformation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        # Only process the columns we need - ignore all other TestRail columns
        result_df = pd.DataFrame(index=df.index)
        
        for jira_field in self.config["jira_fields"]:
            if jira_field in self.config["static_values"]:
                # Static values (like "Test" for Issue Type)
                result_df[jira_field] = self.config["static_values"][jira_field]
            elif jira_field in self.config["column_mappings"]:
                testrail_field = self.config["column_mappings"][jira_field]
                if testrail_field in df.columns:
                    # Map from TestRail column to Jira field
                    result_df[jira_field] = df[testrail_field]
                    
                    # Apply transformation if needed
                    if jira_field in self.config["transformations"]:
                        transform_func = self.config["transformations"][jira_field]
                        if transform_func == "format_summary":
                            result_df[jira_field] = df.apply(
                                lambda row: self.format_summary(row["Title"], row["ID"]), axis=1
                            )
                        elif transform_func == "format_description":
                            result_df[jira_field] = df.apply(
                                lambda row: self.format_description(row), axis=1
                            )
                        else:
                            result_df[jira_field] = result_df[jira_field].apply(
                                getattr(self, transform_func)
                            )
                else:
                    # Column not found in TestRail export - set empty
                    result_df[jira_field] = ""
            else:
                # Jira field not mapped - set empty
                result_df[jira_field] = ""
        
        # Clean up NaN values - replace with empty strings
        result_df = result_df.fillna("")
        
        # Rename Labels columns to have the same name in the final CSV
        result_df = self._rename_labels_columns(result_df)
        
        return result_df
    
    def _rename_labels_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep Labels columns as Labels_1, Labels_2, Labels_3 for now - will rename during CSV writing"""
        return df
    
    def _write_csv_with_duplicate_columns(self, df: pd.DataFrame, output_file: str) -> None:
        """Write CSV with duplicate 'Labels' column names"""
        import csv
        
        # Prepare the header with duplicate 'Labels' names
        header = []
        for col in df.columns:
            if col.startswith('Labels_'):
                header.append('Labels')
            else:
                header.append(col)
        
        # Write the CSV file with proper quoting to handle multi-line cells
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            
            # Write header
            writer.writerow(header)
            
            # Write data rows
            for _, row in df.iterrows():
                writer.writerow(row.values)
    
    def _show_preview(self, df: pd.DataFrame) -> None:
        print(f"\n📄 Preview ({len(df)} rows):")
        print(df.head(3).to_string(index=False))
    
    def _show_available_columns(self, df: pd.DataFrame) -> None:
        """Show which columns are available in the TestRail export and which ones we're using."""
        needed_columns = set(self.config["column_mappings"].values())
        needed_columns.add("ID")  # Always need ID for Summary formatting
        
        available = set(df.columns)
        using = needed_columns.intersection(available)
        missing = needed_columns - available
        ignored = available - needed_columns
        
        print(f"\n📋 TestRail Export Analysis:")
        print(f"   Total columns in export: {len(available)}")
        print(f"   ✅ Using: {sorted(using)}")
        if missing:
            print(f"   ❌ Missing (needed): {sorted(missing)}")
        print(f"   ⏭️  Ignoring: {len(ignored)} columns")
        if len(ignored) < 10:  # Only show if not too many
            print(f"      Ignored columns: {sorted(ignored)}")
        print()
    
    def format_summary(self, title: Any, test_id: Any) -> str:
        if pd.isna(title):
            return ""
        title_str = str(title)
        if pd.notna(test_id):
            id_str = str(test_id)
            if not id_str.startswith('C'):
                id_num = int(id_str) if id_str.isdigit() else 0
                id_str = f"C{id_num:05d}"
        else:
            id_str = "C00000"
        return f"{title_str} - {id_str}"
    
    def format_description(self, row: pd.Series) -> str:
        """
        Format description field with ID first, then multiple sections from TestRail columns.
        Structure: ID + 1 line break + *Overview* + *Preconditions* + *Steps* + *Expected Result*
        Each section separated by 2 line breaks.
        """
        # Get the ID and format it with C prefix if needed
        test_id = row.get("ID", "")
        if pd.notna(test_id):
            id_str = str(test_id)
            if not id_str.startswith('C'):
                id_num = int(id_str) if id_str.isdigit() else 0
                id_str = f"C{id_num:05d}"
        else:
            id_str = "C00000"
        
        sections = []
        
        # Section 1: Overview - get actual data from Overview column
        overview_data = row.get("Overview", "")
        if pd.notna(overview_data) and str(overview_data).strip():
            overview_content = str(overview_data).strip()
            sections.append(f"*Overview*\n\n{overview_content}\n----")
        else:
            sections.append("*Overview*\n\n[No overview data]\n----")
        
        # Section 2: Preconditions - get actual data from Preconditions column
        preconditions_data = row.get("Preconditions", "")
        if pd.notna(preconditions_data) and str(preconditions_data).strip():
            preconditions_content = str(preconditions_data).strip()
            sections.append(f"*Preconditions*\n\n{preconditions_content}\n")
        else:
            sections.append("*Preconditions*\n\n[No preconditions data]\n----")
        
        # Section 3: Steps  
        sections.append("*Steps*\n\n[Steps content will go here]")
        
        # Section 4: Expected Result
        sections.append("*Expected Result*\n\n[Expected Result content will go here]")
        
        # Start with ID + clear line break, then join sections with 2 line breaks between them
        return f"{id_str}\n\n" + "\n\n".join(sections)


def main():
    transformer = CSVTransformer()
    result = transformer.transform("examples/sample_testrail_export.csv", "examples/jira_import.csv", preview=True, show_columns=True)
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()