"""
CSV Transformer Module

Core functionality for transforming TestRail CSV files to Jira import format.
Provides flexible column mapping, data validation, and transformation capabilities.
"""

import pandas as pd
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime


class CSVTransformer:
    """
    Main class for transforming CSV files from TestRail format to Jira format.
    
    Features:
    - Flexible column mapping via configuration
    - Data validation and error reporting
    - Custom transformation functions
    - Preview mode for testing changes
    - Batch processing support
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the transformer with optional configuration file.
        
        Args:
            config_path: Path to JSON configuration file for mappings
        """
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.errors = []
        self.warnings = []
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('transformer.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from JSON file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded configuration from {config_path}")
                return config
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Default configuration
        return {
            "column_mappings": {
                "Summary": "Title",
                "Issue Type": "Test",
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
                "Component": "extract_component"
            },
            "required_fields": ["Summary", "Issue Type"],
            "jira_fields": [
                "Summary", "Issue Type", "Priority", "Component", 
                "Description", "Project Key", "Labels"
            ]
        }
    
    def transform(self, input_file: str, output_file: str, preview: bool = False) -> Dict:
        """
        Transform TestRail CSV to Jira format.
        
        Args:
            input_file: Path to input TestRail CSV file
            output_file: Path for output Jira CSV file
            preview: If True, show preview without saving
            
        Returns:
            Dictionary with transformation results and statistics
        """
        try:
            # Reset error tracking
            self.errors = []
            self.warnings = []
            
            # Read input CSV
            self.logger.info(f"Reading input file: {input_file}")
            df = pd.read_csv(input_file)
            original_count = len(df)
            
            # Validate input data
            self._validate_input(df)
            
            # Apply transformations
            transformed_df = self._apply_transformations(df)
            
            # Validate output data
            self._validate_output(transformed_df)
            
            # Preview or save
            if preview:
                self._show_preview(transformed_df)
            else:
                transformed_df.to_csv(output_file, index=False)
                self.logger.info(f"Transformation complete. Output saved to: {output_file}")
            
            # Return results summary
            return {
                "success": True,
                "original_rows": original_count,
                "transformed_rows": len(transformed_df),
                "errors": self.errors,
                "warnings": self.warnings,
                "output_file": output_file if not preview else None
            }
            
        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "errors": self.errors,
                "warnings": self.warnings
            }
    
    def _validate_input(self, df: pd.DataFrame) -> None:
        """Validate input DataFrame structure and data."""
        self.logger.info("Validating input data...")
        
        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("Input CSV file is empty")
        
        # Check for required columns (based on mappings)
        testrail_columns = list(self.config["column_mappings"].values())
        missing_columns = [col for col in testrail_columns if col not in df.columns]
        
        if missing_columns:
            self.warnings.append(f"Missing expected columns: {missing_columns}")
            self.logger.warning(f"Missing columns: {missing_columns}")
        
        # Check for empty required fields
        for jira_field, testrail_field in self.config["column_mappings"].items():
            if jira_field in self.config["required_fields"] and testrail_field in df.columns:
                empty_count = df[testrail_field].isna().sum()
                if empty_count > 0:
                    self.warnings.append(f"{empty_count} rows have empty {testrail_field}")
    
    def _apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all configured transformations to create Jira-formatted DataFrame."""
        self.logger.info("Applying transformations...")
        
        result_df = pd.DataFrame()
        
        # Apply column mappings and transformations
        for jira_field in self.config["jira_fields"]:
            if jira_field in self.config["static_values"]:
                # Static value
                result_df[jira_field] = self.config["static_values"][jira_field]
            elif jira_field in self.config["column_mappings"]:
                # Direct mapping
                testrail_field = self.config["column_mappings"][jira_field]
                if testrail_field in df.columns:
                    result_df[jira_field] = df[testrail_field]
                    
                    # Apply transformation if configured
                    if jira_field in self.config["transformations"]:
                        transform_func = self.config["transformations"][jira_field]
                        result_df[jira_field] = result_df[jira_field].apply(
                            getattr(self, transform_func)
                        )
                else:
                    self.warnings.append(f"Source column {testrail_field} not found for {jira_field}")
                    result_df[jira_field] = ""
            else:
                # Field not configured, set empty
                result_df[jira_field] = ""
        
        return result_df
    
    def _validate_output(self, df: pd.DataFrame) -> None:
        """Validate the transformed DataFrame."""
        self.logger.info("Validating output data...")
        
        # Check required fields
        for field in self.config["required_fields"]:
            if field in df.columns:
                empty_count = df[field].isna().sum() + (df[field] == "").sum()
                if empty_count > 0:
                    self.errors.append(f"{empty_count} rows missing required field: {field}")
    
    def _show_preview(self, df: pd.DataFrame) -> None:
        """Display preview of transformed data."""
        print("\n" + "="*80)
        print("TRANSFORMATION PREVIEW")
        print("="*80)
        print(f"Rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))
        print("\nLast 5 rows:")
        print(df.tail().to_string(index=False))
        print("="*80 + "\n")
        
        # Show column statistics
        print("COLUMN STATISTICS:")
        for col in df.columns:
            non_empty = df[col].notna().sum() - (df[col] == "").sum()
            print(f"  {col}: {non_empty}/{len(df)} non-empty values")
    
    # Transformation functions - customize these for your specific needs
    def priority_mapping(self, priority: Any) -> str:
        """
        Map TestRail priority values to Jira priority values.
        
        Args:
            priority: Original priority value
            
        Returns:
            Mapped priority value
        """
        if pd.isna(priority):
            return "Medium"
        
        priority_str = str(priority).lower()
        priority_map = {
            "1": "Low",
            "2": "Medium", 
            "3": "High",
            "4": "Highest",
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "critical": "Highest"
        }
        
        return priority_map.get(priority_str, "Medium")
    
    def extract_component(self, section: Any) -> str:
        """
        Extract component name from TestRail section.
        
        Args:
            section: TestRail section value
            
        Returns:
            Component name for Jira
        """
        if pd.isna(section):
            return ""
        
        # Example: Extract first part before " > " if hierarchical
        section_str = str(section)
        if " > " in section_str:
            return section_str.split(" > ")[0]
        return section_str
    
    def generate_labels(self, row: pd.Series) -> str:
        """
        Generate labels based on multiple fields.
        
        Args:
            row: DataFrame row
            
        Returns:
            Comma-separated labels
        """
        labels = []
        
        # Add section-based label
        if "Section" in row and pd.notna(row["Section"]):
            section_label = str(row["Section"]).replace(" ", "-").lower()
            labels.append(f"section-{section_label}")
        
        # Add type-based label
        labels.append("manual-test")
        
        return ",".join(labels)


def main():
    """Example usage of the CSVTransformer."""
    transformer = CSVTransformer()
    
    # Example transformation
    result = transformer.transform(
        input_file="examples/testrail_export.csv",
        output_file="examples/jira_import.csv",
        preview=True
    )
    
    print("\nTransformation Results:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Rows processed: {result['original_rows']} → {result['transformed_rows']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    if result['warnings']:
        print(f"\nWarnings: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    if result['errors']:
        print(f"\nErrors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    main()