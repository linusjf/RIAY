#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : spinner
# @created     : Sunday Aug 03, 2025 18:03:41 IST
#
# @description :
######################################################################

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

if ! declare -f spinner::start_spinner > /dev/null; then
  function spinner::start_spinner() {
    local message="${1:-Working}"
    local time_in_seconds="${2:-0.1}"
    (
      local i=0
      local sp=$'|/-\\'
      while true; do
        printf "\r%s... %s" "$message" "${sp:i++%${#sp}:1}" >&2
        sleep "$time_in_seconds"
      done
    ) &
    export spinner_pid=$!
  }
  export -f spinner::start_spinner
fi

if ! declare -f spinner::stop_spinner > /dev/null; then
  function spinner::stop_spinner() {
    local pid="$1"
    kill "$pid" &> /dev/null
    wait "$pid" 2> /dev/null || true
    printf "\r%-40s\r" "" >&2 # Clear spinner line
  }
  export -f spinner::stop_spinner
fi
