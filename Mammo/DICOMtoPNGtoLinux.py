import os
import pandas as pd
import pydicom
import numpy as np
from PIL import Image
from collections import defaultdict

# Input CSV file and SSD output folder
csv_file = "/home/yu-tingtseng_sa/GitHub/AI-ethnicity-med-image/data/Mammo/All_XWalk_Outcome_cleaned.csv"
data = pd.read_csv(csv_file, low_memory=False)

# Define the correct base path
correct_base_path = "/mnt/disk_share/AIRM"

# Replace 'Q:\' with the correct base path and standardize separators
data['FilePath'] = data['FilePath'].str.replace(r"^Q:\\", correct_base_path + "/", regex=True)
data['FilePath'] = data['FilePath'].str.replace(r"\\\\|\\", "/", regex=True)

output_folder = "/mnt/data1"
log_file = "/mnt/data1/conversion_log.txt"

# Function to validate folder_path
def is_valid_path(path):
    return isinstance(path, (str, bytes, os.PathLike)) and not pd.isna(path)

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

# Counter for processed images
processed_images = 0
# max_images = 10

# Iterate over each row in the CSV
for _, row in data.iterrows():
    #if processed_images >= max_images:
    #    print("Reached the limit of 10 images. Stopping test.")
    #    break

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
        #    if processed_images >= max_images:
        #        break

            if "LCC" in file_name or "RCC" in file_name:
                dicom_path = os.path.join(folder_path, file_name)

                # Replicate the folder structure in the output directory
                relative_path = os.path.relpath(folder_path, correct_base_path)
                target_folder = os.path.join(output_folder, relative_path)
                os.makedirs(target_folder, exist_ok=True)

                # Define the output PNG file path
                output_path = os.path.join(target_folder, f"{os.path.splitext(file_name)[0]}.png")

                # Convert DICOM to PNG
                if convert_dicom_to_png(dicom_path, output_path):
                    print(f"Converted: {file_name} -> {output_path}")
                    log_conversion(output_path, "Success")
                else:
                    print(f"Failed: {file_name}")
                    log_conversion(output_path, "Failed")

                # Increment the processed images counter
                processed_images += 1
    else:
        print(f"Folder does not exist: {folder_path}")
        log_conversion(folder_path, "Folder Missing")
        
# Define the base directory
base_directory = "/mnt/data1"

# Dictionary to store the counts
folder_counts = defaultdict(int)

# Traverse the base directory
for root, _, files in os.walk(base_directory):
    # Get the first-level folder name
    relative_path = os.path.relpath(root, base_directory)
    first_folder = relative_path.split(os.sep)[0] if relative_path != "." else None

    # Skip if we're not in a subfolder
    if first_folder:
        # Count PNG files in the current folder
        for file in files:
            if file.lower().endswith(".png"):
                folder_counts[first_folder] += 1

# Print the counts
print("PNG file counts by first-level folder:")
for folder, count in folder_counts.items():
    print(f"{folder}: {count}")

# Optional: Save the counts to a file
output_file = "/mnt/data1/png_file_counts.txt"
with open(output_file, "w") as f:
    for folder, count in folder_counts.items():
        f.write(f"{folder}: {count}\n")
print(f"Counts saved to {output_file}")