# Quick Start Guide - HIPAA-Compliant Audio Transcription

This guide will get you up and running with the HIPAA-compliant audio transcription system.

---

## Overview

This system transcribes audio recordings (e.g., doctor-patient conversations) and identifies different speakers, all while maintaining HIPAA compliance for healthcare PHI.

---

## Installation Steps

### Step 1: Install ComfyUI (if not already installed)

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Run ComfyUI
python main.py
```

ComfyUI will start a web server (usually at http://127.0.0.1:8188)

### Step 2: Install This Node Pack

**Option A: From Git (Recommended)**

1. In ComfyUI web interface, open **Manager → Install Custom Nodes**
2. Click **Install from Git URL**
3. Enter your repository URL: `https://github.com/YOUR_USERNAME/mytest.git`
4. Click Install
5. Restart ComfyUI

**Option B: Manual Installation**

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/YOUR_USERNAME/mytest.git ComfyUI-llama-cpp-cli
cd ComfyUI-llama-cpp-cli
# Restart ComfyUI
```

### Step 3: Install Whisper.cpp (for local transcription)

```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Compile
make

# Download a model (base.en is good for English)
bash ./models/download-ggml-model.sh base.en

# The compiled binary is at: ./main
# The model is at: ./models/ggml-base.en.bin
```

### Step 4: Set Up Secure Directories

```bash
# Create secure directories for PHI
sudo mkdir -p /secure/phi_audio
sudo mkdir -p /secure/transcriptions
sudo mkdir -p /secure

# Set strict permissions (only owner can access)
sudo chmod 700 /secure
sudo chmod 700 /secure/phi_audio
sudo chmod 700 /secure/transcriptions

# Create directory for models
sudo mkdir -p /models/audio
```

### Step 5: Install Whisper Binary and Model

```bash
# Copy whisper.cpp binary
sudo cp whisper.cpp/main /models/audio/whisper.cpp
sudo chmod 755 /models/audio/whisper.cpp

# Copy model
sudo cp whisper.cpp/models/ggml-base.en.bin /models/audio/
sudo chmod 644 /models/audio/ggml-base.en.bin
```

### Step 6: Verify Installation

```bash
# Test whisper.cpp
/models/audio/whisper.cpp --help

# Check directories
ls -la /secure
ls -la /models/audio
```

---

## Basic Usage

### Method 1: Using ComfyUI Interface (Recommended for Beginners)

1. **Start ComfyUI:**
   ```bash
   cd ComfyUI
   python main.py
   ```

2. **Open web browser:** Go to http://127.0.0.1:8188

3. **Add the transcription node:**
   - Right-click on canvas → **Add Node**
   - Navigate to **Healthcare/PHI** → **Audio Transcription • HIPAA Compliant**

4. **Configure the node:**
   - `audio_path`: Path to your audio file (e.g., `/secure/phi_audio/recording.wav`)
   - `user_id`: Your user ID (e.g., `dr_smith`)
   - `patient_encounter_id`: Patient encounter ID (e.g., `ENC123456`)
   - `num_speakers`: How many people are speaking (e.g., `2` for doctor + patient)
   - `enable_audit_logging`: Set to `True` (REQUIRED for HIPAA)
   - `save_encrypted_output`: Set to `True` (REQUIRED for HIPAA)

5. **Run the workflow:**
   - Click **Queue Prompt** button
   - Wait for processing to complete
   - View outputs in the node

6. **View results:**
   - `transcription`: The full transcription text
   - `diarized_text`: Transcription with speaker labels
   - `security_info`: Security status and audit information

### Method 2: Using Python Script (Advanced)

Create a Python script to use the node directly:

```python
import sys
sys.path.append('/path/to/ComfyUI/custom_nodes/ComfyUI-llama-cpp-cli')

from audio_transcribe import AudioTranscriptionHIPAANode

# Create node instance
node = AudioTranscriptionHIPAANode()

