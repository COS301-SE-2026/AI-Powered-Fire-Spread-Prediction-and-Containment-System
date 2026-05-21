export type BadgeStyle = {
    bg?: string;
    text?: string;
    border?: string;
};

export const statusBadge = {
    pending: { bg: 'bg-torch/10', text: 'text-torch', border: 'border-torch/25' },
    approved: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
    rejected: { bg: 'bg-flare/10', text: 'text-flare', border: 'border-flare/25' },
    revoked: { bg: 'bg-neutral/10', text: 'text-neutral', border: 'border-neutral/25' },
    none: { }
}