#!/usr/bin/env python3
from src.transformer import CSVTransformer

def main():
    transformer = CSVTransformer()
    result = transformer.transform('examples/sample_testrail_export.csv', 'examples/jira_import.csv')
    
    if result['success']:
        print(f"📊 {result['original_rows']} rows transformed")

if __name__ == "__main__":
    main()