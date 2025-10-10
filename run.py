#!/usr/bin/env python3
from src.transformer import CSVTransformer

def main():
    transformer = CSVTransformer()
    result = transformer.transform('examples/sample_testrail_export.csv', 'examples/jira_import.csv')
    
    if result['success']:
        if 'filtered_rows' in result:
            print(f"📊 {result['filtered_rows']} rows transformed (filtered from {result['original_rows']} total rows)")
        else:
            print(f"📊 {result['transformed_rows']} rows transformed")

if __name__ == "__main__":
    main()