#!/usr/bin/env bash
# Common test utilities and helpers

set -eo pipefail

declare -i TOTAL_TESTS=0
declare -i PASSED_TESTS=0
declare -i FAILED_TESTS=0
declare -i SKIPPED_TESTS=0

print_header() {
  printf "\n\033[1m%s\033[0m\n" "$1"
}

print_summary() {
  print_header "Test Summary"
  printf "  Total:  %d\n" $TOTAL_TESTS
  printf "  \033[32mPassed: %d\033[0m\n" $PASSED_TESTS
  printf "  \033[31mFailed: %d\033[0m\n" $FAILED_TESTS
  printf "  \033[33mSkipped: %d\033[0m\n" $SKIPPED_TESTS

  if [ $FAILED_TESTS -gt 0 ]; then
    printf "\n\033[31mSome tests failed!\033[0m\n"
    exit 1
  fi
}

run_test() {
  local test_num=$1
  local description=$2
  local expected_exit=$3
  shift 3

  ((TOTAL_TESTS++))
  printf "  %-50s" "$description..."

  if "$@"; then
    actual_exit=0
  else
    actual_exit=$?
  fi

  if [ "$actual_exit" -eq "$expected_exit" ]; then
    printf "\033[32mPASS\033[0m\n"
    ((PASSED_TESTS++))
  else
    printf "\033[31mFAIL (expected %d, got %d)\033[0m\n" "$expected_exit" "$actual_exit"
    ((FAILED_TESTS++))
  fi
}

assert_file_exists() {
  local file=$1
  if [ ! -f "$file" ]; then
    echo "File $file does not exist"
    return 1
  fi
}

assert_file_not_exists() {
  local file=$1
  if [ -f "$file" ]; then
    echo "File $file exists but should not"
    return 1
  fi
}

assert_dir_exists() {
  local dir=$1
  if [ ! -d "$dir" ]; then
    echo "Directory $dir does not exist"
    return 1
  fi
}

assert_contains() {
  local pattern=$1
  local file=$2
  if ! grep -q "$pattern" "$file"; then
    echo "Pattern '$pattern' not found in $file"
    return 1
  fi
}

cleanup_test_dir() {
  if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
    rm -rf "$TEST_DIR"
  fi
}

trap cleanup_test_dir EXIT
