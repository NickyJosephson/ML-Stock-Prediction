import pandas as pd
import os

# Directory paths
input_dir = './data/s3_parquet/'  # Directory containing Parquet files
output_dir = './data/s3_csv/'  # Directory to save CSV files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over all files in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.parquet'):  # Check for Parquet files
        parquet_file = os.path.join(input_dir, file_name)  # Full path to the Parquet file
        csv_file = os.path.join(output_dir, file_name.replace('.parquet', '.csv'))  # Replace extension
        
        # Convert Parquet to CSV
        try:
            df = pd.read_parquet(parquet_file)
            df.to_csv(csv_file, index=False)
            print(f"Converted {parquet_file} to {csv_file}")
        except Exception as e:
            print(f"Failed to convert {parquet_file}: {e}")