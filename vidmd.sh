#!/usr/bin/env bash
######################################################################
# Video Markdown Generator
# Generates markdown for embedding YouTube videos with thumbnails
# Supports both standard YouTube embeds and custom day-of-year thumbnails
######################################################################

set -euo pipefail
shopt -s inherit_errexit

readonly VIDEO_ID_LENGTH=11
readonly MAX_CAPTION_LENGTH=100
# array of youtube thumbnail sizes in descending order. Not all may be available.
# cycle through the sizes to pick the largest
# available one.
# https://developers.google.com/youtube/v3/docs/thumbnails
readonly THUMBNAIL_SIZES=(
  "maxres"
  "standard"
  "high"
  "medium"
  "default"
)

######################################################################
# Display error message and exit with failure status
# Globals: None
# Arguments:
#   $1 - Error message
# Outputs: Error message to STDERR
# Returns: None (exits with status 1)
######################################################################
die() {
  printf "%s\n" "$1" >&2
  exit 1
}

######################################################################
# Verify required commands are available
# Globals: None
# Arguments:
#   $@ - Commands to check
# Outputs: Error message to STDERR if command missing
# Returns: None (exits with status 1 if command missing)
######################################################################
require() {
  for cmd in "$@"; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
      die "Required command '$cmd' not found"
    fi
  done
}

######################################################################
# Get repository root name
# Globals: None
# Arguments: None
# Outputs: Repository root name to STDOUT
# Returns: None (exits with status 1 if git command fails)
######################################################################
getroot() {
  require git basename
  basename "$(git rev-parse --show-toplevel)"
}

######################################################################
# Display usage information for standard video markdown
# Globals: None
# Arguments: None
# Outputs: Usage message to STDOUT
# Returns: None (exits with status 1)
######################################################################
usagevidmd() {
  cat << EOF
Usage: $0 vidid vidurl caption
  vidid   - YouTube video ID (11 characters)
  vidurl  - Full video URL
  caption - Video title (max $MAX_CAPTION_LENGTH chars)
EOF
  exit 1
}

######################################################################
# Display usage information for localized video markdown
# Globals: None
# Arguments: None
# Outputs: Usage message to STDOUT
# Returns: None (exits with status 1)
######################################################################
usagevidmdloc() {
  cat << EOF
Usage: $0 vidid vidurl caption doy
  vidid   - YouTube video ID (11 characters)
  vidurl  - Full video URL
  caption - Video title (max $MAX_CAPTION_LENGTH chars)
  doy     - Day of year (1-366)
EOF
  exit 1
}

