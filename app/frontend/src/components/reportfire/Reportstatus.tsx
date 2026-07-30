import React from "react";
import { FileCheck, Clock, CheckCircle2, XCircle } from "lucide-react";
import type { ReportStatus } from "../../types/report";
import { StatusCard } from "../reportfire/StatusCard";

interface StatusProps {
    readonly status: ReportStatus;
    readonly refNumber: string;
    readonly locationText?: string;
};

export default function ReportStatus({ status, refNumber, locationText }: StatusProps) {
    let label = "";
    let detail = "";
    let Icon = Clock;
    let color = "text-text-primary";

    if (status === "received"){
        label="Report submitted";
        detail="Ref assigned, awaiting review";
        Icon = FileCheck;
        color = "text-text-primary";
    } else if (status === "pending") {
        label = "Pending";
        detail = "Started verification process";
        Icon = Clock;
        color = "text-warning";
    } else if (status === "verified") {
        label = "Verified";
        detail = "Push notifications sent out";
        Icon = CheckCircle2;
        color = "text-success";
    } else if (status === "rejected") {
        label = "Rejected";
        detail = "Report could not be verified";
        Icon = XCircle;
        color = "text-error";
    }

    return (
        <StatusCard label={label} detail={detail} Icon={Icon} color={color} refNumber={refNumber} locationText={locationText}/>
    );
}