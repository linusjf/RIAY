#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : genmonthtests
# @created     : Monday May 26, 2025 18:30:48 IST
#
# @description :
######################################################################

readonly GENMONTH_SCRIPT="${SCRIPT_DIR}/genmonth"

print_header "Running genmonth sanity tests"

print_header "Test 6: Version flag"
run_test 6 "Should show version with -v" 0 "${GENMONTH_SCRIPT}" -v
run_test 6 "Should show version with --version" 0 "${GENMONTH_SCRIPT}" --version

print_header "Test 7: Help/usage"
run_test 7 "Should show usage with no args" 1 "${GENMONTH_SCRIPT}" || true
run_test 7 "Should show usage with -h" 0 "${GENMONTH_SCRIPT}" -h
run_test 7 "Should show usage with --help" 0 "${GENMONTH_SCRIPT}" --help

print_header "Test 8: Dry run mode"
run_test 8 "Should run dry mode with -n" 0 "${GENMONTH_SCRIPT}" -n "$TEST_MONTH" "$TEST_YEAR"
run_test 8 "Should run dry mode with --dry-run" 0 "${GENMONTH_SCRIPT}" --dry-run "$TEST_MONTH" "$TEST_YEAR"
run_test 8 "Should run dry mode with -n" 0 "${GENMONTH_SCRIPT}" -n "$TEST_MONTH"
run_test 8 "Should run dry mode with --dry-run" 0 "${GENMONTH_SCRIPT}" --dry-run "$TEST_MONTH"

print_header "Test 9: Debug mode"
run_test 9 "Should enable debug with -d" 0 "${GENMONTH_SCRIPT}" -d "$TEST_MONTH" "$TEST_YEAR" || true
run_test 9 "Should enable debug with --debug" 0 "${GENMONTH_SCRIPT}" --debug "$TEST_MONTH" "$TEST_YEAR" || true
run_test 9 "Should enable debug with -d" 0 "${GENMONTH_SCRIPT}" -d "$TEST_MONTH" || true
run_test 9 "Should enable debug with --debug" 0 "${GENMONTH_SCRIPT}" --debug "$TEST_MONTH" || true

print_header "Test 10: Invalid inputs"
run_test 10 "Should reject invalid month (0)" 2 "${GENMONTH_SCRIPT}" 0 "$TEST_YEAR" || true
run_test 10 "Should reject invalid month (13)" 2 "${GENMONTH_SCRIPT}" 13 "$TEST_YEAR" || true
run_test 10 "Should reject invalid year (short)" 2 "${GENMONTH_SCRIPT}" "$TEST_MONTH" 23 || true
run_test 10 "Should reject non-numeric month" 2 "${GENMONTH_SCRIPT}" "Jan" "$TEST_YEAR" || true
run_test 10 "Should reject non-numeric year" 2 "${GENMONTH_SCRIPT}" "$TEST_MONTH" "TwoThousand" || true

print_header "Test 11: File generation"
run_test 11 "Should generate markdown file" 0 "${GENMONTH_SCRIPT}" "$TEST_MONTH" "$TEST_YEAR"
run_test 11 "Generated file should exist" 0 test -f "January.md"
run_test 11 "Should generate markdown file" 0 "${GENMONTH_SCRIPT}" "$TEST_MONTH"
run_test 11 "Generated file should exist" 0 test -f "January.md"
