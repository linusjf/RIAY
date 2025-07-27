<!-- generate toc using markdown-toc-gen only -->
<!-- toc -->

- [Prerequisites](#prerequisites)
  - [Environment variables](#environment-variables)
  - [Configuration](#configuration)
    - [General Settings](#general-settings)
    - [Overlay Icon Configuration](#overlay-icon-configuration)
    - [File Configuration](#file-configuration)
    - [API Request Settings](#api-request-settings)
    - [Transcription Settings](#transcription-settings)
    - [YouTube Settings](#youtube-settings)
    - [AI Model Settings](#ai-model-settings)
    - [Image Generation Settings](#image-generation-settings)
    - [Art Downloader Settings](#art-downloader-settings)
    - [Content Documentation Settings](#content-documentation-settings)
  - [Vale](#vale)
- [Add the daily Youtube video](#add-the-daily-youtube-video)
- [Add additional Youtube video to a day](#add-additional-youtube-video-to-a-day)
- [Add today's sharing](#add-todays-sharing)
- [Merge monthly markdown files into one large README](#merge-monthly-markdown-files-into-one-large-readme)
- [Generate table of contents for markdown files](#generate-table-of-contents-for-markdown-files)
- [Using the commands utility that accepts text commands in file `commands.txt`](#using-the-commands-utility-that-accepts-text-commands-in-file-commandstxt)

<!-- tocstop -->

# HOWTO

<!-- markdownlint-disable MD033 -->

## Prerequisites

- [curl](https://curl.se/)
- [gm](http://www.graphicsmagick.org/)
- [m4](https://www.gnu.org/software/m4/m4.html)
- [stitchmd](https://github.com/abhinav/stitchmd)
- [doctoc](https://github.com/ktechhub/doctoc)
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

1. Export environment variable `DEEPINFRA_TOKEN` by adding the following line to `.bash_profile`.

   ```bash
   export DEEPINFRA_TOKEN=<api_key>
   ```

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

#### Transcription Settings

```bash
# Whether to transcribe videos
TRANSCRIBE_VIDEOS=false
# Whether to transcribe locally
TRANSCRIBE_LOCALLY=false
# Whether to use faster-whisper python library
USE_FASTER_WHISPER=true
# Whether to enable failover mode
ENABLE_FAILOVER_MODE=true

# ASR API KEY
ASR_LLM_API_KEY="$DEEPINFRA_TOKEN"
# ASR LLM base url
ASR_LLM_BASE_URL="https://api.deepinfra.com/v1"
# ASR LLM endpoint
ASR_LLM_ENDPOINT="/openai/audio/transcriptions"
# ASR LLM model
ASR_LLM_MODEL="openai/whisper-large-v3"
# ASR local model
ASR_LOCAL_MODEL="small"
# Initial prompt for whisper
ASR_INITIAL_PROMPT="In Ascension Press' Rosary in a Year podcast, Fr. Mark-Mary Ames meditates with sacred art, saint writings, and scripture. Poco a poco."
# Whether to carry initial prompt
ASR_CARRY_INITIAL_PROMPT=true
# Beam size for ASR
ASR_BEAM_SIZE=5
```

#### YouTube Settings

```bash
# Number of retries for yt-dlp
YT_DLP_RETRIES=20
# Timeout for yt-dlp (seconds)
YT_DLP_SOCKET_TIMEOUT=30
# Captions output directory
CAPTIONS_OUTPUT_DIR="captions"
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
# The meta-prompt to generate image prompt and caption
SUMMARY_IMAGE_META_PROMPT='You are an assistant that extracts visual meaning from text. Given any descriptive input, generate:
1. "image_prompt" - a detailed, visual description suitable for generating an image.
2. "caption" - a brief, expressive caption that summarizes or enhances the image concept. No colons.
Return your response as a JSON object in the format: {"caption": "This is the generated caption", "image_prompt": "This is the image prompt"}'
CAPTION_PROMPT='You are an assistant who extracts visual meaning from text related to Christian art. Given any descriptive input, generate:
1. "caption" - a brief, expressive caption that summarizes or enhances the text using any information you have concerning Christian art the text identifies.
Return your response as a JSON object in the format: {"caption": "This is the generated caption"}'
SUMMARY_ARTWORK_DETAILS_PROMPT="From the following text, extract any described artwork and return a JSON object with:
\"details\": A detailed summary including the artwork's title, artist, date, medium, style, current location of artwork (location) and subject. Fill values with empty string if not specified in the text.
\"filename\": A lowercase alphanumeric string (no hyphens or underscores), 20 characters or fewer, representing a mostly unique filename derived from the title, artist, and date.
\"caption\": A caption (in proper English), no more than 20 words, that uses title, artist, date,location, medium and subject (in that ordered priority).
If no artwork is described in the text, return an empty JSON object {}."
```

#### Image Generation Settings

```bash
# Whether to auto-generate images
AUTO_GENERATE_IMAGES=false
# Path to image generation script
IMAGE_GENERATION_SCRIPT="openaigenerateimage"
# Deepinfra image generation model
DEEPINFRA_IMAGE_GENERATION_MODEL="stabilityai/sd3.5"
# Fal.ai image generation model
FALAI_IMAGE_GENERATION_MODEL="janus"
```

#### Art Downloader Settings

```bash
# Whether to auto-download art
AUTO_DOWNLOAD_ART=false
# Art downloader directory
ART_DOWNLOADER_DIR="artdownloads"
# Whether to verify art images
VERIFY_ART_IMAGES=true
# Art verifier script
ART_VERIFIER_SCRIPT="matchimagetometadata.py"
# Art metadata prompt
ART_METADATA_PROMPT="You are an expert on Christian art.
Provided the following details about the artwork '{}'
analyze the image and generate the following detailed metadata in json format (no markdown, no nesting of attributes, all top-level):
\"title\": The title of the artwork,
\"artist\": The artist or artists,
\"medium\": oil on canvas, fresco, marble sculpture, etc.,
\"location\": where the artwork is currently located,
\"date\": the creation year and century,
\"style\": the artistic style or artistic school that influenced the art,
\"description\": Description of the artwork (including visual elements, composition, subject matter, and style).
\"image_color\": Whether the image is in Color, Grayscale, Monochrome, Duotone/Tritone, Sepia,Color-tinted grayscale, Black-and-white etc.
\"watermarked\": Whether the image is watermarked or not.
\"caption\": A caption (in proper English), no more than 20 words, that uses title, artist, date, location, medium and description (in that ordered priority).
\"analyzed\": Whether the analysis was possible or not.
\"comments:\": Your comments other than the fields above and if analysis was possible or not and why.
Do not add any extraneous information that will mangle the json object expected."
# Image content validation strictness
IMAGE_CONTENT_VALIDATION="lenient"
# Vector embeddings model api key
VECTOR_EMBEDDINGS_MODEL_API_KEY="$DEEPINFRA_TOKEN"
# Vector embeddings provider base url
VECTOR_EMBEDDINGS_BASE_URL="https://api.deepinfra.com/v1/openai"
# Vector embeddings model
VECTOR_EMBEDDINGS_MODEL="thenlper/gte-large"
# Whether to look for alternate images
FIND_ALTERNATE_IMAGES=false
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
