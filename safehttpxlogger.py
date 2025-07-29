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
from typing import Optional, Dict, List, Tuple, Union, Any
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

class SafeHttpxLogger:
    REDACT_KEYS: set[str] = {"password", "token", "api_key", "authorization"}
    REDACT_VALUE_PREFIXES: set[str] = {"bearer", "basic"}
    MAX_BODY_LENGTH: int = 200
    ENABLE_BODY_LOGGING: bool = os.getenv("DEBUG_LOG_PAYLOADS", "false").lower() == "true"

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger: logging.Logger = logger or logging.getLogger("safe-httpx-logger")
        logging.basicConfig(level=logging.DEBUG if self.ENABLE_BODY_LOGGING else logging.INFO)

    def attach(self, client: httpx.Client) -> None:
        client.event_hooks.update({
            "request": [self.log_request],
            "response": [self.log_response]
        })

    def log_request(self, request: httpx.Request) -> None:
        redacted_url: str = self._redact_url(request.url)
        self.logger.info(f">>> {request.method} {redacted_url}")

        headers: Dict[str, str] = self._redact_headers(request.headers)
        self.logger.debug(f">>> Headers: {headers}")

        if self.ENABLE_BODY_LOGGING and request.content:
            try:
                content: str = request.content.decode() if isinstance(request.content, bytes) else str(request.content)
                redacted: str = self._sanitize_json(content)
                self.logger.debug(f">>> Body: {self._truncate(redacted)}")
            except Exception as e:
                self.logger.debug(f">>> Body could not be logged: {e}")

    def log_response(self, response: httpx.Response) -> None:
        self.logger.info(f"<<< {response.status_code} {response.url}")
        self.logger.debug(f"<<< Response Headers: {dict(response.headers)}")

    def _redact_url(self, url: httpx.URL) -> str:
        parsed = urlparse(str(url))
        query: List[Tuple[str, str]] = parse_qsl(parsed.query, keep_blank_values=True)
        redacted_query: List[Tuple[str, str]] = [
            (k, "***REDACTED***") if k.lower() in self.REDACT_KEYS else (k, v)
            for k, v in query
        ]
        new_query: str = urlencode(redacted_query)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

    def _redact_headers(self, headers: httpx.Headers) -> Dict[str, str]:
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
        return any(value.lower().startswith(prefix) for prefix in self.REDACT_VALUE_PREFIXES)

    def _truncate(self, body: str) -> str:
        return body[:self.MAX_BODY_LENGTH] + ("..." if len(body) > self.MAX_BODY_LENGTH else "")
