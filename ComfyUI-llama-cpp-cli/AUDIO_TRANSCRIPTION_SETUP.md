# Audio Transcription Setup Guide

This guide explains how to set up audio transcription with speaker diarization (distinguishing between multiple speakers).

## Two Options Available

### Option 1: Basic Audio Transcription (No pip packages required)
- Uses **whisper.cpp** CLI (similar to llama.cpp approach)
- Works in sandboxed environments
- Simple speaker assignment (alternating or basic heuristics)
- **Recommended for:** Users who want minimal dependencies

### Option 2: Advanced Audio Transcription (Requires pip packages)
- Uses **OpenAI Whisper** + **pyannote.audio**
- Best-in-class speaker diarization
- More accurate speaker detection
- **Recommended for:** Users who want the highest quality results

---

## Option 1: Basic Setup (whisper.cpp)

### Prerequisites

1. **Download and compile whisper.cpp**

```bash
# Clone whisper.cpp repository
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Compile
make

# The binary will be at: ./main
```

2. **Download a Whisper model**

```bash
# Download base English model (recommended)
bash ./models/download-ggml-model.sh base.en

# Or download other models:
# tiny.en, small.en, medium.en, large
```

3. **Set up file paths**

Place the compiled binary and model in these locations (or customize in the node):
- Binary: `/models/audio/whisper.cpp`
- Model: `/models/audio/ggml-base.en.bin`

### Usage

1. Add the **"Audio Transcription • Basic (CLI)"** node in ComfyUI
2. Set the `audio_path` to your audio file (WAV format recommended)
3. Configure:
   - `num_speakers`: Number of speakers in the audio (default: 2)
   - `enable_diarization`: Enable speaker detection (default: True)
   - `language`: Language code (default: "en")

### Outputs
- `transcription`: Full transcription without speaker labels
- `diarized_text`: Transcription with speaker labels (Speaker 1, Speaker 2, etc.)

### Limitations
- Simple speaker assignment (not as accurate as advanced option)
- Requires audio in WAV format
- Speaker detection is basic (alternating or energy-based)

---

## Option 2: Advanced Setup (Python Libraries)

### Prerequisites

1. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install openai-whisper pyannote.audio torch torchaudio
```

2. **Get HuggingFace Access Token** (for speaker diarization)

   a. Create account at https://huggingface.co/

   b. Accept conditions for pyannote models:
      - Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
      - Click "Agree and access repository"

   c. Get your access token:
      - Go to: https://huggingface.co/settings/tokens
      - Create a new token with "read" permissions
      - Copy the token

### Usage

1. Add the **"Audio Transcription • Advanced (Python)"** node in ComfyUI
2. Set the `audio_path` to your audio file
3. Configure:
   - `whisper_model`: Model size (tiny, base, small, medium, large)
   - `num_speakers`: Number of speakers (or leave auto-detect)
   - `language`: Language code (default: "en")
   - `huggingface_token`: Your HuggingFace token (required for diarization)

### Outputs
- `transcription`: Full transcription without speaker labels
- `diarized_text`: Transcription with accurate speaker labels
- `json_output`: Structured JSON with timestamps and speaker info

### Supported Audio Formats
- WAV, MP3, MP4, FLAC, and most common formats
- Automatically converted by whisper

---

## Audio File Requirements

### For Best Results:
- **Format**: WAV (16-bit PCM) or high-quality MP3
- **Sample Rate**: 16 kHz or higher
- **Channels**: Mono or Stereo
- **Quality**: Clear audio with minimal background noise

### Preparing Audio Files

If you need to convert audio:

```bash
# Using ffmpeg to convert to optimal format
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

---

## Troubleshooting

### Basic Node Issues

**Error: "Whisper.cpp binary not found"**
- Ensure whisper.cpp is compiled and path is correct
- Default path: `/models/audio/whisper.cpp`
- Set custom path in `whisper_bin` parameter

**Error: "Whisper model not found"**
- Download the model using whisper.cpp's download script
- Default path: `/models/audio/ggml-base.en.bin`
- Set custom path in `model_path` parameter

**Error: "Audio file not found"**
- Check that the audio file path is correct
- Use absolute paths

### Advanced Node Issues

**ImportError: No module named 'whisper'**
```bash
pip install openai-whisper
```

**ImportError: No module named 'pyannote.audio'**
```bash
pip install pyannote.audio
```

**Error: "HuggingFace token required"**
- Get token from: https://huggingface.co/settings/tokens
- Accept model conditions: https://huggingface.co/pyannote/speaker-diarization-3.1

**Poor Speaker Detection**
- Ensure audio quality is good
- Try adjusting `num_speakers` parameter
- Use longer audio clips (30+ seconds) for better results
- Consider using the Advanced node instead of Basic

---

## Performance Notes

### Basic Node (whisper.cpp)
- Fast inference (CPU or GPU)
- Minimal memory usage
- Good for real-time or large batches

### Advanced Node (Python)
- Higher accuracy
- Requires more memory (GPU recommended)
- Slower but better quality

---

## Examples

### Example 1: Two-person conversation

```
Input: interview.wav (2 people talking)
num_speakers: 2

Output:
[Speaker 1] [00:00:00.000 --> 00:00:05.000]
Hello, thank you for joining us today.

[Speaker 2] [00:00:05.000 --> 00:00:08.000]
Thank you for having me.

[Speaker 1] [00:00:08.000 --> 00:00:12.000]
Let's start with your background...
```

### Example 2: Meeting with multiple speakers

```
Input: meeting.wav (4 people)
num_speakers: 4

Output includes Speaker 1, Speaker 2, Speaker 3, Speaker 4 labels
```

---

## References

- whisper.cpp: https://github.com/ggerganov/whisper.cpp
- OpenAI Whisper: https://github.com/openai/whisper
- pyannote.audio: https://github.com/pyannote/pyannote-audio
- HuggingFace: https://huggingface.co/pyannote/speaker-diarization-3.1
