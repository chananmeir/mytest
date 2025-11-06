import { NextResponse } from "next/server";
import { getDatabase } from "@/lib/mongodb";
import { Document, Paragraph, TextRun, HeadingLevel, AlignmentType, Packer } from "docx";
import { ObjectId } from "mongodb";

export async function POST(request: Request) {
  try {
    const { config, sections } = await request.json();

    // Create Word document
    const doc = new Document({
      sections: [
        {
          properties: {},
          children: [
            // Title
            new Paragraph({
              text: config.reportTitle,
              heading: HeadingLevel.HEADING_1,
              alignment: AlignmentType.CENTER,
              spacing: {
                after: 400,
              },
            }),

            // Report Information
            new Paragraph({
              text: "Report Information",
              heading: HeadingLevel.HEADING_2,
              spacing: {
                before: 200,
                after: 200,
              },
            }),

            new Paragraph({
              children: [
                new TextRun({ text: "Specialty: ", bold: true }),
                new TextRun(config.specialtyType),
              ],
              spacing: { after: 100 },
            }),

            new Paragraph({
              children: [
                new TextRun({ text: "Claimant: ", bold: true }),
                new TextRun(
                  `${config.claimantFirstName} ${config.claimantLastName}`
                ),
              ],
              spacing: { after: 100 },
            }),

            new Paragraph({
              children: [
                new TextRun({ text: "Gender: ", bold: true }),
                new TextRun(config.claimantGender),
              ],
              spacing: { after: 100 },
            }),

            new Paragraph({
              children: [
                new TextRun({ text: "Report Date: ", bold: true }),
                new TextRun(new Date().toLocaleDateString()),
              ],
              spacing: { after: 400 },
            }),

            // Add all sections
            ...sections.flatMap((section: any) => {
              if (!section.content) return [];

              // Replace generic terms with actual claimant name
              let processedContent = section.content;
              const claimantName = `${config.claimantFirstName} ${config.claimantLastName}`;
              processedContent = processedContent.replace(
                /\bthe claimant\b/gi,
                claimantName
              );
              processedContent = processedContent.replace(
                /\bclaimant\b/gi,
                claimantName
              );

              return [
                new Paragraph({
                  text: section.title,
                  heading: HeadingLevel.HEADING_2,
                  spacing: {
                    before: 300,
                    after: 200,
                  },
                }),
                new Paragraph({
                  text: processedContent,
                  spacing: {
                    after: 200,
                  },
                }),
              ];
            }),
          ],
        },
      ],
    });

    // Generate buffer
    const buffer = await Packer.toBuffer(doc);

    // Save to database
    const db = await getDatabase();
    const result = await db.collection("reports").insertOne({
      title: config.reportTitle,
      specialtyType: config.specialtyType,
      claimantName: `${config.claimantFirstName} ${config.claimantLastName}`,
      claimantGender: config.claimantGender,
      perspective: config.perspective,
      sections: sections,
      documentBuffer: buffer,
      createdAt: new Date(),
    });

    return NextResponse.json({
      reportId: result.insertedId.toString(),
      message: "Report processed successfully",
    });
  } catch (error) {
    console.error("Report processing error:", error);
    return NextResponse.json(
      { error: "Failed to process report" },
      { status: 500 }
    );
  }
}
