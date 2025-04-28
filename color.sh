#!/usr/bin/env bash

# @file color.sh
# @brief Provides color utilities for terminal output
# @description Contains functions for colored output and constants for common colors.
# Colors are automatically disabled when output is not a terminal or when NO_COLOR is set.
# shellcheck disable=SC2034

# --- Color Constants ---
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]] && [[ "${TERM:-}" != "dumb" ]]; then
  readonly COLOR_RED='\x1b[0;31m'
  readonly COLOR_GREEN='\033[0;32m'
  readonly COLOR_YELLOW='\033[0;33m'
  readonly COLOR_BLUE='\033[0;34m'
  readonly COLOR_MAGENTA='\033[0;35m'
  readonly COLOR_CYAN='\033[0;36m'
  readonly COLOR_NC='\033[0m' # No Color
else
  readonly COLOR_RED=''
  readonly COLOR_GREEN=''
  readonly COLOR_YELLOW=''
  readonly COLOR_BLUE=''
  readonly COLOR_MAGENTA=''
  readonly COLOR_CYAN=''
  readonly COLOR_NC=''
fi

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
# Source util.sh if available
if [[ -f "${SCRIPT_DIR}/util.sh" ]]; then
  source "${SCRIPT_DIR}/util.sh"
fi

#######################################
# Print error message to STDERR
# Globals:
#   COLOR_RED
#   COLOR_NC
# Arguments:
#   $1 - Error message
# Outputs:
#   Writes colored error message to STDERR
#######################################
if ! declare -f print_error > /dev/null; then
  function print_error() {
    err "${COLOR_RED}Error: ${1}${COLOR_NC}"
  }
  export -f print_error
fi

#######################################
# Print info message to STDOUT if verbose
# Globals:
#   COLOR_GREEN
#   COLOR_NC
#   verbose
# Arguments:
#   $1 - Info message
# Outputs:
#   Writes colored info message to STDOUT if verbose enabled
#######################################
if ! declare -f print_info > /dev/null; then
  function print_info() {
    [[ "${verbose:=false}" == true ]] && out "${COLOR_GREEN}Info: $1${COLOR_NC}" || true
  }
  export -f print_info
fi

#######################################
# Print warning message to STDERR
# Globals:
#   COLOR_YELLOW
#   COLOR_NC
# Arguments:
#   $1 - Warning message
# Outputs:
#   Writes colored warning message to STDERR
#######################################
if ! declare -f print_warning > /dev/null; then
  function print_warning() {
    err "${COLOR_YELLOW}Warning: $1${COLOR_NC}"
  }
  export -f print_warning
fi

#######################################
# Print debug message to STDOUT if debug
# Globals:
#   COLOR_BLUE
#   COLOR_NC
#   debug
# Arguments:
#   $1 - Debug message
# Outputs:
#   Writes colored debug message to STDOUT if debug enabled
#######################################
if ! declare -f print_debug > /dev/null; then
  function print_debug() {
    [[ $- == *x* ]] && out "${COLOR_BLUE}Debug: $1${COLOR_NC}" || true
  }
  export -f print_debug
fi

#######################################
# Print success message to STDOUT
# Globals:
#   COLOR_GREEN
#   COLOR_NC
# Arguments:
#   $1 - Success message
# Outputs:
#   Writes colored success message to STDOUT
#######################################
if ! declare -f print_success > /dev/null; then
  function print_success() {
    out "${COLOR_GREEN}Success: $1${COLOR_NC}"
  }
  export -f print_success
fi

export COLOR_RED COLOR_GREEN COLOR_YELLOW COLOR_BLUE COLOR_MAGENTA COLOR_CYAN COLOR_NC

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  debug=true
  verbose=true
  printf "${COLOR_RED}%s${COLOR_NC}\n" "red"
  printf "${COLOR_GREEN}%s${COLOR_NC}\n" "green"
  printf "${COLOR_YELLOW}%s${COLOR_NC}\n" "yellow"
  printf "${COLOR_BLUE}%s${COLOR_NC}\n" "blue"
  printf "${COLOR_MAGENTA}%s${COLOR_NC}\n" "magenta"
  printf "${COLOR_CYAN}%s${COLOR_NC}\n" "cyan"
  print_success "Success"
  print_debug "Debug"
  print_warning "Warning"
  print_info "Info"
  err "Error"
  out "Print out"
  die "Ending ..."
fi
