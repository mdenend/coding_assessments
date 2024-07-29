from pathlib import Path
import yaml

def load_config(config_loc:str="config/config.yml"):
    file_path = Path(config_loc)
    with file_path.open() as f:
        return yaml.safe_load(f)
