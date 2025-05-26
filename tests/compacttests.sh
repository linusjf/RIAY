#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : compacttests
# @created     : Monday May 26, 2025 19:05:19 IST
#
# @description :
######################################################################

readonly COMPACT_SCRIPT="${SCRIPT_DIR}/compact"

readonly TEST_COMPACT_FILE="$COMPACT_FILE"
readonly TEST_COMPACT_DIR="test_compact_dir"

create_test_compact() {
  mkdir -p "${TEST_COMPACT_DIR}"
  cat << EOF > "${TEST_COMPACT_DIR}/${TEST_COMPACT_FILE}"
file1.md
file2.md
file3.md
EOF

  cat << EOF > "${TEST_COMPACT_DIR}/file1.md"
# File 1
Content 1
EOF

  cat << EOF > "${TEST_COMPACT_DIR}/file2.md"
# File 2
Content 2
EOF

  cat << EOF > "${TEST_COMPACT_DIR}/file3.md"
# File 3
Content 3
EOF
}

print_header "Running compact sanity tests"

print_header "Test 48: Version flag"
run_test 48 "Should show version with --version" 0 "${COMPACT_SCRIPT}" --version

print_header "Test 49: Help/usage"
run_test 49 "Should show usage with -h" 0 "${COMPACT_SCRIPT}" -h
run_test 49 "Should show usage with --help" 0 "${COMPACT_SCRIPT}" --help

print_header "Test 50: Debug mode"
run_test 50 "Should enable debug with -d" 1 "${COMPACT_SCRIPT}" -d || true
run_test 50 "Should enable debug with --debug" 1 "${COMPACT_SCRIPT}" --debug || true

print_header "Test 51: Invalid inputs"
run_test 51 "Should reject invalid directory" 1 "${COMPACT_SCRIPT}" /nonexistent || true

print_header "Test 52: Basic execution"
create_test_compact
run_test 52 "Should run successfully" 0 "${COMPACT_SCRIPT}" "${TEST_COMPACT_DIR}"
