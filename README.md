# gio-sat-transponder
This repository will have the details of the code and hardware requerd to be used with liniar transponder
Proposed communication protocol stack

 <img src="New_QO_100_sat.jpg" alt="laers" > 

[SIP PBX] <-> [VoIP Gateway/Linux PC] <-> [Codec2/FreeDV or G.729 Encoder] <-> [Modem + RF] <-> [Remote Node]
PROTOCOL STACK (Simplified)

 <img src="new_gio_1.jpg" alt="laers" > 
|Layer           |Function                          |Protocol/Tech             |<br>
|Application     |SIP call control + voice data     |SIP, RTP, SIP proxy       |<br>
|Transport       |Real-time transport of audio      |UDP                       |<br>
|Codec           |Compresses audio to fit narrowband|Codec2, G.729, Opus       |<br>
|Framing         |Frames data for modem             |SLIP, KISS, custom framing|<br>
|Modulation      |Converts digital to analog RF     |BPSK, QPSK, 16-QAM        |<br>
|RF Physical     |Transmit over the 333 kHz channel |Custom/SDR/Analog RF      |<br>
## HARDWARE SETUP OPTIONS
Option A: Using PC + SDR (Software-Defined Radio)<br>
## 🖥️ At SIP PBX side:<br>
    • Software:<br>
        ◦ SIP server (Asterisk, FreeSWITCH)<br>
        ◦ Softphone (Linphone, Zoiper) or SIP client daemon<br>
        ◦ FreeDV or Codec2 encoder (freedv_tx, c2enc)<br>
    • RF Interface:<br>
        ◦ SDR device (e.g., HackRF, LimeSDR, PlutoSDR)<br>
        ◦ GNU Radio or freedv modem integration<br>
## 📻 At RF side:<br>
    • Use GNU Radio flow graph to:
        ◦ Modulate compressed audio (BPSK or QPSK)
        ◦ Keep channel usage under 333 kHz
        ◦ Handle framing, preamble, sync
## Example SDR flow graph:<br>
    • Codec2 Input (1400 bps)
    • BPSK Modulator
    • Root Raised Cosine Filter
    • Transmit via SDR (333 kHz bandwidth)

## 🛠️ Option B: Embedded Setup (Low-power field unit)
    • Raspberry Pi or ESP32 for codec and packet logic
    • G.729 or Codec2 running via linphonec or freedv
    • Modem:
        ◦ Custom FSK/PSK modem via Si4463 or CC1101 (with 300–500 kbps modes)
        ◦ RF front-end tuned for your channel (e.g., 433 MHz/868 MHz/2.4 GHz)
    • Power:
        ◦ LiFePO4 battery + solar panel
    • Antenna:
        ◦ Helical or yagi for link reliability

📞 4. SOFTWARE COMPONENTS (SIP + VOIP + RF)
🖥️ On Linux PC (SIP Gateway):

# Install SIP client and audio tool
sudo apt install linphone-cli sox freedv gstreamer1.0-tools

# SIP call to destination (auto-answer mode)
linphonec -c /path/to/config -a -s sip:1002@pbx.server

# Pipe audio to Codec2 encoder
linphonec > pipe | sox -t raw -r 8k -e signed -b 16 -c 1 - -t raw -r 8k -e signed -b 16 -c 1 - | c2enc 1400 - - | modem_tx

Replace modem_tx with your SDR or RF module interface script.
## 📡 Modem (e.g., GNU Radio or Embedded)
    • Sample baud rate: 20–60 kbps
    • Use differential BPSK or QPSK
    • Frame structure:
        ◦ [Preamble][Sync Word][Header][Compressed Voice][CRC]

## 📶 5. EXAMPLE: Using Codec2 + FreeDV over RF
You can use FreeDV mode 700D or 1600 (700–1600 bps), perfect for 333 kHz:
freedv_tx 700D mic_input.raw > /dev/ttyUSB0
Or with freedv-gui (audio + waterfall + modem all-in-one).

## 📜 6. Summary Table

Component
Tech/Tool
SIP PBX
Asterisk or FreeSWITCH
VoIP Codec
Codec2 (700D, 1300, 1600) or G.729
Audio Interface
ALSA, SoX, GStreamer
Modulation
BPSK/QPSK/16-QAM
Radio Interface
SDR (HackRF, LimeSDR) or CC1101
Bandwidth Used
2.4–32 kbps payload + framing, well within 333 kHz
Full Duplex Mode
TDD switching or dual RF links

