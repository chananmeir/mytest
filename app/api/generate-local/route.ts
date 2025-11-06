import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { writeFile, unlink } from "fs/promises";
import { join } from "path";

const execAsync = promisify(exec);

// Configuration for local LLM
const LLAMA_BIN = process.env.LLAMA_BIN || "/models/llm/llama";
const LLAMA_MODEL = process.env.LLAMA_MODEL || "/models/llm/mistral-7b-instruct-v0.1.Q4_0.gguf";
const TEMP_DIR = process.env.TEMP_DIR || "/tmp/llama";

// Same section prompts as the original generate API
const sectionPrompts: Record<string, { transcription: string; notes: string }> = {
  accident_details: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the mechanism of the accident into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the mechanism of the accident into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  initial_complaints: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the initial complaints resultant from the accident into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the initial complaints resultant from the accident into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  current_complaints: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the current complaints resultant from the accident in question into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the current complaints resultant from the accident in question into a detailed narrative description written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  course_treatment: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the course of treatment following the accident in question into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the course of treatment following the accident in question into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  past_medical: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's previous medical history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's previous medical history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  medications: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident medications into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident medications into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  childhood_education: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's childhood and educational history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's childhood and educational history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  social_history: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's social history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's social history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  functional_status: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident functional status into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident functional status into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  substance_use: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's substance use into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's substance use into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  occupational_history: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident occupational history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's pre and post-accident occupational history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  past_psychiatric: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's past mental health history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's past mental health history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  family_psychiatric: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's family psychiatric health history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's family psychiatric health history into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  mental_health_screening: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's mental health status into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's mental health status into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  clinical_examination: {
    transcription:
      "Re-word this transcription between doctor ({specialty}) and ({gender}) claimant which describes the claimant's clinical examination into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes between doctor ({specialty}) and ({gender}) claimant which describes the claimant's clinical examination into a detailed narrative description, written in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
  question_answer: {
    transcription:
      "Re-word this transcription completed by the doctor ({specialty}) as relates to the ({gender}) claimant which details the doctor's opinions based on the third party independent medical examination. Write in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
    notes:
      "Re-word these point form notes completed by the doctor ({specialty}) as relates to the ({gender}) claimant which details the doctor's opinions based on the third party independent medical examination. Write in medical/legal report format. Write the paragraph in ({perspective}) person. Replace any patient names with generic terms like 'the claimant' for privacy.",
  },
};

function buildPrompt(
  sectionId: string,
  inputMethod: string,
  inputData: string,
  config: any
): string {
  const prompts = sectionPrompts[sectionId];
  if (!prompts) {
    throw new Error(`Unknown section: ${sectionId}`);
  }

  const isTranscription =
    inputMethod === "upload-transcription" || inputMethod === "live-transcription" || inputMethod === "audio-upload";
  const basePrompt = isTranscription ? prompts.transcription : prompts.notes;

  const prompt = basePrompt
    .replace("{specialty}", config.specialtyType)
    .replace("{gender}", config.claimantGender)
    .replace("{perspective}", config.perspective);

  return `${prompt}\n\nInput:\n${inputData}`;
}

async function generateWithLocalLLM(prompt: string): Promise<string> {
  try {
    // Check if llama binary exists
    try {
      await execAsync(`test -f ${LLAMA_BIN}`);
    } catch (error) {
      throw new Error(
        `Llama.cpp binary not found at ${LLAMA_BIN}. Please install llama.cpp and set LLAMA_BIN environment variable.`
      );
    }

    // Create temp directory
    await execAsync(`mkdir -p ${TEMP_DIR}`);

    // Create a temp file for the prompt
    const tempPromptFile = join(TEMP_DIR, `prompt_${Date.now()}.txt`);
    await writeFile(tempPromptFile, prompt);

    // Build llama.cpp command
    const systemPrompt = "You are a professional medical report writer specializing in medical/legal documentation. Generate clear, professional, and detailed medical narratives based on the provided information.";

    const fullPrompt = `${systemPrompt}\n\n${prompt}`;

    const cmd = `${LLAMA_BIN} -m ${LLAMA_MODEL} -n 2000 -p "${fullPrompt.replace(/"/g, '\\"')}" --temp 0.7 --top-p 0.95 --log-disable --silent-prompt`;

    const { stdout, stderr } = await execAsync(cmd, {
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      timeout: 120000, // 2 minute timeout
    });

    // Clean up temp file
    try {
      await unlink(tempPromptFile);
    } catch (e) {
      // Ignore cleanup errors
    }

    // Extract the generated text (llama.cpp outputs the prompt + generation)
    let content = stdout.trim();

    // Try to remove the prompt from output if it's echoed
    if (content.startsWith(systemPrompt)) {
      content = content.substring(systemPrompt.length).trim();
    }

    if (!content) {
      throw new Error("Local LLM returned empty response");
    }

    return content;
  } catch (error: any) {
    throw new Error(`Local LLM generation failed: ${error.message}`);
  }
}

export async function POST(request: Request) {
  try {
    const { sectionId, inputMethod, inputData, config } = await request.json();

    const prompt = buildPrompt(sectionId, inputMethod, inputData, config);

    // Generate content using local LLM
    const content = await generateWithLocalLLM(prompt);

    return NextResponse.json({
      content,
      provider: "local",
      model: LLAMA_MODEL
    });
  } catch (error: any) {
    console.error("Local generation error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate content with local LLM",
        details: error.message
      },
      { status: 500 }
    );
  }
}
