"""
Data Validator Module

Comprehensive validation for CSV data transformation.
Validates input data, transformation rules, and output compliance.
"""

import pandas as pd
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataValidator:
    """
    Validates CSV data before and after transformation.
    
    Features:
    - Input data structure validation
    - Field format validation  
    - Business rule validation
    - Output compliance checking
    - Detailed error reporting
    """
    
    def __init__(self, config: Dict):
        """
        Initialize validator with configuration.
        
        Args:
            config: Configuration dictionary with validation rules
        """
        self.config = config
        self.errors = []
        self.warnings = []
    
    def validate_input_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate input DataFrame structure and content.
        
        Args:
            df: Input DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        
        # Basic structure validation
        self._validate_structure(df)
        
        # Field content validation
        self._validate_field_content(df)
        
        # Business rule validation
        self._validate_business_rules(df)
        
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "row_count": len(df),
            "column_count": len(df.columns)
        }
    
    def validate_output_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate output DataFrame for Jira compliance.
        
        Args:
            df: Output DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        
        # Required fields validation
        self._validate_required_fields(df)
        
        # Jira-specific validation
        self._validate_jira_compliance(df)
        
        # Data quality checks
        self._validate_data_quality(df)
        
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "ready_for_import": len(self.errors) == 0
        }
    
    def _validate_structure(self, df: pd.DataFrame) -> None:
        """Validate basic DataFrame structure."""
        if df.empty:
            self.errors.append("DataFrame is empty")
            return
        
        if len(df.columns) == 0:
            self.errors.append("DataFrame has no columns")
            return
        
        # Check for duplicate columns
        if len(df.columns) != len(set(df.columns)):
            duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
            self.errors.append(f"Duplicate columns found: {duplicates}")
        
        # Check for completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            self.warnings.append(f"Completely empty columns: {empty_cols}")
    
    def _validate_field_content(self, df: pd.DataFrame) -> None:
        """Validate individual field content and formats."""
        # Check expected columns from mappings
        expected_cols = list(self.config.get("column_mappings", {}).values())
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            self.warnings.append(f"Expected columns not found: {missing_cols}")
        
        # Validate specific field formats
        for col in df.columns:
            self._validate_column_format(df, col)
    
    def _validate_column_format(self, df: pd.DataFrame, column: str) -> None:
        """Validate format of specific column."""
        if column not in df.columns:
            return
        
        col_data = df[column].dropna()
        if col_data.empty:
            return
        
        # Email format validation
        if 'email' in column.lower():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = col_data[~col_data.astype(str).str.match(email_pattern)]
            if not invalid_emails.empty:
                self.warnings.append(f"Invalid email formats in {column}: {len(invalid_emails)} entries")
        
        # Date format validation
        if any(date_word in column.lower() for date_word in ['date', 'created', 'updated']):
            self._validate_date_format(col_data, column)
        
        # Priority validation
        if 'priority' in column.lower():
            self._validate_priority_values(col_data, column)
    
    def _validate_date_format(self, data: pd.Series, column: str) -> None:
        """Validate date format in a column."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
        
        for value in data.astype(str).head(10):  # Check first 10 values
            is_valid_date = False
            for fmt in date_formats:
                try:
                    datetime.strptime(value, fmt)
                    is_valid_date = True
                    break
                except ValueError:
                    continue
            
            if not is_valid_date and value.lower() not in ['nan', 'none', '']:
                self.warnings.append(f"Unrecognized date format in {column}: {value}")
                break
    
    def _validate_priority_values(self, data: pd.Series, column: str) -> None:
        """Validate priority values."""
        allowed_priorities = self.config.get("validation_rules", {}).get("allowed_priorities", [])
        if not allowed_priorities:
            return
        
        invalid_priorities = data[~data.astype(str).isin([str(p) for p in allowed_priorities])]
        if not invalid_priorities.empty:
            unique_invalid = invalid_priorities.unique()[:5]  # Show first 5
            self.warnings.append(f"Invalid priority values in {column}: {unique_invalid}")
    
    def _validate_business_rules(self, df: pd.DataFrame) -> None:
        """Validate business-specific rules."""
        # Check for reasonable row count
        if len(df) > 10000:
            self.warnings.append(f"Large dataset ({len(df)} rows) - consider batch processing")
        
        # Check for suspicious duplicate content
        if 'Title' in df.columns:
            duplicate_titles = df[df['Title'].duplicated()]
            if not duplicate_titles.empty:
                self.warnings.append(f"{len(duplicate_titles)} duplicate titles found")
    
    def _validate_required_fields(self, df: pd.DataFrame) -> None:
        """Validate required fields for Jira import."""
        required_fields = self.config.get("required_fields", [])
        
        for field in required_fields:
            if field not in df.columns:
                self.errors.append(f"Required field missing: {field}")
            else:
                empty_count = df[field].isna().sum() + (df[field] == "").sum()
                if empty_count > 0:
                    self.errors.append(f"Required field '{field}' has {empty_count} empty values")
    
    def _validate_jira_compliance(self, df: pd.DataFrame) -> None:
        """Validate Jira-specific requirements."""
        validation_rules = self.config.get("validation_rules", {})
        
        # Summary length validation
        if "Summary" in df.columns:
            max_length = validation_rules.get("max_summary_length", 255)
            long_summaries = df[df["Summary"].astype(str).str.len() > max_length]
            if not long_summaries.empty:
                self.errors.append(f"{len(long_summaries)} summaries exceed {max_length} characters")
        
        # Description length validation
        if "Description" in df.columns:
            max_length = validation_rules.get("max_description_length", 32767)
            long_descriptions = df[df["Description"].astype(str).str.len() > max_length]
            if not long_descriptions.empty:
                self.errors.append(f"{len(long_descriptions)} descriptions exceed {max_length} characters")
        
        # Issue Type validation
        if "Issue Type" in df.columns:
            allowed_types = validation_rules.get("required_issue_types", [])
            if allowed_types:
                invalid_types = df[~df["Issue Type"].isin(allowed_types)]
                if not invalid_types.empty:
                    self.errors.append(f"Invalid Issue Types found. Allowed: {allowed_types}")
        
        # Project Key validation
        if "Project Key" in df.columns:
            project_keys = df["Project Key"].dropna().unique()
            for key in project_keys:
                if not re.match(r'^[A-Z][A-Z0-9_]*$', str(key)):
                    self.errors.append(f"Invalid Project Key format: {key}")
    
    def _validate_data_quality(self, df: pd.DataFrame) -> None:
        """General data quality validation."""
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            self.warnings.append(f"{empty_rows} completely empty rows found")
        
        # Check for excessive missing data
        for col in df.columns:
            missing_percent = (df[col].isna().sum() / len(df)) * 100
            if missing_percent > 50:
                self.warnings.append(f"Column '{col}' is {missing_percent:.1f}% empty")
        
        # Check for suspicious special characters in text fields
        text_columns = ["Summary", "Description", "Component"]
        for col in text_columns:
            if col in df.columns:
                special_chars = df[col].astype(str).str.contains(r'[^\w\s\-.,;:()!?]', na=False)
                if special_chars.any():
                    count = special_chars.sum()
                    self.warnings.append(f"{count} entries in '{col}' contain special characters")
    
    def generate_validation_report(self, input_validation: Dict, output_validation: Dict) -> str:
        """
        Generate a comprehensive validation report.
        
        Args:
            input_validation: Results from input validation
            output_validation: Results from output validation
            
        Returns:
            Formatted validation report string
        """
        report = []
        report.append("CSV TRANSFORMATION VALIDATION REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Input validation section
        report.append("INPUT DATA VALIDATION:")
        report.append(f"  Status: {'✓ PASS' if input_validation['is_valid'] else '✗ FAIL'}")
        report.append(f"  Rows: {input_validation['row_count']}")
        report.append(f"  Columns: {input_validation['column_count']}")
        
        if input_validation['errors']:
            report.append("  Errors:")
            for error in input_validation['errors']:
                report.append(f"    - {error}")
        
        if input_validation['warnings']:
            report.append("  Warnings:")
            for warning in input_validation['warnings']:
                report.append(f"    - {warning}")
        
        report.append("")
        
        # Output validation section
        report.append("OUTPUT DATA VALIDATION:")
        report.append(f"  Status: {'✓ PASS' if output_validation['is_valid'] else '✗ FAIL'}")
        report.append(f"  Jira Ready: {'✓ YES' if output_validation['ready_for_import'] else '✗ NO'}")
        
        if output_validation['errors']:
            report.append("  Errors:")
            for error in output_validation['errors']:
                report.append(f"    - {error}")
        
        if output_validation['warnings']:
            report.append("  Warnings:")
            for warning in output_validation['warnings']:
                report.append(f"    - {warning}")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)