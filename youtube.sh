#!/usr/bin/env bash

# YouTube API utilities for video information and caption processing

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    readonly SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    readonly SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/require.sh"
source "${SCRIPT_DIR}/curl.sh"

if ! declare -p youtube__THUMBNAIL_SIZES &> /dev/null; then
  # array of youtube thumbnail sizes in descending order. Not all may be available.
  # cycle through the sizes to pick the largest
  # available one.
  # https://developers.google.com/youtube/v3/docs/thumbnails
  readonly youtube__THUMBNAIL_SIZES=(
    "maxres"
    "standard"
    "high"
    "medium"
    "default"
  )
fi

if ! declare -f youtube::thumbnailurl > /dev/null; then
  function youtube::thumbnailurl() {
    require_commands curl grep
    local vid="$1"
    local api_url="https://www.googleapis.com/youtube/v3/videos?id=$vid&key=$YOUTUBE_API_KEY&part=snippet&fields=items(snippet(thumbnails(<size>(url))))"
    for size in "${youtube__THUMBNAIL_SIZES[@]}"; do
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
  export -f youtube::thumbnailurl
fi

if ! declare -f youtube::get_video_title > /dev/null; then
  function youtube::get_video_title() {
    require_commands jq
    require_vars YOUTUBE_API_KEY

    local video_id="$1"
    local response
    response="$(safe_curl_request "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${video_id}&key=${YOUTUBE_API_KEY}")"
    local video_count
    video_count=$(echo "$response" | jq '.items | length')

    if [[ "$video_count" -eq 0 ]]; then
      err "Video ${video_id} does NOT exist or is private/unavailable."
      return 1
    fi
    echo "$response" | jq -r '.items[0].snippet.title'
  }
  export -f youtube::get_video_title
fi

if ! declare -f youtube::download_captions > /dev/null; then
  function youtube::download_captions() {
    require_commands yt-dlp

    local video_id="$1"
    local prefix="$2"
    rm -f -- "${prefix}${video_id}.*"
    yt-dlp \
      --write-auto-sub \
      --sub-lang "en" \
      --skip-download \
      --sub-format "vtt" \
      -o "${prefix}${video_id}.%(ext)s" \
      "https://www.youtube.com/watch?v=${video_id}" > /dev/null 2>&1
  }
  export -f youtube::download_captions
fi

if ! declare -f youtube::extract_text_from_vtt > /dev/null; then
  function youtube::extract_text_from_vtt() {
    require_commands jq grep sed

    local vtt_file="$1"
    local res
    res="$(grep -vE '^[0-9]+$|^[0-9]{2}:' -- "$vtt_file" \
      | sed -e '/^WEBVTT/d' \
        -e '/^Kind/d' \
        -e '/^Language/d' \
        -e 's/\[Music\]//g' \
        -e '/^[[:space:]]*$/d' \
        -e 's/<[^>]*>//g' \
      | tr '\n' ' ' \
      | jq -Rs .)"
    res="${res:1:-1}"
    echo -n "$res"
  }
  export -f youtube::extract_text_from_vtt
fi

if ! declare -f youtube::check_video_exists > /dev/null; then
  # Check if YouTube video exists
  # Globals: none
  # Arguments: video_id
  # Outputs: none
  # Returns: 0 if video exists, 1 otherwise
  function youtube::check_video_exists() {
    local video_id="$1"
    local url="https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${video_id}&format=json"
    local http_status

    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    [[ "$http_status" == "200" ]]
  }
  export -f youtube::check_video_exists
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
