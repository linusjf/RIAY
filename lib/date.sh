#!/usr/bin/env bash
######################################################################
# Date Utility Functions
# Provides date-related functions for working with days of year
######################################################################

set -euo pipefail
shopt -s inherit_errexit
if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"
source "${SCRIPT_DIR}/lib/util.sh"
source "${SCRIPT_DIR}/lib/validators.sh"

require_commands date

#######################################
# Validate month number
# Globals: none
# Arguments:
#   $1 - Month number
# Outputs: Error to STDERR if invalid
# Returns: 0 if valid, 1 otherwise
#######################################
if ! declare -f date::validatemonth > /dev/null; then
  date::validatemonth() {
    [[ "$1" =~ ^0?[1-9]$|^1[0-2]$ ]] || {
      err "Error: Month number must be between 1 and 12"
      return 1
    }
  }
  export -f date::validatemonth
fi

######################################################################
# Validate day number for a given year
# Globals: None
# Arguments:
#   $1 - Day number
#   $2 - Year (optional, defaults to current year)
# Outputs: Error to STDERR if invalid
# Returns: 0 if valid, 1 otherwise
######################################################################
if ! declare -f date::validate_daynumber > /dev/null; then
  date::validate_daynumber() {
    validators::validate_arg_count "$#" 1 2 || {
      err "Error: One or two arguments 'doy' and optional 'year' expected"
      return 1
    }
    validators::isnumeric "$1" || {
      err "Error: Day number must be numeric"
      return 1
    }

    local year=${2:-$(date +%Y)}
    validators::isnumeric "$year" || {
      err "Error: Year must be numeric"
      return 1
    }

    local max_days
    max_days=$(date::daycount "$year")
    [[ $1 -ge 1 && $1 -le $max_days ]] || {
      err "Error: Day number must be between 1 and $max_days for year $year"
      return 1
    }
    return 0
  }
  export -f date::validate_daynumber
fi

######################################################################
# Get month name from day of year
# Globals: None
# Arguments:
#   $1 - Day of year
#   $2 - Year (optional, defaults to current year)
# Outputs: Month name to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
if ! declare -f date::mfromdoy > /dev/null; then
  date::mfromdoy() {
    validators::validate_arg_count "$#" 1 2 || die "One or two arguments 'doy' and optional 'year' expected"
    validators::isnumeric "$1" || die "$1 is not numeric"
    
    local day year max_days
    day=$((10#$1))
    year=${2:-$(date +%Y)}
    validators::isnumeric "$year" || die "$year is not numeric"
    max_days=$(date::daycount "$year")
    
    [[ $day -ge 1 && $day -le $max_days ]] || die "Day of year must be between 1 and $max_days for year $year"
    date --date="jan 1 $year + $((day - 1)) days" +%B
  }
  export -f date::mfromdoy
fi

######################################################################
# Get full date from day of year
# Globals: None
# Arguments:
#   $1 - Day of year
#   $2 - Year (optional, defaults to current year)
# Outputs: Formatted date to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
if ! declare -f date::datefromdoy > /dev/null; then
  date::datefromdoy() {
    validators::validate_arg_count "$#" 1 2 || die "One or two arguments 'doy' and optional 'year' expected"
    validators::isnumeric "$1" || die "$1 is not numeric"
    
    local day year max_days
    day=$((10#$1))
    year=${2:-$(date +%Y)}
    validators::isnumeric "$year" || die "$year is not numeric"
    max_days=$(date::daycount "$year")
    
    [[ $day -ge 1 && $day -le $max_days ]] || die "Day of year must be between 1 and $max_days for year $year"
    date --date="jan 1 $year + $((day - 1)) days" "+%B %d, %Y"
  }
  export -f date::datefromdoy
fi

######################################################################
# Get month name from month number
# Globals: None
# Arguments:
#   $1 - Month number (1-12)
# Outputs: Month name to STDOUT
# Returns: None (exits with status 1 on error)
######################################################################
if ! declare -f date::monthfromnumber > /dev/null; then
  date::monthfromnumber() {
    case $1 in
      [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
      0[1-9]) date -d "${1}/01" +%B ;;
      *) die "Invalid month number: $1" ;;
    esac
  }
  export -f date::monthfromnumber
fi

if ! declare -f date::monthnumberfrommonth > /dev/null; then
  date::monthnumberfrommonth() {
    month_name="$1"
    year="${2:-$(date +%Y)}"
    month_number=$(date -d "1 $month_name $year" +"%m")
    echo "$month_number"
  }
  export -f date::monthnumberfrommonth
fi

if ! declare -f date::isleapyear > /dev/null; then
  date::isleapyear() {
    year="${1:-$(date +%Y)}"

    ((year % 4 == 0 && year % 100 != 0)) \
      || ((year % 400 == 0))
  }
  export -f date::isleapyear
fi

if ! declare -f date::daycount > /dev/null; then
  date::daycount() {
    year="${1:-$(date +%Y)}"
    # Check if year is a leap year
    if date::isleapyear "$year"; then
      echo 366
    else
      echo 365
    fi
  }
  export -f date::daycount
fi
