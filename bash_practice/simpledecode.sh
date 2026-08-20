#!/bin/bash

echo "Enter the name of the base64 encoded file"
read -r encoded_file

echo "Enter the name of the decoded file"
read -r decoded_file

while IFS= read -r line; do
	printf '%s\n' "$line" | base64 -d
	printf '\n'

done <"$encoded_file" > "$decoded_file"
