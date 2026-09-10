import { API_URL } from "../config";
export type BoardInsightsSource = {
  period_code: string;
  metric_code: string;
  value: number;
  source_page: number | null;
  document_id: number;
  document_name: string;
};

export type BoardInsightsDataQuality = {
  as_of_date: string;
  unvalidated_pending_documents: {
    document_id: number;
    name: string;
    uploaded_at: string;
  }[];
  flagged_numbers: string[];
};

export type BoardInsightsResponse = {
  insights: string;
  sources: BoardInsightsSource[];
  data_quality: BoardInsightsDataQuality;
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