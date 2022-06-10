import datajoint as dj
from datajoint_extension.utils.schema import LazySchema

# Argument to LazySchema is optional. If it's empty and:
# if "workflow" is defined in dj.config, use that as the database prefix,
# otherwise use the package import name as the prefix.
# the module name ("parent") will be appended to the prefix, sep='_'.
schema = LazySchema()


@schema
class Parent(dj.Manual):
    definition = """
    field : VARCHAR(8)
    """
