# Scripts

This document describes all bash scripts in the project, their functionality, dependencies, environment variables, and called scripts.

## Table of Contents

1. [summarizevideo](#summarizevideo)
1. [findsnippetdays](#findsnippetdays)
1. [apply_overlayicon](#apply_overlayicon)
1. [genoverlays](#genoverlays)
1. [setupimgs](#setupimgs)
1. [setup](#setup)
1. [compact](#compact)
1. [genmonth](#genmonth)
1. [lintall](#lintall)
1. [replaceemojis](#replaceemojis)
1. [removeallsnippets](#removeallsnippets)
1. [findsnippetfiles](#findsnippetfiles)
1. [genmdfromvids](#genmdfromvids)
1. [addsnippets](#addsnippets)
1. [genvidthmd](#genvidthmd)
1. [genoverlay](#genoverlay)
1. [getgeminimodels](#getgeminimodels)
1. [annotatejpg](#annotatejpg)
1. [removesnippets](#removesnippets)
1. [addvideotoday](#addvideotoday)
1. [addsummariestodays](#addsummariestodays)
1. [gentoc](#gentoc)
1. [stitch](#stitch)
1. [addimgtoday](#addimgtoday)
1. [restoreemojis](#restoreemojis)
1. [annotatedayjpgs](#annotatedayjpgs)
1. [addvideo](#addvideo)
1. [genindexrst](#genindexrst)
1. [genstitchmd](#genstitchmd)

---

## summarizevideo

**Description**: Summarizes YouTube videos by extracting captions and using AI APIs (Gemini/DeepSeek) to generate markdown formatted summaries.\
**Dependencies**: jq, curl, yt-dlp, tee\
**Environment Variables**:

- YOUTUBE_API_KEY
- DEEPSEEK_API_KEY
- VIDEOS_FILE
- GAP_BW_REQS
- TEMPERATURE
- CHUNK_SUMMARY_PROMPT
- FINAL_SUMMARY_PROMPT
- LOGGING\
  **Called Scripts**:
- require.sh
- util.sh
- curl.sh
- youtube.sh
- lockconfig.sh\
  **Called Functions**:
- version
- usage
- get_day_index
- check_dependencies
- get_chunk_prompt
- get_final_prompt
- summarize_chunk_deepseek
- summarize_chunk
- final_summary_deepseek
- main

## findsnippetdays

**Description**: Finds and extracts day numbers from snippet files in month directories.\
**Dependencies**: sed, basename, grep, find, tr\
**Environment Variables**: None\
**Called Scripts**:

- util.sh
- color.sh
- require.sh\
  **Called Functions**:
- usage
- version
- main
- extract_day_number

## apply_overlayicon

**Description**: Applies overlay icon to DayXXX.jpg files in specified directory.\
**Dependencies**: find, parallel, tee\
**Environment Variables**:

- ICON_FILE
- ICON_SIZE
- ICON_OFFSET
- ICON_COMMENT
- LOGGING\
  **Called Scripts**:
- lockconfig.sh
  **Called Functions**:
- version
- usage
- err
- log
- validate_environment
- main

## genoverlays

**Description**: Processes video IDs from file and generates overlays.\
**Dependencies**: tee\
**Environment Variables**:

- VIDEOS_FILE
- LOGGING\
  **Called Scripts**:
- lockconfig.sh
- genoverlay\
  **Called Functions**:
- usage
- main

## setupimgs

**Description**: Processes and converts images in a directory, moves downloads to jpgs directory.\
**Dependencies**: gm, rm, mv\
**Environment Variables**: None\
**Called Scripts**:

- require.sh
  **Called Functions**:
- usage
- is_valid_dir
- get_downloads_dir
- main

## setup

**Description**: Creates monthly directories and files, videos file and header.md files.\
**Dependencies**: None\
**Environment Variables**:

- YEAR
- VIDEOS_FILE
- COMPACT_FILE\
  **Called Scripts**:
- lockconfig.sh\
  **Called Functions**:
- version
- backup_file
- confirm_overwrite
- setup_directories
- create_header_file
- main

## compact

**Description**: Compacts multiple markdown files into single output using m4 preprocessing.\
**Dependencies**: m4, mktemp, awk, rm\
**Environment Variables**:

- COMPACT_FILE\
  **Called Scripts**:
- lockconfig.sh
- require.sh
- vidmd.sh\
  **Called Functions**:
- usage
- is_valid_dir
- main

## genmonth

**Description**: Generates monthly markdown file with video index and table of contents.\
**Dependencies**: date, markdown-toc\
**Environment Variables**: None\
**Called Scripts**:

- require.sh
- date.sh
- lockconfig.sh
- compact
- gentoc\
  **Called Functions**:
- version
- usage
- validate_inputs
- generate_month_file
- dry_run
- main

## lintall

**Description**: Lints and formats all markdown files in project using markdownlint and mdformat.\
**Dependencies**: markdownlint, mdformat\
**Environment Variables**: None\
**Called Scripts**:

- require.sh\
  **Called Functions**:
- version
- usage
- main

## replaceemojis

**Description**: Replaces specific emoji characters in markdown files.\
**Dependencies**: None\
**Environment Variables**: None\
**Called Scripts**: None\
**Called Functions**:

- version
- usage
- main

## removeallsnippets

**Description**: Removes all snippets by running removesnippets for each month (1-12).\
**Dependencies**: None\
**Environment Variables**: None\
**Called Scripts**:

- removesnippets\
  **Called Functions**:
- version
- main

## findsnippetfiles

**Description**: Finds markdown files containing 'Snippet' in month directories.\
**Dependencies**: find, grep, sort\
**Environment Variables**: None\
**Called Scripts**:

- require.sh\
  **Called Functions**:
- check_requirements
- main

## genmdfromvids

**Description**: Generates markdown files from video IDs with thumbnails and metadata.\
**Dependencies**: jq, curl, git\
**Environment Variables**:

- YEAR
- YOUTUBE_API_KEY\
  **Called Scripts**: None

## addsnippets

**Description**: Adds snippet images to markdown files and generates compact versions.\
**Dependencies**: date, markdown-toc-gen\
**Environment Variables**:

- GITHUB_USERNAME
- YEAR\
  **Called Scripts**:
- require.sh
- vidmd.sh
- lockconfig.sh\
  **Called Functions**:
- usage
- main

## genvidthmd

**Description**: Generates markdown for embedding YouTube videos.\
**Dependencies**: curl\
**Environment Variables**: None\
**Called Scripts**: None

## genoverlay

**Description**: Generates overlay images for YouTube videos.\
**Dependencies**: curl, realpath\
**Environment Variables**:

- YOUTUBE_API_KEY\
  **Called Scripts**:
- require.sh
- vidmd.sh
- overlayicon\
  **Called Functions**:
- usage
- version
- main

## annotatejpg

**Description**: Adds metadata comments to JPG files.\
**Dependencies**: exiftool, file\
**Environment Variables**: None\
**Called Scripts**:

- util.sh
- require.sh\
  **Called Functions**:
- version
- usage
- main

## removesnippets

**Description**: Removes snippet references from day markdown files.\
**Dependencies**: git, find, sed, grep, basename\
**Environment Variables**:

- GITHUB_USERNAME\
  **Called Scripts**:
- util.sh
- require.sh
- findsnippetfiles\
  **Called Functions**:
- version
- usage
- get_findsnippetfiles_path
- validate_month
- month_number_to_name
- get_repo_name
- process_month_files
- process_file
- remove_snippet
- verify_remaining_snippets
- main

## addvideotoday

**Description**: Adds YouTube video metadata to daily markdown files.\
**Dependencies**: jq, curl, git\
**Environment Variables**:

- YEAR
- YOUTUBE_API_KEY\
  **Called Scripts**:
- require.sh
- util.sh
- git.sh
- lockconfig.sh
- summarizevideo\
  **Called Functions**:
- usage
- version
- validate_arguments
- check_required_tools
- fetch_video_metadata
- extract_thumbnail_url
- extract_video_title
- download_thumbnail
- backup_file
- remove_existing_video_entry
- append_video_info
- main

## addsummariestodays

**Description**: Adds AI-generated summaries to day markdown files.\
**Dependencies**: None\
**Environment Variables**:

- YEAR
- VIDEOS_FILE\
  **Called Scripts**:
- lockconfig.sh
- summarizevideo\
  **Called Functions**:

## gentoc

**Description**: Generates and updates table of contents for Markdown files.\
**Dependencies**: markdown-toc-gen\
**Environment Variables**: None\
**Called Scripts**:

- require.sh\
  **Called Functions**:
- validate_input
- generate_toc
- version
- usage
- main

## stitch

**Description**: Generates README.md from stitch.md using stitchmd.\
**Dependencies**: stitchmd\
**Environment Variables**: None\
**Called Scripts**:

- require.sh\
  **Called Functions**:
- validate_input
- generate_readme
- main

## addimgtoday

**Description**: Adds image to day markdown file with caption.\
**Dependencies**: file, git\
**Environment Variables**:

- YEAR\
  **Called Scripts**:
- lockconfig.sh\
  **Called Functions**:
- usage
- version
- append_image_markdown
- main

## restoreemojis

**Description**: Replaces certain emojis in markdown files with alternatives.\
**Dependencies**: None\
**Environment Variables**: None\
**Called Scripts**: None\
**Called Functions**:

- version
- usage
- main

## annotatedayjpgs

**Description**: Annotates DayXXX.jpg files in month directories with timestamp metadata.\
**Dependencies**: None\
**Environment Variables**: None\
**Called Scripts**:

- color.sh
- annotatejpg\
  **Called Functions**:
- usage
- version
- cleanup
- process_month
- main

## addvideo

**Description**: Adds new videos to system by generating markdown and updating indexes.\
**Dependencies**: sed, basename, date, markdown-toc, tee\
**Environment Variables**:

- YOUTUBE_API_KEY
- GITHUB_USERNAME
- YEAR
- COMPACT_FILE
- VIDEOS_FILE\
  **Called Scripts**:
- require.sh
- internet.sh
- vidmd.sh
- lockconfig.sh
- genoverlay
- genvidthmd
- summarizevideo
- compact\
  **Called Functions**:
- version
- usage
- validate_inputs
- generate_files
- dry_run
- main
- checkinternet

## genindexrst

**Description**: Generates index.rst for Sphinx documentation.\
**Dependencies**: None\
**Environment Variables**:

- PROJECT
- YEAR\
  **Called Scripts**:
- lockconfig.sh\
  **Called Functions**:
- version
- usage
- main

## genstitchmd

**Description**: Generates stitch.md from CONTENT_DOCS.\
**Dependencies**: None\
**Environment Variables**: None\
**Called Scripts**:

- lockconfig.sh\
  **Called Functions**:
- version
- main
