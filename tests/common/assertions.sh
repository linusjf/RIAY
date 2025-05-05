#!/usr/bin/env bash
# Custom test assertions

assert_exit_code() {
    local expected=$1
    local actual=$2
    local message=${3:-"Expected exit code $expected but got $actual"}

    if [ $actual -ne $expected ]; then
        echo "$message"
        return 1
    fi
}

assert_output_contains() {
    local pattern=$1
    local output=$2
    local message=${3:-"Expected output to contain '$pattern'"}

    if ! echo "$output" | grep -q "$pattern"; then
        echo "$message"
        return 1
    fi
}

assert_output_not_contains() {
    local pattern=$1
    local output=$2
    local message=${3:-"Expected output not to contain '$pattern'"}

    if echo "$output" | grep -q "$pattern"; then
        echo "$message"
        return 1
    fi
}

assert_file_permissions() {
    local file=$1
    local expected=$2
    local actual=$(stat -c "%a" "$file")

    if [ $actual -ne $expected ]; then
        echo "Expected permissions $expected for $file but got $actual"
        return 1
    fi
}

assert_file_owner() {
    local file=$1
    local expected=$2
    local actual=$(stat -c "%U" "$file")

    if [ "$actual" != "$expected" ]; then
        echo "Expected owner $expected for $file but got $actual"
        return 1
    fi
}

assert_var_set() {
    local var_name=$1
    if [ -z "${!var_name}" ]; then
        echo "Variable $var_name is not set"
        return 1
    fi
}

assert_var_not_set() {
    local var_name=$1
    if [ -n "${!var_name}" ]; then
        echo "Variable $var_name is set but should not be"
        return 1
    fi
}
