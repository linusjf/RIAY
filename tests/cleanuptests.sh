#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : cleanuptests
# @created     : Monday May 26, 2025 18:59:27 IST
#
# @description :
######################################################################

readonly CLEANUP_SCRIPT="${SCRIPT_DIR}/cleanup"

print_header "Running cleanup sanity tests"

print_header "Test 40: Help/usage"
run_test 40 "Should show usage with no args" 0 "${CLEANUP_SCRIPT}"
run_test 40 "Should show usage with -h" 0 "${CLEANUP_SCRIPT}" -h
run_test 40 "Should show usage with --help" 0 "${CLEANUP_SCRIPT}" --help

print_header "Test 41: Basic execution"
touch testfile.tmp
run_test 41 "Should run successfully" 0 "${CLEANUP_SCRIPT}"
rm -f testfile.tmp

print_header "Test 42: Backup cleanup"
touch testfile~
touch testfile.bak
touch testfile.backup
run_test 42 "Should clean up backup files" 0 "${CLEANUP_SCRIPT}" --backups
rm -f testfile~ testfile.bak testfile.backup

print_header "Test 43: Unknown option"
run_test 43 "Should show unknown option message" 1 "${CLEANUP_SCRIPT}" --invalidoption
