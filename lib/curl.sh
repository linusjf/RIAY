#!/usr/bin/env bash
# HTTP request utility with retry logic and error handling

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    readonly SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    readonly SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"
source "${SCRIPT_DIR}/lib/files.sh"
require_commands curl sed cat rm date head tail basename mktemp grep cut tr mkdir

: "${CURL_MAX_RETRIES:=3}"
: "${CURL_INITIAL_RETRY_DELAY:=1}"
: "${CURL_MAX_RETRY_DELAY:=100}"
: "${CURL_RETRY_EXP_BASE:=2}"
: "${CURL_CONNECT_TIMEOUT:=30}"
: "${CURL_MAX_TIME:=90}"

if ! declare -p curl__HTTP_STATUS_CODES &> /dev/null; then
  declare -A curl__HTTP_STATUS_CODES=(
    [000]="No Response - Unable to connect/Network error"
    [100]="Continue"
    [101]="Switching Protocols"
    [102]="Processing"
    [103]="Early Hints"
    [200]="OK"
    [201]="Created"
    [202]="Accepted"
    [203]="Non-Authoritative Information"
    [204]="No Content"
    [205]="Reset Content"
    [206]="Partial Content"
    [207]="Multi-Status"
    [208]="Already Reported"
    [218]="This is fine"
    [226]="IM Used"
    [300]="Multiple Choices"
    [301]="Moved Permanently"
    [302]="Found"
    [303]="See Other"
    [304]="Not Modified"
    [305]="Use Proxy"
    [307]="Temporary Redirect"
    [308]="Permanent Redirect"
    [400]="Bad Request/Invalid Argument/Failed Precondition"
    [401]="Unauthorized/Authentication Fails"
    [402]="Payment Required/Insufficient Balance"
    [403]="Forbidden/Permission Denied"
    [404]="Not Found"
    [405]="Method Not Allowed"
    [406]="Not Acceptable"
    [407]="Proxy Authentication Required"
    [408]="Request Timeout"
    [409]="Conflict"
    [410]="Gone"
    [411]="Length Required"
    [412]="Precondition Failed"
    [413]="Payload Too Large"
    [414]="URI Too Long"
    [415]="Unsupported Media Type"
    [416]="Range Not Satisfiable"
    [417]="Expectation Failed"
    [418]="I'm a teapot"
    [419]="Page Expired"
    [420]="Method Failure/Enhance Your Calm"
    [421]="Misdirected Request"
    [422]="Unprocessable Entity/Invalid Parameters"
    [423]="Locked"
    [424]="Failed Dependency"
    [425]="Too Early"
    [426]="Upgrade Required"
    [428]="Precondition Required"
    [429]="Too Many Requests/Resource Exhausted/Rate Limit Reached"
    [430]="Request Header Fields Too Large/Shopify Security Rejection"
    [431]="Request Header Fields Too Large"
    [440]="Login Time-out"
    [444]="No Response"
    [449]="Retry With"
    [450]="Blocked By Windows Parental Controls"
    [451]="Unavailable For Legal Reasons/Redirect"
    [460]="Client closed the connection with the load balancer before the idle timeout period elapsed. Typically, when client timeout is sooner than the Elastic Load Balancer's timeout"
    [463]="The load balancer received an X-Forwarded-For request header with more than 30 IP addresses"
    [464]="Incompatible protocol versions between Client and Origin server"
    [494]="Request header too large"
    [495]="SSL Certificate Error"
    [496]="SSL Certificate Required"
    [497]="HTTP Request Sent To HTTPS Port"
    [498]="Invalid Token"
    [499]="Token Required/Client Closed Request"
    [500]="Internal Server Error"
    [501]="Not Implemented"
    [502]="Bad Gateway"
    [503]="Service Unavailable/Server Overloaded"
    [504]="Gateway Timeout/Deadline Exceeded"
    [505]="HTTP Version Not Supported"
    [506]="Variant Also Negotiates"
    [507]="Insufficient Storage"
    [508]="Loop Detected"
    [509]="Bandwidth Limit Exceeded"
    [510]="Not Extended"
    [511]="Network Authentication Required"
    [520]="Web Server Returned an Unknown Error"
    [521]="Web Server Is Down"
    [522]="Connection Timed Out"
    [523]="Origin Is Unreachable"
    [524]="A Timeout Occurred"
    [525]="SSL Handshake Failed"
    [526]="Invalid SSL Certificate"
    [529]="Site is overloaded"
    [530]="Site is frozen/Origin DNS Error/Error 530"
    [540]="Temporarily disabled"
    [561]="Unauthorized"
    [598]="Network read timeout error"
    [599]="Network connect timeout error"
    [783]="Unexpected token"
    [999]="Non-standard"
  )
