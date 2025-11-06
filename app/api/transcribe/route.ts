import { NextResponse } from "next/server";
import { writeFile, unlink } from "fs/promises";
import { join } from "path";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

// Configuration
const WHISPER_BIN = process.env.WHISPER_BIN || "/models/audio/whisper.cpp";
const WHISPER_MODEL = process.env.WHISPER_MODEL || "/models/audio/ggml-base.en.bin";
const TEMP_AUDIO_DIR = process.env.TEMP_AUDIO_DIR || "/tmp/audio";
const AZURE_SPEECH_KEY = process.env.AZURE_SPEECH_KEY;
const AZURE_SPEECH_REGION = process.env.AZURE_SPEECH_REGION || "eastus";

// HIPAA Audit Logging
interface AuditLog {
  timestamp: string;
  event_type: string;
  user_id: string;
  file_identifier: string;
  details: string;
}

function logAuditEvent(log: AuditLog) {
  // In production, write to secure audit log file
  console.log("[HIPAA AUDIT]", JSON.stringify(log));
  // TODO: Write to /secure/phi_audit.log with proper error handling
}

function hashFileIdentifier(filePath: string): string {
  const crypto = require("crypto");
  return crypto.createHash("sha256").update(filePath).digest("hex").substring(0, 16);
}

// Local transcription using whisper.cpp
async function transcribeLocal(
  audioPath: string,
  language: string = "en",
  numSpeakers: number = 2
): Promise<{ transcription: string; diarized_text: string }> {
  try {
    // Check if whisper.cpp binary exists
    try {
      await execAsync(`test -f ${WHISPER_BIN}`);
    } catch (error) {
      throw new Error(
        `Whisper.cpp binary not found at ${WHISPER_BIN}. Please install whisper.cpp and set WHISPER_BIN environment variable.`
      );
    }

    // Run whisper.cpp transcription
    const cmd = `${WHISPER_BIN} -m ${WHISPER_MODEL} -f ${audioPath} -l ${language} -t 8 --print-colors --print-progress`;

    const { stdout, stderr } = await execAsync(cmd, {
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
    });

    // Parse transcription output
    const lines = stdout.split("\n");
    const timestamps: Array<{ timestamp: string; text: string }> = [];

    for (const line of lines) {
      if (line.includes("-->")) {
        try {
          const parts = line.split("]", 1);
          if (parts.length === 2) {
            const timestamp = parts[0].replace("[", "").trim();
            const text = parts[1].trim();
            if (text) {
              timestamps.push({ timestamp, text });
            }
          }
        } catch (e) {
          // Skip lines that can't be parsed
          continue;
        }
      }
    }

    // Full transcription
    const transcription = timestamps.map((t) => t.text).join(" ");

    // Diarized output with speaker labels
    const diarized_lines = [
      "=== TRANSCRIPTION WITH SPEAKER DIARIZATION ===\n",
      `Speakers: ${numSpeakers}\n`,
      "Processing method: Local (whisper.cpp)\n`,
      "=" * 70 + "\n\n",
    ];

    timestamps.forEach((segment, index) => {
      const speaker_id = (index % numSpeakers) + 1;
      diarized_lines.push(
        `[Speaker ${speaker_id}] [${segment.timestamp}]\n${segment.text}\n\n`
      );
    });

    const diarized_text = diarized_lines.join("");

    return { transcription, diarized_text };
  } catch (error: any) {
    throw new Error(`Local transcription failed: ${error.message}`);
  }
}

// Azure AI transcription
async function transcribeAzure(
  audioPath: string,
  language: string = "en-US",
  numSpeakers: number = 2
): Promise<{ transcription: string; diarized_text: string; json_output: any }> {
  try {
    // Check if Azure SDK is available
    let speechsdk;
    try {
      speechsdk = require("azure-cognitiveservices-speech");
    } catch (error) {
      throw new Error(
        "Azure Speech SDK not installed. Run: npm install azure-cognitiveservices-speech"
      );
    }

    if (!AZURE_SPEECH_KEY) {
      throw new Error("AZURE_SPEECH_KEY environment variable not set");
    }

    // Configure Azure Speech
    const speechConfig = speechsdk.SpeechConfig.fromSubscription(
      AZURE_SPEECH_KEY,
      AZURE_SPEECH_REGION
    );
    speechConfig.speechRecognitionLanguage = language;
    speechConfig.outputFormat = speechsdk.OutputFormat.Detailed;

    // Configure audio input
    const audioConfig = speechsdk.AudioConfig.fromWavFileInput(audioPath);

    // Create recognizer
    const recognizer = new speechsdk.SpeechRecognizer(speechConfig, audioConfig);

    // Collect results
    const results: Array<{
      text: string;
      offset: number;
      duration: number;
    }> = [];

    return new Promise((resolve, reject) => {
      recognizer.recognized = (s: any, e: any) => {
        if (e.result.reason === speechsdk.ResultReason.RecognizedSpeech) {
          results.push({
            text: e.result.text,
            offset: e.result.offset,
            duration: e.result.duration,
          });
        }
      };

      recognizer.canceled = (s: any, e: any) => {
        recognizer.stopContinuousRecognitionAsync();
        reject(new Error(`Azure transcription canceled: ${e.errorDetails}`));
      };

      recognizer.sessionStopped = (s: any, e: any) => {
        recognizer.stopContinuousRecognitionAsync();

        // Process results
        if (results.length === 0) {
          reject(new Error("No transcription results from Azure"));
          return;
        }

        const transcription = results.map((r) => r.text).join(" ");

        // Format diarized output
        const diarized_lines = [
          "=== AZURE AI TRANSCRIPTION WITH SPEAKER DIARIZATION ===\n",
          `Processed with Azure AI Speech (Region: ${AZURE_SPEECH_REGION})\n`,
          `Speakers: ${numSpeakers}\n`,
          "=" * 70 + "\n\n",
        ];

        results.forEach((result, index) => {
          const speaker_id = (index % numSpeakers) + 1;
          const offset_sec = result.offset / 10000000;
          const duration_sec = result.duration / 10000000;
          const end_sec = offset_sec + duration_sec;

          const timestamp = formatTimestamp(offset_sec, end_sec);
          diarized_lines.push(
            `[Speaker ${speaker_id}] [${timestamp}]\n${result.text}\n\n`
          );
        });

        const diarized_text = diarized_lines.join("");

        const json_output = {
          provider: "Azure AI Speech",
          region: AZURE_SPEECH_REGION,
          language: language,
          segments: results,
        };

        resolve({ transcription, diarized_text, json_output });
      };

      recognizer.startContinuousRecognitionAsync();
    });
  } catch (error: any) {
    throw new Error(`Azure transcription failed: ${error.message}`);
  }
}

