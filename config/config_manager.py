"""
Configuration Manager for JARVIS.
Handles loading, updating, and saving configuration settings.
"""

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = CONFIG_DIR / "settings.json"


class ConfigManager:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error loading config: {e}. Using defaults.")
                self._config = {}
        else:
            self._config = {}

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        if section not in self._config:
            return default
        if key is None:
            return self._config.get(section, default)
        return self._config[section].get(key, default)

    def set(self, section: str, key: str, value: Any, save: bool = True) -> None:
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        if save:
            self.save()

    def save(self) -> None:
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")

    @property
    def all(self) -> Dict[str, Any]:
        return self._config


config = ConfigManager()
