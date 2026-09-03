import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  extractDocumentMetrics,
  getDocuments,
  getDocumentStatus,
  uploadDocument,
} from "../api/documents";

export default function Documents() {
  const queryClient =
    useQueryClient();

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(
    null,
  );

  const [
    activeDocumentId,
    setActiveDocumentId,
  ] = useState<
    number | null
  >(null);

  const [
    extractionMessage,
    setExtractionMessage,
  ] = useState<
    string | null
  >(null);

  const extractionStarted =
    useRef<Set<number>>(
      new Set(),
    );

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
    refetchInterval: 3000,
  });

  const statusQuery = useQuery({
    queryKey: [
      "document-status",
      activeDocumentId,
    ],
    queryFn: () =>
      getDocumentStatus(
        activeDocumentId!,
      ),
    enabled:
      activeDocumentId
      !== null,
    refetchInterval: (query) => {
      const status =
        query.state.data
          ?.status;

      if (
        status === "failed"
      ) {
        return false;
      }

      if (
        query.state.data
          ?.extraction_available
      ) {
        return false;
      }

      return 2000;
    },
  });

  const extractionMutation =
    useMutation({
      mutationFn:
        extractDocumentMetrics,

      onSuccess: (
        result,
      ) => {
        setExtractionMessage(
          result
            .promoted_to_reported_metrics
            ? `${result.metric_count} validated metrics loaded into the Board Report.`
            : "Metrics were extracted but validation did not pass.",
        );

        queryClient.invalidateQueries({
          queryKey: [
            "documents",
          ],
        });

        queryClient.invalidateQueries({
          queryKey: [
            "dashboard",
          ],
        });

        queryClient.invalidateQueries({
          queryKey: [
            "reported-metrics",
          ],
        });
      },

      onError: (
        error,
      ) => {
        setExtractionMessage(
          error instanceof Error
            ? error.message
            : "Metric extraction failed.",
        );
      },
    });

  const uploadMutation =
    useMutation({
      mutationFn:
        uploadDocument,

      onSuccess: (
        document,
      ) => {
        setSelectedFile(
          null,
        );

        setExtractionMessage(
          null,
        );

        setActiveDocumentId(
          document.id,
        );

        queryClient.invalidateQueries({
          queryKey: [
            "documents",
          ],
        });
      },
    });

  useEffect(() => {
    const status =
      statusQuery.data;

    if (
      !status
      || !status.extraction_available
      || activeDocumentId
        === null
      || extractionStarted.current.has(
        activeDocumentId,
      )
    ) {
      return;
    }

    extractionStarted.current.add(
      activeDocumentId,
    );

    extractionMutation.mutate(
      activeDocumentId,
    );
  }, [
    activeDocumentId,
    statusQuery.data,
  ]);

  function handleUpload() {
    if (!selectedFile) {
      return;
    }

    uploadMutation.mutate(
      selectedFile,
    );
  }

  return (
    <div>
      <header>
        <p className="text-sm font-medium text-zinc-500">
          Senus PLC
        </p>

        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-zinc-950">
          Documents
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          Source financial documents powering the Board Report.
        </p>
      </header>

      <section className="mt-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div>
          <h2 className="font-semibold text-zinc-950">
            Upload Financial Document
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            PDF documents are processed by MinerU, validated and loaded into the financial model automatically.
          </p>
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <label className="flex flex-1 cursor-pointer items-center rounded-lg border border-dashed border-zinc-300 bg-zinc-50 px-4 py-3 text-sm text-zinc-600 hover:bg-zinc-100">
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(
                event,
              ) => {
                setSelectedFile(
                  event.target
                    .files?.[0]
                    ?? null,
                );
              }}
            />

            {selectedFile
              ? selectedFile.name
              : "Choose PDF document"}
          </label>

          <button
            type="button"
            disabled={
              !selectedFile
              || uploadMutation.isPending
            }
            onClick={
              handleUpload
            }
            className="rounded-lg bg-zinc-950 px-5 py-3 text-sm font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {uploadMutation.isPending
              ? "Uploading..."
              : "Upload"}
          </button>
        </div>

        {uploadMutation.isError && (
          <p className="mt-3 text-sm text-red-600">
            {uploadMutation.error
              instanceof Error
              ? uploadMutation.error.message
              : "Upload failed."}
          </p>
        )}

        {activeDocumentId
          !== null
          && (
            <ProcessingStatus
              status={
                statusQuery.data
                  ?.status
                ?? "uploaded"
              }
              extractionAvailable={
                statusQuery.data
                  ?.extraction_available
                ?? false
              }
              extracting={
                extractionMutation
                  .isPending
              }
              message={
                extractionMessage
              }
            />
          )}
      </section>

      <section className="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h2 className="font-semibold text-zinc-950">
            Source Documents
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Documents used to populate validated financial metrics.
          </p>
        </div>

        {documentsQuery.isLoading ? (
          <div className="p-8 text-center text-sm text-zinc-400">
            Loading documents...
          </div>
        ) : documentsQuery.isError ? (
          <div className="p-8 text-center text-sm text-red-500">
            Unable to load documents.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-200 bg-zinc-50">
                  <th className="px-6 py-3 text-left font-medium text-zinc-500">
                    Document
                  </th>

                  <th className="px-6 py-3 text-left font-medium text-zinc-500">
                    Type
                  </th>

                  <th className="px-6 py-3 text-left font-medium text-zinc-500">
                    Status
                  </th>

                  <th className="px-6 py-3 text-right font-medium text-zinc-500">
                    Uploaded
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-zinc-100">
                {documentsQuery.data?.map(
                  (document) => (
                    <tr
                      key={
                        document.id
                      }
                    >
                      <td className="px-6 py-4 font-medium text-zinc-950">
                        {
                          document.name
                        }
                      </td>

                      <td className="px-6 py-4 text-zinc-600">
                        {formatDocumentType(
                          document.document_type,
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <StatusBadge
                          status={
                            document.status
                          }
                        />
                      </td>

                      <td className="px-6 py-4 text-right text-zinc-500">
                        {formatDate(
                          document.created_at,
                        )}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function ProcessingStatus({
  status,
  extractionAvailable,
  extracting,
  message,
}: {
  status: string;
  extractionAvailable: boolean;
  extracting: boolean;
  message: string | null;
}) {
  let text =
    "Preparing document...";

  if (
    status === "pending"
    || status
      === "processing"
  ) {
    text =
      "Reading financial document...";
  }

  if (
    extractionAvailable
    && extracting
  ) {
    text =
      "Extracting and validating financial metrics...";
  }

  if (message) {
    text = message;
  }

  if (status === "failed") {
    text =
      "Document processing failed.";
  }

  return (
    <div className="mt-5 rounded-lg bg-zinc-50 px-4 py-3">
      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 rounded-full bg-zinc-900" />

        <p className="text-sm font-medium text-zinc-700">
          {text}
        </p>
      </div>
    </div>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  const label =
    status
      .replaceAll("_", " ")
      .replace(
        /\b\w/g,
        (character) =>
          character.toUpperCase(),
      );

  return (
    <span className="inline-flex rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600">
      {label}
    </span>
  );
}

function formatDocumentType(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}

function formatDate(
  value: string,
) {
  return new Intl.DateTimeFormat(
    "en-IE",
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    },
  ).format(
    new Date(value),
  );
}