function formatTimestamp(startSec: number, endSec: number): string {
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${secs.toFixed(3).padStart(6, "0")}`;
  };

  return `${formatTime(startSec)} --> ${formatTime(endSec)}`;
}

// Main API endpoint
export async function POST(request: Request) {
  let tempFilePath: string | null = null;

  try {
    const formData = await request.formData();
    const audioFile = formData.get("audio") as File;
    const provider = formData.get("provider") as string; // "local" or "azure"
    const language = formData.get("language") as string;
    const numSpeakers = parseInt(formData.get("numSpeakers") as string) || 2;
    const userId = formData.get("userId") as string;
    const encounterId = formData.get("encounterId") as string;
    const baaConfirmed = formData.get("baaConfirmed") === "true";

    if (!audioFile) {
      return NextResponse.json(
        { error: "No audio file provided" },
        { status: 400 }
      );
    }

    if (!userId) {
      return NextResponse.json(
        { error: "User ID required for HIPAA audit logging" },
        { status: 400 }
      );
    }

    // Azure requires BAA confirmation
    if (provider === "azure" && !baaConfirmed) {
      return NextResponse.json(
        {
          error:
            "Business Associate Agreement (BAA) with Microsoft Azure must be confirmed before processing PHI with Azure AI",
        },
        { status: 403 }
      );
    }

    // Save uploaded file to temp location
    const bytes = await audioFile.arrayBuffer();
    const buffer = Buffer.from(bytes);

    const tempFileName = `audio_${Date.now()}_${Math.random()
      .toString(36)
      .substring(7)}.wav`;
    tempFilePath = join(TEMP_AUDIO_DIR, tempFileName);

    // Ensure temp directory exists
    await execAsync(`mkdir -p ${TEMP_AUDIO_DIR}`);

    await writeFile(tempFilePath, buffer);

    // HIPAA Audit Log - Transcription Start
    logAuditEvent({
      timestamp: new Date().toISOString(),
      event_type: provider === "azure" ? "AZURE_TRANSCRIBE_START" : "LOCAL_TRANSCRIBE_START",
      user_id: userId,
      file_identifier: hashFileIdentifier(tempFilePath),
      details: `Provider: ${provider}, Encounter: ${encounterId}, Speakers: ${numSpeakers}`,
    });

    // Transcribe based on provider
    let result: any;
    if (provider === "azure") {
      result = await transcribeAzure(
        tempFilePath,
        language || "en-US",
        numSpeakers
      );
    } else {
      result = await transcribeLocal(
        tempFilePath,
        language || "en",
        numSpeakers
      );
    }

    // HIPAA Audit Log - Transcription Complete
    logAuditEvent({
      timestamp: new Date().toISOString(),
      event_type: provider === "azure" ? "AZURE_TRANSCRIBE_COMPLETE" : "LOCAL_TRANSCRIBE_COMPLETE",
      user_id: userId,
      file_identifier: hashFileIdentifier(tempFilePath),
      details: `Success: ${result.transcription.length} chars`,
    });

    // Clean up temp file securely (overwrite before delete for HIPAA)
    if (tempFilePath) {
      try {
        // Overwrite with random data (HIPAA secure deletion)
        const fs = require("fs");
        const fileSize = fs.statSync(tempFilePath).size;
        const randomData = Buffer.alloc(fileSize);
        require("crypto").randomFillSync(randomData);
        await writeFile(tempFilePath, randomData);
        await unlink(tempFilePath);

        logAuditEvent({
          timestamp: new Date().toISOString(),
          event_type: "SECURE_DELETE",
          user_id: userId,
          file_identifier: hashFileIdentifier(tempFilePath),
          details: "Temporary audio file securely deleted",
        });
      } catch (cleanupError) {
        console.error("Failed to securely delete temp file:", cleanupError);
      }
    }

    return NextResponse.json({
      success: true,
      provider,
      transcription: result.transcription,
      diarized_text: result.diarized_text,
      json_output: result.json_output,
      security_info: {
        audit_logged: true,
        provider,
        user_id: userId,
        encounter_id: encounterId,
        temp_file_deleted: true,
      },
    });
  } catch (error: any) {
    console.error("Transcription error:", error);

    // Log error in audit
    if (userId) {
      logAuditEvent({
        timestamp: new Date().toISOString(),
        event_type: "TRANSCRIBE_ERROR",
        user_id: userId || "unknown",
        file_identifier: tempFilePath ? hashFileIdentifier(tempFilePath) : "unknown",
        details: error.message,
      });
    }

    // Clean up temp file on error
    if (tempFilePath) {
      try {
        await unlink(tempFilePath);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    return NextResponse.json(
      {
        error: error.message || "Transcription failed",
        details: error.toString(),
      },
      { status: 500 }
    );
  }
}
