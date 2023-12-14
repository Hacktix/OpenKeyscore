from argparse import Namespace

class KeyscoreConfig():
    _config = {}

    def get(key: str, default = None):
        return KeyscoreConfig._config[key] if key in KeyscoreConfig._config else default
    
    def _load_config_from_args(args: Namespace):
        for key, value in args.__dict__.items():
            if value is not None:
                KeyscoreConfig._config[key] = value