# HOWTO

<!-- markdownlint-disable MD033 -->

<!-- toc -->

- [Prerequisites](#prerequisites)
  - [Environment variables](#environment-variables)
  - [Configuration](#configuration)
    - [General Settings](#general-settings)
    - [Overlay Icon Configuration](#overlay-icon-configuration)
    - [File Configuration](#file-configuration)
    - [API Request Settings](#api-request-settings)
    - [AI Model Settings](#ai-model-settings)
    - [Content Documentation Settings](#content-documentation-settings)
  - [Vale](#vale)
- [Add the daily Youtube video](#add-the-daily-youtube-video)
- [Add additional Youtube video to a day](#add-additional-youtube-video-to-a-day)
- [Add today's sharing](#add-todays-sharing)
- [Merge monthly markdown files into one large README](#merge-monthly-markdown-files-into-one-large-readme)
- [Generate table of contents for markdown files](#generate-table-of-contents-for-markdown-files)
- [Using the commands utility that accepts text commands in file `commands.txt`](#using-the-commands-utility-that-accepts-text-commands-in-file-commandstxt)

<!-- tocstop -->

## Prerequisites

- [curl](https://curl.se/)
- [gm](http://www.graphicsmagick.org/)
- [m4](https://www.gnu.org/software/m4/m4.html)
- [stitchmd](https://github.com/abhinav/stitchmd)
- [markdown-toc-gen](https://github.com/thesilk-tux/markdown-toc-gen)
- [mdformat](https://github.com/hukkin/mdformat)
- [markdownlint](https://github.com/DavidAnson/markdownlint)
- [vale](https://github.com/errata-ai/vale)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [exiftool](https://exiftool.org/)

1. Create an empty `videos.txt` file under the root directory.
1. Create a directory for each month of the year under the root directory.
1. Add a `header.md` file under each monthly directory with the following content.
   Example for January:
   <pre><code>&lt;!-- toc --&gt;&lt;!-- tocstop --&gt;</code></pre>

```markdown
# January 2025

RIAY January 2025
```

`markdown-toc-gen` won't generate the table of contents
for the monthly markdown (in this case, `January.md`)
without the mandatory `<-- toc -->` and `<!-- tocstop -->` comments header.

You can replace the top-level markdown header

```markdown
# January 2025

RIAY January 2025
```

with your own if you wish.

Add a `compact.txt` file with the first line as `header.md` under each monthly directory.
This ensures the presence of the header for each month's markdown.

Note: You can do all this by simply executing the script `setup`.

### Environment variables

1. Export an environment variable `GITHUB_USERNAME` by adding the following line to your `.bash_profile` file.

1. Substitute your Github user id for `<userid>`.

   ```bash
   export GITHUB_USERNAME="<userid>"
   ```

1. Export environment variable `YOUTUBE_API_KEY` by adding the following line to `.bash_profile`.

   ```bash
   export YOUTUBE_API_KEY=<api_key>
   ```

   Substitute your Google API Key which can access YouTube Data API.
   Set up your API key using instructions at <https://support.google.com/googleapi/answer/6158862?hl=en>

1. Export environment variable `DEEPSEEK_API_KEY` by adding the following line to `.bash_profile`.

   ```bash
   export DEEPSEEK_API_KEY=<api_key>
   ```

   Substitute your DeepSeek API Key which can access YouTube Data API.
   Set up your API key using instructions at <https://docs.aicontentlabs.com/articles/deepseek-api-key/>

**Note:** You will need to set up either DeepSeek or Gemini API keys for AI-generation of podcast summaries.

### Configuration

The configuration file `config.env` is located in the repo's root directory.

It contains the following settings:

#### General Settings

```bash
# Project config values
PROJECT="Rosary In A Year (RIAY)"
# Turn on or turn off logging
LOGGING=false
# The year in which the podcasts are being followed
YEAR=2025

# Github config values
REPO_OWNER=linusjf
REPO_NAME=RIAY
```

#### Overlay Icon Configuration

```bash
ICON_FILE="play-button.png"
ICON_SIZE="256x256"
ICON_OFFSET="+32+0"
ICON_COMMENT="Play Icon Added"
```

#### File Configuration

```bash
COMPACT_FILE="compact.txt"
VIDEOS_FILE="videos.txt"
```

#### API Request Settings

```bash
# Time between successive requests to the LLM models (seconds)
GAP_BW_REQS=0
# Maximum number of retries for a REST API call
CURL_MAX_RETRIES=5
# Initial retry delay (seconds) - increases exponentially
CURL_INITIAL_RETRY_DELAY=2
# Connection timeout for curl requests (seconds)
CURL_CONNECT_TIMEOUT=30
# Maximum time for curl operations (seconds)
CURL_MAX_TIME=90
```

#### AI Model Settings

```bash
# Temperature for LLM responses (0 for deterministic output)
TEMPERATURE=0.5

# text llm api key
TEXT_LLM_API_KEY="$DEEPSEEK_API_KEY"
# text llm base url
TEXT_LLM_BASE_URL="https://api.deepseek.com"
# text llm chat model endpoint
TEXT_LLM_CHAT_ENDPOINT="/chat/completions"
# text llm model used for summarization
TEXT_LLM_MODEL="deepseek-chat"

# The system prompt for summarizing text.
SYSTEM_SUMMARY_PROMPT="You are a helpful assistant that summarizes content. Be concise, helpful."
# The prompt for summarizing chunks within the podcast transcript.
CHUNK_SUMMARY_PROMPT="Summarize this text, excluding plugs, branding, and promotions. Avoid mention of Day, podcast and Rosary in a Day. Additionally, exclude repetitive prayers such as Our Father, Hail Mary and Glory Be. Retain details of artwork decribed including title, artist (full name), current location of artwork, medium, style, date (year, decade and century) and brief description."
# The prompt for the final summary of all the chunk summaries
FINAL_SUMMARY_PROMPT="Summarize the following text in the voice and style of C.S. Lewis, employing his clarity, moral insight, and rhetorical flair, as if writing directly to an intelligent but unassuming reader. Generate a title as well. Avoid modern jargon, maintain a tone of gentle conviction, and present the ideas as timeless truths. Do not include any meta-commentary, footnotes, or explanations. Retain details of artworks. Start with a level three markdown header
'### AI-Generated Summary: '. Append your generated title (no colons, proper grammar) to the header."
```

#### Content Documentation Settings

```bash
# List of files for generating documentation
CONTENT_DOCS=(
  "RIAY=start.md"
  "January=January.md"
  "February=February.md"
  "March=March.md"
  "April=April.md"
  "May=May.md"
  "June=June.md"
  "July=July.md"
  "August=August.md"
  "September=September.md"
  "October=October.md"
  "November=November.md"
  "December=December.md"
)
```

The config values can be modified as per your preferences.

### Vale

Initialize `vale` styles by executing the command `vale sync`. This should download the specified styles in `.vale.ini`.

## Add the daily Youtube video

Execute the script `addvideo` with the following parameters:

- video id - the id of the Youtube video
- caption or title (in double quotes)

Example:

```bash
./addvideo 5I2BbalTOPo "Hagar and Ishmael"
```

Results:

1. Computes the `day of year` from the length of the videos.txt file.
   `day of year = (number of lines in videos.txt) + 1`
   In this case, 10.
1. Appends the Video id to the file `videos.txt` present in the root directory.
1. Generates markdown file `Day010.md` in the `January` subdirectory.
   1. This markdown file has a link to the Youtube video.
   1. It also has AI-Generated summary of the podcast.
1. Generates image file `Day010.jpg` in the `January/jpgs` directory.
1. Appends `Day010.md` filename to the `January/compact.txt` file.
1. Updates `January.md` file in the root directory with the contents of `Day010.md`.
1. Updated files:
   1. `./videos.txt`
   1. `./January.md`
   1. `./January/compact.txt`
1. Created files:
   1. `./January/Day010.md`
   1. `./January/jpgs/Day010.jpg`

## Add additional Youtube video to a day

When you have to add an additional video to the markdown for that day, you can execute the script `addvideotoday` with the following parameters:

- video id - the id of the Youtube video
- day of year - the day of the year for which the video is to be added

Example:

```bash
./addvideotoday 5I2BbalTOPo 21
```

Results:

1. Updates markdown file `Day021.md` in the `January` subdirectory.
   1. This markdown file has a link to the Youtube video.
   1. It also has AI-Generated summary of the podcast.
1. Generates image file `<videoid>.jpg` in the `January/jpgs` directory.
1. Updates `January.md` file in the root directory with the contents of `Day021.md`.
1. Updated files:
   1. `January/Day021.md`
   1. `./January.md`
1. Created files:
   1. `./January/jpgs/<videoid>.jpg`

## Add today's sharing

1. First, add today's video.
1. Edit the generated `Dayxxx.md` file for today.
1. Paste the sharing text into the file adding appropriate markdown headers as needed.
1. Save the file.
1. Execute script `genmonth` with the following parameters:

- month index - 1 - 12

- optional four digit year - 20XX

  Example:

  ```bash
  ./genmonth 01 2025
  OR

  ./genmonth 01
  # The year value will be picked from the environment variable YEAR
  ```

  Results:

  Updates the `January.md` file with the sharing text added to the `Day010.md` file.

You can add sharing to other days as well in a similar fashion.
Don't forget to execute `genmonth` with the appropriate month index for that day.

You can get the month index by executing the following bash command:

```bash
date --date="$(date --date='jan 1 + 30 days' '+%B %d,      %Y')" +%m
```

Decrement the day of year by 1 and substitute it in the command.
The preceding gives the month index for day 31.

## Merge monthly markdown files into one large README

1. Edit the `stitch.md` file provided to include the markdown files you wish to merge.

1. The file format follows:

   ```markdown
   # README

   - [RIAY](start.md)
   - [January](January.md)
   - [February](February.md)
   - [March](March.md)
   - [April](April.md)
   - [May](May.md)
   - [June](June.md)
   - [July](July.md)
   - [August](August.md)
   - [September](September.md)
   - [October](October.md)
   - [November](November.md)
   - [December](December.md)
   ```

   Include or exclude any files you need or don't need.

1. Execute the `stitch` script.

```bash
./stitch
```

Results:

Generates README with all the contents of the listed markdown files in `stitch.md`.

## Generate table of contents for markdown files

Execute the `gentoc` script as follows:

```bash
./gentoc <path to markdown file>
```

Before executing the script, update the file and place the comment `<!-- toc -->` and `<!-- tocstop -->` to generate the table of contents inside these markers.

Results:

Generates the table of contents per the existing headings in the markdown file.

## Using the commands utility that accepts text commands in file `commands.txt`

1. Install ANTLR4

Use [pyenv](https://github.com/pyenv/pyenv) to install and set up your Python3 environment.

Example of setting up your Python and ANTLR4 environment

```bash
pyenv install 3.10
pyenv global 3.10
pip install antlr4-tools antlr4-python3-runtime python-dotenv
```

1. Add commands to the `commands.txt` file.

Available commands:

- addvideo
- addvideotoday
- addimgtoday
- genmonth
- lintall
- stitch
- gentoc

**Note:** The `addvideotoday` and `addimgtoday` commands need the day of year to be a three digit number.
Hence, 1 becomes 001, 20 becomes 020 and 99 is 099.

For simplicity and consistency, the commands wrap their command line equivalents.

1. Execute the commands.py script.

```bash
./commands.py
```

This executes the commands in order as placed in the `commands.txt`. If any command fails, the program outputs an error message for that command and executes all following commands.

1. Example `commands.txt` file

```text
# example commands
addvideo "abc123456" "Example video" # add example video
addvideotoday "abc123456" 010 # add example video to day 10 markdown.
genmonth 01 2025 # generate markdown for month January, 2025
lintall # lint all the markdown files
```

The program ignores everything after the `#` symbol and treats it like a new line character.