fi

if ! declare -f curl::redact_keys > /dev/null; then
  function curl::redact_keys() {
    local input="$1"
    echo "$input" | sed -E 's/(key=|Bearer )[^&"\}]*/REDACTED/g'
  }
  export -f curl::redact_keys
fi

if ! declare -f curl::save_failed_response > /dev/null; then
  function curl::save_failed_response() {
    local data="$1"
    local response="$2"
    local endpoint="$3"
    local timestamp
    timestamp=$(date -u +"%Y%m%d_%H%M%S")

    local sanitized_endpoint=$(echo "$endpoint" | sed -E 's/(key=|Bearer )[^&"\}]*/REDACTED/g' | sed 's/[^a-zA-Z0-9_-]/_/g')
    local curltempdir=$"$(files::get_temp_dir)/safe_curl"
    mkdir -p "$curltempdir"
    local filename="${curltempdir}/failed_response_${sanitized_endpoint}_${timestamp}.json"

    {
      curl::redact_keys "$data"
      curl::redact_keys "$response"
    } >> "$filename"
    err "Saved failed response to $filename (API keys redacted)"
  }
  export -f curl::save_failed_response
fi

if ! declare -f curl::should_retry > /dev/null; then
  function curl::should_retry() {
    local status_code="$1"
    retry_status_codes=(408 429 500 502 503 504)
    for _ in "${retry_status_codes[@]}"; do
      if [[ $status_code -eq _ ]]; then
        return 0
      fi
    done
    return 1
  }
  export -f curl::should_retry
fi

if ! declare -f curl::handle_retry > /dev/null; then
  function curl::handle_retry() {
    local status_code="$1"
    local retry_count="$2"
    local delay="$3"
    local response_headers="$4"
    local url="$5"

    if [[ $status_code -eq 408 ]] || [[ $status_code -eq 429 ]] || [[ $status_code -eq 503 ]]; then
      local retry_after=$(echo "$response_headers" | grep -i '^retry-after:' | cut -d' ' -f2- | tr -d '\r')
      if [[ -n "$retry_after" ]]; then
        >&2 echo "Request failed with status $status_code: ${curl__HTTP_STATUS_CODES[$status_code]}, retrying in $retry_after seconds (Retry-After header value, attempt $retry_count/$CURL_MAX_RETRIES)"
      elif [[ $status_code -eq 429 ]]; then
        >&2 echo "Request failed with status 429 (Too Many Requests) but no Retry-After header provided, aborting..."
        return 1
      else
        >&2 echo "Request failed with status $status_code: ${curl__HTTP_STATUS_CODES[$status_code]}, retrying in $delay seconds (attempt $retry_count/$CURL_MAX_RETRIES)"
      fi
    else
      >&2 echo "Request failed with status $status_code: ${curl__HTTP_STATUS_CODES[$status_code]}, retrying in $delay seconds (attempt $retry_count/$CURL_MAX_RETRIES)"
    fi

    sleep "${retry_after:-${delay}}"
  }
  export -f curl::handle_retry
fi

