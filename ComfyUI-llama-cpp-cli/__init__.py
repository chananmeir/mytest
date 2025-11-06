
# ComfyUI-llama-cpp-cli
# ComfyUI custom node pack for LLM and HIPAA-compliant audio transcription
# Supports both local processing (no dependencies) and Azure AI (cloud-based)

from .llama_cli import NODE_CLASS_MAPPINGS as LLAMA_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as LLAMA_DISPLAY_MAPPINGS
from .audio_transcribe import NODE_CLASS_MAPPINGS as AUDIO_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as AUDIO_DISPLAY_MAPPINGS

# Try to import Azure node (optional - requires azure-cognitiveservices-speech)
try:
    from .audio_transcribe_azure import NODE_CLASS_MAPPINGS as AZURE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as AZURE_DISPLAY_MAPPINGS
    azure_available = True
    print("✅ Azure AI transcription available (azure-cognitiveservices-speech installed)")
except ImportError:
    AZURE_MAPPINGS = {}
    AZURE_DISPLAY_MAPPINGS = {}
    azure_available = False
    print("ℹ️ Azure AI transcription not available (install: pip install azure-cognitiveservices-speech)")

# Combine all node mappings
NODE_CLASS_MAPPINGS = {**LLAMA_MAPPINGS, **AUDIO_MAPPINGS, **AZURE_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**LLAMA_DISPLAY_MAPPINGS, **AUDIO_DISPLAY_MAPPINGS, **AZURE_DISPLAY_MAPPINGS}

# Export availability flag
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'azure_available']
