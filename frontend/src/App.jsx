import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import ExcelImportPage from './pages/ExcelImportPage';
import WorkflowTrackerPage from './pages/WorkflowTrackerPage';
import LoginPage from './pages/LoginPage';

function MainApp() {
  const { user, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [navParams, setNavParams] = useState({});

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm font-mono">
        Loading Italian Visa Bot System...
      </div>
    );
  }

  // If no authenticated user, show LoginPage with optional bypass
  if (!user) {
    return <LoginPage />;
  }

  const handleNavigate = (tab, params = {}) => {
    setNavParams(params);
    setCurrentTab(tab);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar currentTab={currentTab} onSelectTab={(tab) => handleNavigate(tab)} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {currentTab === 'dashboard' && (
          <DashboardPage 
            onNavigate={handleNavigate} 
            onSelectCustomer={(id) => handleNavigate('customers', { openId: id })} 
          />
        )}

        {currentTab === 'customers' && (
          <CustomersPage 
            initialFilter={navParams.filterStatus} 
            openIdOnLoad={navParams.openId} 
          />
        )}

        {currentTab === 'excel' && (
          <ExcelImportPage onNavigate={handleNavigate} />
        )}

        {currentTab === 'automation' && (
          <WorkflowTrackerPage initialBookingId={navParams.bookingId} />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/60 py-4 text-center text-xs text-slate-600">
        Italian Embassy Visa Appointment Automation System • Almaviva Egypt Portal
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainApp />
      </AuthProvider>
    </ThemeProvider>
  );
}
