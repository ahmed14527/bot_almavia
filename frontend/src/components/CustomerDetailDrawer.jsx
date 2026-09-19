import React, { useState } from 'react';
import { 
  X, 
  Play, 
  RotateCcw, 
  Ban, 
  Trash2, 
  AlertTriangle, 
  CheckCircle2, 
  Calendar, 
  Fingerprint, 
  FileText, 
  Clock, 
  ExternalLink,
  ShieldCheck 
} from 'lucide-react';
import StatusBadge from './StatusBadge';
import api from '../api/client';

const CustomerDetailDrawer = ({ booking, isOpen, onClose, onRefresh }) => {
  const [loadingAction, setLoadingAction] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !booking) return null;

  const triggerAction = async (endpoint) => {
    setLoadingAction(true);
    setError('');
    try {
      await api.post(`/bookings/${booking.id}/${endpoint}/`);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError(err.message || `Action ${endpoint} failed`);
    } finally {
      setLoadingAction(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete ${booking.email}?`)) return;
    setLoadingAction(true);
    try {
      await api.delete(`/bookings/${booking.id}/`);
      if (onRefresh) onRefresh();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to delete customer');
    } finally {
      setLoadingAction(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/70 backdrop-blur-sm">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col">
          
          {/* Drawer Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <StatusBadge status={booking.status} />
                <span className="text-xs text-slate-400">ID #{booking.id}</span>
              </div>
              <h3 className="text-lg font-bold text-white truncate">
                {booking.full_name || booking.email}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="p-6 space-y-6 overflow-y-auto flex-1">
            
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
                {error}
              </div>
            )}

            {/* Workflow Progress Banner */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
                <span>Automation Workflow</span>
                <span>Step {booking.step_progress || 0} of {booking.total_steps || 8}</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 mb-3 overflow-hidden">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${
                    booking.status === 'SUCCESS' ? 'bg-emerald-500' :
                    booking.status === 'WAITING_FOR_USER' ? 'bg-amber-500' :
                    booking.status === 'FAILED' ? 'bg-rose-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${Math.min(100, ((booking.step_progress || 0) / (booking.total_steps || 8)) * 100)}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Current: {booking.current_step || 'Awaiting execution'}
              </p>
            </div>

            {/* WAITING_FOR_USER Alert Banner */}
            {booking.status === 'WAITING_FOR_USER' && (
              <div className="bg-amber-500/15 border border-amber-500/30 rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-2 text-amber-300 text-sm font-semibold">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Human Verification Required</span>
                </div>
                <p className="text-xs text-slate-300">
                  {booking.action_required || 'Security challenge / CAPTCHA detected. Complete the action in the browser, then click Resume.'}
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => triggerAction('resume')}
                    disabled={loadingAction}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400 transition-colors shadow-sm"
                  >
                    Resume Workflow
                  </button>
                  <button
                    onClick={() => triggerAction('cancel')}
                    disabled={loadingAction}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Confirmed Appointment Banner */}
            {booking.status === 'SUCCESS' && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Appointment Confirmed!</span>
                </div>
                {booking.reference_number && (
                  <div className="text-xs text-slate-300">
                    <span className="text-slate-400">Reference: </span>
                    <span className="font-mono font-bold text-white">{booking.reference_number}</span>
                  </div>
                )}
                {booking.appointment_date && (
                  <div className="text-xs text-slate-300">
                    <span className="text-slate-400">Date: </span>
                    <span className="font-semibold text-emerald-300">{booking.appointment_date}</span>
                  </div>
                )}
              </div>
            )}

            {/* Error Banner */}
            {booking.error_message && (
              <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-4 text-xs text-rose-300 space-y-1">
                <span className="font-semibold block">Error Details:</span>
                <p className="font-mono">{booking.error_message}</p>
              </div>
            )}

            {/* Customer Details Information List */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Applicant Data</h4>
              
              <div className="bg-slate-950 border border-slate-800/80 rounded-xl divide-y divide-slate-800/80 text-xs">
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Passport Number</span>
                  <span className="font-mono font-bold text-white">{booking.passport_number}</span>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Email Address</span>
                  <span className="text-slate-200">{booking.email}</span>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Nationality</span>
                  <span className="text-slate-200">{booking.nationality}</span>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Date of Birth</span>
                  <span className="text-slate-200">{booking.birth_date}</span>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Phone Number</span>
                  <span className="text-slate-200">{booking.phone_number}</span>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <span className="text-slate-400">Password</span>
                  <span className="text-slate-400 font-mono">•••••••••••• (Protected)</span>
                </div>
                {booking.retry_count > 0 && (
                  <div className="p-3 flex justify-between items-center">
                    <span className="text-slate-400">Execution Retries</span>
                    <span className="text-slate-300">{booking.retry_count}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Captured Screenshot */}
            {booking.last_screenshot && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Session Capture</span>
                  <a
                    href={booking.last_screenshot}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-400 hover:underline flex items-center gap-1"
                  >
                    Open image <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden">
                  <img
                    src={booking.last_screenshot}
                    alt="Bot Screenshot"
                    className="w-full h-auto object-contain"
                  />
                </div>
              </div>
            )}

            {/* Timestamps */}
            <div className="text-[11px] text-slate-500 space-y-1 pt-2">
              <div>Created: {new Date(booking.created_at).toLocaleString()}</div>
              <div>Last Updated: {new Date(booking.updated_at).toLocaleString()}</div>
            </div>

          </div>

          {/* Drawer Actions Footer */}
          <div className="p-6 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between gap-2">
            <button
              onClick={handleDelete}
              disabled={loadingAction}
              className="p-2.5 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              title="Delete Customer"
            >
              <Trash2 className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-2">
              {booking.status === 'RUNNING' && (
                <button
                  onClick={() => triggerAction('cancel')}
                  disabled={loadingAction}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-rose-300 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
                >
                  <Ban className="w-3.5 h-3.5" />
                  Cancel
                </button>
              )}

              {(booking.status === 'FAILED' || booking.status === 'CANCELLED') && (
                <button
                  onClick={() => triggerAction('retry')}
                  disabled={loadingAction}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Retry Bot
                </button>
              )}

              {booking.status === 'PENDING' && (
                <button
                  onClick={() => triggerAction('start')}
                  disabled={loadingAction}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-500/20 transition-all"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  Start Automation
                </button>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default CustomerDetailDrawer;
