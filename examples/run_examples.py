#!/usr/bin/env python3
"""
Example Usage Scripts

Demonstrates various ways to use the TestRail to Jira CSV Converter.
Run these examples to see the transformer in action.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transformer import CSVTransformer
from validator import DataValidator
import pandas as pd


def example_basic_transformation():
    """Example 1: Basic transformation with default settings."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Transformation")
    print("=" * 60)
    
    # Create transformer with default config
    transformer = CSVTransformer()
    
    # Transform the sample file
    result = transformer.transform(
        input_file="examples/sample_testrail_export.csv",
        output_file="examples/output_basic.csv"
    )
    
    print(f"Transformation {'successful' if result['success'] else 'failed'}")
    if result['success']:
        print(f"Processed {result['original_rows']} → {result['transformed_rows']} rows")
    
    return result['success']


def example_custom_configuration():
    """Example 2: Using custom configuration."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Configuration")
    print("=" * 60)
    
    # Create transformer with custom config
    transformer = CSVTransformer("config/zephyr_config.json")
    
    # Transform with custom settings
    result = transformer.transform(
        input_file="examples/sample_testrail_export.csv",
        output_file="examples/output_zephyr.csv"
    )
    
    print(f"Custom transformation {'successful' if result['success'] else 'failed'}")
    if result['warnings']:
        print(f"Warnings: {len(result['warnings'])}")
        for warning in result['warnings'][:3]:  # Show first 3
            print(f"  - {warning}")
    
    return result['success']


def example_preview_mode():
    """Example 3: Preview transformation without saving."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Preview Mode")
    print("=" * 60)
    
    transformer = CSVTransformer()
    
    # Preview transformation
    result = transformer.transform(
        input_file="examples/sample_testrail_export.csv",
        output_file="",  # Not used in preview mode
        preview=True
    )
    
    print(f"Preview {'successful' if result['success'] else 'failed'}")
    return result['success']


def example_validation():
    """Example 4: Data validation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Data Validation")
    print("=" * 60)
    
    # Load configuration and data
    transformer = CSVTransformer()
    validator = DataValidator(transformer.config)
    
    # Read sample data
    df = pd.read_csv("examples/sample_testrail_export.csv")
    
    # Validate input
    input_validation = validator.validate_input_data(df)
    print(f"Input validation: {'PASS' if input_validation['is_valid'] else 'FAIL'}")
    
    if input_validation['warnings']:
        print(f"Warnings ({len(input_validation['warnings'])}):")
        for warning in input_validation['warnings']:
            print(f"  - {warning}")
    
    # Transform and validate output
    transformed_df = transformer._apply_transformations(df)
    output_validation = validator.validate_output_data(transformed_df)
    print(f"Output validation: {'PASS' if output_validation['is_valid'] else 'FAIL'}")
    
    return input_validation['is_valid'] and output_validation['is_valid']


def example_custom_transformations():
    """Example 5: Custom transformation functions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Custom Transformations")
    print("=" * 60)
    
    class CustomTransformer(CSVTransformer):
        """Extended transformer with custom functions."""
        
        def format_test_steps(self, steps: str) -> str:
            """Custom function to format test steps for Jira."""
            if pd.isna(steps):
                return ""
            
            # Format steps with proper Jira markdown
            formatted = str(steps).replace('\n', '\n\n')
            return f"h4. Test Steps\n{formatted}"
        
        def generate_test_labels(self, row: pd.Series) -> str:
            """Generate test-specific labels."""
            labels = ["manual-test"]
            
            # Add priority-based label
            if "Priority" in row and pd.notna(row["Priority"]):
                priority = str(row["Priority"]).lower()
                labels.append(f"priority-{priority}")
            
            # Add section-based label  
            if "Section" in row and pd.notna(row["Section"]):
                section = str(row["Section"]).split(" > ")[0].lower().replace(" ", "-")
                labels.append(f"area-{section}")
            
            return ",".join(labels)
    
    # Use custom transformer
    transformer = CustomTransformer()
    
    # Apply custom transformation
    df = pd.read_csv("examples/sample_testrail_export.csv")
    transformed_df = transformer._apply_transformations(df)
    
    print("Sample transformed labels:")
    if "Labels" in transformed_df.columns:
        for i, labels in enumerate(transformed_df["Labels"].head(3)):
            print(f"  Row {i+1}: {labels}")
    
    return True


def example_batch_processing():
    """Example 6: Batch processing multiple files."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Batch Processing Simulation")
    print("=" * 60)
    
    # For demonstration, we'll process the same file multiple times
    # In real usage, you'd have multiple input files
    
    transformer = CSVTransformer()
    files_processed = 0
    
    # Simulate processing multiple files
    sample_files = [
        ("examples/sample_testrail_export.csv", "examples/batch_output_1.csv"),
        ("examples/sample_testrail_export.csv", "examples/batch_output_2.csv"),
    ]
    
    for input_file, output_file in sample_files:
        if Path(input_file).exists():
            result = transformer.transform(input_file, output_file)
            if result['success']:
                files_processed += 1
                print(f"✅ Processed {Path(input_file).name} → {Path(output_file).name}")
            else:
                print(f"❌ Failed to process {Path(input_file).name}")
    
    print(f"\nBatch processing complete: {files_processed}/{len(sample_files)} files")
    return files_processed == len(sample_files)


def run_all_examples():
    """Run all examples and show summary."""
    print("🚀 TestRail to Jira CSV Converter - Examples")
    print("=" * 80)
    
    examples = [
        ("Basic Transformation", example_basic_transformation),
        ("Custom Configuration", example_custom_configuration), 
        ("Preview Mode", example_preview_mode),
        ("Data Validation", example_validation),
        ("Custom Transformations", example_custom_transformations),
        ("Batch Processing", example_batch_processing),
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            success = example_func()
            results[name] = success
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("EXAMPLES SUMMARY")
    print("=" * 80)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    total_passed = sum(results.values())
    total_examples = len(results)
    print(f"\nOverall: {total_passed}/{total_examples} examples passed")
    
    if total_passed == total_examples:
        print("\n🎉 All examples completed successfully!")
        print("The CSV transformer is ready to use with your TestRail data.")
    else:
        print(f"\n⚠️  {total_examples - total_passed} examples had issues.")
        print("Check the output above for details.")


if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    run_all_examples()