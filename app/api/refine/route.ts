import { NextResponse } from "next/server";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: Request) {
  try {
    const { content, command, config } = await request.json();

    const prompt = `${command}\n\nOriginal content:\n${content}\n\nPlease apply the requested modification while maintaining the medical/legal report format and ${config.perspective} person perspective.`;

    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content:
            "You are a professional medical report editor. Refine the provided medical/legal report content according to the user's instructions while maintaining professional standards and format.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    const refinedContent = completion.choices[0].message.content;

    return NextResponse.json({ content: refinedContent });
  } catch (error) {
    console.error("Refinement error:", error);
    return NextResponse.json(
      { error: "Failed to refine content" },
      { status: 500 }
    );
  }
}
