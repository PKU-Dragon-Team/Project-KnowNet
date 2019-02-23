"""Utils for config management."""

import json
import os
import platform
from collections import OrderedDict
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Hashable, Mapping, Sequence, Union


class ConfigOpType(Enum):
    """Enum class defining Operators in config schema."""

    TYPE = auto()
    RANGE = auto()
    FUNCTION = auto()


class ConfigManager(OrderedDict):
    """Contain config and works like a Dict.

    have some utils for schema checking
    """

    KEY_TYPE = Union[Hashable, ConfigOpType]

    def check_subtree(self, layer: Dict, condition: Dict, strict: bool = True) -> bool:
        """Check a part of inner data with a condition dict."""
        for key, value in condition.items():
            if isinstance(key, str):
                if key.startswith('@*'):
                    for node, subtree in layer.items():
                        if not self.check_subtree(subtree, value):
                            if strict:
                                raise KeyError(f'Wildcard checking {key} failed on {node}')
                            return False
                elif key.startswith('$'):
                    continue

            if key not in layer:
                if value.get('$optional'):
                    continue
                elif '$default' in value:
                    layer[key] = value.get('$default')
                else:
                    if strict:
                        raise KeyError(f'Not optional key {key} does not exist.')
                    return False

            conditions: Dict[ConfigOpType, Any] = value.get('$condition')
            if conditions:
                for op, val in conditions.items():
                    if not self._check_one_condition(layer[key], op, val):
                        if strict:
                            raise KeyError(f'Operator {op} failed on {key}.')
                        return False

            if not self.check_subtree(layer[key], value):
                if strict:
                    raise KeyError(f'Subtree checking failed on {key}.')
                return False

        return True

    def check_schema(self, schema: Dict, strict: bool = True) -> bool:
        """Check inner data with a schema dict."""
        return self.check_subtree(self, schema, strict)

    @staticmethod
    def _check_one_condition(node: Any, op: ConfigOpType, val: Any) -> bool:
        if op == ConfigOpType.TYPE:
            if not isinstance(node, val):
                return False
        elif op == ConfigOpType.RANGE:
            left, right = val
            if left is not None and not left <= val:
                return False
            if right is not None and not val < right:
                return False
        elif op == ConfigOpType.FUNCTION:
            if not val(node):
                return False
        else:
            raise KeyError(f'Operator {op} not supported.')

        return True

    def _check_one_node(self, node: Any, condition: Mapping[ConfigOpType, Any] = None, strict: bool = True) -> bool:
        if not condition:
            return True

        for op, val in condition.items():
            if not self._check_one_condition(node, op, val):
                if strict:
                    raise KeyError(f'Operator {op} failed on {node}.')
                return False

        return True

    def check_node(self, path: Sequence, condition: Mapping = None, strict: bool = True) -> bool:
        """Check a node in inner data."""
        d = self
        for name in path:
            if name not in d:
                if strict:
                    raise KeyError(f'Node {name} does not exist.')
                return False
            d = d[name]

        return self._check_one_node(d, condition)

    def check_get(self, path: Sequence, condition: Mapping = None, strict: bool = True) -> Any:
        """Check and get a node."""
        if self.check_node(path, condition, strict):
            d = self
            for name in path:
                d = d[name]
            return d
        raise KeyError


GLOBAL_CONFIG_FILENAME = "knownet.json"


def get_global_config() -> ConfigManager:
    global_config = ConfigManager()

    current_platform = platform.system()
    if current_platform == 'Linux':
        site_wise = Path('/etc')
        user = Path.home()
    elif current_platform == 'Windows':
        site_wise = Path(os.getenv("PROGRAMDATA", ''))
        user = Path(os.getenv("APPDATA", ''))

    site_wise_file = site_wise / GLOBAL_CONFIG_FILENAME
    if site_wise_file.exists():
        with site_wise_file.open() as f:
            global_config.update(json.load(f))

    user_file = user / GLOBAL_CONFIG_FILENAME
    if user.exists():
        with user_file.open() as f:
            global_config.update(json.load(f))

    # check local config file, from current work folder up, up to 10 level
    p_cwd = Path.cwd()
    for _ in range(10):
        detect_file = p_cwd / GLOBAL_CONFIG_FILENAME
        if detect_file.exists():
            with detect_file.open() as f:
                global_config.update(json.load(f))
            break
        p_cwd = p_cwd.parent

    return global_config
