import React, {useState} from "react";


interface PasswordInputProps {
  id: string;
  name?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  error?: string;
  autoComplete?: string;
  className?: string;
}

const baseFieldClass =(hasError?: string)=>{
    if(hasError){
        return 'input input-error w-full pr-10'
    }
    return 'input input-neutral focus:border-primary w-full pr-10'
};

export default function PasswordInput({
  id,
  name = '',
  value,
  onChange,
  placeholder = '',
  error = undefined,
  autoComplete = 'current-password',
  className = '',
}: PasswordInputProps) {
    const [visible, setVisble] = useState(false);
    return (
        <div className = "relative">
            <input
                id={id}
                name={name}
                type={visible ? 'text' : 'password'}
                placeholder={placeholder}
                className={`${baseFieldClass(error)} ${className}`}
                value={value}
                onChange={onChange}
                autoComplete={autoComplete}
            />
            <button
                type="button"
                onClick={() => setVisble((prev) => !prev)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white"
            >
                {visible ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 3C5.58 3 2.11 6.06 1 10c1.11 3.94 4.58 7 9 7s7.89-3.06 9-7c-1.11-3.94-4.58-7-9-7zm0 12a5 5 0 110-10 5 5 0 010 10z" />
                        <path d="M10 7a3 3 0 100 6 3 3 0 000-6z" />
                    </svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 3C5.58 3 2.11 6.06 1 10c1.11 3.94 4.58 7 9 7s7.89-3.06 9-7c-1.11-3.94-4.58-7-9-7zm0 12a5 5 0 110-10 5 5 0 010 10z" />
                        <path d="M10 7a3 3 0 100 6 3 3 0 000-6z" />
                        <path d="M2.293 2.293a1 1 0 011.414 0l14 14a1 1 0 01-1.414 1.414l-14-14a1 1 0 010-1.414z" />
                    </svg>
                )}
            </button>
        </div>
    );
}