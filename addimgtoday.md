# addimgtoday - Image Markdown Appender

## Description
A bash script that appends image markdown to a specified daily markdown file. It validates inputs, resolves paths, and formats the markdown output.

## Features
- Validates image path and format (JPEG only)
- Checks day number validity (1-366)
- Verifies target markdown file exists
- Appends properly formatted markdown with caption
- Supports logging to files
- Includes error handling and usage documentation

## Requirements
- Bash 4.0+
- Core utilities: realpath, date, cat, tee
- Configuration via config.env
- Common functions from lib/ directory

## Usage
