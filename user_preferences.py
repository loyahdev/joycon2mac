import json
from pathlib import Path
from appdirs import user_data_dir

APP_NAME = "joycon2mouse"
APP_AUTHOR = "moutella"  # Optional, used on Windows


def get_settings_path():
    settings_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir / "settings.json"


def load_settings():
    settings_file = get_settings_path()
    if settings_file.exists():
        with open(settings_file, "r") as f:
            return json.load(f)
    create_default_settings()
    return load_settings()
    

def save_settings(settings):
    settings_file = get_settings_path()
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)


def create_default_settings():
    settings_file = get_settings_path()
    print(get_settings_path())
    with open(settings_file, "w") as f:
        settings = {
            "ignore_opening_window": False,
            "start_with_sync": False,
            "devices": {},
            "onboarding_complete": False
        }
        json.dump(settings, f, indent=2)

if __name__ == "__main__":
    print(load_settings())
else:
    settings = load_settings()