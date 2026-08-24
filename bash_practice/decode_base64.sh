#!/bin/bash

# Script description
# Reads Base64 strings from an input file
# and decodes each entry into plaintext.
#
# Usage:
# ./decode_base64.sh
#
# The script will ask for:
# 1. The input file containing Base64 strings
# 2. The output file for decoded plaintext


# Display the script heading in yellow
echo -e "\033[1;33m===================================="
echo "     Base64 Decoding"
echo -e "====================================\033[0m"
echo


# Ask the user for the input file
echo "Enter the input file containing Base64 strings:"
iecho

# Store the input filename
read -r input_file
echo


# Check whether the input file exists
if [ ! -f "$input_file" ]; then
        # Display an error message
        echo "Error: The file '$input_file' does not exist."
        exit 1
fi


# Ask the user for the output file
echo "Enter the output file for decoded plaintext:"
echo

# Store the output filename
read -r output_file
echo


# Check whether the base64 command is available
if command -v base64 >/dev/null 2>&1; then

        # Detect which decode option the system supports
        if base64 --decode </dev/null >/dev/null 2>&1; then
                decode_flag="--decode"

        elif base64 -d </dev/null >/dev/null 2>&1; then
                decode_flag="-d"

        elif base64 -D </dev/null >/dev/null 2>&1; then
                decode_flag="-D"

        else
                # No supported base64 decode flag was found
                decode_flag=""
        fi

else
        # Base64 command is not available
        decode_flag=""
fi


# Use Python3 if no suitable base64 decode flag was found
if [ -z "$decode_flag" ]; then

        # Check whether Python3 is available
        if command -v python3 >/dev/null 2>&1; then
                encoder="python3"
        else
                # Neither base64 nor Python3 is available
                echo "Error: No Base64 decoder is available."
                exit 1
        fi

else
        # Use the system base64 command
        encoder="base64"
fi


# Check whether the output file can be created
if ! : > "$output_file"; then
        echo "Error: Cannot create or write to '$output_file'."
        exit 1
fi


# Read the input file one line at a time
while IFS= read -r encoded; do

        # Decode using the system base64 command
        if [ "$encoder" = "base64" ]; then

                # Attempt to decode the current Base64 string
                decoded=$(printf '%s' "$encoded" | base64 "$decode_flag" 2>/dev/null)

                # Check whether decoding was successful
                if [ $? -ne 0 ]; then

                        # Write an explanatory placeholder for invalid input
                        printf '%s\n' "[Decode error: invalid Base64 input]" >> "$output_file"

                        # Continue with the next line
                        continue
                fi

        else

                # Decode using Python3
                decoded=$(printf '%s' "$encoded" | python3 -c 'import sys,base64; print(base64.b64decode(sys.stdin.read(), validate=True).decode())' 2>/dev/null)

                # Check whether Python3 decoding was successful
                if [ $? -ne 0 ]; then

                        # Write an explanatory placeholder for invalid input
                        printf '%s\n' "[Decode error: invalid Base64 input]" >> "$output_file"

                        # Continue with the next line
                        continue
                fi
        fi


        # Write the decoded plaintext to the output file
        printf '%s\n' "$decoded" >> "$output_file"

done < "$input_file"


# Display the input and output files
echo
echo "Input file: $input_file"
echo
echo "Decoded file: $output_file"
echo
echo "Base64 decoding was successful"
