# Script Documentation

This document describes all bash scripts in the project, their functionality, dependencies, and environment variables used.

## Table of Contents

1. [summarizevideo](#summarizevideo)
2. [findsnippetdays](#findsnippetdays)
3. [apply_overlayicon](#apply_overlayicon)
4. [genoverlays](#genoverlays)
5. [setupimgs](#setupimgs)
6. [replacevmds](#replacevmds)
7. [genvidmd](#genvidmd)
8. [setup](#setup)
9. [compact](#compact)
10. [genmonth](#genmonth)
11. [lintall](#lintall)
12. [replaceemojis](#replaceemojis)
13. [removeallsnippets](#removeallsnippets)
14. [findsnippetfiles](#findsnippetfiles)
15. [genmdfromvids](#genmdfromvids)
16. [addsnippets](#addsnippets)
17. [genvidthmd](#genvidthmd)
18. [genoverlay](#genoverlay)
19. [getgeminimodels](#getgeminimodels)
20. [annotatejpg](#annotatejpg)
21. [removesnippets](#removesnippets)
22. [addvideotoday](#addvideotoday)
23. [addsummariestodays](#addsummariestodays)
24. [gentoc](#gentoc)
25. [stitch](#stitch)
26. [addimgtoday](#addimgtoday)
27. [restoreemojis](#restoreemojis)
28. [overlayicon](#overlayicon)
29. [overlayimg](#overlayimg)
30. [annotatedayjpgs](#annotatedayjpgs)
31. [addvideo](#addvideo)

---

## summarizevideo

**Description**: Summarizes YouTube videos by extracting captions and using AI APIs (Gemini/DeepSeek) to generate markdown formatted summaries  
**Dependencies**: jq, curl, yt-dlp  
**Environment Variables**:

- YOUTUBE_API_KEY
- GEMINI_API_KEY
- DEEPSEEK_API_KEY
- VIDEOS_FILE
- GAP_BW_REQS
- TEMPERATURE
- CHUNK_SUMMARY_PROMPT
- FINAL_SUMMARY_PROMPT
- LOGGING  
  **Called Scripts**:
- require.sh
- util.sh
- curl.sh
- youtube.sh
- lockconfig.sh

## findsnippetdays

**Description**: Finds and extracts day numbers from snippet files in month directories  
**Dependencies**: sed, basename, grep, find, tr  
**Environment Variables**: None  
**Called Scripts**:

- util.sh
- color.sh
- require.sh

## apply_overlayicon

**Description**: Applies overlay icon to DayXXX.jpg files in specified directory  
**Dependencies**: find, xargs  
**Environment Variables**:

- ICON_FILE
- ICON_SIZE
- ICON_OFFSET
- ICON_COMMENT
- LOGGING  
  **Called Scripts**:
- lockconfig.sh
- overlayicon

## genoverlays

**Description**: Processes video IDs from file and generates overlays  
**Dependencies**: None  
**Environment Variables**:

- VIDEOS_FILE
- LOGGING  
  **Called Scripts**:
- lockconfig.sh
- genoverlay

## setupimgs

**Description**: Processes and converts images in a directory, moves downloads to jpgs directory  
**Dependencies**: gm, rm, mv  
**Environment Variables**: None  
**Called Scripts**: None

## replacevmds

**Description**: Processes markdown files and replaces video markdown syntax  
**Dependencies**: mv, mktemp, curl  
**Environment Variables**: None  
**Called Scripts**:

- vidmd.sh

## genvidmd

**Description**: Generates markdown for embedding YouTube videos with overlay images  
**Dependencies**: None  
**Environment Variables**:

- GITHUB_USERNAME  
  **Called Scripts**:
- require.sh
- internet.sh
- vidmd.sh
- overlayimg

## setup

**Description**: Creates monthly directories and files, videos file and header.md files  
**Dependencies**: None  
**Environment Variables**:

- YEAR
- VIDEOS_FILE
- COMPACT_FILE  
  **Called Scripts**:
- lockconfig.sh

## compact

**Description**: Compacts multiple markdown files into single output using m4 preprocessing  
**Dependencies**: m4, mktemp, awk, rm  
**Environment Variables**:

- COMPACT_FILE  
  **Called Scripts**:
- lockconfig.sh
- require.sh
- vidmd.sh

## genmonth

**Description**: Generates monthly markdown file with video index and table of contents  
**Dependencies**: date, markdown-toc  
**Environment Variables**: None  
**Called Scripts**:

- vidmd.sh
- compact
- gentoc

## lintall

**Description**: Lints and formats all markdown files in project using markdownlint and mdformat  
**Dependencies**: markdownlint, mdformat  
**Environment Variables**: None  
**Called Scripts**:

- require.sh

## replaceemojis

**Description**: Replaces specific emoji characters in markdown files  
**Dependencies**: None  
**Environment Variables**: None  
**Called Scripts**: None

## removeallsnippets

**Description**: Removes all snippets by running removesnippets for each month (1-12)  
**Dependencies**: None  
**Environment Variables**: None  
**Called Scripts**:

- removesnippets

## findsnippetfiles

**Description**: Finds markdown files containing 'Snippet' in month directories  
**Dependencies**: find, grep, sort  
**Environment Variables**: None  
**Called Scripts**:

- require.sh

## genmdfromvids

**Description**: Generates markdown files from video IDs with thumbnails and metadata  
**Dependencies**: jq, curl, git  
**Environment Variables**:

- YEAR
- YOUTUBE_API_KEY  
  **Called Scripts**: None

## addsnippets

**Description**: Adds snippet images to markdown files and generates compact versions  
**Dependencies**: date, markdown-toc-gen  
**Environment Variables**:

- GITHUB_USERNAME
- YEAR  
  **Called Scripts**:
- require.sh
- vidmd.sh
- lockconfig.sh

## genvidthmd

**Description**: Wrapper for vidmd.sh that generates markdown for videos  
**Dependencies**: curl  
**Environment Variables**: None  
**Called Scripts**:

- vidmd.sh

## genoverlay

**Description**: Generates overlay images for YouTube videos  
**Dependencies**: curl, realpath  
**Environment Variables**:

- YOUTUBE_API_KEY  
  **Called Scripts**:
- require.sh
- vidmd.sh
- overlayicon

## getgeminimodels

**Description**: Fetches available Gemini models from API and saves to geminimodelids.txt  
**Dependencies**: curl, jq  
**Environment Variables**:

- GEMINI_API_KEY  
  **Called Scripts**: None

## annotatejpg

**Description**: Adds metadata comments to JPG files  
**Dependencies**: exiftool, file  
**Environment Variables**: None  
**Called Scripts**:

- util.sh
- require.sh

## removesnippets

**Description**: Removes snippet references from day markdown files  
**Dependencies**: git, find, sed, grep, basename  
**Environment Variables**:

- GITHUB_USERNAME  
  **Called Scripts**:
- util.sh
- require.sh
- findsnippetfiles

## addvideotoday

**Description**: Adds YouTube video metadata to daily markdown files  
**Dependencies**: jq, curl, git  
**Environment Variables**:

- YEAR
- YOUTUBE_API_KEY  
  **Called Scripts**:
- require.sh
- util.sh
- git.sh
- lockconfig.sh
- summarizevideo

## addsummariestodays

**Description**: Adds AI-generated summaries to day markdown files  
**Dependencies**: None  
**Environment Variables**:

- YEAR
- VIDEOS_FILE  
  **Called Scripts**:
- lockconfig.sh
- summarizevideo

## gentoc

**Description**: Generates and updates table of contents for Markdown files  
**Dependencies**: markdown-toc-gen  
**Environment Variables**: None  
**Called Scripts**:

- require.sh

## stitch

**Description**: Generates README.md from stitch.md using stitchmd  
**Dependencies**: stitchmd  
**Environment Variables**: None  
**Called Scripts**:

- require.sh

## addimgtoday

**Description**: Adds image to day markdown file with caption  
**Dependencies**: file, git  
**Environment Variables**:

- YEAR  
  **Called Scripts**:
- lockconfig.sh

## restoreemojis

**Description**: Replaces certain emojis in markdown files with alternatives  
**Dependencies**: None  
**Environment Variables**: None  
**Called Scripts**: None

## overlayicon

**Description**: Applies play button overlay to JPEG images  
**Dependencies**: gm, file, grep, mktemp, exiftool  
**Environment Variables**:

- ICON_FILE
- ICON_SIZE
- ICON_OFFSET
- ICON_COMMENT  
  **Called Scripts**:
- lockconfig.sh

## overlayimg

**Description**: Downloads YouTube thumbnail and overlays play icon  
**Dependencies**: None  
**Environment Variables**: None  
**Called Scripts**:

- vidmd.sh
- overlayicon

## annotatedayjpgs

**Description**: Annotates DayXXX.jpg files in month directories with timestamp metadata  
**Dependencies**: None  
**Environment Variables**: None  
**Called Scripts**:

- color.sh
- annotatejpg

## addvideo

**Description**: Adds new videos to system by generating markdown and updating indexes  
**Dependencies**: sed, basename, date, markdown-toc  
**Environment Variables**:

- YOUTUBE_API_KEY
- GITHUB_USERNAME
- YEAR
- COMPACT_FILE
- VIDEOS_FILE  
  **Called Scripts**:
- require.sh
- internet.sh
- vidmd.sh
- lockconfig.sh
- genoverlay
- genvidthmd
- summarizevideo
- compact
