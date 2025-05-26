#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : lintalltests
# @created     : Monday May 26, 2025 18:51:50 IST
#
# @description :
######################################################################

readonly LINTALL_SCRIPT="${SCRIPT_DIR}/lintall"

print_header "Running lintall sanity tests"

print_header "Test 24: Version flag"
run_test 24 "Should have a version flag" 0 "${LINTALL_SCRIPT}" --version || true

print_header "Test 25: Help/usage"
run_test 25 "Should show usage with -h" 0 "${LINTALL_SCRIPT}" -h
run_test 25 "Should show usage with --help" 0 "${LINTALL_SCRIPT}" --help

print_header "Test 26: Debug mode"
run_test 26 "Should enable debug with -d" 0 "${LINTALL_SCRIPT}" -d || true
run_test 26 "Should enable debug with --debug" 0 "${LINTALL_SCRIPT}" --debug || true

print_header "Test 27: Verbose mode"
run_test 27 "Should enable verbose with -v" 0 "${LINTALL_SCRIPT}" -v || true
run_test 27 "Should enable verbose with --verbose" 0 "${LINTALL_SCRIPT}" --verbose || true

print_header "Test 28: Basic execution"
run_test 28 "Should run successfully" 0 "${LINTALL_SCRIPT}"
