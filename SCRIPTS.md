# SCRIPTS

- [addimgtoday](#addimgtoday---image-markdown-appender)
- [addsnippets](#addsnippets---snippet-image-processor)
- [addsummariestodays](#addsummariestodays)

## addimgtoday - Image Markdown Appender

### Description

______________________________________________________________________

A bash script that appends image markdown to a specified daily markdown file. It validates inputs, resolves paths, and formats the markdown output.

### Features

______________________________________________________________________

- Validates image path and format (JPEG only)
- Checks day number validity (1-366)
- Verifies target markdown file exists
- Appends properly formatted markdown with caption
- Supports logging to files
- Includes error handling and usage documentation

### Requirements

______________________________________________________________________

- Bash 4.0+
- Core utilities: realpath, date, cat, tee
- Configuration via config.env
- Common functions from lib/ directory

### Usage

______________________________________________________________________

#### Basic Syntax

______________________________________________________________________

## addsnippets - Snippet Image Processor

### Overview

The `addsnippets` script processes snippet images for specified days of year (DOY) and:

1. Adds them to corresponding markdown files
1. Generates compact versions with table of contents for each month

### Usage

## addsummariestodays

A script to add AI-generated summaries to daily markdown files for a range of days.

### Usage
