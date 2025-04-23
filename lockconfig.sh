#!/usr/bin/env bash
if [[ -z "$SCRIPT_DIR" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/require.sh"

if ! declare -f lock_config_vars > /dev/null; then
  lock_config_vars() {
    require_commands compgen grep comm
    local config_file="$1"
    local before_vars after_vars config_vars var

    # Save current variable names before sourcing
    before_vars="$(compgen -v)"
    source "$config_file"
    after_vars="$(compgen -v)"

    # Get new variables introduced by the config
    config_vars="$(comm -13 <(echo "$before_vars" | sort) <(echo "$after_vars" | sort))"

    for var in $config_vars; do
      # Check if it's an array
      if declare -p "$var" 2> /dev/null | grep -q 'declare -a'; then
        # Lock all elements of the array
        declare -r -a "$var"
      else
        readonly "$var"
      fi
    done
  }
fi
