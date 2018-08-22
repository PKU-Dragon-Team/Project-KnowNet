"""Example of acceptable schema.

# naming style:

- name: "docset"
- property: "$title"
- operator: ConfigOpType.TYPE
- wildcard: "@*"
"""

from data_platform.config import ConfigOpType

schema = {
    "pre_init": {
        "$optional": True,  # optional
        "type": {},  # empty means only check existance
        "protocol": {
            "$optional": True  # if optional, use $optional tag
        }
    },
    "init": {
        "location": {
            "$default": "",  # default value
            "$condition": {  # conditions using $condition tag
                ConfigOpType.TYPE: str  # TYPE check isinstance
            }
        },
        "port": {
            "$optional": True,
            "$condition": {
                ConfigOpType.TYPE: int,
                ConfigOpType.RANGE: (  # RANGE accept a tuple
                    0, 65535)
            }
        },
    },
    "post_init": {
        "$optional": True,  # optional
        "@*": {  # wildcard is used to check inner subtree without checking the name
            "$condition": {
                ConfigOpType.FUNCTION: lambda node: 'banned' not in node  # FUNCTION accept any one argument function
            }
        }
    }
}
