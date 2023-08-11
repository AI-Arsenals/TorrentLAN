#!/bin/bash

# Iterate over each .js file
for file in $(find ./ -type f -name "*.js"); do
    # Ask for confirmation
    read -p "Modify '$file'? (y/n): " choice

    if [[ "$choice" =~ ^[Yy]$ ]]; then
        # Read the content of the file
        content=$(cat "$file")

        # Modify the content using awk
        modified_content=$(echo "$content" | awk '{gsub(/api\//, "http://127.0.0.1:8000/api/")} 1')

        # Overwrite the original file with the modified content
        echo "$modified_content" > "$file"
        echo "File '$file' modified."
    else
        echo "Skipped '$file'."
    fi
done
