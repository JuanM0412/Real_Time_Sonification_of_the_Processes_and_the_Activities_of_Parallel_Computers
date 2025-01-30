#!/bin/bash

# Variables
CONNECTOR=""
REMOTE_FILE=""
PY_SCRIPT_PATH=""
PY_SCRIPT=""
LOCAL_DIR=""
NODES=$1 # argv[1]
TIMES=$2 # argv[2]

# Run the Python script on APOLO
ssh -tt $CONNECTOR << EOF
cd $PY_SCRIPT_PATH
python3 $PY_SCRIPT --nodes=$NODES --times=$TIMES
exit
EOF

# Transfer the file using SFTP
sftp $CONNECTOR << EOF
get $REMOTE_FILE $LOCAL_DIR
exit
EOF

echo "Done"
