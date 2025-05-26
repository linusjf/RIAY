#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : addimgtodaytests
# @created     : Monday May 26, 2025 18:56:57 IST
#
# @description :
######################################################################

readonly ADDIMGTODAY_SCRIPT="${SCRIPT_DIR}/addimgtoday"

print_header "Running addimgtoday sanity tests"

print_header "Test 35: Version flag"
run_test 35 "Should show version with -v" 0 "${ADDIMGTODAY_SCRIPT}" -v
run_test 35 "Should show version with --version" 0 "${ADDIMGTODAY_SCRIPT}" --version

print_header "Test 36: Help/usage"
run_test 36 "Should show usage with no args" 2 "${ADDIMGTODAY_SCRIPT}" || true
run_test 36 "Should show usage with -h" 0 "${ADDIMGTODAY_SCRIPT}" -h
run_test 36 "Should show usage with --help" 0 "${ADDIMGTODAY_SCRIPT}" --help

print_header "Test 37: Invalid inputs"
run_test 37 "Should reject invalid number of arguments" 2 "${ADDIMGTODAY_SCRIPT}" "1" || true
curl https://yavuzceliker.github.io/sample-images/image-1.jpg --output example.jpg &> /dev/null || true
run_test 37 "Should reject invalid day number" 6 "${ADDIMGTODAY_SCRIPT}" "example.jpg" "Caption" "invalid" || true
run_test 37 "Should reject invalid image path" 3 "${ADDIMGTODAY_SCRIPT}" "invalid" "Caption" "1" || true

print_header "Test 38: Basic execution"
curl https://yavuzceliker.github.io/sample-images/image-1.jpg --output example.jpg &> /dev/null || true
run_test 38 "Should run successfully" 0 "${ADDIMGTODAY_SCRIPT}" "example.jpg" "Caption" "1" || true

print_header "Test 39: Debug mode"
curl https://yavuzceliker.github.io/sample-images/image-1.jpg --output example.jpg &> /dev/null || true
run_test 39 "Should enable debug with -d" 0 "${ADDIMGTODAY_SCRIPT}" -d "example.jpg" "Caption" "1" || true
curl https://yavuzceliker.github.io/sample-images/image-1.jpg --output example.jpg &> /dev/null || true
run_test 39 "Should enable debug with --debug" 0 "${ADDIMGTODAY_SCRIPT}" --debug "example.jpg" "Caption" "1" || true
