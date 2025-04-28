#!/usr/bin/env bash
# HTTP request utility with retry logic and error handling

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/require.sh"
source "${SCRIPT_DIR}/lockconfig.sh"
lock_config_vars "${SCRIPT_DIR}/config.env"

if ! declare -p HTTP_STATUS_CODES &> /dev/null; then
  declare -A HTTP_STATUS_CODES=(
    [000]="Returned with an HTTP/2 GOAWAY frame if the compressed length of any of the headers exceeds 8K bytes or if more than 10K requests are served through one connection"
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
    [419]="Page Expired"
    [420]="Method Failure/Enhance Your Calm"
    [421]="Misdirected Request"
    [422]="Unprocessable Entity"
    [423]="Locked"
    [424]="Failed Dependency"
    [425]="Too Early"
    [426]="Upgrade Required"
    [428]="Precondition Required"
    [429]="Too Many Requests"
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
    [503]="Service Unavailable"
    [504]="Gateway Timeout"
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

: "${MAX_RETRIES:=3}"
: "${INITIAL_RETRY_DELAY:=1}"

if ! declare -f redact_keys > /dev/null; then
  function redact_keys() {
    local input="$1"
    echo "$input" | sed -E 's/(key=|Bearer )[^&"\}]*/REDACTED/g'
  }
  export -f redact_keys
fi

if ! declare -f save_failed_response > /dev/null; then
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
  export -f save_failed_response
fi

if ! declare -f safe_curl_request > /dev/null; then
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
        --connect-timeout "${CONNECT_TIMEOUT:-30}"
        --max-time "${MAX_TIME:-90}"
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
      --connect-timeout "${CONNECT_TIMEOUT:-30}" \
      --max-time "${MAX_TIME:-90}" \
      --show-error \
      >&2

    save_failed_response "$data" "$response" "$(basename "$url")"
    rm -f "$output_file"
    err "Request failed after $MAX_RETRIES attempts. Last status code: $status_code: ${HTTP_STATUS_CODES[$status_code]}"
    return 2
  }
  export -f safe_curl_request
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main() {
    echo "This is a library of functions and not meant to be executed directly" >&2
    return 1
  }
  main "$@"
fi
