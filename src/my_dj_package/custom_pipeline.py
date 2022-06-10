from datajoint_extension.pipeline.child import some_schema_requirement
from datajoint_extension.tables import Child, Parent, Sibling


# register the below function to be called when the function in
# datajoint_extension.pipeline.child has None as the input type
@some_schema_requirement.register
def _some_schema_requirement(obj: None):
    return "some/different/path"
