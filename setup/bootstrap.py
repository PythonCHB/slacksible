#! /Users/jhefner/python_dev/uw_python/project/bin/python

import os
import sys
import logging


"""
$ export ara_location=$(python -c "import os,ara; print(os.path.dirname(ara.__file__))")
$ cat > ansible.cfg <<EOF
[defaults]
# callback_plugins configuration is required for the ARA callback
callback_plugins = $ara_location/plugins/callbacks

# action_plugins and library configuration is required for the ara_record and ara_read modules
action_plugins = $ara_location/plugins/actions
library = $ara_location/plugins/modules
EOF


"""

def main():
    pass


if __name__ == '__main__':
    main()