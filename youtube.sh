#!/usr/bin/env bash

# Source require.sh for dependency checking
source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/require.sh"

if ! declare -f get_video_title > /dev/null; then
  function get_video_title() {
    require_commands jq
    require_vars YOUTUBE_API_KEY

    local video_id="$1"
    response="$(safe_curl_request "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${video_id}&key=${YOUTUBE_API_KEY}")"
    video_count=$(echo "$response" | jq '.items | length')
    if [ "$video_count" -eq 0 ]; then
      echo "Video ${video_id} does NOT exist or is private/unavailable." >&2
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
    yt-dlp --write-auto-sub --sub-lang "en" --skip-download --sub-format "vtt" \
      -o "${prefix}${video_id}.%(ext)s" "https://www.youtube.com/watch?v=${video_id}" > /dev/null 2>&1
  }
fi

if ! declare -f extract_text_from_vtt > /dev/null; then
  function extract_text_from_vtt() {
    require_commands jq grep sed

    local vtt_file="$1"
    local res="$(grep -vE '^[0-9]+$|^[0-9]{2}:' -- "$vtt_file" \
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
