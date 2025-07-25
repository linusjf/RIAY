#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : platform
# @created     : Monday Jun 16, 2025 17:07:53 IST
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

source "${SCRIPT_DIR}/lib/require.sh"

require_commands grep

if ! declare -f platform::is_WSL > /dev/null; then
  function platform::is_WSL() {
    [[ -e /proc/version ]] && [[ -r /proc/version ]] && grep -qEi "(Microsoft|WSL)" /proc/version
  }
  export -f platform::is_WSL
fi

if ! declare -f platform::is_termux > /dev/null; then
  function platform::is_termux() {
    [[ -d /data/data/com.termux/files/usr/ ]]
  }
  export -f platform::is_termux
fi

if ! declare -f platform::is_arch_linux > /dev/null; then
  function platform::is_arch_linux() {
    [[ -f /etc/os-release ]] && grep -q '^ID=arch' /etc/os-release
  }
  export -f platform::is_arch_linux
fi

if ! declare -f platform::is_ubuntu > /dev/null; then
  function platform::is_ubuntu() {
    [[ -f /etc/os-release ]] && grep -q '^ID=ubuntu' /etc/os-release
  }
  export -f platform::is_ubuntu
fi

if ! declare -f platform::is_ubuntu_based > /dev/null; then
  function platform::is_ubuntu_based() {
    [[ -f /etc/os-release ]] && grep -qi 'ubuntu' /etc/os-release
  }
  export -f platform::is_ubuntu_based
fi
