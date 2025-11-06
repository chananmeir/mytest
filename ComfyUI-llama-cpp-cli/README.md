
# ComfyUI-llama-cpp-cli

A ComfyUI node pack with two main features:
1. **LLM Text Generation** - Calls a local `llama.cpp` executable with a `.gguf` LLM model
2. **HIPAA-Compliant Audio Transcription with Speaker Diarization** - Transcribes healthcare audio and distinguishes between multiple speakers

## ⚠️ HIPAA Compliance for Healthcare

This audio transcription system is specifically designed for **healthcare applications** with Protected Health Information (PHI).

**Key HIPAA Features:**
- ✅ 100% Local Processing (no cloud services)
- ✅ Audit Logging for PHI access
- ✅ Encrypted output storage
- ✅ Secure file deletion
- ✅ No external API calls
- ✅ Access control integration

**For healthcare users, see [HIPAA_COMPLIANCE.md](ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md) before deployment.**

Features:
- No pip packages required for basic functionality
- Works in sandboxed environments (e.g., MimicPC)
- Install via **ComfyUI-Manager → Custom Nodes → Install from Git** (or ZIP)
- HIPAA-compliant local processing for healthcare PHI

## Install (from Git)

1. Create a GitHub repo named **ComfyUI-llama-cpp-cli**.
2. Upload all files from this ZIP to the repo root.
3. In ComfyUI, open **Manager → Custom Nodes → Install from Git** and paste your repo URL.
4. Restart ComfyUI.

## Install (from ZIP)

1. In ComfyUI, open **Manager → Custom Nodes → Install from ZIP**, select this ZIP.
2. Restart ComfyUI.

## Expected files on disk

### For LLM Text Generation:
- llama binary (executable): `/models/llm/llama`
- gguf model: `/models/llm/mistral-7b-instruct-v0.1.Q4_0.gguf`

### For Audio Transcription (Basic):
- whisper.cpp binary: `/models/audio/whisper.cpp`
- whisper model: `/models/audio/ggml-base.en.bin`

> You can override all paths on the node inputs.

---

## Usage

### LLM Text Generation

1. Add node **"LLM • llama.cpp (CLI)"** (search `LlamaCppCLINode`).
2. Enter a prompt; adjust `max_tokens` if needed.
3. (Optional) Set `llama_bin` and `model_path` if your paths differ.
4. Connect the output `text` anywhere you want (e.g., into a prompt builder).

### Audio Transcription with Speaker Diarization (HIPAA-Compliant)

⚠️ **For Healthcare PHI Processing**

#### HIPAA-Compliant Audio Transcription Node

**Node:** "Audio Transcription • HIPAA Compliant"

**Required for HIPAA Compliance:**
- ✅ 100% local processing (no cloud services)
- ✅ Audit logging enabled
- ✅ Encrypted output storage
- ✅ User ID and encounter tracking
- ✅ No internet connectivity during processing

**Parameters:**
- `audio_path`: Path to PHI audio file
- `user_id`: Unique identifier of user accessing PHI (REQUIRED)
- `patient_encounter_id`: Patient encounter ID (recommended)
- `num_speakers`: Number of speakers (e.g., doctor + patient = 2)
- `enable_audit_logging`: MUST be True for HIPAA compliance
- `save_encrypted_output`: MUST be True for HIPAA compliance

**Outputs:**
- `transcription`: Full text transcription
- `diarized_text`: Text with speaker labels (Speaker 1, Speaker 2, etc.)
- `security_info`: Security status and audit information

**Example:**
```
audio_path: /secure/phi_audio/encounter_001.wav
user_id: dr_smith
patient_encounter_id: ENC123456
num_speakers: 2
enable_audit_logging: True (REQUIRED)
save_encrypted_output: True (REQUIRED)
```

#### Secure File Deletion Node

**Node:** "Secure File Deletion • HIPAA Compliant"

Use this node to securely delete PHI files after retention period expires.

**Parameters:**
- `file_path`: Path to file to delete
- `user_id`: User performing deletion
- `confirmation`: Must be True to proceed
- `overwrite_passes`: Number of overwrite passes (default: 3)

**IMPORTANT:** See [HIPAA_COMPLIANCE.md](ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md) for complete deployment requirements.

**For detailed setup, see:**
- [HIPAA_COMPLIANCE.md](ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md) - HIPAA compliance requirements
- [AUDIO_TRANSCRIPTION_SETUP.md](ComfyUI-llama-cpp-cli/AUDIO_TRANSCRIPTION_SETUP.md) - Technical setup

---

## Troubleshooting

### LLM Issues
- If you see "binary not found", fix the `llama_bin` path.
- If you see "model not found", fix `model_path`.
- If llama.cpp returns an error, the node will pass it through so you can see it.

### Audio Transcription Issues (HIPAA-Compliant)
- **Whisper.cpp not found**: Ensure whisper.cpp is compiled and installed at `/models/audio/whisper.cpp`
- **Audit logging failed**: Ensure `/secure` directory exists with proper permissions (0o700)
- **Encryption failed**: Check write permissions on `/secure/transcriptions`
- **Network access detected**: Ensure system is on isolated network with no internet
- **For detailed troubleshooting**: See [HIPAA_COMPLIANCE.md](HIPAA_COMPLIANCE.md)

### HIPAA Compliance Issues
- **For all HIPAA-related questions**: Consult [HIPAA_COMPLIANCE.md](HIPAA_COMPLIANCE.md)
- **For technical setup**: See [AUDIO_TRANSCRIPTION_SETUP.md](AUDIO_TRANSCRIPTION_SETUP.md)
- **For legal compliance**: Consult your healthcare compliance attorney
