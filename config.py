from argparse import Namespace
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class KeyscoreConfig():
    _config = {}

    def get(key: str, default = None):
        return KeyscoreConfig._config[key] if key in KeyscoreConfig._config else default
    
    def _load_config_from_args(args: Namespace):
        for key, value in args.__dict__.items():
            if value is not None:
                KeyscoreConfig._config[key] = value
        KeyscoreConfig._load_env_var_configs()
            
    def _load_env_var_configs():
        for envkey, envvar in os.environ.items():
            if envkey.startswith("KSC_"):
                KeyscoreConfig._config[envkey[4:].lower()] = envvar