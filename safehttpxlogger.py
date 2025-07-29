#!/usr/bin/env python
"""
Safehttpxlogger.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : safehttpxlogger
# @created     : Tuesday Jul 29, 2025 14:22:30 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import httpx
import logging
import os
import json
import time
from typing import Optional, Dict, List, Tuple, Union, Any
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

class SafeHttpxLogger:
    REDACT_KEYS: set[str] = {"password", "token", "api_key", "authorization"}
    REDACT_VALUE_PREFIXES: set[str] = {"bearer", "basic"}
    MAX_BODY_LENGTH: int = 200
    ENABLE_BODY_LOGGING: bool = os.getenv("DEBUG_LOG_PAYLOADS", "false").lower() == "true"

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        redact_keys: Optional[set[str]] = None,
        redact_prefixes: Optional[set[str]] = None,
        max_body_length: Optional[int] = None
    ) -> None:
        """Initialize the logger with optional custom configuration.
        
        Args:
            logger: Custom logger instance to use
            redact_keys: Set of keys to redact in URLs and JSON bodies
            redact_prefixes: Set of value prefixes that indicate sensitive data
            max_body_length: Maximum length of logged body content
        """
        self.logger: logging.Logger = logger or logging.getLogger("safe-httpx-logger")
        self.REDACT_KEYS = redact_keys or self.REDACT_KEYS
        self.REDACT_VALUE_PREFIXES = redact_prefixes or self.REDACT_VALUE_PREFIXES
        self.MAX_BODY_LENGTH = max_body_length or self.MAX_BODY_LENGTH
        logging.basicConfig(level=logging.DEBUG if self.ENABLE_BODY_LOGGING else logging.INFO)

    def attach(self, client: httpx.Client) -> None:
        """Attach logging hooks to an HTTPX client."""
        client.event_hooks.update({
            "request": [self._pre_request, self.log_request],
            "response": [self.log_response, self._post_response]
        })

    def _pre_request(self, request: httpx.Request) -> None:
        """Store request start time for performance measurement."""
        request.context["start_time"] = time.time()

    def _post_response(self, response: httpx.Response) -> None:
        """Log request duration."""
        duration = time.time() - response.request.context["start_time"]
        self.logger.debug(f"Request took {duration:.2f} seconds")

    def log_request(self, request: httpx.Request) -> None:
        """Log HTTP request details."""
        try:
            redacted_url: str = self._redact_url(request.url)
            self.logger.info(f">>> {request.method} {redacted_url}")

            headers: Dict[str, str] = self._redact_headers(request.headers)
            self.logger.debug(f">>> Headers: {headers}")

            if self.ENABLE_BODY_LOGGING and request.content:
                self._log_request_body(request)
        except Exception as e:
            self.logger.error(f"Failed to log request: {e}", exc_info=True)

    def _log_request_body(self, request: httpx.Request) -> None:
        """Handle request body logging."""
        try:
            content: str = request.content.decode() if isinstance(request.content, bytes) else str(request.content)
            redacted: str = self._sanitize_json(content)
            self.logger.debug(f">>> Body: {self._truncate(redacted)}")
        except UnicodeDecodeError:
            self.logger.debug(">>> Binary body content (not logged)")
        except Exception as e:
            self.logger.debug(f">>> Body logging error: {e}")

    def log_response(self, response: httpx.Response) -> None:
        """Log HTTP response details."""
        try:
            self.logger.info(f"<<< {response.status_code} {response.url}")
            self.logger.debug(f"<<< Response Headers: {self._redact_headers(response.headers)}")

            if self.ENABLE_BODY_LOGGING and response.content:
                self._log_response_body(response)
        except Exception as e:
            self.logger.error(f"Failed to log response: {e}", exc_info=True)

    def _log_response_body(self, response: httpx.Response) -> None:
        """Handle response body logging."""
        try:
            content: str = response.text
            redacted: str = self._sanitize_json(content)
            self.logger.debug(f"<<< Body: {self._truncate(redacted)}")
        except Exception as e:
            self.logger.debug(f"<<< Response body could not be logged: {e}")

    def _redact_url(self, url: httpx.URL) -> str:
        """Redact sensitive information from URL."""
        try:
            parsed = urlparse(str(url))
            if parsed.password:  # Redact URL passwords
                netloc: str = f"{parsed.username}:***REDACTED***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
            else:
                netloc = parsed.netloc
                
            query: List[Tuple[str, str]] = parse_qsl(parsed.query, keep_blank_values=True)
            redacted_query: List[Tuple[str, str]] = [
                (k, "***REDACTED***") if k.lower() in self.REDACT_KEYS else (k, v)
                for k, v in query
            ]
            new_query: str = urlencode(redacted_query)
            return urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        except Exception as e:
            self.logger.warning(f"URL redaction failed: {e}")
            return str(url)

    def _redact_headers(self, headers: httpx.Headers) -> Dict[str, str]:
        """Redact sensitive headers."""
        redacted: Dict[str, str] = {}
        for k, v in headers.items():
            k_lower: str = k.lower()
            if k_lower in self.REDACT_KEYS:
                redacted[k] = "***REDACTED***"
            elif any(v.lower().startswith(prefix) for prefix in self.REDACT_VALUE_PREFIXES):
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = v
        return redacted

    def _sanitize_json(self, body: str) -> str:
        """Sanitize JSON body by redacting sensitive fields.
        
        Args:
            body: The JSON string to sanitize
            
        Returns:
            Redacted JSON string or fallback message if parsing fails
        """
        try:
            data: Union[Dict[str, Any], List[Any]] = json.loads(body)
            if isinstance(data, dict):
                for key in data:
                    if key.lower() in self.REDACT_KEYS or self._looks_like_token(str(data[key])):
                        data[key] = "***REDACTED***"
            return json.dumps(data)
        except Exception:
            return "[Non-JSON or malformed body]"

    def _looks_like_token(self, value: str) -> bool:
        """Check if a value looks like a token that should be redacted."""
        return any(value.lower().startswith(prefix) for prefix in self.REDACT_VALUE_PREFIXES)

    def _truncate(self, body: str) -> str:
        """Truncate long body content for logging."""
        return body[:self.MAX_BODY_LENGTH] + ("..." if len(body) > self.MAX_BODY_LENGTH else "")
