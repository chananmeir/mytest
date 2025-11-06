
# ComfyUI-llama-cpp-cli
# Minimal ComfyUI custom node pack that calls a local llama.cpp binary via subprocess.
# No pip dependencies required.

from .llama_cli import NODE_CLASS_MAPPINGS as LLAMA_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as LLAMA_DISPLAY_MAPPINGS
from .audio_transcribe import NODE_CLASS_MAPPINGS as AUDIO_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as AUDIO_DISPLAY_MAPPINGS

# Combine all node mappings
NODE_CLASS_MAPPINGS = {**LLAMA_MAPPINGS, **AUDIO_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**LLAMA_DISPLAY_MAPPINGS, **AUDIO_DISPLAY_MAPPINGS}
