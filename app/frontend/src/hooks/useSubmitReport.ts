// hooks/users/useSubmitReport.ts
import { useCallback, useState } from 'react';
import { apiCall } from '../lib/api';
import type { FireReportDetailResponse } from '../types/Report';
import { offlineStore } from '../lib/offlineStore';

export interface SubmitReportInput {
  location: string;
  description: string;
  photo?: File;
  lat: number;
  lng: number;
  boundaryRadius: number;
}

export function useSubmitReport() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queuedOffline, setQueuedOffline] = useState(false);


  const submitReport = useCallback(
    async (input: SubmitReportInput): Promise<FireReportDetailResponse | null> => {
      setSubmitting(true);
      setError(null);
      setQueuedOffline(false);

      try {
        let imageUrl: string | undefined;

        if (input.photo) {
          const formData = new FormData();
          formData.append('file', input.photo);

          const uploadRes = await fetch('/api/uploads/photo', {
            method: 'POST',
            credentials: 'include',
            body: formData,
          });

          if (!uploadRes.ok) {
            throw new Error('Image upload failed');
          }

          const uploadResult = await uploadRes.json();
          imageUrl = uploadResult.object_key;
        }

        const report: FireReportDetailResponse = await apiCall(
          '/api/users/reported-fires',
          'POST',
          {
            location_text: input.location,
            description: input.description,
            image_url: imageUrl,
            lat: input.lat,
            lng: input.lng,
            boundary_radius: input.boundaryRadius,
          }
        );

        return report;
      } catch (err: unknown) {
        if (err instanceof TypeError && err.message === 'Failed to fetch'){
          try {
            await offlineStore.queueFireReport({
              lat: input.lat,
              lng: input.lng,
              location_text: input.location,
              description: input.description ?? null,
              boundary_radius: input.boundaryRadius,
              photoFile: input.photo,
            });
            setQueuedOffline(true);
            return null;
          } catch (queueErr) {
            console.error('Fialed to queue report offline', queueErr);
            setError('Unable to save report offline. Pease try again once connected.');
            return null;
          }
        }
        const message =
          err instanceof Error ? err.message : 'Failed to submit report. Please try again.';
        console.error('Failed to submit report', err);
        setError(message);
        return null;
      } finally {
        setSubmitting(false);
      }
    },
    []
  );

  return { submitReport, submitting, error, queuedOffline };
}
