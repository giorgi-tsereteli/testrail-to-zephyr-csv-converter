"""
CSV Transformer Module - Converts TestRail CSV to Jira import format.
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
                "Project Key": "PROJ"
            },
            "transformations": {
                "Priority": "priority_mapping",
                "Component": "extract_component",
                "Summary": "format_summary"
            },
            "jira_fields": [
                "Issue Type", "Summary", "Priority", "Component", 
                "Description", "Project Key", "Labels"
            ]
        }
    
    def transform(self, input_file: str, output_file: str, preview: bool = False) -> Dict:
        try:
            df = pd.read_csv(input_file)
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
        result_df = pd.DataFrame(index=df.index)
        
        for jira_field in self.config["jira_fields"]:
            if jira_field in self.config["static_values"]:
                result_df[jira_field] = self.config["static_values"][jira_field]
            elif jira_field in self.config["column_mappings"]:
                testrail_field = self.config["column_mappings"][jira_field]
                if testrail_field in df.columns:
                    result_df[jira_field] = df[testrail_field]
                    
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
                    result_df[jira_field] = ""
            else:
                result_df[jira_field] = ""
        
        return result_df
    
    def _show_preview(self, df: pd.DataFrame) -> None:
        print(f"\n📄 Preview ({len(df)} rows):")
        print(df.head(3).to_string(index=False))
    
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
    result = transformer.transform("examples/sample_testrail_export.csv", "examples/jira_import.csv", preview=True)
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()