import time

from src import config
from src import manualMov, autoMov

parser = config.config()

if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manualMov.main()
    else:
        autoMov.main()
