#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"
# Git-related utility functions

if ! declare -f git::get_github_repo > /dev/null; then
  function git::get_github_repo() {
    require_commands git
    local git_url
    git_url=$(git remote get-url origin 2> /dev/null)

    if [[ "$git_url" == git@github.com:* ]]; then
      printf "%s" "$git_url" | sed -E 's|git@github.com:([^\.]+)(\.git)?|\1|'
    elif [[ "$git_url" == https://github.com/* ]]; then
      printf "%s" "$git_url" | sed -E 's|https://github.com/([^\.]+)(\.git)?|\1|'
    else
      die "Error: Could not determine GitHub repo from remote: $git_url"
    fi
  }
  export -f git::get_github_repo
fi

######################################################################
# Get repository root name
# Globals: None
# Arguments: None
# Outputs: Repository root name to STDOUT
# Returns: None (exits with status 1 if git command fails)
######################################################################
if ! declare -f git::getroot > /dev/null; then
  git::getroot() {
    require_commands basename
    basename "$(git::get_github_repo)"
  }
  export -f git::getroot
fi
