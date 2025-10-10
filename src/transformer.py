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
                "Description": "ID"
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
                # Empty Labels columns for QA engineers to manually fill if needed. Data on label is not exported from TestRail
                # ⚠️ Added label MUST exist in the Jira instance beforehand. Example: "automation"
                "Labels_1": "",
                "Labels_2": "",
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
            
            if show_columns:
                self._show_available_columns(df)
            
            transformed_df = self._apply_transformations(df)
            
            if preview:
                self._show_preview(transformed_df)
            else:
                transformed_df.to_csv(output_file, index=False)
                print(f"✅ Transformation complete: {output_file}")
            
            return {
                "success": True,
                "original_rows": len(df),
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
        
        # Rename Labels columns to have the same name in the final CSV
        result_df = self._rename_labels_columns(result_df)
        
        return result_df
    
    def _rename_labels_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename Labels_1, Labels_2, Labels_3 to all be 'Labels' in the final CSV"""
        column_mapping = {}
        for col in df.columns:
            if col.startswith('Labels_'):
                column_mapping[col] = 'Labels'
        
        return df.rename(columns=column_mapping)
    
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
        Format description field with multiple sections from TestRail columns.
        Structure: *Overview* + *Preconditions* + *Steps* + *Expected Result*
        Each section separated by 2 line breaks.
        """
        sections = []
        
        # Section 1: Overview (using ID for now - will be replaced with actual Overview data)
        sections.append("*Overview*\n\n[Overview content will go here]")
        
        # Section 2: Preconditions
        sections.append("*Preconditions*\n\n[Preconditions content will go here]")
        
        # Section 3: Steps  
        sections.append("*Steps*\n\n[Steps content will go here]")
        
        # Section 4: Expected Result
        sections.append("*Expected Result*\n\n[Expected Result content will go here]")
        
        # Join all sections with 2 line breaks between them
        return "\n\n".join(sections)


def main():
    transformer = CSVTransformer()
    result = transformer.transform("examples/sample_testrail_export.csv", "examples/jira_import.csv", preview=True, show_columns=True)
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()