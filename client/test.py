import os
import pandas as pd

# Get the current directory of the script
current_dir = os.path.dirname(__file__)

# Construct the full path to the CSV file
csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))

username = pd.read_csv(csv_path)["Username"]
password = pd.read_csv(csv_path)["Password"]