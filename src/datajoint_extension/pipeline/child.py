from functools import singledispatch

import datajoint as dj
from datajoint_extension.pipeline.parent import Parent
from datajoint_extension.utils.generic import pkg_abspath
from datajoint_extension.utils.schema import LazySchema

schema = LazySchema()


@singledispatch
def some_schema_requirement(obj):
    return pkg_abspath(obj)


@schema
class Sibling(dj.Manual):
    definition = """
    field2 : VARCHAR(8)
    """


@schema
class Child(dj.Computed):
    definition = """
    -> Parent
    -> Sibling
    path : VARCHAR(512)
    """

    def make(self, key):
        key |= {"path": some_schema_requirement(None)}
        self.insert1(key)
