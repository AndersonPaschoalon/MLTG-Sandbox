#!/bin/bash
# This script just does whateneaver is necessary to update the libraries. 
#

#
# update CppTools
#

SOURCE_TAR_GZ="/home/anderson/Workspace/CppTools/Linux/pkg/cpptools_0.1.0.0.tar.gz"
DESTINATION="/home/anderson/Workspace/OpenLiTGen/Sources/libs"
FOLDER_NAME="cpptools_0.1.0.0"

# Copy the tar.gz file to the destination
cp "$SOURCE_TAR_GZ" "$DESTINATION"

# Navigate to the destination directory
cd "$DESTINATION"

# Create the folder for extraction
mkdir -p "$FOLDER_NAME"

# Extract the contents of the tar.gz file into the folder
tar -xzvf "$FOLDER_NAME.tar.gz" -C "$FOLDER_NAME" 

echo "Extraction completed to $DESTINATION/$FOLDER_NAME"

