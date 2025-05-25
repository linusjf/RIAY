#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : imageprompt
# @created     : Wednesday May 21, 2025 09:14:41 IST
#
# @description Contains functions to extract caption and image prompt from json input.
######################################################################

set -euo pipefail
shopt -s inherit_errexit

# Source utility functions
if [[ -z "${SCRIPT_DIR:-}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
source "${SCRIPT_DIR}/lib/require.sh"

require_commands jq sed

if ! declare -f imageprompt::get_caption > /dev/null; then
  function imageprompt::get_caption() {
    json="$1"
    echo "$json" | jq -r '.caption' | sed 's/\.//g'
  }
  export -f imageprompt::get_caption
fi

if ! declare -f imageprompt::get_prompt > /dev/null; then
  function imageprompt::get_prompt() {
    json="$1"
    echo "$json" | jq -r '.image_prompt'
  }
  export -f imageprompt::get_prompt
fi
