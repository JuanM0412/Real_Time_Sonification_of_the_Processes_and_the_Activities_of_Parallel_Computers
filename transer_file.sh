#!/bin/bash

# Variables
CONNECTOR="apolo"
REMOTE_FILE="/home/jmgomezp/sound/cpu_usage_output.txt"
PY_SCRIPT_PATH="/home/jmgomezp/sound"
PY_SCRIPT="cpu.py"
LOCAL_DIR="$HOME"
NODES=$1
TIMES=$2

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