# Transcribe audio
result = node.transcribe_hipaa(
    audio_path="/secure/phi_audio/recording.wav",
    user_id="dr_smith",
    patient_encounter_id="ENC123456",
    num_speakers=2,
    enable_diarization=True,
    enable_audit_logging=True,
    save_encrypted_output=True
)

# Get results
transcription, diarized_text, security_info = result

# Print results
print("=== TRANSCRIPTION ===")
print(transcription)
print("\n=== DIARIZED (WITH SPEAKERS) ===")
print(diarized_text)
print("\n=== SECURITY INFO ===")
print(security_info)
```

Run it:
```bash
python transcribe_audio.py
```

---

## Example Workflow

### Scenario: Doctor-Patient Consultation

1. **Record consultation audio:**
   - Save as WAV file: `/secure/phi_audio/consultation_20251106.wav`

2. **Transcribe with ComfyUI:**
   - Set `audio_path`: `/secure/phi_audio/consultation_20251106.wav`
   - Set `user_id`: `dr_johnson`
   - Set `patient_encounter_id`: `ENC789012`
   - Set `num_speakers`: `2` (doctor + patient)
   - Enable audit logging: `True`
   - Enable encrypted output: `True`

3. **Review output:**
   ```
   === HIPAA-COMPLIANT TRANSCRIPTION WITH SPEAKER DIARIZATION ===
   Speakers detected: 2
   Processing method: Local only (no cloud services)
   ======================================================================

   [Speaker 1] [00:00:00.000 --> 00:00:05.000]
   Good morning, how are you feeling today?

   [Speaker 2] [00:00:05.000 --> 00:00:10.000]
   I've been experiencing chest pain for the past few days.

   [Speaker 1] [00:00:10.000 --> 00:00:15.000]
   Can you describe the pain? Is it sharp or dull?

   [Speaker 2] [00:00:15.000 --> 00:00:20.000]
   It's more of a dull, pressing sensation.
   ```

4. **Encrypted output saved at:**
   - `/secure/transcriptions/transcription_dr_johnson_20251106_100530.txt`

5. **Audit log entry created at:**
   - `/secure/phi_audit.log`

---

## Understanding the Outputs

### Output 1: Transcription
- Plain text transcription without speaker labels
- Useful for quick reading or text analysis
- Example: "Good morning, how are you feeling today? I've been experiencing..."

### Output 2: Diarized Text
- Transcription with speaker labels (Speaker 1, Speaker 2, etc.)
- Includes timestamps for each segment
- Formatted for clinical documentation
- Example: "[Speaker 1] [00:00:00 --> 00:00:05] Good morning..."

### Output 3: Security Info
- Compliance status
- Audit logging confirmation
- File locations
- User information
- Example:
  ```
  ✓ Audit logging enabled
  ✓ Local processing verified
  ✓ Encrypted output saved: /secure/transcriptions/...
  ✓ Transcription completed successfully
  ✓ Processed 45 audio segments
  ✓ User: dr_smith
  ✓ Encounter ID: ENC123456
  ```

---

## Common Audio Formats

### Supported Formats:
- **WAV** (recommended) - Best quality, no compression
- MP3 - Supported but may have quality loss
- FLAC - Lossless compression, good quality
- M4A - Supported

### Converting Audio to WAV:

**Using FFmpeg:**
```bash
# Install ffmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
# or
brew install ffmpeg  # macOS

# Convert MP3 to WAV
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav

# Convert M4A to WAV
ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav

# Convert any format to optimal WAV
ffmpeg -i input.* -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

**Parameters explained:**
- `-ar 16000`: Sample rate 16kHz (good for speech)
- `-ac 1`: Mono channel
- `-c:a pcm_s16le`: 16-bit PCM encoding

---

## Secure File Deletion

After the retention period expires, securely delete PHI files:

### Using ComfyUI:

1. Add node: **Healthcare/PHI → Secure File Deletion • HIPAA Compliant**
2. Configure:
   - `file_path`: Path to file to delete
   - `user_id`: Your user ID
   - `confirmation`: Set to `True`
   - `overwrite_passes`: Number of overwrites (default: 3)
