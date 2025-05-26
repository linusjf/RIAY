#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : addsummariestodaystests
# @created     : Monday May 26, 2025 19:10:44 IST
#
# @description :
######################################################################

readonly ADDSUMMARIES_SCRIPT="${SCRIPT_DIR}/addsummariestodays"

readonly TEST_VIDEOS_FILE="$VIDEOS_FILE"

create_test_videos() {
  cat << EOF > "${TEST_VIDEOS_FILE}"
dQw4w9WgXcQ
CfU7rIufywo
Io1G_5I7a-0
EOF
}

create_test_day_file() {
  local month="$1"
  local day="$2"
  local content="$3"
  mkdir -p "$month"
  printf -v filename "Day%03d.md" "$day"
  echo "$content" > "${month}/${filename}"
}

print_header "Running addsummariestodays sanity tests"

print_header "Test 53: Version flag"
run_test 53 "Should show version with --version" 0 "${ADDSUMMARIES_SCRIPT}" --version

print_header "Test 54: No args"
run_test 54 "Should show usage with no args" 1 "${ADDSUMMARIES_SCRIPT}" || true

print_header "Test 55: Help/usage"
run_test 55 "Should show usage with -h" 0 "${ADDSUMMARIES_SCRIPT}" -h
run_test 55 "Should show usage with --help" 0 "${ADDSUMMARIES_SCRIPT}" --help

print_header "Test 56: Invalid inputs"
run_test 56 "Should reject invalid day range (non-numeric)" 1 "${ADDSUMMARIES_SCRIPT}" "one" "ten" || true
run_test 56 "Should reject invalid day range (start > end)" 2 "${ADDSUMMARIES_SCRIPT}" "10" "5" || true
run_test 56 "Should reject invalid --ai-handling value" 6 "${ADDSUMMARIES_SCRIPT}" --ai-handling=invalid 1 1 || true

print_header "Test 57: AI handling options"
create_test_videos
create_test_day_file "January" 1 "# Day 1\n### AI-Generated Summary: Test"
run_test 57 "Should skip with --ai-handling=skip" 0 "${ADDSUMMARIES_SCRIPT}" --ai-handling=skip 1 1 || true
run_test 57 "Should overwrite with --ai-handling=overwrite" 0 "${ADDSUMMARIES_SCRIPT}" --ai-handling=overwrite 1 1 || true

print_header "Test 58: Basic execution"
run_test 58 "Should run successfully with --ai-handling=prompt" 0 "${ADDSUMMARIES_SCRIPT}" 1 1 <<< "Y" || true
run_test 58 "Should run successfully with --ai-handling=prompt" 0 "${ADDSUMMARIES_SCRIPT}" 1 1 <<< "N" || true
create_test_videos
create_test_day_file "January" 1 "# Day 1"
run_test 58 "Should run successfully with --ai-handling=prompt" 0 "${ADDSUMMARIES_SCRIPT}" 1 1 || true
run_test 58 "Should run successfully with --ai-handling=overwrite" 0 "${ADDSUMMARIES_SCRIPT}" --ai-handling=overwrite 1 1 || true
