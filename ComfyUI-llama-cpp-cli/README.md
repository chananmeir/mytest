
# ComfyUI-llama-cpp-cli

A ComfyUI node pack with two main features:
1. **LLM Text Generation** - Calls a local `llama.cpp` executable with a `.gguf` LLM model
2. **Audio Transcription with Speaker Diarization** - Transcribes audio and distinguishes between multiple speakers

Features:
- No pip packages required for basic functionality
- Works in sandboxed environments (e.g., MimicPC)
- Install via **ComfyUI-Manager → Custom Nodes → Install from Git** (or ZIP)
- Optional advanced features with pip packages for enhanced audio transcription

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

### Audio Transcription with Speaker Diarization

**Two nodes available:**

#### 1. Basic Audio Transcription (No pip packages required)
- Add node **"Audio Transcription • Basic (CLI)"**
- Set `audio_path` to your audio file (WAV format)
- Set `num_speakers` to the number of people speaking
- Enable/disable `enable_diarization` for speaker detection
- Outputs:
  - `transcription`: Full text without speaker labels
  - `diarized_text`: Text with speaker labels (Speaker 1, Speaker 2, etc.)

#### 2. Advanced Audio Transcription (Requires pip packages)
- Install dependencies: `pip install -r requirements.txt`
- Get HuggingFace token from https://huggingface.co/settings/tokens
- Accept conditions: https://huggingface.co/pyannote/speaker-diarization-3.1
- Add node **"Audio Transcription • Advanced (Python)"**
- Set `audio_path`, `whisper_model`, `num_speakers`
- Enter your `huggingface_token`
- Outputs:
  - `transcription`: Full text
  - `diarized_text`: Text with accurate speaker labels
  - `json_output`: Structured JSON with timestamps and speakers

**For detailed audio transcription setup, see [AUDIO_TRANSCRIPTION_SETUP.md](AUDIO_TRANSCRIPTION_SETUP.md)**

---

## Troubleshooting

### LLM Issues
- If you see "binary not found", fix the `llama_bin` path.
- If you see "model not found", fix `model_path`.
- If llama.cpp returns an error, the node will pass it through so you can see it.

### Audio Transcription Issues
- **Basic Node**: Ensure whisper.cpp is compiled and paths are correct
- **Advanced Node**: Install required packages with `pip install -r requirements.txt`
- **Speaker Detection**: Use Advanced node for better accuracy
- See [AUDIO_TRANSCRIPTION_SETUP.md](AUDIO_TRANSCRIPTION_SETUP.md) for detailed troubleshooting
