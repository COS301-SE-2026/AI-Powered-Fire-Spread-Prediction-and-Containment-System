import React, { ComponentPropsWithoutRef, ReactNode } from 'react';

export type ButtonVariant = 'fire' | 'dark' | 'ghost' | 'red';

export interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  children: ReactNode;
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  fire: 'bg-[#E84500] text-white border-none hover:bg-[#E84500] hover:brightness-110',
  dark:    'bg-[#1E2436] text-[#CBD0DC] border border-[#2D3450] hover:text-white hover:border-[#3D4560]',
  red:     'bg-transparent text-[#E84500] border border-[#E84500] hover:bg-[#E84500]/10',
  ghost:   'bg-transparent text-[#4B5268] border border-[#1E2436] hover:text-[#9CA3AF]',
};

export default function Button({ children, variant = 'dark', className = '', ...props }: ButtonProps) {
  return (
    <button
      className={`btn btn-sm rounded-[4px] tracking-widest uppercase font-bold transition-all ${variantClasses[variant]} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}