######################################################################
# Generate play icon URL for given day of year
# Globals:
#   GITHUB_USERNAME - GitHub username
# Arguments:
#   $1 - Day of year
# Outputs: URL to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
playiconurl() {
  local root doy_raw doy_padded month
  root="$(getroot)"
  doy_raw="$1"
  doy_padded="$(printf "%03d" "${doy_raw#0}")"
  month="$(mfromdoy "${doy_padded#0}")"
  printf "https://raw.githubusercontent.com/%s/%s/refs/heads/main/%s/jpgs/Day%s.jpg\n" \
    "${GITHUB_USERNAME}" "$root" "$month" "$doy_padded"
}

thumbnailurl() {
  require curl grep
  local vid="$1"
  local api_url="https://www.googleapis.com/youtube/v3/videos?id=$vid&key=$YOUTUBE_API_KEY&part=snippet&fields=items(snippet(thumbnails(<size>(url))))"
  for size in "${THUMBNAIL_SIZES[@]}"; do
    sized_api_url="${api_url//<size>/$size}"
    if url=$(
      curl -s "$sized_api_url" | grep -oP 'https://[^"\}\]]*'
    ); then
      printf "%s\n" "$url"
      return 0
    fi
  done
  return 1
}

######################################################################
# Download thumbnail for given video ID
# Globals: None
# Arguments:
#   $1 - Video ID
#   $2 - Output filename
# Outputs: None
# Returns: 1 if download fails
######################################################################
downloadthumbnail() {
  require curl
  local url
  url="$(thumbnailurl "$1")" || return 1
  curl --silent "$url" --output "$2"
}

######################################################################
# Generate standard video markdown
# Globals: None
# Arguments:
#   $1 - Video ID
#   $2 - Video URL
#   $3 - Caption
# Outputs: Markdown to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
vidmd() {
  [[ $# -lt 3 ]] && usagevidmd
  local vidid="$1" vidurl="$2" caption="$3" imgurl
  imgurl="$(thumbnailurl "$vidid")" || die "Error: Thumbnails unverifiable or absent"
  printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
}

######################################################################
# Generate localized video markdown with day-of-year thumbnail
# Globals: None
# Arguments:
#   $1 - Video ID
#   $2 - Video URL
#   $3 - Caption
#   $4 - Day of year
# Outputs: Markdown to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
vidmdloc() {
  [[ $# -lt 4 ]] && usagevidmdloc
  local vidid="$1" vidurl="$2" caption="$3" doy="$4" imgurl
  imgurl="$(playiconurl "${doy#0}")"
  printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
}

######################################################################
# Check if input is numeric
# Globals: None
# Arguments:
#   $1 - Value to check
# Outputs: None
# Returns: 0 if numeric, 1 otherwise
######################################################################
isnumeric() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

######################################################################
# Get month name from day of year
# Globals: None
# Arguments:
#   $1 - Day of year
# Outputs: Month name to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
mfromdoy() {
  isnumeric "$1" || die "$1 is not numeric"
  require date
  local day
  # convert number to base ten
  day=$((${1}))
  [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
  date --date="jan 1 + $((day - 1)) days" +%B
}

######################################################################
# Get full date from day of year
# Globals: None
# Arguments:
#   $1 - Day of year
# Outputs: Formatted date to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
datefromdoy() {
  isnumeric "$1" || die "$1 is not numeric"
  require date
  local day
  # convert number to base ten
  day=$((${1}))
  [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
  date --date="jan 1 + $((day - 1)) days" "+%B %d,%Y"
}

######################################################################
# Get month name from month number
# Globals: None
# Arguments:
#   $1 - Month number (1-12)
# Outputs: Month name to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
monthfromnumber() {
  require date
  case $1 in
    [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
    0[1-9]) date -d "${1}/01" +%B ;;
    *) die "Invalid month number: $1" ;;
  esac
}

######################################################################
# Validate input length
# Globals: None
# Arguments:
#   $1 - Input value
#   $2 - Maximum length
#   $3 - Error message prefix
# Outputs: Error message to STDERR if validation fails
# Returns: None (exits with status 1 on error)
######################################################################
validate_input() {
  local value="$1" max_length="$2" error_message="$3"
  [[ -z "$value" ]] && die "Error: $error_message cannot be empty"
  [[ ${#value} -gt "$max_length" ]] && die "Error: $error_message too long. Maximum $max_length characters"
  return 0
}

######################################################################
# Validate video ID format
# Globals:
#   VIDEO_ID_LENGTH - Expected video ID length
# Arguments:
#   $1 - Video ID
# Outputs: Error message to STDERR if validation fails
# Returns: None (exits with status 1 on error)
######################################################################
validate_vid() {
  [[ "$1" =~ ^[a-zA-Z0-9_-]{$VIDEO_ID_LENGTH}$ ]] || die "Invalid video ID $1. Expected $VIDEO_ID_LENGTH characters"
  validate_input "$1" "$VIDEO_ID_LENGTH" "Video ID"
}

######################################################################
# Validate caption length
# Globals:
#   MAX_CAPTION_LENGTH - Maximum allowed caption length
# Arguments:
#   $1 - Caption text
# Outputs: Error message to STDERR if validation fails
# Returns: None (exits with status 1 on error)
######################################################################
validate_caption() {
  validate_input "$1" "$MAX_CAPTION_LENGTH" "Caption"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    # Example main function if needed
    :
  }
  main "$@"
fi
