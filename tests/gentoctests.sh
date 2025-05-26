#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : gentoctests
# @created     : Monday May 26, 2025 18:37:41 IST
#
# @description :
######################################################################

readonly GENTOC_SCRIPT="${SCRIPT_DIR}/gentoc"

create_test_md() {
  cat << EOF > "${TEST_MD_FILE}"
# Test Document

## Section 1
Content

## Section 2
More content
EOF
}

print_header "Running gentoc sanity tests"

print_header "Test 12: Version flag"
run_test 12 "Should show version with -v" 0 "${GENTOC_SCRIPT}" -v
run_test 12 "Should show version with --version" 0 "${GENTOC_SCRIPT}" --version

print_header "Test 13: Help/usage"
run_test 13 "Should show usage with no args" 1 "${GENTOC_SCRIPT}" || true
run_test 13 "Should show usage with -h" 0 "${GENTOC_SCRIPT}" -h
run_test 13 "Should show usage with --help" 0 "${GENTOC_SCRIPT}" --help

print_header "Test 14: Debug mode"
run_test 14 "Should enable debug with -d" 2 "${GENTOC_SCRIPT}" -d "${TEST_MD_FILE}" || true
run_test 14 "Should enable debug with --debug" 2 "${GENTOC_SCRIPT}" --debug "${TEST_MD_FILE}" || true

print_header "Test 15: Invalid inputs"
run_test 15 "Should reject missing file argument" 1 "${GENTOC_SCRIPT}" || true
run_test 15 "Should reject non-existent file" 2 "${GENTOC_SCRIPT}" nonexistent.md || true

print_header "Test 16: TOC generation"
create_test_md
run_test 16 "Should generate TOC for valid file" 0 "${GENTOC_SCRIPT}" "${TEST_MD_FILE}"
