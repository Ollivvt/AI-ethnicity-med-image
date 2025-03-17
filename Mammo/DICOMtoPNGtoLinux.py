import os
import pandas as pd
import pydicom
import numpy as np
from PIL import Image
from collections import defaultdict

# Input CSV file and SSD output folder
csv_file = "/home/yu-tingtseng_sa/GitHub/AI-ethnicity-med-image/data/Mammo/D1-D6_SA.csv"
data = pd.read_csv(csv_file, low_memory=False)

# Define the correct base path
correct_base_path = "/mnt/disk_share"

# Replace 'Q:\' with the correct base path and standardize separators
data['FilePath'] = data['FilePath'].str.replace(r"^Q:\\", correct_base_path + "/", regex=True)
data['FilePath'] = data['FilePath'].str.replace(r"\\\\|\\", "/", regex=True)

# Exclude rows where ethnicity is "U"
data = data[data["ethnicity"] != "U"]

output_folder = "/mnt/data2"
log_file = "/mnt/data2/sa_conversion_log.txt"

# Function to validate folder_path
def is_valid_path(path):
    return isinstance(path, (str, bytes, os.PathLike)) and not pd.isna(path)

# Function to read existing log entries
def get_processed_files(log_path):
    processed_files = set()
    if os.path.exists(log_path):
        with open(log_path, "r") as log:
            for line in log:
                parts = line.strip().split(",")
                if len(parts) == 2 and parts[1] == "Success":
                    processed_files.add(parts[0])  # Add processed file path
    return processed_files

# Load already processed files
processed_files = get_processed_files(log_file)

# Function to convert DICOM to PNG while keeping original dimensions
def convert_dicom_to_png(dicom_path, output_path):
    try:
        # Load the DICOM file
        ds = pydicom.dcmread(dicom_path)
        pixel_array = ds.pixel_array.astype(np.float32)

        # Adjust using Rescale Slope and Intercept (if available)
        slope = getattr(ds, "RescaleSlope", 1)
        intercept = getattr(ds, "RescaleIntercept", 0)
        pixel_array = pixel_array * slope + intercept

        # Apply Windowing
        if hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth"):
            window_center = ds.WindowCenter if isinstance(ds.WindowCenter, float) else ds.WindowCenter[0]
            window_width = ds.WindowWidth if isinstance(ds.WindowWidth, float) else ds.WindowWidth[0]

            # Calculate the minimum and maximum pixel values for the window
            min_value = window_center - window_width / 2
            max_value = window_center + window_width / 2

            # Clip the pixel values to the window
            pixel_array = np.clip(pixel_array, min_value, max_value)

        # Normalize pixel values to the range [0, 255]
        pixel_array -= pixel_array.min()
        pixel_array /= pixel_array.max()
        pixel_array *= 255

        # Convert to uint8 for image saving
        image_array = pixel_array.astype(np.uint8)

        # Convert to a PIL Image and save
        image = Image.fromarray(image_array)
        image.save(output_path)
        return True
    except Exception as e:
        print(f"Error converting {dicom_path}: {e}")
        return False

# Function to log details
def log_conversion(file_name, status):
    with open(log_file, "a") as log:
        log.write(f"{file_name},{status}\n")

# Create the base output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over each row in the filtered CSV
for _, row in data.iterrows():
    folder_path = row["FilePath"]
    
    # Validate folder_path
    if not is_valid_path(folder_path):
        print(f"Invalid or missing folder path: {folder_path}")
        log_conversion(folder_path, "Invalid Path")
        continue  # Skip this row

    # Check if the folder exists
    if os.path.exists(folder_path):
        # List all files in the folder
        for file_name in os.listdir(folder_path):
            if "LCC_Processed" in file_name or "RCC_Processed" in file_name:
                dicom_path = os.path.join(folder_path, file_name)

                # Replicate the folder structure in the output directory
                relative_path = os.path.relpath(folder_path, correct_base_path)
                target_folder = os.path.join(output_folder, relative_path)
                os.makedirs(target_folder, exist_ok=True)

                # Define the output PNG file path
                output_path = os.path.join(target_folder, f"{os.path.splitext(file_name)[0]}.png")

                # Skip if file already processed
                if output_path in processed_files or os.path.exists(output_path):
                    print(f"Skipping (already processed): {file_name}")
                    continue

                # Convert DICOM to PNG
                if convert_dicom_to_png(dicom_path, output_path):
                    print(f"Converted: {file_name} -> {output_path}")
                    log_conversion(output_path, "Success")
                else:
                    print(f"Failed: {file_name}")
                    log_conversion(output_path, "Failed")

    else:
        print(f"Folder does not exist: {folder_path}")
        log_conversion(folder_path, "Folder Missing")