3. Run workflow

### Using Python:

```python
from audio_transcribe import SecureDeletionNode

node = SecureDeletionNode()
result = node.secure_delete(
    file_path="/secure/phi_audio/old_recording.wav",
    user_id="dr_smith",
    confirmation=True,
    overwrite_passes=3
)

print(result)
```

---

## Viewing Audit Logs

Audit logs are stored in JSON format at `/secure/phi_audit.log`

### View recent audit events:

```bash
# View last 10 entries
tail -n 10 /secure/phi_audit.log | python -m json.tool

# Search for specific user
grep "dr_smith" /secure/phi_audit.log | python -m json.tool

# Search for deletions
grep "DELETE" /secure/phi_audit.log | python -m json.tool
```

### Example audit log entry:

```json
{
  "timestamp": "2025-11-06T10:30:15.123456",
  "event_type": "TRANSCRIBE_START",
  "file_identifier": "a3b5c7d9e1f2g3h4",
  "user_id": "dr_smith",
  "details": "Encounter: ENC123456, Speakers: 2",
  "node_version": "1.0.0"
}
```

---

## Troubleshooting

### Problem: "Whisper.cpp binary not found"

**Solution:**
```bash
# Check if binary exists
ls -la /models/audio/whisper.cpp

# If not, copy it
sudo cp /path/to/whisper.cpp/main /models/audio/whisper.cpp
sudo chmod 755 /models/audio/whisper.cpp
```

### Problem: "Whisper model not found"

**Solution:**
```bash
# Check if model exists
ls -la /models/audio/ggml-base.en.bin

# If not, download and copy it
cd whisper.cpp
bash ./models/download-ggml-model.sh base.en
sudo cp models/ggml-base.en.bin /models/audio/
```

### Problem: "Audit logging failed"

**Solution:**
```bash
# Create secure directory
sudo mkdir -p /secure
sudo chmod 700 /secure

# Check permissions
ls -la /secure

# Create audit log file
sudo touch /secure/phi_audit.log
sudo chmod 600 /secure/phi_audit.log
```

### Problem: "Audio file not found"

**Solution:**
```bash
# Check file path is correct
ls -la /secure/phi_audio/recording.wav

# Copy your audio file
sudo cp /path/to/your/audio.wav /secure/phi_audio/
```

### Problem: "Permission denied"

**Solution:**
```bash
# Change ownership to your user
sudo chown -R $USER:$USER /secure
sudo chown -R $USER:$USER /models/audio

# Or run with sudo (not recommended)
sudo python main.py
```

### Problem: Poor transcription quality

**Solutions:**
1. **Use better model:**
   ```bash
   # Download larger model
   cd whisper.cpp
   bash ./models/download-ggml-model.sh medium.en
   sudo cp models/ggml-medium.en.bin /models/audio/
   ```

   Then set `model_path` to `/models/audio/ggml-medium.en.bin`

2. **Improve audio quality:**
   - Use better microphone
   - Reduce background noise
   - Ensure clear speech
   - Convert to optimal format:
     ```bash
     ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
     ```

3. **Try different language:**
   - Set `language` parameter (e.g., `"es"` for Spanish, `"fr"` for French)

### Problem: Speaker diarization not accurate

**Current Status:**
The basic implementation uses simple speaker alternation. For better accuracy:

1. **Improve in future:**
   - Implement energy-based clustering
   - Add pitch analysis
   - Use locally-hosted pyannote.audio models

2. **Workaround:**
   - Manually review and correct speaker labels
   - Use clear audio with distinct speakers
   - Ensure speakers don't talk over each other

---

## Performance Tips

### Speed up transcription:

1. **Use smaller model for faster processing:**
   - `tiny.en` - Fastest, lower accuracy
   - `base.en` - Good balance (default)
   - `small.en` - Better accuracy, slower
   - `medium.en` - High accuracy, much slower
   - `large` - Best accuracy, very slow

