import React, { useState } from 'react';
// We use a clean relative import bypass to pull his component logic safely
import { AdminApprovalCard } from '../../components/admin/approvalCard';

export default function TestSandboxPage() {
  const [requests, setRequests] = useState([
    {
      id: "usr_req_90124",
      fullName: "James Smith",
      email: "j.smith@email.com",
      accountCreated: "14 May 2026",
      dateRequested: "20 May 2026",
      currentRole: "Registered User",
      requestedRole: "Admin" as const,
      justification: "",
    }
  ]);

  const handleActionComplete = (requestId: string, status: string) => {
    console.log(`Action logs captured for request ${requestId}: ${status}`);
    setRequests(prev => prev.filter(req => req.id !== requestId));
  };

  return (
    <div className="min-h-screen bg-[#1E2436] flex flex-col items-center justify-center p-6 gap-6 font-sans">

      {/* Render Frame Container */}
      <div className="w-full max-w-md p-2 bg-[#2D3450]/30 rounded-xl border border-[#2D3450] backdrop-blur-sm">
        {requests.length > 0 ? (
          requests.map(req => (
            <AdminApprovalCard
              key={req.id}
              request={req}
              onActionComplete={handleActionComplete}
            />
          ))
        ) : (
          <div className="p-8 text-center text-sm text-[#CBD0DC]/60 font-medium" />
        )}
      </div>
    </div>
  );
}