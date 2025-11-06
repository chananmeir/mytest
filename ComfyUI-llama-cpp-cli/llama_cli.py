
import os
import subprocess

print("✅ ComfyUI-llama-cpp-cli loaded")

DEFAULT_LLAMA_BIN = "/models/llm/llama"
DEFAULT_MODEL_PATH = "/models/llm/mistral-7b-instruct-v0.1.Q4_0.gguf"

class LlamaCppCLINode:
    """
    Call a local llama.cpp binary (CLI) with a GGUF model.
    Works in sandboxed ComfyUI (e.g., MimicPC) — no pip needed.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "### Instruction:\nDescribe a robot on Mars."}),
            },
            "optional": {
                "max_tokens": ("INT", {"default": 128, "min": 1, "max": 4096}),
                "llama_bin": ("STRING", {"default": DEFAULT_LLAMA_BIN}),
                "model_path": ("STRING", {"default": DEFAULT_MODEL_PATH}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0}),
                "mirostat": ("INT", {"default": 0, "min": 0, "max": 2}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "LLM"

    def generate(self, prompt, max_tokens=128, llama_bin=DEFAULT_LLAMA_BIN, model_path=DEFAULT_MODEL_PATH, temperature=0.7, top_p=0.95, mirostat=0):
        # Validate paths
        if not os.path.exists(llama_bin):
            return (f"⚠️ llama.cpp binary not found: {llama_bin}",)
        if not os.path.exists(model_path):
            return (f"⚠️ GGUF model not found: {model_path}",)

        # Build CLI command
        cmd = [
            llama_bin,
            "-m", model_path,
            "-n", str(max_tokens),
            "-p", prompt,
            "--log-disable",
            "--silent-prompt",
            "--simple-io",
            "--temp", str(temperature),
            "--top-p", str(top_p),
        ]
        if mirostat in (1, 2):
            cmd += ["--mirostat", str(mirostat)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                return (f"⚠️ llama.cpp failed (code {result.returncode}): {stderr}",)
            return (result.stdout.strip(),)
        except Exception as e:
            return (f"⚠️ Error: {e}",)

NODE_CLASS_MAPPINGS = {
    "LlamaCppCLINode": LlamaCppCLINode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LlamaCppCLINode": "LLM • llama.cpp (CLI)"
}
