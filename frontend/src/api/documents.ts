import { API_URL } from "../config";
export type DocumentRecord = {
  id: number;
  name: string;
  document_type: string;
  status: string;
  created_at: string;
};

export type DocumentStatus = {
  document_id: number;
  name: string;
  status: string;
  mineru_task_id: string | null;
  extraction_available: boolean;
};

export type ExtractionResponse = {
  document_id: number;
  raw_candidate_count: number;
  metric_count: number;
  validation: {
    status: string;
    checks: unknown[];
  };
  promoted_to_reported_metrics: boolean;
};



export async function getDocuments(): Promise<DocumentRecord[]> {
  const response = await fetch(
    `${API_URL}/api/documents`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load documents: ${response.status}`,
    );
  }

  return response.json();
}

export async function uploadDocument(
  file: File,
): Promise<{
  id: number;
  name: string;
  status: string;
}> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail ?? "Upload failed.",
    );
  }

  return response.json();
}

export async function getDocumentStatus(
  documentId: number,
): Promise<DocumentStatus> {
  const response = await fetch(
    `${API_URL}/api/documents/${documentId}/status`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load document status: ${response.status}`,
    );
  }

  return response.json();
}

export async function extractDocumentMetrics(
  documentId: number,
): Promise<ExtractionResponse> {
  const response = await fetch(
    `${API_URL}/api/documents/${documentId}/extract-metrics`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail ?? "Metric extraction failed.",
    );
  }

  return response.json();
}