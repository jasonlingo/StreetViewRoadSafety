import yaml

with open("../config/config.yaml") as stream:
    try:
        CONFIG = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print "Loading config file failed!"
        raise