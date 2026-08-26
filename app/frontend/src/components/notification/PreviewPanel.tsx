import { useNotifications } from '../../hooks/useNotification';

export function PreviewPanel() {
  const { notifications, previewToast } = useNotifications();

  return (
    <div className="flex gap-2 flex-wrap p-4 bg-carbon-card rounded border border-border-subtle">
      <p className="w-full text-xs text-text-muted uppercase font-semibold mb-1">
        Toast preview - click to trigger
      </p>
      {notifications.map((n) => (
        <button
          key={n.id}
          type="button"
          onClick={() => previewToast(n)}
          className="btn btn-sm btn-outline"
        >
          {n.type} · {n.severity}
        </button>
      ))}
    </div>
  );
}
