import { NextResponse } from "next/server";
import { getDatabase } from "@/lib/mongodb";

export async function GET(request: Request) {
  try {
    const db = await getDatabase();
    const reports = await db
      .collection("reports")
      .find({})
      .sort({ createdAt: -1 })
      .project({ documentBuffer: 0 }) // Exclude large buffer from list
      .toArray();

    return NextResponse.json({ reports });
  } catch (error) {
    console.error("Fetch reports error:", error);
    return NextResponse.json(
      { error: "Failed to fetch reports" },
      { status: 500 }
    );
  }
}
