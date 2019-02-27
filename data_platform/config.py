"""Utils for config management."""

import json
import os
import platform
from collections import OrderedDict
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Hashable, Mapping, NamedTuple, Optional, Sequence, Text, Union


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

    @classmethod
    def _check_str_key(cls, layer: Dict, key: Text, value: Dict, strict: bool) -> bool:
        if isinstance(key, str):
            if cls._check_wildcard_key(layer, key, value, strict) is False:
                return False

            if key.startswith('$'):
                return True
        return True

    @classmethod
    def _check_wildcard_key(cls, layer: Dict, key: Text, value: Dict, strict: bool) -> bool:
        if key.startswith('@*'):
            for node, subtree in layer.items():
                if not cls.check_subtree(subtree, value):
                    if strict:
                        raise KeyError(f'Wildcard checking {key} failed on {node}')
                    return False
        return True

    @classmethod
    def _check_conditions(cls, layer: Dict, key: Text, value: Dict[Text, Dict[ConfigOpType, Any]], strict: bool) -> bool:
        conditions: Optional[Dict[ConfigOpType, Any]] = value.get('$condition')
        if conditions:
            for op, val in conditions.items():
                if not cls._check_one_condition(layer[key], op, val):
                    if strict:
                        raise KeyError(f'Operator {op} failed on {key}.')
                    return False
        return True

    @classmethod
    def _handle_missing_key(cls, layer: Dict, key: Text, value: Dict, strict: bool) -> bool:
        if key not in layer:
            if value.get('$optional'):
                return True

            if '$default' in value:
                layer[key] = value.get('$default')
            else:
                if strict:
                    raise KeyError(f'Not optional key {key} does not exist.')
                return False
        return True

    @classmethod
    def check_subtree(cls, layer: Dict, condition: Dict, strict: bool = True) -> bool:
        """Check a part of inner data with a condition dict."""
        for key, value in condition.items():
            if cls._check_str_key(layer, key, value, strict) is False:
                return False

            if cls._handle_missing_key(layer, key, value, strict) is False:
                return False

            if cls._check_conditions(layer, key, value, strict) is False:
                return False

            # recursive check subtrees
            if not cls.check_subtree(layer[key], value):
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


GLOBAL_CONFIG_FILENAME = ".knownet.json"


class ConfigFiles(NamedTuple):
    site_wise: Path
    user: Path
    local: Path


class ConfigDicts(NamedTuple):
    site_wise: Dict
    user: Dict
    local: Dict


def get_global_config(config_dicts: ConfigDicts = None) -> ConfigManager:
    if config_dicts is None:
        config_dicts = get_global_config_dicts(get_global_config_files())

    global_config = ConfigManager()

    global_config.update(config_dicts.site_wise)
    global_config.update(config_dicts.user)
    global_config.update(config_dicts.local)

    return global_config


def get_global_config_dicts(config_files: ConfigFiles) -> ConfigDicts:
    site_wise: Dict = {}
    user: Dict = {}
    local: Dict = {}

    if config_files.site_wise.exists():
        with config_files.site_wise.open() as f:
            site_wise = json.load(f)

    if config_files.user.exists():
        with config_files.user.open() as f:
            user = json.load(f)

    if config_files.local.exists():
        with config_files.local.open() as f:
            local = json.load(f)

    return ConfigDicts(site_wise, user, local)


def get_global_config_files() -> ConfigFiles:
    current_platform = platform.system()
    if current_platform == 'Linux':
        site_wise = Path('/etc')  # /etc/
        user = Path.home()  # ~/
    elif current_platform == 'Windows':
        site_wise = Path(os.getenv("PROGRAMDATA", ''))  # %PROGRAMDATA%
        user = Path(os.getenv("APPDATA", ''))  # %APPDATA%

    site_wise_file = site_wise / GLOBAL_CONFIG_FILENAME
    user_file = user / GLOBAL_CONFIG_FILENAME

    # check local config file, from current work folder up, up to 10 level
    p_cwd = Path.cwd()
    for _ in range(10):
        detect_file = p_cwd / GLOBAL_CONFIG_FILENAME
        if detect_file.exists():
            break
        p_cwd = p_cwd.parent

    return ConfigFiles(site_wise_file, user_file, detect_file)
