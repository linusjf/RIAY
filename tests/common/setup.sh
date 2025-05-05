#!/usr/bin/env bash
# Test environment setup utilities

setup_test_env() {
  export TEST_DIR=$(mktemp -d)
  export ORIG_DIR=$PWD
  cd "$TEST_DIR" || exit 1
}

reset_test_env() {
  cd "$ORIG_DIR" || exit 1
  if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
    rm -rf "$TEST_DIR"
  fi
  unset TEST_DIR
  unset ORIG_DIR
}

copy_test_scripts() {
  local script_dir="$(dirname "$0")/.."
  cp "$script_dir/cleanup" "$TEST_DIR/"
  cp "$script_dir/genmonth" "$TEST_DIR/"
  cp "$script_dir/gentoc" "$TEST_DIR/"
  cp -r "$script_dir/lib" "$TEST_DIR/"
  cp "$script_dir/config.env" "$TEST_DIR/"
}

create_test_files() {
  local dir=$1
  mkdir -p "$dir"
  touch "$dir"/{test.tmp,backup~,temp.log,temp.vtt,failed.json}
}

create_test_markdown() {
  local file=$1
  cat > "$file" << EOF
# Test Document

## Section 1
Content

## Section 2
More content
EOF
}

setup_month_dirs() {
  for month in January February March April May June July August September October November December; do
    mkdir -p "$month"
    echo "header.md" > "$month/compact.txt"
    create_test_markdown "$month/header.md"
  done
}
