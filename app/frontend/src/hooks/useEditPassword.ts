import { useCallback } from "react";
import { apiCall } from "@/lib/api";

export function useEditPassword(){
    const editPassword = useCallback(async (current: string, next: string, confirm: string) => {
        if (next.length < 8){
            throw new Error("Password muct be at least 8 characters");
        }
        if (next !== confirm){
            throw new Error("Passwords do not match");
        }
        await apiCall('/api/auth/edit_password', 'POST', {
            current_password: current,
            new_password: next,
        });
    }, []);
    return { editPassword };
}