import os

from datajoint_extension.utils.schema import set_missing_configs

set_missing_configs(file=os.getenv("DJ_CONFIG"))
