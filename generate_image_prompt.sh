#!/bin/bash

# Check if input file argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No input file provided"
    echo "Usage: $0 /path/to/DayXXXSummary.txt"
    exit 1
fi

input_file="$1"
output_file="${input_file/Summary.txt/ImagePrompt.json}"

# Check if required environment variables are set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "Error: DEEPSEEK_API_KEY environment variable not set"
    exit 1
fi

if [ -z "$SUMMARY_IMAGE_META_PROMPT" ]; then
    echo "Error: SUMMARY_IMAGE_META_PROMPT environment variable not set"
    exit 1
fi

# Read the summary content
summary_content=$(<"$input_file")

# Call DeepSeek API to generate the image prompt
response=$(curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {
        "role": "system",
        "content": "'"$SUMMARY_IMAGE_META_PROMPT"'"
      },
      {
        "role": "user",
        "content": "'"$summary_content"'"
      }
    ],
    "temperature": 0.7
  }')

# Extract the generated content from the response
generated_content=$(echo "$response" | jq -r '.choices[0].message.content')

# Save to JSON file
echo "$generated_content" > "$output_file"

echo "Image prompt generated and saved to $output_file"
