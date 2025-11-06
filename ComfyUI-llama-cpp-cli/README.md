
# ComfyUI-llama-cpp-cli

A ComfyUI node pack with two main features:
1. **LLM Text Generation** - Calls a local `llama.cpp` executable with a `.gguf` LLM model
2. **HIPAA-Compliant Audio Transcription with Speaker Diarization** - Transcribes healthcare audio and distinguishes between multiple speakers

## ⚠️ HIPAA Compliance for Healthcare

This audio transcription system is specifically designed for **healthcare applications** with Protected Health Information (PHI).

**Two HIPAA-Compliant Options:**

### Option 1: Local Processing (Whisper.cpp)
- ✅ 100% Local Processing (no cloud services)
- ✅ Zero ongoing costs
- ✅ No Business Associate Agreement needed
- ✅ Works offline
- ✅ Complete data control

### Option 2: Azure AI Cloud (Microsoft Azure)
- ✅ Enterprise-grade accuracy (95-98%)
- ✅ Advanced speaker diarization
- ✅ HIPAA-compliant with BAA
- ✅ Minimal setup required
- ✅ Microsoft-managed infrastructure
- ⚠️ Requires Business Associate Agreement (BAA)
- 💰 $1 per hour of audio

**Both options include:**
- ✅ Audit Logging for PHI access
- ✅ Encrypted output storage
- ✅ Secure file deletion
- ✅ Access control integration

**Documentation:**
- Local processing: [HIPAA_COMPLIANCE.md](ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md)
- Azure AI: [AZURE_HIPAA_SETUP.md](ComfyUI-llama-cpp-cli/AZURE_HIPAA_SETUP.md)

Features:
- No pip packages required for local processing
- Optional Azure AI for best accuracy (requires BAA)
- Works in sandboxed environments (e.g., MimicPC)
- Install via **ComfyUI-Manager → Custom Nodes → Install from Git** (or ZIP)
- Choose local or cloud based on your needs

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

Choose between **Local Processing** (free, local control) or **Azure AI** (best accuracy, requires BAA):

---

#### Option 1: Local Processing Node (No Cloud, No Cost)

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

**Setup:** See [AUDIO_TRANSCRIPTION_SETUP.md](AUDIO_TRANSCRIPTION_SETUP.md) for whisper.cpp installation

---

#### Option 2: Azure AI Cloud Node (Best Accuracy, Requires BAA)

**Node:** "Audio Transcription • Azure AI HIPAA"

**⚠️ CRITICAL:** You MUST sign a Business Associate Agreement (BAA) with Microsoft before using this node.

**Advantages:**
- ✅ 95-98% accuracy (better than local)
- ✅ Advanced speaker diarization
- ✅ Medical terminology support
- ✅ Enterprise-grade reliability
- ✅ Zero infrastructure maintenance

**Requirements:**
- ✅ Azure account with Speech Service
- ✅ Signed BAA with Microsoft (required!)
- ✅ Install: `pip install azure-cognitiveservices-speech`

**Parameters:**
- `audio_path`: Path to PHI audio file
- `azure_speech_key`: Your Azure Speech API key
- `azure_region`: Azure region (e.g., "eastus")
- `user_id`: Unique identifier (REQUIRED)
- `baa_confirmed`: Set to True ONLY after BAA is signed
- `patient_encounter_id`: Patient encounter ID (recommended)
- `num_speakers`: Number of speakers
- `enable_audit_logging`: MUST be True for HIPAA compliance
- `save_encrypted_output`: MUST be True for HIPAA compliance

**Outputs:**
- `transcription`: Full text transcription
- `diarized_text`: Text with speaker labels
- `json_output`: Structured JSON with timestamps
- `security_info`: Security and compliance status

**Example:**
```
audio_path: /secure/phi_audio/encounter_001.wav
azure_speech_key: YOUR_AZURE_KEY
azure_region: eastus
user_id: dr_smith
baa_confirmed: True (ONLY after signing BAA!)
patient_encounter_id: ENC123456
num_speakers: 2
enable_audit_logging: True (REQUIRED)
save_encrypted_output: True (REQUIRED)
```

**Cost:** ~$1.00 per hour of audio

**Setup:** See [AZURE_HIPAA_SETUP.md](AZURE_HIPAA_SETUP.md) for complete Azure setup and BAA instructions

---

#### Secure File Deletion Node

**Node:** "Secure File Deletion • HIPAA Compliant"

Use this node to securely delete PHI files after retention period expires.

**Parameters:**
- `file_path`: Path to file to delete
- `user_id`: User performing deletion
- `confirmation`: Must be True to proceed
- `overwrite_passes`: Number of overwrite passes (default: 3)

**Works with both local and Azure transcriptions.**

---

**Documentation:**
- Local: [HIPAA_COMPLIANCE.md](HIPAA_COMPLIANCE.md) + [AUDIO_TRANSCRIPTION_SETUP.md](AUDIO_TRANSCRIPTION_SETUP.md)
- Azure: [AZURE_HIPAA_SETUP.md](AZURE_HIPAA_SETUP.md)
- Quick Start: [QUICK_START.md](QUICK_START.md)

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
