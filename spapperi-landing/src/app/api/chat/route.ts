import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const body = await request.json();

        // Use internal docker network DNS if in container
        // Priority:
        // 1. BACKEND_INTERNAL_URL (Explicit internal docker DNS, e.g. http://spapperi-backend:8000)
        // 2. NEXT_PUBLIC_API_URL (Fallback, usage in local dev)
        // 3. Hardcoded Default
        const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://spapperi-backend:8000";

        console.log(`Proxying chat request to: ${BACKEND_URL}/api/chat`);

        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            console.error("Backend error:", response.status, response.statusText);
            return NextResponse.json(
                { error: "Backend service unavailable" },
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
