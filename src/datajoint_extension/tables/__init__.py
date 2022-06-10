"""
Import important tables.
"""


from datajoint_extension.pipeline.child import Child, Sibling
from datajoint_extension.pipeline.child import schema as child_schema
from datajoint_extension.pipeline.parent import Parent
from datajoint_extension.pipeline.parent import schema as parent_schema

parent_schema.activate()
child_schema.activate()

__all__ = [
    "Parent",
    "Child",
    "Sibling"
]
