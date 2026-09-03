import { API_URL } from "../config";
export type BoardInsightsResponse = {
  insights: string;
};



export async function generateBoardInsights(
  question?: string,
): Promise<BoardInsightsResponse> {
  const response = await fetch(
    `${API_URL}/api/ai/board-insights`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        question:
          question || null,
      }),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to generate AI analysis.",
    );
  }

  return response.json();
}