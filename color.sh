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

# --- Utility Functions ---
function out() { printf "%b\n" "$*"; }
function err() { >&2 printf "%b\n" "$*"; }
function die() {
  >&2 printf "%b\n" "$*"
  exit 1
}

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
function print_error() {
  err "${COLOR_RED}Error: ${1}${COLOR_NC}"
}

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
function print_info() {
  [[ "${verbose:=false}" == true ]] && out "${COLOR_GREEN}Info: $1${COLOR_NC}" || true
}

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
function print_warning() {
  err "${COLOR_YELLOW}Warning: $1${COLOR_NC}"
}

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
function print_debug() {
  [[ $- == *x* ]] && out "${COLOR_BLUE}Debug: $1${COLOR_NC}" || true
}

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
function print_success() {
  out "${COLOR_GREEN}Success: $1${COLOR_NC}"
}

export -f out err die print_error print_info print_warning print_debug print_success

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
