#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : stitchtests
# @created     : Monday May 26, 2025 18:44:52 IST
#
# @description :
######################################################################

readonly STITCH_SCRIPT="${SCRIPT_DIR}/stitch"
readonly TEST_STITCH_FILE="test_stitch.md"
readonly TEST_STITCH_CONTENT="stitch.md"

create_test_stitch() {
  cat << EOF > "${TEST_STITCH_FILE}"
# Test Stitch Document

## Introduction
Test content

## Features
- Feature 1
- Feature 2
EOF
}

create_real_stitch() {
  cat << EOF > "${TEST_STITCH_CONTENT}"
# README

- [RIAY](start.md)
- [January](January.md)
- [February](February.md)
- [March](March.md)
- [April](April.md)
- [May](May.md)
- [June](June.md)
- [July](July.md)
- [August](August.md)
- [September](September.md)
- [October](October.md)
- [November](November.md)
- [December](December.md)
- [HOWTO](HOWTO.md)
- [SCRIPTS](SCRIPTS.md)
EOF
}

print_header "Running stitch sanity tests"

print_header "Test 17: Version flag"
run_test 17 "Should show version with -v" 0 "${STITCH_SCRIPT}" -v
run_test 17 "Should show version with --version" 0 "${STITCH_SCRIPT}" --version

print_header "Test 18: Help/usage"
run_test 18 "Should show usage with no args" 0 "${STITCH_SCRIPT}"
run_test 18 "Should show usage with -h" 0 "${STITCH_SCRIPT}" -h
run_test 18 "Should show usage with --help" 0 "${STITCH_SCRIPT}" --help

print_header "Test 19: Debug mode"
run_test 19 "Should enable debug with -d" 0 "${STITCH_SCRIPT}" -d || true
run_test 19 "Should enable debug with --debug" 0 "${STITCH_SCRIPT}" --debug || true

print_header "Test 20: Input validation"
run_test 20 "Should pass with no parameters" 0 "${STITCH_SCRIPT}"

print_header "Test 21: Basic file generation"
create_test_stitch
mv "${TEST_STITCH_FILE}" stitch.md
run_test 21 "Should not generate README.md with wrong file format" 3 "${STITCH_SCRIPT}" || true

print_header "Test 22: Real-world file generation"
create_real_stitch
run_test 22 "Should generate README from real stitch.md" 0 "${STITCH_SCRIPT}"

print_header "Test 23: Missing stitch.md"
rm -f stitch.md
run_test 23 "Should fail when stitch.md is missing" 1 "${STITCH_SCRIPT}" || true
