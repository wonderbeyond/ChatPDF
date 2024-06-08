import os.path as op

import yaml

with open(op.expanduser("~/.config/chatpdf.yaml")) as f:
    settings = yaml.safe_load(f)

if __name__ == "__main__":
    print("Settings:", settings)
