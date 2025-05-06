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
# Source utility functions
if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
source "${SCRIPT_DIR}/lib/require.sh"
source "${SCRIPT_DIR}/lib/util.sh"
source "${SCRIPT_DIR}/lib/date.sh"
source "${SCRIPT_DIR}/lib/git.sh"
require_commands tr date cat curl gm mv file grep mktemp exiftool dirname rm

if ! declare -f vidmd::usagevidmd > /dev/null; then
  ######################################################################
  # Display usage information for standard video markdown
  # Globals: None
  # Arguments: None
  # Outputs: Usage message to STDOUT
  # Returns: None (exits with status 1)
  ######################################################################
  vidmd::usagevidmd() {
    cat << EOF
Usage: $0 vidid vidurl caption
    vidid   - YouTube video ID (11 characters)
    vidurl  - Full video URL
    caption - Video title (max $MAX_CAPTION_LENGTH chars)
EOF
    exit 1
  }
  export -f vidmd::usagevidmd
fi

if ! declare -f vidmd::usagevidmdloc > /dev/null; then
  ######################################################################
  # Display usage information for localized video markdown
  # Globals: None
  # Arguments: None
  # Outputs: Usage message to STDOUT
  # Returns: None (exits with status 1)
  ######################################################################
  vidmd::usagevidmdloc() {
    cat << EOF
Usage: $0 vidid vidurl caption doy
    vidid   - YouTube video ID (11 characters)
    vidurl  - Full video URL
    caption - Video title (max $MAX_CAPTION_LENGTH chars)
    doy     - Day of year (1-366)
EOF
    exit 1
  }
  export -f vidmd::usagevidmdloc
fi

if ! declare -f vidmd::usagegenvidthmd > /dev/null; then
  function vidmd::usagegenvidthmd() {
    cat << EOF
Usage: $0 vid vidurl caption [doy]
Arguments:
  vid      - YouTube video ID
  vidurl   - YouTube video URL
  caption  - Video title
  doy      - (Optional) Day of the year (numeric)
EOF
    exit 1
  }
  export -f vidmd::usagegenvidthmd

fi

