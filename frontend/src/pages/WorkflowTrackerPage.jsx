import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RotateCcw, 
  Ban, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  ShieldCheck, 
  Clock, 
  Eye, 
  ExternalLink,
  ChevronRight,
  Workflow
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import api from '../api/client';

const WORKFLOW_STEPS = [
  { step: 1, name: 'Browser Session', desc: 'Initialize secure headless/GUI browser environment' },
  { step: 2, name: 'Portal Navigation', desc: 'Open egy.almaviva-visa.it official appointment portal' },
  { step: 3, name: 'User Authentication', desc: 'Enter applicant email & password to authenticate' },
  { step: 4, name: 'Security Check', desc: 'Detect CAPTCHA, Cloudflare challenge, or OTP' },
  { step: 5, name: 'Booking Portal', desc: 'Navigate to official appointment booking section' },
  { step: 6, name: 'Applicant Form', desc: 'Open applicant profile and required data form' },
  { step: 7, name: 'Document Entry', desc: 'Submit passport details, DOB, and documents' },
  { step: 8, name: 'Confirmation', desc: 'Confirm appointment and verify official reference' },
];

const WorkflowTrackerPage = ({ initialBookingId }) => {
  const [bookings, setBookings] = useState([]);
  const [selectedId, setSelectedId] = useState(initialBookingId || null);
  const [currentBooking, setCurrentBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState('');

  const fetchBookingsList = async () => {
    try {
      const res = await api.get('/bookings/');
      const list = res.data?.results || res.data || [];
      setBookings(list);
      if (!selectedId && list.length > 0) {
        const priority = list.find((b) => b.status === 'RUNNING' || b.status === 'WAITING_FOR_USER') || list[0];
        setSelectedId(priority.id);
      }
    } catch (err) {
      console.error('Failed to load bookings list:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentBookingStatus = async () => {
    if (!selectedId) return;
    try {
      const res = await api.get(`/bookings/${selectedId}/`);
      setCurrentBooking(res.data);
    } catch (err) {
      console.error('Failed to poll status:', err);
    }
  };

  useEffect(() => {
    fetchBookingsList();
  }, []);

  useEffect(() => {
    fetchCurrentBookingStatus();
    const interval = setInterval(fetchCurrentBookingStatus, 2500);
    return () => clearInterval(interval);
  }, [selectedId]);

  const handleAction = async (endpoint) => {
    if (!selectedId) return;
    setActionLoading(true);
    setActionMsg('');
    try {
      await api.post(`/bookings/${selectedId}/${endpoint}/`);
      await fetchCurrentBookingStatus();
      setActionMsg(`Action '${endpoint}' executed successfully.`);
    } catch (err) {
      setActionMsg(`Error: ${err.message || 'Action failed'}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      
      {/* Top Header & Customer Selector */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Workflow className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold text-white">Live Embassy Workflow Tracker</h2>
          </div>
          <p className="text-xs text-slate-400">
            Observe step-by-step bot automation on egy.almaviva-visa.it with human verification controls.
          </p>
        </div>

        {/* Customer Selector */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium whitespace-nowrap">Select Job:</span>
          <select
            value={selectedId || ''}
            onChange={(e) => setSelectedId(Number(e.target.value))}
            className="bg-slate-950 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-500 font-mono"
          >
            {bookings.map((b) => (
              <option key={b.id} value={b.id}>
                #{b.id} - {b.full_name || b.email} ({b.status})
              </option>
            ))}
          </select>
        </div>
      </div>

      {currentBooking ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Progress & Stepper Panel */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Status Overview Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <StatusBadge status={currentBooking.status} />
                    <span className="text-xs font-mono text-slate-400">
                      Passport: {currentBooking.passport_number}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white">
                    {currentBooking.full_name || currentBooking.email}
                  </h3>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    {currentBooking.email} • Nationality: {currentBooking.nationality}
                  </div>
                </div>

                {/* Control Actions Bar */}
                <div className="flex items-center gap-2">
                  {currentBooking.status === 'RUNNING' && (
                    <button
                      onClick={() => handleAction('cancel')}
                      disabled={actionLoading}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-rose-300 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
                    >
                      <Ban className="w-3.5 h-3.5" />
                      Cancel
                    </button>
                  )}

                  {currentBooking.status === 'WAITING_FOR_USER' && (
                    <button
                      onClick={() => handleAction('resume')}
                      disabled={actionLoading}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-300 shadow-md transition-colors"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      Resume Workflow
                    </button>
                  )}

                  {(currentBooking.status === 'PENDING' || currentBooking.status === 'FAILED' || currentBooking.status === 'CANCELLED') && (
                    <button
                      onClick={() => handleAction(currentBooking.status === 'PENDING' ? 'start' : 'retry')}
                      disabled={actionLoading}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-500/20 transition-all"
                    >
                      {currentBooking.status === 'PENDING' ? (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          Start Automation
                        </>
                      ) : (
                        <>
                          <RotateCcw className="w-3.5 h-3.5" />
                          Retry Automation
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {actionMsg && (
                <div className="mb-4 p-2.5 rounded-lg bg-blue-500/15 border border-blue-500/30 text-blue-300 text-xs">
                  {actionMsg}
                </div>
              )}

              {/* WAITING_FOR_USER Action Banner */}
              {currentBooking.status === 'WAITING_FOR_USER' && (
                <div className="p-4 rounded-xl bg-amber-500/15 border border-amber-500/40 mb-4 animate-pulse space-y-2">
                  <div className="flex items-center gap-2 text-amber-300 text-xs font-bold">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span>ACTION REQUIRED: Solve Security Challenge</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    {currentBooking.action_required || 'The official website is requesting human verification (CAPTCHA / OTP). Complete it in the browser, then click Resume.'}
                  </p>
                </div>
              )}

              {/* SUCCESS Confirmation Banner */}
              {currentBooking.status === 'SUCCESS' && (
                <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/30 mb-4 space-y-1">
                  <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Appointment Booked and Verified!</span>
                  </div>
                  <div className="text-xs text-slate-300 font-mono">
                    Reference: <span className="text-white font-bold">{currentBooking.reference_number || 'Confirmed'}</span>
                  </div>
                  {currentBooking.appointment_date && (
                    <div className="text-xs text-slate-300 font-mono">
                      Date: <span className="text-emerald-300 font-semibold">{currentBooking.appointment_date}</span>
                    </div>
                  )}
                </div>
              )}

              {/* FAILED Error Banner */}
              {currentBooking.status === 'FAILED' && (
                <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 mb-4 space-y-1 text-xs text-rose-300">
                  <div className="flex items-center gap-2 font-bold">
                    <XCircle className="w-4 h-4" />
                    <span>Execution Stopped</span>
                  </div>
                  <p className="font-mono">{currentBooking.error_message || 'Workflow halted due to error.'}</p>
                </div>
              )}

              {/* Overall Progress Bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Workflow Progress</span>
                  <span className="font-mono font-bold text-white">
                    Step {currentBooking.step_progress || 0} / {currentBooking.total_steps || 8}
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div
                    className={`h-full transition-all duration-700 rounded-full ${
                      currentBooking.status === 'SUCCESS' ? 'bg-emerald-500' :
                      currentBooking.status === 'WAITING_FOR_USER' ? 'bg-amber-400' :
                      currentBooking.status === 'FAILED' ? 'bg-rose-500' : 'bg-blue-500'
                    }`}
                    style={{
                      width: `${Math.min(100, ((currentBooking.step_progress || 0) / (currentBooking.total_steps || 8)) * 100)}%`,
                    }}
                  />
                </div>
                <div className="text-[11px] text-slate-400 font-mono pt-1">
                  Status detail: {currentBooking.current_step || 'Idle'}
                </div>
              </div>
            </div>

            {/* Stepper Timeline */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-5">
                Workflow Step Execution Sequence
              </h4>

              <div className="space-y-4">
                {WORKFLOW_STEPS.map((s) => {
                  const currentProgress = currentBooking.step_progress || 0;
                  const isCompleted = currentProgress > s.step || (currentProgress === s.step && currentBooking.status === 'SUCCESS');
                  const isCurrent = currentProgress === s.step && currentBooking.status !== 'SUCCESS';
                  const isPending = currentProgress < s.step;

                  return (
                    <div
                      key={s.step}
                      className={`flex items-start gap-3.5 p-3 rounded-xl transition-all ${
                        isCurrent
                          ? currentBooking.status === 'WAITING_FOR_USER'
                            ? 'bg-amber-500/10 border border-amber-500/30'
                            : 'bg-blue-500/10 border border-blue-500/30'
                          : isCompleted
                          ? 'bg-slate-950/40 border border-slate-800/80'
                          : 'opacity-50'
                      }`}
                    >
                      <div className="pt-0.5">
                        {isCompleted ? (
                          <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          </div>
                        ) : isCurrent ? (
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                            currentBooking.status === 'WAITING_FOR_USER'
                              ? 'bg-amber-500 text-slate-950 animate-bounce'
                              : 'bg-blue-600 text-white animate-pulse'
                          }`}>
                            {s.step}
                          </div>
                        ) : (
                          <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] text-slate-400 font-mono">
                            {s.step}
                          </div>
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className={`text-xs font-bold ${isCurrent ? 'text-white' : 'text-slate-300'}`}>
                            Step {s.step}: {s.name}
                          </span>
                          {isCompleted && <span className="text-[10px] text-emerald-400 font-medium">Completed</span>}
                          {isCurrent && (
                            <span className={`text-[10px] font-semibold ${
                              currentBooking.status === 'WAITING_FOR_USER' ? 'text-amber-400' : 'text-blue-400'
                            }`}>
                              {currentBooking.status === 'WAITING_FOR_USER' ? 'Awaiting User' : 'Active'}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{s.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Right Panel: Live Session Capture & Audit Info */}
          <div className="space-y-6">
            
            {/* Live Screenshot View */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3 text-xs font-bold text-white">
                <span className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4 text-blue-400" />
                  Session Screen Capture
                </span>
                {currentBooking.last_screenshot && (
                  <a
                    href={currentBooking.last_screenshot}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-blue-400 hover:underline flex items-center gap-1"
                  >
                    Full image <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {currentBooking.last_screenshot ? (
                <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden">
                  <img
                    src={currentBooking.last_screenshot}
                    alt="Session Screenshot"
                    className="w-full h-auto object-contain"
                  />
                </div>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/60 p-8 text-center text-slate-500 text-xs">
                  No screenshot captured yet for this job.
                </div>
              )}
            </div>

            {/* Applicant Quick Profile */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Applicant Credentials
              </h4>

              <div className="bg-slate-950 rounded-xl border border-slate-800 divide-y divide-slate-800/80 text-xs">
                <div className="p-3 flex justify-between">
                  <span className="text-slate-400">Passport</span>
                  <span className="font-mono font-bold text-white">{currentBooking.passport_number}</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-400">Nationality</span>
                  <span className="text-slate-200">{currentBooking.nationality}</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-400">Birth Date</span>
                  <span className="text-slate-200">{currentBooking.birth_date}</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-400">Phone</span>
                  <span className="text-slate-200">{currentBooking.phone_number}</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-400">Retries</span>
                  <span className="text-slate-300 font-mono">{currentBooking.retry_count || 0}</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-500 text-sm">
          No booking job selected.
        </div>
      )}

    </div>
  );
};

export default WorkflowTrackerPage;
