import React, { useState } from 'react';
// We use a clean relative import bypass to pull his component logic safely
import Card from '../../components/Card';
import Button from '../../components/Button';

export default function TestSandboxPage() {
  const [requests, setRequests] = useState([
    {
      id: "usr_req_90124",
      email: "keyseri@rekenaarasus.co.za",
      currentRole: "Registered User",
      requestedRole: "Firefighter",
      timestamp: new Date().toISOString(),
    }
  ]);

  const handleActionComplete = (requestId: string, status: string) => {
    console.log(`Action logs captured for request ${requestId}: ${status}`);
    setRequests(prev => prev.filter(req => req.id !== requestId));
  };

  const cardActionButtons = (
    <div className="flex gap-2">
      <Button
        variant="ghost"
        onClick={() => handleActionComplete("usr_req_role_change_approval", "rejected")}
        className="h-11 min-h-[44px] px-6 font-bold" 
      >
        Reject
      </Button>
      
      <Button
        variant="fire"
        onClick={() => handleActionComplete("usr_req_role_change_approval", "approved")}
        className="h-11 min-h-[44px] px-6 font-bold"
      >
        Approve
      </Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#1E2436] flex flex-col items-center justify-center p-6 gap-6 font-sans">
      <div className="text-center space-y-2 max-w-md">
        <h1 className="text-xl font-bold text-white tracking-tight">
          Admin Approval
        </h1>
      </div>

      {/* Render Frame Container */}
      <div className="w-full max-w-md p-2 bg-[#2D3450]/30 rounded-xl border border-[#2D3450] backdrop-blur-sm">
        {requests.length > 0 ? (
          requests.map(req => (
            <Card 
              key={req.id}
              title={`Requested Role Change`} 
              actions={cardActionButtons}
            >
              <div className="flex flex-col space-y-3 text-[#CBD0DC]">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">User Account</span>
                  <p className="text-sm font-semibold font-mono text-white truncate">{req.email}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div className="bg-[#1E2436] p-2 rounded border border-[#2D3450]">
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Current</span>
                    <span className="text-xs font-bold">{req.currentRole}</span>
                  </div>
                  <div className="bg-[#E84500]/10 p-2 rounded border border-[#E84500]/30">
                    <span className="text-[9px] uppercase font-bold text-[#E84500] block">Target</span>
                    <span className="text-xs font-black text-[#E84500]"> {req.requestedRole}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="p-8 text-center text-sm text-[#CBD0DC]/60 font-medium">
            
          </div>
        )}
      </div>
    </div>
  );
}