Shell script exsample
#!/bin/bash
# Description: End-to-end SIP VoIP over RF using Codec2 and FreeDV modem
# Requirements: linphonec, sox, freedv, asterisk (optional), rtl_sdr/hackrf, gnuradio, codec2
# ---- CONFIG ----
SIP_USER="1001"
SIP_PASS="your_password"
SIP_DOMAIN="your.sipserver.local"
REMOTE_USER="1002"
CODEC_MODE="700D"  # Options: 700D, 1600, 1300

# Audio paths
AUDIO_INPUT="/tmp/mic_in.raw"
CODEC_OUT="/tmp/codec2_out.bin"
RF_STREAM="/tmp/rf_stream.bin"
# ---- START SIP CALL ----
echo "Starting SIP call with $REMOTE_USER@$SIP_DOMAIN"
linphonecsh init
linphonecsh generic 'register --host $SIP_DOMAIN --username $SIP_USER --password $SIP_PASS'
linphonecsh generic "call sip:$REMOTE_USER@$SIP_DOMAIN"
# ---- CAPTURE AUDIO FROM CALL ----
# Assumes audio is routed via PulseAudio or ALSA virtual device
arecord -f S16_LE -r 8000 -c 1 -t raw > "$AUDIO_INPUT" &
REC_PID=$!
# ---- ENCODE AUDIO WITH CODEC2 ----
echo "Encoding with Codec2 - Mode $CODEC_MODE"
c2enc "$CODEC_MODE" "$AUDIO_INPUT" "$CODEC_OUT" &
ENC_PID=$!
# ---- MODULATE AND TRANSMIT OVER RF ----
# Replace below with your SDR or GNU Radio transmitter command
echo "Transmitting via GNU Radio/SDR..."
cat "$CODEC_OUT" | ./modem_tx_gnuradio.py &
TX_PID=$!
# Wait until call ends or interrupted
trap "kill $REC_PID $ENC_PID $TX_PID; linphonecsh generic 'terminate'; linphonecsh exit" INT
wait

he script and GNU Radio flowgraphs are now separated into clear code blocks:
    1. 🖥️ Shell script for SIP call and Codec2 audio piping.
       
    2. 📡 GNU Radio TX flowgraph for BPSK modulation.
    3. 📻 GNU Radio RX flowgraph for BPSK demodulation.
## Feed the received file /tmp/codec2_rx.bit into a Codec2 decoder to listen to the audio.

🔧 Install Codec2 tools (if not already):

     sudo apt install codec2
🔄 Decode to WAV:

     c2dec 1300 /tmp/codec2_rx.bit -o /tmp/codec2_rx.wav
     aplay /tmp/codec2_rx.wav
Replace 1300 with 700C, 1600, etc., depending on your Codec2 bitrate.
## Step 2: Real-Time Audio Over GFSK (Send + Receive)
This replaces the File Source/Sink with live audio + UDP to integrate with SIP or VoIP.
### 🎙 TX Side: Live Microphone to GFSK

Replace File Source with a UDP Source block.

        Host: 127.0.0.1
        Port: 12345
        Type: Byte
 <img src="pluto_tx.jpg" alt="pluto_tx" > 
        
### Start a shell tool that encodes your mic into Codec2 and sends to that port:
        arecord -f S16_LE -r 8000 -t raw | c2enc 1300 - - | nc -u 127.0.0.1 12345
### 🎧 RX Side: GFSK to Speaker

Replace File Sink with UDP Sink:

        Host: 127.0.0.1
        Port: 12346
        Type: Byte
On the receiver:
        
<img src="pluto_rx.jpg" alt="pluto_tx" > 

      nc -ul 12346 | c2dec 1300 - - | aplay -f S16_LE -r 8000
## Step 3: Add CRC and Packet Framing
To improve reliability over RF, wrap Codec2 frames with a simple protocol.
###🛠 Add in GNU Radio:
Use Packet Encoder and Packet Decoder blocks.<br>
Use CRC32 for error detection.<br>
Set payload size to match Codec2 frame (e.g., 7 bytes for 1300 bit/s every 40ms).<br>
###📦 Block Chain (TX):

       UDP Source → Packet Encoder (7 bytes) → GFSK Mod → Pluto Sink
###📦 Block Chain (RX):

      Pluto Source → GFSK Demod → Packet Decoder → UDP Sink
## 🎁 TX (Framing) Side Blocks
1. Protocol Formatter

    Found under: digital/protocols

    Used to create tagged frames.

    Formatter Object: packet_utils.default_formatter(pmt.intern("packet_len"))

    This will tag each packet with its length.