if ! declare -f vidmd::usageoverlayimg > /dev/null; then
  vidmd::usageoverlayimg() {
    cat << EOF
Usage: ${0##*/} [OPTIONS] vid output
Options:
  -d, --debug    Enable debug output (set -x)

Arguments:
  vid    - YouTube video ID
  output - Path to output JPEG file
EOF
    exit 1
  }
  export -f vidmd::usageoverlayimg
fi

if ! declare -f vidmd::playiconurl > /dev/null; then
  ######################################################################
  # Generate play icon URL for given day of year
  # Globals:
  #   GITHUB_USERNAME - GitHub username
  # Arguments:
  #   $1 - Day of year
  # Outputs: URL to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  vidmd::playiconurl() {
    local root doy_raw doy_padded month
    root="$(git::getroot)"
    doy_raw="$1"
    doy_padded="$(printf "%03d" "${doy_raw#0}")"
    month="$(date::mfromdoy "${doy_padded#0}")"
    printf "https://raw.githubusercontent.com/%s/%s/refs/heads/main/%s/jpgs/Day%s.jpg\n" \
      "${GITHUB_USERNAME}" "$root" "$month" "$doy_padded"
  }
  export -f vidmd::playiconurl
fi

if ! declare -f vidmd::downloadthumbnail > /dev/null; then
  ######################################################################
  # Download thumbnail for given video ID
  # Globals: None
  # Arguments:
  #   $1 - Video ID
  #   $2 - Output filename
  # Outputs: None
  # Returns: 1 if download fails
  ######################################################################
  vidmd::downloadthumbnail() {
    local url
    url="$(youtube::thumbnailurl "$1")" || return 1
    curl --silent "$url" --output "$2"
  }
  export -f vidmd::downloadthumbnail
fi

if ! declare -f vidmd::vidmd > /dev/null; then
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
  vidmd::vidmd() {
    [[ $# -lt 3 ]] && usagevidmd
    local vidid="$1" vidurl="$2" caption="$3" imgurl
    imgurl="$(youtube::thumbnailurl "$vidid")" || die "Error: Thumbnails unverifiable or absent"
    printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
  }
  export -f vidmd::vidmd
fi

if ! declare -f vidmd::vidmdloc > /dev/null; then
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
  vidmd::vidmdloc() {
    [[ $# -lt 4 ]] && usagevidmdloc
    local vidid="$1" vidurl="$2" caption="$3" doy="$4" imgurl
    imgurl="$(vidmd::playiconurl "${doy#0}")"
    printf '[![%s](%s)](%s "%s")\n' "$caption" "$imgurl" "$vidurl" "$caption"
  }
  export -f vidmd::vidmdloc
fi

if ! declare -f vidmd::validate_input > /dev/null; then
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
  vidmd::validate_input() {
    local value="$1" max_length="$2" error_message="$3"
    [[ -z "$value" ]] && die "Error: $error_message cannot be empty"
    [[ ${#value} -gt "$max_length" ]] && die "Error: $error_message too long. Maximum $max_length characters"
    return 0
  }
  export -f vidmd::validate_input
fi

if ! declare -f vidmd::validate_vid > /dev/null; then
  ######################################################################
  # Validate video ID format
  # Globals:
  #   VIDEO_ID_LENGTH - Expected video ID length
  # Arguments:
  #   $1 - Video ID
  # Outputs: Error message to STDERR if validation fails
  # Returns: None (exits with status 1 on error)
  ######################################################################
  vidmd::validate_vid() {
    [[ "$1" =~ ^[a-zA-Z0-9_-]{$VIDEO_ID_LENGTH}$ ]] || die "Invalid video ID $1. Expected $VIDEO_ID_LENGTH characters"
    vidmd::validate_input "$1" "$VIDEO_ID_LENGTH" "Video ID"
  }
  export -f vidmd::validate_vid
fi

if ! declare -f vidmd::validate_caption > /dev/null; then
  ######################################################################
  # Validate caption length
  # Globals:
  #   MAX_CAPTION_LENGTH - Maximum allowed caption length
  # Arguments:
  #   $1 - Caption text
  # Outputs: Error message to STDERR if validation fails
  # Returns: None (exits with status 1 on error)
  ######################################################################
  vidmd::validate_caption() {
    vidmd::validate_input "$1" "$MAX_CAPTION_LENGTH" "Caption"
  }
  export -f vidmd::validate_caption
fi

if ! declare -f vidmd::genvidthmd > /dev/null; then
  function vidmd::genvidthmd() {
    # Validate arguments
    if [[ $# -lt 3 ]]; then
      vidmd::usagegenvidthmd
    fi
    local vid="$1"
    local vidurl="$2"
    local caption="$3"
    local doy="${4:-}"

    # Validate video URL format
    if [[ ! "$vidurl" =~ ^https?:// ]]; then
      die "Error: Invalid video URL format"
    fi

    # Validate day of year if provided
    if [[ -n "$doy" ]]; then
      if ! date::isnumeric "$doy"; then
        die "Error: 'doy' must be a numeric value"
      fi
      vidmd::vidmdloc "$vid" "$vidurl" "$caption" "$doy"
    else
      vidmd::vidmd "$vid" "$vidurl" "$caption"
    fi
  }
  export -f vidmd::genvidthmd
fi

######################################################################
# Check if file already has play icon comment
######################################################################
if ! declare -f vidmd::has_play_icon > /dev/null; then
  vidmd::has_play_icon() {
    exiftool -Comment "$1" 2> /dev/null | grep -q "${ICON_COMMENT}"
  }
  export -f vidmd::has_play_icon
fi

######################################################################
# Verify file is a valid JPEG
######################################################################
if ! declare -f vidmd::is_jpeg_file > /dev/null; then
  vidmd::is_jpeg_file() {
    file "$1" | grep -q 'JPEG'
  }
  export -f vidmd::is_jpeg_file
fi

######################################################################
######################################################################
if ! declare -f vidmd::is_jpeg_extension > /dev/null; then
  vidmd::is_jpeg_extension() {
    local ext="${1##*.}"
    local ext_lower
    ext_lower=$(echo "${ext}" | tr '[:upper:]' '[:lower:]')
    [[ "${ext_lower}" == "jpg" || "${ext_lower}" == "jpeg" ]]
  }
  export -f vidmd::is_jpeg_extension
fi

if ! declare -f vidmd::overlayicon > /dev/null; then
  vidmd::overlayicon() {

    # Validate arguments
    if [[ $# -ne 1 ]]; then
      die "Missing file argument"
    fi

    local file_path="$1"

    # Check file exists
    if [[ ! -f "${file_path}" ]]; then
      die "File '${file_path}' not found"
    fi

    # Check file type
    if ! vidmd::is_jpeg_file "${file_path}"; then
      die "'${file_path}' is not a valid JPEG file"
    fi

    # Check if already processed
    if vidmd::has_play_icon "${file_path}"; then
      echo "File '${file_path}' already has play icon overlay"
      return 0
    fi

    # Check overlay icon exists
    if [[ ! -f "${ICON_FILE}" ]]; then
      die "Overlay icon '${ICON_FILE}' not found"
    fi

    # Create temporary file
    local tmp_file
    tmp_file="$(mktemp)" || die "Failed to create temporary file"

    # Apply overlay
    if ! gm composite -gravity center -geometry "${ICON_SIZE}${ICON_OFFSET}" \
      "${ICON_FILE}" "${file_path}" "${tmp_file}"; then
      rm -f "${tmp_file}"
      die "Failed to overlay icon onto '${file_path}'"
    fi

    # Replace original file
    if ! mv "${tmp_file}" "${file_path}"; then
      rm -f "${tmp_file}"
      die "Failed to replace original file with overlaid image"
    fi

    # Add exif data to file
    if ! exiftool -overwrite_original -Comment="${ICON_COMMENT}" "${file_path}" &> /dev/null; then
      err "Failed to add comment in exif data to ${file_path}"
    fi
  }
  export -f vidmd::overlayicon
fi

if ! declare -f vidmd::overlayimg > /dev/null; then
  vidmd::overlayimg() {

    # Validate arguments
    if [[ $# -ne 2 ]]; then
      vidmd::usageoverlayimg
    fi

    local vid="$1"
    local output="$2"
    # Validate output path
    if [[ -d "${output}" ]]; then
      die "Output path '${output}' is a directory"
    fi

    if [[ ! -d "$(dirname "${output}")" ]]; then
      die "Parent directory for output path does not exist"
    fi

    # Validate file extension
    if ! vidmd::is_jpeg_extension "${output}"; then
      die "Output file must have a '.jpg' or '.jpeg' extension"
    fi

    # Download thumbnail
    if ! vidmd::downloadthumbnail "${vid}" "${output}"; then
      die "Failed to download thumbnail for video ID '${vid}'"
    fi

    # Overlay icon
    if ! vidmd::overlayicon "${output}"; then
      die "Failed to overlay icon on '${output}'"
    fi

    exit 0
  }
  export -f vidmd::overlayimg
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    # Example main function if needed
    :
  }
  main "$@"
fi
