import React from 'react';
import { 
  Clock, 
  PlayCircle, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  Ban 
} from 'lucide-react';

const StatusBadge = ({ status, className = '' }) => {
  const normStatus = (status || 'PENDING').toUpperCase();

  switch (normStatus) {
    case 'RUNNING':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 ${className}`}>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          Running
        </span>
      );

    case 'WAITING_FOR_USER':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30 animate-pulse ${className}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          Action Required
        </span>
      );

    case 'SUCCESS':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${className}`}>
          <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          Confirmed
        </span>
      );

    case 'FAILED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 ${className}`}>
          <XCircle className="w-3.5 h-3.5 shrink-0" />
          Failed
        </span>
      );

    case 'RETRYING':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 ${className}`}>
          <RotateCcw className="w-3.5 h-3.5 animate-spin shrink-0" />
          Retrying
        </span>
      );

    case 'CANCELLED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20 ${className}`}>
          <Ban className="w-3.5 h-3.5 shrink-0" />
          Cancelled
        </span>
      );

    case 'PENDING':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700 ${className}`}>
          <Clock className="w-3.5 h-3.5 shrink-0" />
          Pending
        </span>
      );
  }
};

export default StatusBadge;
