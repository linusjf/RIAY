#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : addvideotodaytests
# @created     : Monday May 26, 2025 18:54:15 IST
#
# @description :
######################################################################

readonly ADDVIDEOTODAY_SCRIPT="${SCRIPT_DIR}/addvideotoday"

print_header "Running addvideotoday sanity tests"

print_header "Test 29: Version flag"
run_test 29 "Should show version with -v" 0 "${ADDVIDEOTODAY_SCRIPT}" -v
run_test 29 "Should show version with --version" 0 "${ADDVIDEOTODAY_SCRIPT}" --version

print_header "Test 30: Help/usage"
run_test 30 "Should show usage with no args" 1 "${ADDVIDEOTODAY_SCRIPT}" || true
run_test 30 "Should show usage with -h" 0 "${ADDVIDEOTODAY_SCRIPT}" -h
run_test 30 "Should show usage with --help" 0 "${ADDVIDEOTODAY_SCRIPT}" --help

print_header "Test 31: Invalid inputs"
run_test 31 "Should reject invalid number of arguments" 1 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" || true
run_test 31 "Should reject invalid video ID" 13 "${ADDVIDEOTODAY_SCRIPT}" "invalid" "1" || true
run_test 31 "Should reject invalid day number (invalid)" 2 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "invalid" || true
run_test 31 "Should reject invalid day number (negative)" 2 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "-1" || true
run_test 31 "Should reject invalid day number (zero)" 2 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "0" || true
run_test 31 "Should reject invalid day number (too large)" 2 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "367" || true
#shellcheck disable=SC2153
if ! date::isleapyear "$YEAR"; then
  run_test 31 "Should reject day 366 in non-leap year" 2 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "366" || true
fi

print_header "Test 32: Missing markdown file"
rm January/Day001.md
run_test 32 "Should fail due to missing markdown file" 6 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "001" || true

print_header "Test 33: Video does not exist"
run_test 33 "Should fail due to video not existing" 7 "${ADDVIDEOTODAY_SCRIPT}" "xxxxxxxxxxx" "2" || true

print_header "Test 34: Basic execution"
run_test 34 "Should run successfully" 0 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "1" || true
if date::isleapyear "$YEAR"; then
  touch December/Day366.md
  run_test 34 "Should accept day 366 in leap year" 0 "${ADDVIDEOTODAY_SCRIPT}" "dQw4w9WgXcQ" "366" || true
fi
