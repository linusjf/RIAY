#!/usr/bin/env bash

# HTTP request utility with retry logic and error handling

set -o errexit
set -o nounset
set -o pipefail

if command -v realpath > /dev/null 2>&1; then
  SCRIPT_DIR="$(dirname "$(realpath "$0")")"
else
  SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
fi

source "${SCRIPT_DIR}/require.sh"

if ! declare -p HTTP_STATUS_CODES &> /dev/null; then
  declare -A HTTP_STATUS_CODES=(
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
    [226]="IM Used"
    [300]="Multiple Choices"
    [301]="Moved Permanently"
    [302]="Found"
    [303]="See Other"
    [304]="Not Modified"
    [305]="Use Proxy"
    [307]="Temporary Redirect"
    [308]="Permanent Redirect"
    [400]="Bad Request"
    [401]="Unauthorized"
    [402]="Payment Required"
    [403]="Forbidden"
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
    [421]="Misdirected Request"
    [422]="Unprocessable Entity"
    [423]="Locked"
    [424]="Failed Dependency"
    [425]="Too Early"
    [426]="Upgrade Required"
    [428]="Precondition Required"
    [429]="Too Many Requests"
    [431]="Request Header Fields Too Large"
    [451]="Unavailable For Legal Reasons"
    [500]="Internal Server Error"
    [501]="Not Implemented"
    [502]="Bad Gateway"
    [503]="Service Unavailable"
    [504]="Gateway Timeout"
    [505]="HTTP Version Not Supported"
    [506]="Variant Also Negotiates"
    [507]="Insufficient Storage"
    [508]="Loop Detected"
    [510]="Not Extended"
    [511]="Network Authentication Required"
  )
fi

: "${MAX_RETRIES:=3}"
: "${INITIAL_RETRY_DELAY:=1}"

function redact_keys() {
  local input="$1"
  echo "$input" | sed -E 's/(key=|Bearer )[^&"\}]*/REDACTED/g'
}

function save_failed_response() {
  local data="$1"
  local response="$2"
  local endpoint="$3"
  local timestamp
  timestamp=$(date -u +"%Y%m%d_%H%M%S")

  local sanitized_endpoint=$(echo "$endpoint" | sed -E 's/(key=|Bearer )[^&"\}]*/REDACTED/g' | sed 's/[^a-zA-Z0-9_-]/_/g')
  local filename="failed_response_${sanitized_endpoint}_${timestamp}.json"

  {
    redact_keys "$data"
    redact_keys "$response"
  } >> "$filename"
  err "Saved failed response to $filename (API keys redacted)"
}

function safe_curl_request() {
  local url="$1"
  local method="${2:-GET}"
  local headers="${3:-}"
  local data="${4:-}"
  local output_file
  output_file=$(mktemp)

  local retry_count=0
  local delay=$INITIAL_RETRY_DELAY
  local status_code=0
  local response=""

  while [[ $retry_count -lt $MAX_RETRIES ]]; do
    status_code=0
    response=""

    local curl_cmd=(
      curl
      --show-error
      --connect-timeout 10
      --max-time 60
      --fail-with-body
      --silent
      --write-out "%{http_code}"
      -D /dev/stdout
      -o "$output_file"
    )

    [[ "$method" == "POST" ]] && curl_cmd+=(-X "POST")
    [[ -n "$headers" ]] && curl_cmd+=(-H "$headers")
    [[ -n "$data" ]] && curl_cmd+=(-d "$data")
    curl_cmd+=("$url")

    [[ "${verbose:-false}" == "true" ]] && >&2 echo "Making $method request to $(redact_keys "$url")"

    local curl_output
    curl_output="$("${curl_cmd[@]}" 2>&1 || true)"
    status_code=$(echo "$curl_output" | tail -n 1)
    response="$(cat "$output_file" || true)"
    local response_headers=$(echo "$curl_output" | head -n -1)

    if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
      [[ "${verbose:-false}" == "true" ]] && >&2 echo "Request to $(redact_keys "$url") succeeded with status $status_code : ${HTTP_STATUS_CODES[$status_code]}"
      echo "$response"
      rm -f "$output_file"
      return 0
    fi

    retry_count=$((retry_count + 1))
    if [[ $retry_count -lt $MAX_RETRIES ]]; then
      save_failed_response "$data" "$response" "$(basename "$url")"

      if [[ $status_code -ge 400 ]] && [[ $status_code -lt 500 ]] && [[ $status_code -ne 408 ]] && [[ $status_code -ne 429 ]]; then
        >&2 echo "Request failed with status $status_code: ${HTTP_STATUS_CODES[$status_code]}, no retries..."
        return 2
      fi

      if [[ $status_code -eq 408 ]] || [[ $status_code -eq 429 ]]; then
        local retry_after=$(echo "$response_headers" | grep -i '^retry-after:' | cut -d' ' -f2- | tr -d '\r')
        if [[ -n "$retry_after" ]]; then
          delay="$retry_after"
          >&2 echo "Request failed with status $status_code: ${HTTP_STATUS_CODES[$status_code]}, retrying in $delay seconds (Retry-After header value, attempt $retry_count/$MAX_RETRIES)"
        elif [[ $status_code -eq 429 ]]; then
          >&2 echo "Request failed with status 429 (Too Many Requests) but no Retry-After header provided, aborting..."
          return 2
        else
          >&2 echo "Request failed with status $status_code: ${HTTP_STATUS_CODES[$status_code]}, retrying in $delay seconds (attempt $retry_count/$MAX_RETRIES)"
        fi
      else
        >&2 echo "Request failed with status $status_code: ${HTTP_STATUS_CODES[$status_code]}, retrying in $delay seconds (attempt $retry_count/$MAX_RETRIES)"
      fi

      sleep "$delay"
      delay=$((delay * 2))
    fi
  done

  >&2 echo "CURL VERBOSE OUTPUT:"
  curl -v "$url" \
    -X "$method" \
    ${headers:+-H "$(redact_keys "$headers")"} \
    ${data:+-d "$(redact_keys "$data")"} \
    --connect-timeout 10 \
    --max-time 60 \
    --show-error \
    >&2

  save_failed_response "$data" "$response" "$(basename "$url")"
  rm -f "$output_file"
  err "Request failed after $MAX_RETRIES attempts. Last status code: $status_code: ${HTTP_STATUS_CODES[$status_code]}"
  return 2
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
