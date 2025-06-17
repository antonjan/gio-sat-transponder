## 1. Shell Script for Linux SIP + Codec2 + RF Transmission Pipeline

```bash
#!/bin/bash

# File: sip_to_rf.sh
# Define SIP call target and audio pipes
SIP_TARGET="sip:1002@192.168.1.100"
CODEC2_MODE=1300

# Start SIP softphone (linphonec) in background
linphonecsh init
linphonecsh dial $SIP_TARGET

# Wait for call to connect
sleep 5

# Record audio from SIP and encode to Codec2
arecord -f S16_LE -c1 -r8000 -t raw | \
  c2enc $CODEC2_MODE - - | \
  ./modem_tx

# On exit
linphonecsh hangup
linphonecsh exit
