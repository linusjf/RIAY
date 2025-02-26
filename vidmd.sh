#!/usr/bin/env bash
######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : vidmd
# @created     : Wednesday Feb 08, 2023 18:45:15 IST
#
# @description :
######################################################################
getroot() {
  hash git basename || exit
  basename "$(git rev-parse --show-toplevel)"
}

usagevidmd() {
  echo "vidmd vidid vidurl caption"
  echo "vid - video id"
  echo "vidurl - video url"
  echo "caption - video title"
  exit 1
}

usagevidmdloc() {
  echo "vidmdloc vidid vidurl caption doy"
  echo "vid - video id"
  echo "vidurl - video url"
  echo "caption - video title"
  echo "doy - day of year"
  exit 1
}

playiconurl() {
  root="$(getroot)"
  doy="$1"
  doy="$(printf "%03d" "${doy#0}")"
  month="$(mfromdoy "$doy")"
  echo "https://raw.githubusercontent.com/${GIT_USER}/${root}/main/${month}/jpgs/Day${doy}.jpg"
}

thumbnailurl() {
  hash curl || exit
  urls=("https://img.youtube.com/vi/${1}/maxresdefault.jpg"
    "https://img.youtube.com/vi/${1}/hqdefault.jpg"
    "https://img.youtube.com/vi/${1}/hq1.jpg"
    "https://img.youtube.com/vi/${1}/hq2.jpg"
    "https://img.youtube.com/vi/${1}/hq3.jpg"
    "https://img.youtube.com/vi/${1}/hq720.jpg"
    "https://img.youtube.com/vi/${1}/mqdefault.jpg"
    "https://img.youtube.com/vi/${1}/mq1.jpg"
    "https://img.youtube.com/vi/${1}/mq2.jpg"
    "https://img.youtube.com/vi/${1}/mq3.jpg"
    "https://img.youtube.com/vi/${1}/sddefault.jpg"
    "https://img.youtube.com/vi/${1}/sd1.jpg"
    "https://img.youtube.com/vi/${1}/sd2.jpg"
    "https://img.youtube.com/vi/${1}/sd3.jpg"
    "https://img.youtube.com/vi/${1}/default.jpg"
    "https://img.youtube.com/vi/${1}/0.jpg"
    "https://img.youtube.com/vi/${1}/1.jpg"
    "https://img.youtube.com/vi/${1}/2.jpg"
    "https://img.youtube.com/vi/${1}/3.jpg")
  for url in "${urls[@]}"; do
    if test 200 -eq "$(curl -o /dev/null --silent -Iw '%{http_code}' "${url}")"; then
      echo "$url"
      return 0
    fi
  done
  return 1
}

downloadthumbnail() {
  hash curl || exit
  url="$(thumbnailurl "$1")"
  if [ -z "${url}" ]; then
    return 1
  else
    curl --silent "$url" --output "$2"
    return $?
  fi
}

vidmd() {
  if test $# -lt 3; then
    usagevidmd
  fi
  vidid="$1"
  vidurl="$2"
  caption="$3"
  if imgurl="$(thumbnailurl "$vidid")"; then
    printf "[![%s](%s)](%s \"%s\")\n" "$caption" "$imgurl" "$vidurl" "$caption"
  else
    echo >&2 "Thumbnails unverifiable,invalid or absent."
    return 1
  fi
}

vidmdloc() {
  if test $# -lt 4; then
    usagevidmdloc
  fi
  vidid="$1"
  vidurl="$2"
  caption="$3"
  doy="$4"
  imgurl="$(playiconurl "${doy#0}")"
  printf "[![%s](%s)](%s \"%s\")\n" "$caption" "$imgurl" "$vidurl" "$caption"
}

isnumeric() {
  if [[ "$1" =~ ^[0-9]+$ ]]; then
    return 0
  fi
  return 1
}

mfromdoy() {
  if ! isnumeric "$1"; then
    echo 2> "$1 is not numeric"
    return 1
  fi
  ((day = 10#$1 - 1))
  hash date || exit
  date --date="jan 1 + $day days" +%B
}

datefromdoy() {
  if ! isnumeric "$1"; then
    echo 2> "$1 is not numeric"
    return 1
  fi
  ((day = 10#$1 - 1))
  hash date || exit
  date --date="jan 1 + $day days" "+%B %d,%Y"
}

monthfromnumber() {
  hash date || exit
  case $1 in
    [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
    *) exit 1 ;;
  esac
}

# Define a function to validate input
validate_input() {
  local value="$1"
  local max_length="$2"
  local error_message="$3"

  if [[ -z "$value" ]]; then
    echo "Error: $error_message cannot be empty." >&2
    return 1
  fi
  if [[ ${#value} -gt $max_length ]]; then
    echo "Error: $error_message too long. Maximum $max_length characters." >&2
    return 1
  fi
}

VIDEO_ID_LENGTH=11
# Define a function to validate the video ID
validate_vid() {
  local vid="$1"
  if [[ ! "$vid" =~ ^[a-zA-Z0-9_-]{${VIDEO_ID_LENGTH}$ ]]; then
    echo "Error: Invalid video ID '$vid'. Expected ${VIDEO_ID_LENGTH} characters." >&2
    return 1
  fi
  validate_input "$vid" ${VIDEO_ID_LENGTH} "Video ID"
}

MAX_CAPTION_LENGTH=100
# Define a function to validate the caption
validate_caption() {
  validate_input "$1" ${MAX_CAPTION_LENGTH} "Caption"
}
