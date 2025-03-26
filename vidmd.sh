#!/usr/bin/env bash
######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : vidmd.sh
# @created     : Wednesday Feb 08, 2023 18:45:15 IST
#
# @description : Utilities for video markdown generation
######################################################################

# Constants
readonly VIDEO_ID_LENGTH=11
readonly MAX_CAPTION_LENGTH=100
readonly THUMBNAIL_URLS=(
  "https://img.youtube.com/vi/vid/maxresdefault.jpg"
  "https://img.youtube.com/vi/vid/hqdefault.jpg"
  "https://img.youtube.com/vi/vid/hq1.jpg"
  "https://img.youtube.com/vi/vid/hq2.jpg"
  "https://img.youtube.com/vi/vid/hq3.jpg"
  "https://img.youtube.com/vi/vid/hq720.jpg"
  "https://img.youtube.com/vi/vid/mqdefault.jpg"
  "https://img.youtube.com/vi/vid/mq1.jpg"
  "https://img.youtube.com/vi/vid/mq2.jpg"
  "https://img.youtube.com/vi/vid/mq3.jpg"
  "https://img.youtube.com/vi/vid/sddefault.jpg"
  "https://img.youtube.com/vi/vid/sd1.jpg"
  "https://img.youtube.com/vi/vid/sd2.jpg"
  "https://img.youtube.com/vi/vid/sd3.jpg"
  "https://img.youtube.com/vi/vid/default.jpg"
  "https://img.youtube.com/vi/vid/0.jpg"
  "https://img.youtube.com/vi/vid/1.jpg"
  "https://img.youtube.com/vi/vid/2.jpg"
  "https://img.youtube.com/vi/vid/3.jpg"
)

# Error handling
die() {
  printf "%s\n" "$1" >&2
  exit 1
}

# Dependency checks
require() {
  for cmd in "$@"; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
      die "Required command '$cmd' not found"
    fi
  done
}

getroot() {
  require git basename
  basename "$(git rev-parse --show-toplevel)"
}

usagevidmd() {
  cat << EOF
Usage: $0 vidid vidurl caption
  vidid   - YouTube video ID (11 characters)
  vidurl  - Full video URL
  caption - Video title (max $MAX_CAPTION_LENGTH chars)
EOF
  exit 1
}

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

playiconurl() {
  local root doy_raw doy_padded month
  root="$(getroot)"
  doy_raw="$1"
  doy_padded="$(printf "%03d" "${doy_raw#0}")"
  month="$(mfromdoy "$doy_padded")"
  echo "https://raw.githubusercontent.com/${GIT_USER}/${root}/refs/heads/main/${month}/jpgs/Day${doy_padded}.jpg"
}

thumbnailurl() {
  require curl
  local vid="$1" url
  for url in "${THUMBNAIL_URLS[@]/vid/$vid}"; do
    if curl --silent --head --fail "$url" > /dev/null; then
      echo "$url"
      return 0
    fi
  done
  return 1
}

downloadthumbnail() {
  require curl
  local url
  url="$(thumbnailurl "$1")" || return 1
  curl --silent "$url" --output "$2"
}

vidmd() {
  [[ $# -lt 3 ]] && usagevidmd
  local vidid="$1" vidurl="$2" caption="$3" imgurl
  imgurl="$(thumbnailurl "$vidid")" || die "Error: Thumbnails unverifiable or absent"
  printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
}

vidmdloc() {
  [[ $# -lt 4 ]] && usagevidmdloc
  local vidid="$1" vidurl="$2" caption="$3" doy="$4" imgurl
  imgurl="$(playiconurl "${doy#0}")"
  printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
}

isnumeric() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

mfromdoy() {
  isnumeric "$1" || die "$1 is not numeric"
  require date
  local day=$((10#$1))
  [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
  date --date="jan 1 + $((day - 1)) days" +%B
}

datefromdoy() {
  isnumeric "$1" || die "$1 is not numeric"
  require date
  local day=$((10#$1))
  [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
  date --date="jan 1 + $((day - 1)) days" "+%B %d,%Y"
}

monthfromnumber() {
  require date
  case $1 in
    [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
    *) die "Invalid month number: $1" ;;
  esac
}

validate_input() {
  local value="$1" max_length="$2" error_message="$3"
  [[ -z "$value" ]] && die "Error: $error_message cannot be empty"
  [[ ${#value} -gt "$max_length" ]] && die "Error: $error_message too long. Maximum $max_length characters"
  return 0
}

validate_vid() {
  [[ "$1" =~ ^[a-zA-Z0-9_-]{$VIDEO_ID_LENGTH}$ ]] || die "Invalid video ID $1. Expected $VIDEO_ID_LENGTH characters"
  validate_input "$1" "$VIDEO_ID_LENGTH" "Video ID"
}

validate_caption() {
  validate_input "$1" "$MAX_CAPTION_LENGTH" "Caption"
}
