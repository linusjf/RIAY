#!/usr/bin/env python
"""
Configenv.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : configenv
# @created     : Sunday Jul 13, 2025 19:29:45 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import os
import re
import threading
from typing import Dict, Any, Union, List

class ConfigEnv:
    BOOL_TRUE = {"true", "1", "yes", "on"}
    BOOL_FALSE = {"false", "0", "no", "off"}
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, filepath: str = 'config.env', override: bool = False, include_os_env: bool=False):
        abs_path = os.path.abspath(filepath)
        key = (abs_path, override, include_os_env)
        if key not in cls._instances:
            with cls._lock:
                # Double-checked locking pattern
                if key not in cls._instances:
                    instance = super(ConfigEnv, cls).__new__(cls)
                    instance.__init__(abs_path, override, include_os_env)
                    cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, filepath: str = 'config.env', override: bool = False, include_os_env: bool=False) -> None:
        self._filepath: str = filepath
        self._types = self._load_types(filepath+".types")
        self._vars: Dict[str, Any] = dict(os.environ) if include_os_env else {}
        self._override: bool = override
        self._load_env()

    def _load_types(self, types_path):
        if os.path.exists(types_path):
            import json
            with open(types_path) as f:
                json_obj = json.load(f)
                return json_obj
        return {}

    def _coerce_type(self, value: str, key: str) -> Union[bool, int, float, str, List[Any]]:
        value = value.strip()

        # Bash-style array
        if value.startswith('(') and value.endswith(')'):
            inner = value[1:-1].strip()
            return [self._coerce_type(v.strip('"').strip("'"), key) for v in inner.split()]

        explicit_type = self._types.get(key)
        if explicit_type == "bool":
            return value.lower() in self.BOOL_TRUE
        if explicit_type == "int":
            return int(value)
        if explicit_type == "float":
            return float(value)

        lower = value.lower()
        if lower in self.BOOL_TRUE:
            return True
        if lower in self.BOOL_FALSE:
            return False
        if re.fullmatch(r'\d+', value):
            return int(value)
        if re.fullmatch(r'\d+\.\d*', value):
            return float(value)
        return value

    def _expand_value(self, value: str) -> str:
        return os.path.expandvars(value)

    def _load_env(self) -> None:
        if not os.path.exists(self._filepath):
            raise FileNotFoundError(f"{self._filepath} not found.")

        with open(self._filepath, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip comments and blank lines
            if not line or line.startswith('#'):
                i += 1
                continue

            if '=' not in line:
                i += 1
                continue

            key, value = map(str.strip, line.split('=', 1))

            # Handle Bash-style arrays
            if value == '(':
                i += 1
                array_items = []
                while i < len(lines):
                    item_line = lines[i].strip()
                    if item_line == ')':
                        break
                    item_line = item_line.strip('"').strip("'")
                    if item_line:
                        array_items.append(self._coerce_type(item_line, key))
                    i += 1
                self._vars[key] = array_items
                if self._override or key not in os.environ:
                    os.environ[key] = ','.join(map(str, array_items))
                i += 1
                continue

            # Handle multi-line string values
            if (value.startswith('"') and not value.endswith('"')) or (value.startswith("'") and not value.endswith("'")):
                quote_char = value[0]
                full_value = value[1:]  # strip leading "
                i += 1
                while i < len(lines):
                    next_line = lines[i].rstrip('\n')
                    if next_line.endswith(quote_char):
                        full_value += '\n' + next_line[:-1]  # strip trailing "
                        break
                    else:
                        full_value += '\n' + next_line
                    i += 1
                value = full_value

            # Remove surrounding quotes (single-line)
            elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            # Expand env vars and coerce
            value = self._expand_value(value)
            coerced = self._coerce_type(value, key)
            self._vars[key] = coerced
            if self._override or key not in os.environ:
                os.environ[key] = str(coerced)

            i += 1

    @property
    def vars(self) -> Dict[str, Any]:
        return dict(self._vars)

    def get(self, key: str, default: Any = None) -> Any:
        return self._vars.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._vars)

    def __getitem__(self, key: str) -> Any:
        return self._vars[key]

    def __contains__(self, key: str) -> bool:
        return key in self._vars

def main() -> None:
    config = ConfigEnv("config.env", include_os_env=True)
    for k, v in config.as_dict().items():
        print(f"{k:<25} = {repr(v)}  # type: {type(v).__name__}")

if __name__ == "__main__":
    main()
