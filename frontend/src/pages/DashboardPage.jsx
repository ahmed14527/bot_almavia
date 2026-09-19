import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Play, 
  FileSpreadsheet, 
  Users, 
  RotateCw, 
  ExternalLink,
  CheckCircle2,
  Workflow
} from 'lucide-react';
import StatsCards from '../components/StatsCards';
import StatusBadge from '../components/StatusBadge';
import WaitingForUserModal from '../components/WaitingForUserModal';
import api from '../api/client';

const DashboardPage = ({ onNavigate, onSelectCustomer }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [waitingModalBooking, setWaitingModalBooking] = useState(null);

  const fetchStats = async () => {
    try {
      const res = await api.get('/dashboard/stats/');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-blue-900/30 via-slate-900 to-slate-900 border border-slate-800 rounded-2xl p-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Embassy Visa Appointment Control Hub
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Automated booking assistant for Italian Embassy visa slots (Almaviva Egypt).
            Provides transparent workflow tracking, automated steps, and human-in-the-loop verification.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onNavigate('excel')}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30 transition-colors"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Import Excel
          </button>

          <button
            onClick={() => onNavigate('customers')}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-blue-600 text-white hover:bg-blue-500 transition-colors shadow-md shadow-blue-500/20"
          >
            <Users className="w-4 h-4" />
            Manage Customers
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCards 
        stats={stats} 
        onFilterSelect={(status) => {
          onNavigate('customers', { filterStatus: status });
        }} 
      />

      {/* Active Jobs Alert Ticker */}
      {stats?.active_jobs && stats.active_jobs.length > 0 && (
        <div className="bg-slate-900/80 border border-blue-500/30 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
              <h3 className="text-sm font-bold text-white">Live Running Workflows ({stats.active_jobs.length})</h3>
            </div>
            <button
              onClick={() => onNavigate('automation')}
              className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-medium"
            >
              Open Live Tracker <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {stats.active_jobs.map((job) => (
              <div
                key={job.id}
                onClick={() => {
                  if (job.status === 'WAITING_FOR_USER') {
                    setWaitingModalBooking(job);
                  } else {
                    onNavigate('automation', { bookingId: job.id });
                  }
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  job.status === 'WAITING_FOR_USER'
                    ? 'bg-amber-500/10 border-amber-500/40 hover:bg-amber-500/15'
                    : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-slate-400">Booking #{job.id}</span>
                  <StatusBadge status={job.status} />
                </div>
                <div className="text-xs font-semibold text-white mb-2 truncate">
                  {job.current_step || 'Processing...'}
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-1.5 rounded-full ${
                      job.status === 'WAITING_FOR_USER' ? 'bg-amber-400' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(100, ((job.step_progress || 0) / (job.total_steps || 8)) * 100)}%` }}
                  />
                </div>
                {job.status === 'WAITING_FOR_USER' && (
                  <div className="mt-2 text-[11px] text-amber-300 font-medium flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Click to resolve verification
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white">Recent Customer Activity</h3>
          <button
            onClick={() => onNavigate('customers')}
            className="text-xs text-blue-400 hover:underline"
          >
            View all customers →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-[11px] uppercase bg-slate-950/60 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Current Step</th>
                <th className="py-3 px-4">Confirmation Details</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {stats?.recent_activity?.length ? (
                stats.recent_activity.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-400">#{item.id}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3 px-4 text-slate-200 font-mono">
                      {item.current_step || 'Pending'}
                    </td>
                    <td className="py-3 px-4">
                      {item.reference_number ? (
                        <span className="font-mono text-emerald-400 font-semibold">
                          {item.reference_number}
                        </span>
                      ) : item.error_message ? (
                        <span className="text-rose-400 truncate max-w-xs block" title={item.error_message}>
                          {item.error_message}
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onNavigate('customers', { openId: item.id })}
                        className="text-blue-400 hover:text-blue-300 font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center py-6 text-slate-500">
                    No customer activity recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Human Verification Modal */}
      {waitingModalBooking && (
        <WaitingForUserModal
          booking={waitingModalBooking}
          onClose={() => setWaitingModalBooking(null)}
          onRefresh={fetchStats}
        />
      )}

    </div>
  );
};

export default DashboardPage;
