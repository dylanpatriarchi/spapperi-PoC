import { NextResponse } from 'next/server';

export async function GET(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;
    const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://spapperi-backend:8000";

    try {
        console.log(`Fetching conversation history from: ${BACKEND_URL}/api/conversation/${id}/history`);

        const response = await fetch(`${BACKEND_URL}/api/conversation/${id}/history`);

        if (!response.ok) {
            console.error("Backend error:", response.status, response.statusText);
            return NextResponse.json(
                { error: "Conversation not found" },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error("Proxy Error:", error);
        return NextResponse.json(
            { error: "Internal Proxy Error" },
            { status: 500 }
        );
    }
}
