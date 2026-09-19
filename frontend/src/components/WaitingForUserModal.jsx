import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Play, 
  Ban, 
  Eye, 
  RefreshCw, 
  ExternalLink 
} from 'lucide-react';
import api from '../api/client';

const WaitingForUserModal = ({ booking, onClose, onRefresh }) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!booking) return null;

  const handleResume = async () => {
    setSubmitting(true);
    setError('');
    try {
      await api.post(`/bookings/${booking.id}/resume/`);
      if (onRefresh) onRefresh();
      if (onClose) onClose();
    } catch (err) {
      setError(err.message || 'Failed to send resume signal.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async () => {
    setSubmitting(true);
    setError('');
    try {
      await api.post(`/bookings/${booking.id}/cancel/`);
      if (onRefresh) onRefresh();
      if (onClose) onClose();
    } catch (err) {
      setError(err.message || 'Failed to cancel workflow.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-amber-500/40 rounded-2xl max-w-xl w-full p-6 shadow-2xl shadow-amber-500/10">
        
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-6 h-6 text-amber-400 animate-bounce" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Action Required: Human Verification</h3>
            <p className="text-xs text-amber-400/90">
              Customer: {booking.full_name || booking.email} ({booking.passport_number})
            </p>
          </div>
        </div>

        {/* Action Prompt */}
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 mb-4 text-sm text-slate-200">
          <p className="font-medium text-amber-300 mb-1">Embassy Portal Security Challenge:</p>
          <p className="text-xs text-slate-300 leading-relaxed">
            {booking.action_required || 'The Italian Visa portal requires manual CAPTCHA / OTP verification. Complete the verification in the active browser, then click Resume below.'}
          </p>
        </div>

        {/* Browser Screenshot if available */}
        {booking.last_screenshot ? (
          <div className="mb-5">
            <div className="flex items-center justify-between mb-1.5 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <Eye className="w-4 h-4 text-blue-400" />
                Live Session Capture:
              </span>
              <a 
                href={booking.last_screenshot} 
                target="_blank" 
                rel="noreferrer" 
                className="text-blue-400 hover:underline flex items-center gap-1"
              >
                Open Full <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950 overflow-hidden max-h-56">
              <img 
                src={booking.last_screenshot} 
                alt="Verification Screenshot" 
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        ) : null}

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
          <button
            type="button"
            onClick={handleCancel}
            disabled={submitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-slate-300 bg-slate-800 hover:bg-rose-500/20 hover:text-rose-300 border border-slate-700 transition-colors disabled:opacity-50"
          >
            <Ban className="w-4 h-4 text-rose-400" />
            Cancel Workflow
          </button>

          <button
            type="button"
            onClick={handleResume}
            disabled={submitting}
            className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50"
          >
            {submitting ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            Resume Workflow
          </button>
        </div>

      </div>
    </div>
  );
};

export default WaitingForUserModal;
