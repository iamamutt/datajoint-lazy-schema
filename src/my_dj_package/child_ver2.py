from pathlib import Path

import datajoint as dj
from datajoint_extension.pipeline.parent import Parent
from datajoint_extension.pipeline.parent import schema as parent_schema
from datajoint_extension.utils.schema import LazySchema

# new schema will have the same prefix defined in dj.config
schema = LazySchema()


# don't want to depend on sibling
@schema
class Child(dj.Computed):
    definition = """
    -> Parent
    path : VARCHAR(512)
    """

    def make(self, key):
        key |= {"path": Path.home()}
        self.insert1(key)


parent_schema.activate()
schema.activate()