2. **Use more CPU threads:**
   Modify `audio_transcribe.py` line 312:
   ```python
   "-t", "8",  # Increase to match your CPU cores
   ```

3. **Use GPU acceleration:**
   Compile whisper.cpp with CUDA support:
   ```bash
   cd whisper.cpp
   make clean
   WHISPER_CUDA=1 make
   ```

---

## Example Use Cases

### Use Case 1: Telemedicine Consultation
```
audio_path: /secure/phi_audio/telemedicine_20251106.wav
user_id: dr_virtual_care
patient_encounter_id: TELE123456
num_speakers: 2 (doctor + patient)
```

### Use Case 2: Therapy Session
```
audio_path: /secure/phi_audio/therapy_session_20251106.wav
user_id: therapist_jones
patient_encounter_id: THER789012
num_speakers: 2 (therapist + client)
```

### Use Case 3: Medical Team Meeting
```
audio_path: /secure/phi_audio/team_meeting_20251106.wav
user_id: dr_team_lead
patient_encounter_id: CASE345678
num_speakers: 5 (multiple doctors discussing case)
```

### Use Case 4: Patient Interview
```
audio_path: /secure/phi_audio/intake_interview_20251106.wav
user_id: nurse_intake
patient_encounter_id: INT901234
num_speakers: 2 (nurse + patient)
```

---

## Important Reminders

### ⚠️ BEFORE Production Use:

1. **Read HIPAA_COMPLIANCE.md** - Critical requirements
2. **Implement production encryption** - Replace placeholder
3. **Isolate network** - No internet during PHI processing
4. **Get legal review** - Healthcare compliance attorney
5. **Train staff** - HIPAA procedures and compliance
6. **Test thoroughly** - With non-PHI data first

### ✅ Best Practices:

1. **Always enable audit logging** - Set to `True`
2. **Always save encrypted output** - Set to `True`
3. **Use descriptive user IDs** - e.g., `dr_smith` not `user1`
4. **Link to patient encounters** - Always provide `patient_encounter_id`
5. **Review transcriptions** - Human review for accuracy
6. **Secure deletion** - Delete after retention period
7. **Regular audits** - Review audit logs monthly
8. **Keep backups** - Encrypted backups of all data

---

## Getting Help

### Documentation:
- **This file (QUICK_START.md)** - Basic usage
- **HIPAA_COMPLIANCE.md** - Full compliance guide
- **AUDIO_TRANSCRIPTION_SETUP.md** - Technical setup details
- **README.md** - Overview and installation

### Support:
- Check documentation first
- Review troubleshooting section
- For HIPAA questions: Consult your compliance officer
- For legal questions: Consult healthcare attorney

---

## Next Steps

1. ✅ Complete installation steps above
2. ✅ Test with sample (non-PHI) audio file
3. ✅ Review HIPAA_COMPLIANCE.md thoroughly
4. ✅ Implement production encryption
5. ✅ Configure network security
6. ✅ Get legal/compliance approval
7. ✅ Train staff on procedures
8. ✅ Deploy with real PHI data

---

## Quick Reference

### File Locations:
```
/models/audio/whisper.cpp          - Whisper binary
/models/audio/ggml-base.en.bin     - Whisper model
/secure/phi_audio/                 - Input audio files (PHI)
/secure/transcriptions/            - Output transcriptions (PHI)
/secure/phi_audit.log              - Audit log
```

### Required Node Parameters:
```
audio_path: /secure/phi_audio/recording.wav
user_id: dr_smith
patient_encounter_id: ENC123456
enable_audit_logging: True (REQUIRED)
save_encrypted_output: True (REQUIRED)
```

### Commands:
```bash
# Start ComfyUI
python main.py

# View audit logs
tail -f /secure/phi_audit.log

# Test whisper.cpp
/models/audio/whisper.cpp --help

# Convert audio to WAV
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

---

**You're now ready to use the HIPAA-compliant audio transcription system!**

Remember: Always prioritize patient privacy and HIPAA compliance. When in doubt, consult your compliance team.
