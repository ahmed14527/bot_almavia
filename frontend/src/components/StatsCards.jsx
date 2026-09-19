import React from 'react';
import { 
  Users, 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock 
} from 'lucide-react';

const StatsCards = ({ stats, onFilterSelect }) => {
  const cards = [
    {
      id: 'ALL',
      title: 'Total Customers',
      value: stats?.total ?? 0,
      icon: Users,
      color: 'blue',
      badgeBg: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    },
    {
      id: 'RUNNING',
      title: 'In Progress',
      value: stats?.running ?? 0,
      icon: Activity,
      color: 'cyan',
      badgeBg: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400',
      pulse: (stats?.running ?? 0) > 0,
    },
    {
      id: 'WAITING_FOR_USER',
      title: 'Action Required',
      value: stats?.waiting_for_user ?? 0,
      icon: AlertTriangle,
      color: 'amber',
      badgeBg: 'bg-amber-500/15 border-amber-500/30 text-amber-400',
      pulse: (stats?.waiting_for_user ?? 0) > 0,
    },
    {
      id: 'SUCCESS',
      title: 'Confirmed Bookings',
      value: stats?.success ?? 0,
      icon: CheckCircle2,
      color: 'emerald',
      badgeBg: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    },
    {
      id: 'FAILED',
      title: 'Failed Attempts',
      value: stats?.failed ?? 0,
      icon: XCircle,
      color: 'rose',
      badgeBg: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    },
    {
      id: 'PENDING',
      title: 'Pending Queue',
      value: stats?.pending ?? 0,
      icon: Clock,
      color: 'slate',
      badgeBg: 'bg-slate-800 border-slate-700 text-slate-300',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.id}
            onClick={() => onFilterSelect && onFilterSelect(card.id)}
            className={`p-4 rounded-xl border bg-slate-900/60 backdrop-blur-sm transition-all cursor-pointer hover:border-slate-600/80 hover:bg-slate-800/40 relative overflow-hidden ${
              card.badgeBg
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">{card.title}</span>
              <Icon className="w-4 h-4 opacity-80" />
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold tracking-tight text-white">
                {card.value}
              </span>
              {card.pulse && (
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;
