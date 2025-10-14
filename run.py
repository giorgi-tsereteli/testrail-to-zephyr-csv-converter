#!/usr/bin/env python3
from src.transformer import CSVTransformer

def main():
    transformer = CSVTransformer()
    result = transformer.transform('data/testrail_export.csv', 'data/jira_import.csv')
    
    if result['success']:
        if 'filtered_rows' in result:
            print(f"📊 {result['filtered_rows']} rows transformed (filtered from {result['original_rows']} total rows)\n")
        else:
            print(f"📊 {result['transformed_rows']} rows transformed\n")

if __name__ == "__main__":
    main()