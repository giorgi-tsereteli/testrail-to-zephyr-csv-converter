#!/usr/bin/env python3
"""
TestRail to Jira CSV Converter - Command Line Interface

Easy-to-use CLI for transforming TestRail CSV exports to Jira import format.
Supports preview, validation, batch processing, and custom configurations.

Usage:
    python cli.py transform input.csv output.csv
    python cli.py preview input.csv --config custom_config.json
    python cli.py validate input.csv
    python cli.py batch input_folder/ output_folder/
"""

import argparse
import sys
import os
from pathlib import Path
import json
from typing import List, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from transformer import CSVTransformer
from validator import DataValidator
import pandas as pd


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Transform TestRail CSV files to Jira import format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transformation
  python cli.py transform input.csv output.csv
  
  # Preview transformation without saving
  python cli.py preview input.csv
  
  # Use custom configuration
  python cli.py transform input.csv output.csv --config zephyr_config.json
  
  # Validate input file
  python cli.py validate input.csv
  
  # Batch process multiple files
  python cli.py batch input_folder/ output_folder/
  
  # Generate sample configuration
  python cli.py init-config my_config.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Transform command
    transform_parser = subparsers.add_parser('transform', help='Transform CSV file')
    transform_parser.add_argument('input_file', help='Input TestRail CSV file')
    transform_parser.add_argument('output_file', help='Output Jira CSV file')
    transform_parser.add_argument('--config', '-c', help='Configuration file path')
    transform_parser.add_argument('--validate', '-v', action='store_true', 
                                help='Validate before transformation')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview transformation')
    preview_parser.add_argument('input_file', help='Input TestRail CSV file')
    preview_parser.add_argument('--config', '-c', help='Configuration file path')
    preview_parser.add_argument('--rows', '-r', type=int, default=5, 
                               help='Number of rows to preview (default: 5)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate CSV file')
    validate_parser.add_argument('input_file', help='Input CSV file to validate')
    validate_parser.add_argument('--config', '-c', help='Configuration file path')
    validate_parser.add_argument('--report', help='Save validation report to file')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process multiple files')
    batch_parser.add_argument('input_dir', help='Input directory with CSV files')
    batch_parser.add_argument('output_dir', help='Output directory for transformed files')
    batch_parser.add_argument('--config', '-c', help='Configuration file path')
    batch_parser.add_argument('--pattern', '-p', default='*.csv', 
                             help='File pattern to match (default: *.csv)')
    
    # Initialize config command
    init_parser = subparsers.add_parser('init-config', help='Generate sample configuration')
    init_parser.add_argument('config_file', help='Output configuration file path')
    init_parser.add_argument('--template', choices=['default', 'zephyr'], 
                           default='default', help='Configuration template')
    
    return parser


def command_transform(args) -> int:
    """Execute transform command."""
    print(f"🔄 Transforming {args.input_file} → {args.output_file}")
    
    # Check input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    # Create transformer
    transformer = CSVTransformer(args.config)
    
    # Optional validation before transformation
    if args.validate:
        print("🔍 Validating input file...")
        validator = DataValidator(transformer.config)
        df = pd.read_csv(args.input_file)
        validation_result = validator.validate_input_data(df)
        
        if not validation_result['is_valid']:
            print("❌ Validation failed:")
            for error in validation_result['errors']:
                print(f"   - {error}")
            
            response = input("Continue with transformation? (y/N): ")
            if response.lower() != 'y':
                return 1
        else:
            print("✅ Input validation passed")
    
    # Perform transformation
    result = transformer.transform(args.input_file, args.output_file)
    
    if result['success']:
        print(f"✅ Transformation completed successfully!")
        print(f"   Rows processed: {result['original_rows']} → {result['transformed_rows']}")
        
        if result['warnings']:
            print(f"⚠️  {len(result['warnings'])} warnings:")
            for warning in result['warnings']:
                print(f"   - {warning}")
    else:
        print(f"❌ Transformation failed: {result.get('error', 'Unknown error')}")
        if result['errors']:
            for error in result['errors']:
                print(f"   - {error}")
        return 1
    
    return 0


def command_preview(args) -> int:
    """Execute preview command."""
    print(f"👀 Previewing transformation of {args.input_file}")
    
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    transformer = CSVTransformer(args.config)
    result = transformer.transform(args.input_file, "", preview=True)
    
    if not result['success']:
        print(f"❌ Preview failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


def command_validate(args) -> int:
    """Execute validate command."""
    print(f"🔍 Validating {args.input_file}")
    
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    # Load configuration and create validator
    config_path = args.config or "config/default_config.json"
    config = {}
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    validator = DataValidator(config)
    
    # Read and validate file
    try:
        df = pd.read_csv(args.input_file)
        validation_result = validator.validate_input_data(df)
        
        # Print results
        if validation_result['is_valid']:
            print("✅ Validation passed!")
        else:
            print("❌ Validation failed!")
            print("\nErrors:")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        if validation_result['warnings']:
            print(f"\n⚠️  Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result['warnings']:
                print(f"  - {warning}")
        
        print(f"\nFile Statistics:")
        print(f"  Rows: {validation_result['row_count']}")
        print(f"  Columns: {validation_result['column_count']}")
        
        # Save report if requested
        if args.report:
            # Create dummy output validation for report
            output_validation = {'is_valid': True, 'ready_for_import': True, 'errors': [], 'warnings': []}
            report = validator.generate_validation_report(validation_result, output_validation)
            
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"\n📄 Validation report saved to {args.report}")
        
        return 0 if validation_result['is_valid'] else 1
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1


def command_batch(args) -> int:
    """Execute batch processing command."""
    print(f"📁 Batch processing {args.input_dir} → {args.output_dir}")
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"❌ Error: Input directory '{args.input_dir}' not found")
        return 1
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find CSV files
    csv_files = list(input_path.glob(args.pattern))
    if not csv_files:
        print(f"❌ No files matching pattern '{args.pattern}' found in {args.input_dir}")
        return 1
    
    print(f"Found {len(csv_files)} files to process")
    
    # Create transformer
    transformer = CSVTransformer(args.config)
    
    success_count = 0
    error_count = 0
    
    for input_file in csv_files:
        output_file = output_path / f"{input_file.stem}_transformed.csv"
        print(f"\n🔄 Processing {input_file.name}...")
        
        result = transformer.transform(str(input_file), str(output_file))
        
        if result['success']:
            print(f"   ✅ Success: {result['original_rows']} → {result['transformed_rows']} rows")
            success_count += 1
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            error_count += 1
    
    print(f"\n📊 Batch processing complete:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    
    return 0 if error_count == 0 else 1


def command_init_config(args) -> int:
    """Execute init-config command."""
    print(f"📝 Creating configuration file: {args.config_file}")
    
    # Load template
    template_path = f"config/{args.template}_config.json"
    if not Path(template_path).exists():
        template_path = "config/default_config.json"
    
    try:
        if Path(template_path).exists():
            with open(template_path, 'r') as f:
                config = json.load(f)
        else:
            # Fallback default config
            config = {
                "description": "Custom configuration for CSV transformation",
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
                "required_fields": ["Summary", "Issue Type"]
            }
        
        # Save new config file
        with open(args.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration file created: {args.config_file}")
        print("💡 Edit this file to customize your transformation settings")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    print("🚀 TestRail to Jira CSV Converter")
    print("=" * 40)
    
    # Route to appropriate command handler
    command_handlers = {
        'transform': command_transform,
        'preview': command_preview,
        'validate': command_validate,
        'batch': command_batch,
        'init-config': command_init_config
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n\n⏹️  Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return 1
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())