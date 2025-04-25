#!/usr/bin/env bash

# YouTube API utilities for video information and caption processing

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR=$(dirname "$(realpath "$0")")
  else
    SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)
  fi
fi

source "${SCRIPT_DIR}/require.sh"
source "${SCRIPT_DIR}/curl.sh"

if ! declare -f get_video_title > /dev/null; then
  function get_video_title() {
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
fi

if ! declare -f download_captions > /dev/null; then
  function download_captions() {
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
fi

if ! declare -f extract_text_from_vtt > /dev/null; then
  function extract_text_from_vtt() {
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
fi

if ! declare -f check_video_exists > /dev/null; then
  # Check if YouTube video exists
  # Globals: none
  # Arguments: video_id
  # Outputs: none
  # Returns: 0 if video exists, 1 otherwise
  function check_video_exists() {
    local video_id="$1"
    local url="https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${video_id}&format=json"
    local http_status

    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    [[ "$http_status" == "200" ]]
  }
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