if ! declare -f curl::download > /dev/null; then
  function curl::download() {
    local url="$1"
    shift
    local output_path="$1"
    shift
    local method="GET"
    if [[ "${1:-}" =~ ^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$ ]]; then
      method="$1"
      shift
    fi

    local retry_count=0
    local delay=${CURL_INITIAL_RETRY_DELAY}
    local status_code=0

    while [[ $retry_count -lt ${CURL_MAX_RETRIES} ]]; do
      status_code=0

      local curl_cmd=(
        curl
        --show-error
        --connect-timeout "${CURL_CONNECT_TIMEOUT}"
        --max-time "${CURL_MAX_TIME}"
        --fail-with-body
        --silent
        --write-out "%{http_code}"
        -D /dev/stdout
        -o "$output_path"
      )

      curl_cmd+=("$@")
      curl_cmd+=(--request "$method")
      curl_cmd+=("$url")
      redacted_command="$(curl::redact_keys "${curl_cmd[*]}")"

      [[ "${verbose:-false}" == "true" ]] && >&2 echo "Making $method download request to $(curl::redact_keys "$url")"

      local curl_output
      curl_output="$("${curl_cmd[@]}" 2>&1 || true)"
      status_code=$(echo "$curl_output" | tail -n 1)
      local response_headers=$(echo "$curl_output" | head -n -1)

      if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
        [[ "${verbose:-false}" == "true" ]] && >&2 echo "Download from $(curl::redact_keys "$url") succeeded with status $status_code : ${curl__HTTP_STATUS_CODES[$status_code]}"
        return 0
      fi

      retry_count=$((retry_count + 1))
      if [[ $retry_count -lt $CURL_MAX_RETRIES ]]; then
        if ! curl::should_retry "$status_code"; then
          return 2
        fi

        if ! curl::handle_retry "$status_code" $((retry_count + 1)) "$delay" "$response_headers" "$url"; then
          return 2
        fi
        delay=$((delay * CURL_RETRY_EXP_BASE))
        delay=$((delay < CURL_MAX_RETRY_DELAY ? delay : CURL_MAX_RETRY_DELAY))
      fi
    done

    >&2 echo "CURL VERBOSE OUTPUT:"
    curl -v \
      --request "$method" \
      "$@" \
      --connect-timeout "${CURL_CONNECT_TIMEOUT}" \
      --max-time "${CURL_MAX_TIME}" \
      --show-error \
      "$url" \
      >&2

    err "Download failed after $CURL_MAX_RETRIES attempts. Last status code: $status_code: ${curl__HTTP_STATUS_CODES[$status_code]}"
    return 2
  }
  export -f curl::download
fi

if ! declare -f curl::request > /dev/null; then
  function curl::request() {
    local url="$1"
    shift

    local method="GET"
    if [[ "${1:-}" =~ ^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$ ]]; then
      method="$1"
      shift
    fi

    local output_file
    output_file=$(mktemp)

    local retry_count=0
    local delay=${CURL_INITIAL_RETRY_DELAY}
    local status_code=0
    local response=""
    local redacted_command=""

    while [[ $retry_count -lt ${CURL_MAX_RETRIES} ]]; do
      status_code=0
      response=""

      local curl_cmd=(
        curl
        --show-error
        --connect-timeout "${CURL_CONNECT_TIMEOUT}"
        --max-time "${CURL_MAX_TIME}"
        --fail-with-body
        --silent
        --write-out "%{http_code}"
        -D /dev/stdout
        -o "$output_file"
      )

      curl_cmd+=("$@")
      curl_cmd+=(--request "$method")
      curl_cmd+=("$url")
      redacted_command="$(curl::redact_keys "${curl_cmd[*]}")"

      [[ "${verbose:-false}" == "true" ]] && >&2 echo "Making $method request to $(curl::redact_keys "$url")"

      local curl_output
      curl_output="$("${curl_cmd[@]}" 2>&1 || true)"
      status_code=$(echo "$curl_output" | tail -n 1)
      response="$(cat "$output_file" || true)"
      local response_headers=$(echo "$curl_output" | head -n -1)

      if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
        [[ "${verbose:-false}" == "true" ]] && >&2 echo "Request to $(curl::redact_keys "$url") succeeded with status $status_code : ${curl__HTTP_STATUS_CODES[$status_code]}"
        echo "$response"
        rm -f "$output_file"
        return 0
      fi

      retry_count=$((retry_count + 1))
      if [[ $retry_count -lt $CURL_MAX_RETRIES ]]; then
        curl::save_failed_response "$redacted_command" "$response" "$(basename "$url")"

        if ! curl::should_retry "$status_code"; then
          return 2
        fi

        if ! curl::handle_retry "$status_code" $((retry_count + 1)) "$delay" "$response_headers" "$url"; then
          return 2
        fi
        delay=$((delay * CURL_RETRY_EXP_BASE))
        delay=$((delay < CURL_MAX_RETRY_DELAY ? delay : CURL_MAX_RETRY_DELAY))
      fi
    done

    >&2 echo "CURL VERBOSE OUTPUT:"
    curl -v \
      --request "$method" \
      "$@" \
      --connect-timeout "${CURL_CONNECT_TIMEOUT}" \
      --max-time "${CURL_MAX_TIME}" \
      --show-error \
      "$url" \
      >&2

    curl::save_failed_response "$redacted_command" "$response" "$(basename "$url")"
    rm -f "$output_file"
    err "Request failed after $CURL_MAX_RETRIES attempts. Last status code: $status_code: ${curl__HTTP_STATUS_CODES[$status_code]}"
    return 2
  }
  export -f curl::request
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
