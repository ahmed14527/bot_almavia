import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  UserPlus, 
  RefreshCw, 
  Play, 
  Trash2, 
  RotateCcw, 
  Eye, 
  AlertTriangle,
  CheckSquare,
  Square
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import CustomerModal from '../components/CustomerModal';
import CustomerDetailDrawer from '../components/CustomerDetailDrawer';
import WaitingForUserModal from '../components/WaitingForUserModal';
import api from '../api/client';

const CustomersPage = ({ initialFilter, openIdOnLoad }) => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialFilter || 'ALL');
  const [selectedIds, setSelectedIds] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeCustomer, setActiveCustomer] = useState(null);
  const [waitingModalBooking, setWaitingModalBooking] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter && statusFilter !== 'ALL') params.status = statusFilter;

      const res = await api.get('/bookings/', { params });
      const results = res.data?.results || res.data || [];
      setCustomers(results);

      // If initial openId requested
      if (openIdOnLoad) {
        const found = results.find((c) => c.id === openIdOnLoad);
        if (found) setActiveCustomer(found);
      }
    } catch (err) {
      console.error('Failed to fetch customers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchCustomers();
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === customers.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(customers.map((c) => c.id));
    }
  };

  const handleStartSingle = async (e, id) => {
    e.stopPropagation();
    try {
      await api.post(`/bookings/${id}/start/`);
      fetchCustomers();
    } catch (err) {
      alert(err.message || 'Failed to start booking');
    }
  };

  const handleRetrySingle = async (e, id) => {
    e.stopPropagation();
    try {
      await api.post(`/bookings/${id}/retry/`);
      fetchCustomers();
    } catch (err) {
      alert(err.message || 'Failed to retry booking');
    }
  };

  const handleStartBatch = async () => {
    if (!selectedIds.length) return;
    setActionLoading(true);
    try {
      await api.post('/bookings/start-batch/', { ids: selectedIds });
      setSelectedIds([]);
      fetchCustomers();
    } catch (err) {
      alert(err.message || 'Failed to start batch');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteBatch = async () => {
    if (!selectedIds.length) return;
    if (!window.confirm(`Delete ${selectedIds.length} selected customers?`)) return;
    setActionLoading(true);
    try {
      await api.post('/bookings/bulk-delete/', { ids: selectedIds });
      setSelectedIds([]);
      fetchCustomers();
    } catch (err) {
      alert(err.message || 'Failed to delete selected');
    } finally {
      setActionLoading(false);
    }
  };

  const statusOptions = [
    { label: 'All', value: 'ALL' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Running', value: 'RUNNING' },
    { label: 'Action Required', value: 'WAITING_FOR_USER' },
    { label: 'Confirmed', value: 'SUCCESS' },
    { label: 'Failed', value: 'FAILED' },
    { label: 'Cancelled', value: 'CANCELLED' },
  ];

  return (
    <div className="space-y-5">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Customers & Booking Pipeline</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage applicant accounts, initiate workflows, and monitor execution states.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-blue-600 text-white hover:bg-blue-500 transition-all shadow-md shadow-blue-500/20"
          >
            <UserPlus className="w-4 h-4" />
            Add Customer
          </button>

          <button
            onClick={fetchCustomers}
            disabled={loading}
            className="p-2 rounded-xl text-slate-400 bg-slate-900 border border-slate-800 hover:text-white hover:bg-slate-800 transition-colors"
            title="Refresh list"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {statusOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setStatusFilter(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                statusFilter === opt.value
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative min-w-[260px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name, passport, email..."
            className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>
      </div>

      {/* Bulk Action Bar (When selected) */}
      {selectedIds.length > 0 && (
        <div className="bg-blue-950/40 border border-blue-500/30 rounded-xl p-3 flex items-center justify-between text-xs text-blue-200 animate-fade-in">
          <div className="flex items-center gap-2 font-medium">
            <CheckSquare className="w-4 h-4 text-blue-400" />
            <span>{selectedIds.length} customer(s) selected</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleStartBatch}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-sm transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              Start Automation
            </button>

            <button
              onClick={handleDeleteBatch}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-semibold transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete Selected
            </button>

            <button
              onClick={() => setSelectedIds([])}
              className="text-slate-400 hover:text-slate-200 px-2"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Customer Data Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-[11px] uppercase bg-slate-950/60 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4 w-10 text-center">
                  <button
                    onClick={toggleSelectAll}
                    className="text-slate-400 hover:text-white"
                  >
                    {selectedIds.length > 0 && selectedIds.length === customers.length ? (
                      <CheckSquare className="w-4 h-4 text-blue-400" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                </th>
                <th className="py-3 px-4">Customer / Email</th>
                <th className="py-3 px-4">Passport No.</th>
                <th className="py-3 px-4">Nationality</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Progress / Step</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading customer accounts...
                  </td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500">
                    No customer records match the criteria.
                  </td>
                </tr>
              ) : (
                customers.map((c) => {
                  const isSelected = selectedIds.includes(c.id);
                  return (
                    <tr
                      key={c.id}
                      onClick={() => setActiveCustomer(c)}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-blue-900/15'
                          : 'hover:bg-slate-800/30'
                      }`}
                    >
                      <td 
                        className="py-3.5 px-4 text-center"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSelect(c.id);
                        }}
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-blue-400 mx-auto" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-600 hover:text-slate-400 mx-auto" />
                        )}
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="font-bold text-white truncate max-w-xs">
                          {c.full_name || c.email}
                        </div>
                        <div className="text-[11px] text-slate-400 truncate max-w-xs">
                          {c.email}
                        </div>
                      </td>

                      <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">
                        {c.passport_number}
                      </td>

                      <td className="py-3.5 px-4 text-slate-300">
                        {c.nationality}
                      </td>

                      <td className="py-3.5 px-4">
                        <StatusBadge status={c.status} />
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="text-xs text-slate-300 font-mono truncate max-w-[200px]">
                          {c.current_step || 'Idle'}
                        </div>
                        {c.status === 'RUNNING' && (
                          <div className="w-24 bg-slate-800 rounded-full h-1 mt-1.5 overflow-hidden">
                            <div
                              className="bg-blue-500 h-1 rounded-full"
                              style={{ width: `${Math.min(100, ((c.step_progress || 0) / (c.total_steps || 8)) * 100)}%` }}
                            />
                          </div>
                        )}
                      </td>

                      <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1.5">
                          {c.status === 'WAITING_FOR_USER' && (
                            <button
                              onClick={() => setWaitingModalBooking(c)}
                              className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 flex items-center gap-1"
                            >
                              <AlertTriangle className="w-3 h-3" />
                              Verify
                            </button>
                          )}

                          {c.status === 'PENDING' && (
                            <button
                              onClick={(e) => handleStartSingle(e, c.id)}
                              className="p-1.5 rounded-lg text-blue-400 hover:text-white hover:bg-blue-600/20 transition-colors"
                              title="Start automation"
                            >
                              <Play className="w-4 h-4 fill-current" />
                            </button>
                          )}

                          {(c.status === 'FAILED' || c.status === 'CANCELLED') && (
                            <button
                              onClick={(e) => handleRetrySingle(e, c.id)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800 transition-colors"
                              title="Retry automation"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                          )}

                          <button
                            onClick={() => setActiveCustomer(c)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                            title="Inspect details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals & Drawers */}
      <CustomerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchCustomers}
      />

      <CustomerDetailDrawer
        booking={activeCustomer}
        isOpen={Boolean(activeCustomer)}
        onClose={() => setActiveCustomer(null)}
        onRefresh={fetchCustomers}
      />

      {waitingModalBooking && (
        <WaitingForUserModal
          booking={waitingModalBooking}
          onClose={() => setWaitingModalBooking(null)}
          onRefresh={fetchCustomers}
        />
      )}

    </div>
  );
};

export default CustomersPage;
