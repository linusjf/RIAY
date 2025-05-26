#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : saveplaylisttests
# @created     : Monday May 26, 2025 19:02:22 IST
#
# @description :
######################################################################

readonly SAVEPLAYLIST_SCRIPT="${SCRIPT_DIR}/saveplaylist"

print_header "Running saveplaylist sanity tests"

print_header "Test 44: Version flag"
run_test 44 "Should show version with --version" 0 "${SAVEPLAYLIST_SCRIPT}" --version

print_header "Test 45: Help/usage"
run_test 45 "Should show usage with no args" 2 "${SAVEPLAYLIST_SCRIPT}" || true
run_test 45 "Should show usage with -h" 0 "${SAVEPLAYLIST_SCRIPT}" -h
run_test 45 "Should show usage with --help" 0 "${SAVEPLAYLIST_SCRIPT}" --help

print_header "Test 46: Invalid inputs"
run_test 46 "Should reject missing playlist ID" 2 "${SAVEPLAYLIST_SCRIPT}" || true
run_test 46 "Should reject invalid playlist ID" 4 "${SAVEPLAYLIST_SCRIPT}" "invalid" || true
run_test 46 "Should reject non-existent playlist " 4 "${SAVEPLAYLIST_SCRIPT}" "PL4iIJvj6ypuG9v3Kg80Qt2ZUnspPHvXO" || true

print_header "Test 47: Verbose mode"
run_test 47 "Should enable verbose with -v" 0 "${SAVEPLAYLIST_SCRIPT}" -v "PLHprCs14Z-sCSlrl1ueVisUKm3lnvqC0S" || true
run_test 47 "Should enable verbose with --verbose" 0 "${SAVEPLAYLIST_SCRIPT}" --verbose "PLHprCs14Z-sCSlrl1ueVisUKm3lnvqC0S" || true
