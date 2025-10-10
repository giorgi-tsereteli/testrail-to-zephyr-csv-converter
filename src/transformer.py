"""
CSV Transformer Module - Converts TestRail CSV to Jira import format.

🔧 QA ENGINEERS: To change Product(s) Affected value:
   1. Find the line with "Product(s) Affected": "Platform"
   2. Change "Platform" to "Dossier" or "RPT" as needed
   3. Search for "CHANGE THIS VALUE HERE" to find it quickly
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
                "Priority": "Priority",
                "Component": "Section",
                "Description": "Preconditions"
            },
            "static_values": {
                "Issue Type": "Test",
                # ⚠️  EDIT HERE: Change "Platform" to "Dossier", "RPT" or other products as needed
                # This will be the 3rd column in the Jira import file
                "Product(s) Affected": "Platform",
                "Project Key": "PROJ"
            },
            "transformations": {
                "Priority": "priority_mapping",
                "Component": "extract_component",
                "Summary": "format_summary"
            },
            "jira_fields": [
                "Issue Type", "Summary", "Product(s) Affected", "Priority", "Component", 
                "Description", "Project Key", "Labels"
            ]
        }
    
    def transform(self, input_file: str, output_file: str, preview: bool = False, show_columns: bool = False) -> Dict:
        try:
            df = pd.read_csv(input_file)
            
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
        
        return result_df
    
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
    
    def priority_mapping(self, priority: Any) -> str:
        if pd.isna(priority):
            return "Medium"
        priority_map = {"1": "Low", "2": "Medium", "3": "High", "4": "Highest", 
                       "low": "Low", "medium": "Medium", "high": "High", "critical": "Highest"}
        return priority_map.get(str(priority).lower(), "Medium")
    
    def extract_component(self, section: Any) -> str:
        if pd.isna(section):
            return ""
        section_str = str(section)
        return section_str.split(" > ")[0] if " > " in section_str else section_str
    
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


def main():
    transformer = CSVTransformer()
    result = transformer.transform("examples/sample_testrail_export.csv", "examples/jira_import.csv", preview=True, show_columns=True)
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()