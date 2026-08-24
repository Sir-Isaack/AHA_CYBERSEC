#!/bin/bash

# Base64 Encoder heading
echo -e "\033[1;36m==================================================="
echo "Base64 Encoder"
echo -e "============================================\033[0m"
echo

# Description: Reads plaintext passwords and Base64-encodes each password

# Ask the user for the input file
echo "Enter the input file containing plaintext passwords:"
read -r password_file

#Confirm whether the specified file exists
if [ ! -f "$password_file" ]; then
        # Display an error if the file does not exist
        echo "Error: The File '$password_file' does not exist"
        exit 1
fi

# Asks the user to enter the name of the output file 
# Stores the file under output_file variable
echo "Enter the output file"
read -r output_file

# Check if the base64 command is available
# Uses base64 for encoding
if command -v base64 >/dev/null 2>&1; then
        encoder="base64"

# If base64 is not available, checks for python3
# Uses python3 as the backup encoder
elif command -v python3 >/dev/null 2>&1; then
        encoder="python3"

#Displays an error message if neither of the encoder is available and exits
else 
        echo "Error: Base64 encoder not available"
        exit 1
fi

#Read the password file one line at a time
count=0

while IFS= read -r password; do

        # Checks whether the current line is empty and Skips it
        if [ -z "$password" ]; then
                continue
        fi

        # Check whether Base64-encode was selected and encodes the password
        if [ "$encoder" = "base64" ]; then
                encoded=$(printf '%s' "$password" | base64)
        # Encoded the passwords using python3
        else
                encoded=$(printf '%s' "$password" | python3 -c 'import sys,base64; print(base64.b64encode(sys.stdin.buffer.read()).decode())')
        fi

        # write the encoded string to the output file.
        printf '%s\n' "$encoded" >> "$output_file"

        count=$((count + 1))

done < "$password_file"

echo
echo "$count lines encoded"
echo
echo "Input file $password_file"
echo
echo "Output file $output_file"
echo
echo "Base64 Encoding was successful"
