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

source "${SCRIPT_DIR}/lib/require.sh"
source "${SCRIPT_DIR}/lib/curl.sh"
source "${SCRIPT_DIR}/lib/validators.sh"

require_commands curl grep jq yt-dlp sed mkdir
require_vars YOUTUBE_API_KEY

: "${YT_DLP_RETRIES:=10}"
: "${YT_DLP_SOCKET_TIMEOUT:=30}"
: "${YT_DLP_CONCURRENT_FRAGMENTS:=5}"

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
    local video_id="$1"
    local response
    response="$(curl::request "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${video_id}&key=${YOUTUBE_API_KEY}")"
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

if ! declare -f youtube::get_subtitles_table > /dev/null; then
  function youtube::get_subtitles_table() {
    local video_id="$1"
    yt-dlp --print subtitles_table --list-subs "$video_id" | sed '${/^NA$/d;}'
  }
  export -f youtube::get_subtitles_table
fi

if ! declare -f youtube::get_caption_languages > /dev/null; then
  function youtube::get_caption_languages() {
    local video_id="$1"
    yt-dlp --dump-json --skip-download "https://www.youtube.com/watch?v=${video_id}" 2> /dev/null \
      | jq -r '[.subtitles, .automatic_captions] | map(keys) | add | unique | .[]'
  }
  export -f youtube::get_caption_languages
fi

if ! declare -f youtube::has_captions_in_language > /dev/null; then
  function youtube::has_captions_in_language() {
    local video_id="$1"
    local language="$2"
    readarray -t languages < <(yt-dlp --dump-json --skip-download "https://www.youtube.com/watch?v=${video_id}" 2> /dev/null \
      | jq -r "[.subtitles, .automatic_captions] | map(keys) | add | unique | .[] | select(test(\"^${language}\"))")
    [[ ${#languages[@]} -gt 0 ]]
  }
  export -f youtube::has_captions_in_language
fi

if ! declare -f youtube::construct_file_name > /dev/null; then
  function youtube::construct_file_name() {
    local video_id="$1"
    local language="$2"
    local ext="$3"
    printf "%s.%s.%s\n" "$video_id" "$language" "$ext"
  }
fi

if ! declare -f youtube::download_captions > /dev/null; then
  function youtube::download_captions() {
    local video_id="$1"
    local prefix="$2"
    local output_dir="${3:-.}"
    local language="${4:-en}"
    local ext="${5:-vtt}"

    local output_file="${output_dir}/${prefix}$(youtube::construct_file_name "$video_id" "$language" "$ext")"
    if ! validators::dir_exists "$output_dir" && ! mkdir -p "$output_dir"; then
      return
    fi
    validators::dir_writable "$output_dir" || return
    rm -f -- "${output_dir}/${prefix}${video_id}.*"
    yt-dlp \
      --verbose \
      --socket-timeout "$YT_DLP_SOCKET_TIMEOUT" \
      --write-auto-sub \
      --sub-lang "$language" \
      --skip-download \
      --sub-format "$ext" \
      --retries "$YT_DLP_RETRIES" \
      --retry-sleep exp=1:300:2 \
      --user-agent "com.google.android.youtube/17.31.35 (Linux; U; Android 11)" \
      -o "${output_file%%.*}" \
      "https://www.youtube.com/watch?v=${video_id}" > /dev/null 2>&1
    echo "$output_file"
  }
  export -f youtube::download_captions
fi

if ! declare -f youtube::extract_text_from_vtt > /dev/null; then
  function youtube::extract_text_from_vtt() {
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

if ! declare -f youtube::has_audio_format > /dev/null; then
  # Check if YouTube video has a certain audio format
  # Globals: none
  # Arguments: video_id
  #            audio_format
  # Outputs: none
  # Returns: 0 if audio format exists, 1 otherwise
  youtube::has_audio_format() {
    local video_id="$1"
    local format="$2"

    yt-dlp -F "https://www.youtube.com/watch?v=$video_id" 2> /dev/null \
      | grep -E "audio only.*$format" > /dev/null
  }
  export -f youtube::has_audio_format
fi

if ! declare -f youtube::bestaudio_filename > /dev/null; then
  youtube::bestaudio_filename() {
    local video_id="$1"
    local filename_format="${2:-"%(id)s.%(ext)s"}"
    yt-dlp --get-filename -f "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio" -o "$filename_format" "https://www.youtube.com/watch?v=$video_id" 2> /dev/null
  }
  export -f youtube::bestaudio_filename
fi

if ! declare -f youtube::download_bestaudio > /dev/null; then
  youtube::download_bestaudio() {
    local video_id="$1"
    local file_name="${2:-"%(id)s.%(ext)s"}"
    if [[ "$file_name" == %* ]]; then
      file_name="$(youtube::bestaudio_filename "$video_id" "$file_name")"
    fi
    rm -f "$file_name" \
      && yt-dlp -f "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio" \
        --retries "$YT_DLP_RETRIES" \
        --fragment-retries "$YT_DLP_RETRIES" \
        --socket-timeout "$YT_DLP_SOCKET_TIMEOUT" \
        --concurrent-fragments "$YT_DLP_CONCURRENT_FRAGMENTS" \
        --no-part \
        --retry-sleep exp=1:300:2 \
        --user-agent "com.google.android.youtube/17.31.35 (Linux; U; Android 11)" \
        -o "${file_name}" \
        "https://www.youtube.com/watch?v=${video_id}" &> /dev/null
  }
  export -f youtube::download_bestaudio
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
