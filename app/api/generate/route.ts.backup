import { NextResponse } from "next/server";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

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
    inputMethod === "upload-transcription" || inputMethod === "live-transcription";
  const basePrompt = isTranscription ? prompts.transcription : prompts.notes;

  const prompt = basePrompt
    .replace("{specialty}", config.specialtyType)
    .replace("{gender}", config.claimantGender)
    .replace("{perspective}", config.perspective);

  return `${prompt}\n\nInput:\n${inputData}`;
}

export async function POST(request: Request) {
  try {
    const { sectionId, inputMethod, inputData, config } = await request.json();

    const prompt = buildPrompt(sectionId, inputMethod, inputData, config);

    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content:
            "You are a professional medical report writer specializing in medical/legal documentation. Generate clear, professional, and detailed medical narratives based on the provided information.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    const content = completion.choices[0].message.content;

    return NextResponse.json({ content });
  } catch (error) {
    console.error("Generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate content" },
      { status: 500 }
    );
  }
}
