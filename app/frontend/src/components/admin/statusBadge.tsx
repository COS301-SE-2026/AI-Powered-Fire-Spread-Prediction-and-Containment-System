export type BadgeStyle = {
    bg?: string;
    text?: string;
    border?: string;
};

export const statusBadge: Record<string, BadgeStyle> = {
    pending: { bg: 'bg-torch/10', text: 'text-torch', border: 'border-torch/25' },
    approved: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
    rejected: { bg: 'bg-flare/10', text: 'text-flare', border: 'border-flare/25' },
    revoked: { bg: 'bg-ignite/20', text: 'text-ignite', border: 'border-ignite/50' },
    none: {},
}