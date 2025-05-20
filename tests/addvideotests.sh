#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : addvideotests
# @created     : Tuesday May 20, 2025 18:54:00 IST
#
# @description :
######################################################################

readonly ADDVIDEO_SCRIPT="${SCRIPT_DIR}/addvideo"

print_header "Running addvideo sanity tests"

print_header "Test 1: Version flag"
run_test 1 "Should show version with -v" 0 "${ADDVIDEO_SCRIPT}" -v
run_test 1 "Should show version with --version" 0 "${ADDVIDEO_SCRIPT}" --version

print_header "Test 2: Help/usage"
run_test 2 "Should show usage with no args" 1 "${ADDVIDEO_SCRIPT}" || true
run_test 2 "Should show usage with -h" 0 "${ADDVIDEO_SCRIPT}" -h
run_test 2 "Should show usage with --help" 0 "${ADDVIDEO_SCRIPT}" --help

print_header "Test 3: Dry run mode"
run_test 3 "Should run dry mode with -n" 0 "${ADDVIDEO_SCRIPT}" -n "CfU7rIufywo" "Test Video" || true
run_test 3 "Should run dry mode with --dry-run" 0 "${ADDVIDEO_SCRIPT}" --dry-run "CfU7rIufywo" "Test Video" || true

print_header "Test 4: Debug mode"
run_test 4 "Should enable debug with -d" 0 "${ADDVIDEO_SCRIPT}" -d "Io1G_5I7a-0" "Test Video" || true
run_test 4 "Should enable debug with --debug" 0 "${ADDVIDEO_SCRIPT}" --debug "2-caLO3rLL8" "News Video" || true

print_header "Test 5: Invalid inputs"
run_test 5 "Should reject invalid video ID" 1 "${ADDVIDEO_SCRIPT}" "invalid" "Test" || true
run_test 5 "Should reject missing caption" 1 "${ADDVIDEO_SCRIPT}" "dQw4w9WgXcQ" || true
