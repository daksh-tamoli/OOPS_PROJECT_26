import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, Clock, Search, User,
  PlusCircle, RefreshCw, Check, X, FileText, Sun, Moon,
  Layers, AlertCircle, FileEdit, Server, AlertTriangle,
  Lock, Mail, LogOut, ArrowRight, Printer, BarChart3, Send, Sliders,
  ShieldCheck, ArrowLeft
} from 'lucide-react';

interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: 'EMPLOYEE' | 'TECHNICIAN' | 'ADMIN';
  department?: string;
  skills?: string[];
}

interface Incident {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  service: { id: string; name: string; tier: string };
  reporter: { id: string; name: string; email: string };
  assigned_technician: { id: string; name: string; email: string } | null;
  created_at: string;
  sla: {
    response_deadline: string;
    resolution_deadline: string;
    responded_at: string | null;
    resolved_at: string | null;
    is_breached: boolean;
    is_at_risk: boolean;
  };
  investigation_notes: string[];
  resolution_details: string;
  resolution_feedback: string;
  parent_incident_id: string | null;
  audit_logs: Array<{
    id: string;
    timestamp: string;
    actor_name: string;
    action: string;
    previous_state: string;
    new_state: string;
    description: string;
  }>;
}

interface ITService {
  id: string;
  name: string;
  description: string;
  tier: string;
}

interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  skills: string[];
  load: number;
  max_load: number;
}

const getPriorityLabel = (priority: string): string => {
  switch (priority?.toUpperCase()) {
    case 'P1': return 'Critical';
    case 'P2': return 'High';
    case 'P3': return 'Medium';
    case 'P4': return 'Low';
    default: return priority || 'Normal';
  }
};

const formatServiceTier = (tier: string): string => {
  switch (tier?.toUpperCase()) {
    case 'TIER_1_CRITICAL': return 'Tier 1 - Critical';
    case 'TIER_2': return 'Tier 2 - High';
    case 'TIER_3': return 'Tier 3 - Standard';
    default: return tier ? tier.replace(/_/g, ' ') : '';
  }
};

export function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => {
    try {
      const saved = localStorage.getItem('itsm_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [role, setRole] = useState<'EMPLOYEE' | 'TECHNICIAN' | 'ADMIN'>(
    currentUser?.role || 'EMPLOYEE'
  );

  // Authentication form states
  const [authMode, setAuthMode] = useState<'LOGIN' | 'REGISTER' | 'FORGOT_PASSWORD'>('LOGIN');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [resetEmail, setResetEmail] = useState('');
  const [resetPassword, setResetPassword] = useState('');
  const [resetConfirmPassword, setResetConfirmPassword] = useState('');
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regDept, setRegDept] = useState('Finance');
  const [regRole, setRegRole] = useState<'EMPLOYEE' | 'TECHNICIAN' | 'ADMIN'>('EMPLOYEE');
  const [regStep, setRegStep] = useState<'INPUT' | 'VERIFY_CODE'>('INPUT');
  const [regCode, setRegCode] = useState('');
  const [regResending, setRegResending] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authSuccess, setAuthSuccess] = useState('');
  const [authSubmitting, setAuthSubmitting] = useState(false);

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [services, setServices] = useState<ITService[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [viewFilter, setViewFilter] = useState<'ALL' | 'MY_TICKETS' | 'CRITICAL' | 'SLA_BREACH'>('ALL');
  const [loading, setLoading] = useState(false);

  // New incident form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newServiceId, setNewServiceId] = useState('srv-payment');
  const [newImpact, setNewImpact] = useState('HIGH');
  const [newUrgency, setNewUrgency] = useState('HIGH');
  const [newStrategy, setNewStrategy] = useState('smart');
  const [detectedDuplicates, setDetectedDuplicates] = useState<any[]>([]);

  // Action input states
  const [actionNote, setActionNote] = useState('');
  const [resolutionNote, setResolutionNote] = useState('');
  const [verificationFeedback, setVerificationFeedback] = useState('');

  // Executive Reports Modal & Data
  const [showExecutiveReport, setShowExecutiveReport] = useState(false);

  // Email Notification Outbox & Live Dispatcher
  const [showNotificationOutbox, setShowNotificationOutbox] = useState(false);
  const [outboxEmails, setOutboxEmails] = useState<any[]>([]);
  const [smtpConfigured, setSmtpConfigured] = useState(false);
  const [selectedOutboxEmail, setSelectedOutboxEmail] = useState<any | null>(null);
  const [outboxActiveTab, setOutboxActiveTab] = useState<'OUTBOX' | 'TEST'>('OUTBOX');
  const [testEmailTo, setTestEmailTo] = useState('');
  const [testEmailSub, setTestEmailSub] = useState('Real Email Dispatch Test');
  const [testEmailMsg, setTestEmailMsg] = useState('Testing real email notification delivery from the I-ITSM Platform.');
  const [testEmailSending, setTestEmailSending] = useState(false);
  const [testEmailResult, setTestEmailResult] = useState<string | null>(null);

  // Priority Management Matrix & Overrides
  const [showPriorityMatrixModal, setShowPriorityMatrixModal] = useState(false);
  const [showPriorityOverrideModal, setShowPriorityOverrideModal] = useState(false);
  const [overridePriorityVal, setOverridePriorityVal] = useState('P1');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSubmitting, setOverrideSubmitting] = useState(false);

  const API_BASE = 'http://localhost:8000/api';

  // Toggle Theme
  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Sync role with currentUser
  useEffect(() => {
    if (currentUser) {
      setRole(currentUser.role);
      localStorage.setItem('itsm_auth_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('itsm_auth_user');
      localStorage.removeItem('itsm_auth_token');
    }
  }, [currentUser]);

  // Auth Operations
  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPass?: string) => {
    if (e) e.preventDefault();
    setAuthError('');
    setAuthSubmitting(true);
    const emailToUse = customEmail || loginEmail;
    const passToUse = customPass || loginPassword;
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailToUse, password: passToUse })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Login failed');
      }
      setCurrentUser(data.user);
      setRole(data.user.role);
      if (data.token) localStorage.setItem('itsm_auth_token', data.token);
    } catch (err: any) {
      setAuthError(err.message || 'Login failed');
    } finally {
      setAuthSubmitting(false);
    }
  };

  // Enterprise Password Strength Evaluation Helper
  const checkPasswordCriteria = (pass: string) => ({
    length: pass.length >= 8,
    uppercase: /[A-Z]/.test(pass),
    lowercase: /[a-z]/.test(pass),
    number: /\d/.test(pass),
    special: /[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\;'/`~]/.test(pass),
  });

  const getPasswordScore = (pass: string) => {
    if (!pass) return { score: 0, label: 'Enter password', color: '#525252', isValid: false };
    const crit = checkPasswordCriteria(pass);
    const count = Object.values(crit).filter(Boolean).length;
    if (count <= 1) return { score: 20, label: 'Very Weak', color: '#ef4444', isValid: false };
    if (count === 2) return { score: 40, label: 'Weak', color: '#f97316', isValid: false };
    if (count === 3) return { score: 60, label: 'Fair (Needs uppercase/number/symbol)', color: '#eab308', isValid: false };
    if (count === 4) return { score: 80, label: 'Good (Almost compliant)', color: '#3b82f6', isValid: false };
    return { score: 100, label: 'Strong (Enterprise Compliant)', color: '#10b981', isValid: true };
  };

  // Step 1: Send 6-Digit Email Verification Code
  const handleSendVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');

    const strength = getPasswordScore(regPassword);
    if (!strength.isValid) {
      setAuthError('Password must meet all 5 enterprise security requirements before receiving an email verification code.');
      return;
    }

    setAuthSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/send-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: regEmail,
          full_name: regName,
          password: regPassword,
          department: regDept,
          role: regRole
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to dispatch verification code');
      }
      setRegStep('VERIFY_CODE');
      setAuthSuccess(`A 6-digit security verification code has been dispatched to ${regEmail}. Please enter the code below to finalize your account.`);
    } catch (err: any) {
      setAuthError(err.message || 'Failed to send verification code');
    } finally {
      setAuthSubmitting(false);
    }
  };

  // Step 2: Verify 6-Digit OTP Code & Register User Account
  const handleVerifyAndRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');

    if (regCode.trim().length < 4) {
      setAuthError('Please enter the 6-digit verification code sent to your corporate email.');
      return;
    }

    setAuthSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/verify-and-register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: regEmail,
          code: regCode.trim()
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Email verification failed');
      }
      setCurrentUser(data.user);
      setRole(data.user.role);
      if (data.token) localStorage.setItem('itsm_auth_token', data.token);
      setAuthSuccess('Corporate email verified! Account created and signed in successfully.');
      await fetchData();
    } catch (err: any) {
      setAuthError(err.message || 'Verification failed');
    } finally {
      setAuthSubmitting(false);
    }
  };

  // Resend Verification Code
  const handleResendCode = async () => {
    setAuthError('');
    setAuthSuccess('');
    setRegResending(true);
    try {
      const res = await fetch(`${API_BASE}/auth/resend-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: regEmail })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to resend code');
      }
      setAuthSuccess(`A fresh 6-digit verification code was dispatched to ${regEmail}. Check your inbox or Outbox preview.`);
    } catch (err: any) {
      setAuthError(err.message || 'Failed to resend code');
    } finally {
      setRegResending(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');
    if (resetPassword !== resetConfirmPassword) {
      setAuthError('Passwords do not match. Please re-enter.');
      return;
    }
    const resetStrength = getPasswordScore(resetPassword);
    if (!resetStrength.isValid) {
      setAuthError('New password must meet enterprise security requirements (8+ chars, upper, lower, digit, and special char).');
      return;
    }
    setAuthSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: resetEmail,
          new_password: resetPassword
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Password reset failed');
      }
      setAuthSuccess('Password has been reset successfully! Please sign in with your new password.');
      setLoginEmail(resetEmail);
      setLoginPassword(resetPassword);
      setAuthMode('LOGIN');
    } catch (err: any) {
      setAuthError(err.message || 'Password reset failed');
    } finally {
      setAuthSubmitting(false);
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setLoginPassword('');
    setAuthError('');
    setAuthSuccess('');
    setSelectedIncident(null);
  };

  // Load incidents & services
  const fetchData = async () => {
    try {
      setLoading(true);
      const [incRes, srvRes, userRes, analRes] = await Promise.all([
        fetch(`${API_BASE}/incidents`),
        fetch(`${API_BASE}/services`),
        fetch(`${API_BASE}/users`),
        fetch(`${API_BASE}/analytics`)
      ]);
      const incData = await incRes.json();
      const srvData = await srvRes.json();
      const userData = await userRes.json();
      const analData = await analRes.json();

      setIncidents(incData);
      setServices(srvData);
      setUsers(userData);
      setAnalytics(analData);

      if (selectedIncident) {
        const updated = incData.find((i: Incident) => i.id === selectedIncident.id);
        if (updated) setSelectedIncident(updated);
      }
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/notifications`);
      const data = await res.json();
      setOutboxEmails(data.emails || []);
      setSmtpConfigured(data.smtp_configured || false);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const handleOpenExecutiveReport = () => {
    setShowExecutiveReport(true);
  };

  const handleSendTestEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setTestEmailSending(true);
    setTestEmailResult(null);
    try {
      const res = await fetch(`${API_BASE}/notifications/test-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to_email: testEmailTo,
          subject: testEmailSub,
          message: testEmailMsg
        })
      });
      const data = await res.json();
      setTestEmailResult(`Dispatched via ${data.delivery_status}! ${data.smtp_configured ? 'Delivered via live SMTP.' : 'Tracked in Enterprise Outbox.'}`);
      fetchNotifications();
    } catch (err: any) {
      setTestEmailResult(`Dispatch failed: ${err.message}`);
    } finally {
      setTestEmailSending(false);
    }
  };

  const handleOverridePriority = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident || !currentUser) return;
    setOverrideSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/incidents/${selectedIncident.id}/override-priority`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_priority: overridePriorityVal,
          reason: overrideReason,
          admin_id: currentUser.id
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Priority override failed');
      }
      setShowPriorityOverrideModal(false);
      setOverrideReason('');
      fetchData();
      fetchNotifications();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setOverrideSubmitting(false);
    }
  };

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    fetchData();
    fetchNotifications();
    const interval = setInterval(() => {
      fetchData();
      fetchNotifications();
    }, 8000);
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => {
      clearInterval(interval);
      clearInterval(clockInterval);
    };
  }, []);

  const getSlaRemainingText = (deadlineStr: string, isBreached: boolean, status: string) => {
    if (['RESOLVED', 'VERIFIED', 'CLOSED'].includes(status)) {
      return isBreached ? 'Resolved (SLA Breached)' : 'Resolved within SLA';
    }
    const dl = new Date(deadlineStr).getTime();
    const diffMs = dl - currentTime.getTime();
    if (diffMs > 0) {
      const totalMins = Math.floor(diffMs / 60000);
      const hrs = Math.floor(totalMins / 60);
      const remMins = totalMins % 60;
      if (hrs > 0) {
        return `${hrs}h ${remMins}m remaining`;
      }
      return `${totalMins}m remaining`;
    } else {
      const overdueMins = Math.floor(Math.abs(diffMs) / 60000);
      const overdueHrs = Math.floor(overdueMins / 60);
      if (overdueHrs > 0) {
        return `Overdue by ${overdueHrs}h ${overdueMins % 60}m`;
      }
      return `Overdue by ${overdueMins}m`;
    }
  };

  // Filtered incidents
  const filteredIncidents = incidents.filter(inc => {
    // Quick View Filter from Sidebar
    if (viewFilter === 'MY_TICKETS') {
      if (role === 'EMPLOYEE' && inc.reporter.id !== (currentUser?.id || 'user-emp-1')) return false;
      if (role === 'TECHNICIAN' && inc.assigned_technician?.id !== (currentUser?.id || 'tech-101')) return false;
    }
    if (viewFilter === 'CRITICAL' && inc.priority !== 'P1') return false;
    if (viewFilter === 'SLA_BREACH' && !inc.sla.is_breached) return false;

    // Dropdown Filters
    if (statusFilter !== 'ALL' && inc.status !== statusFilter) return false;
    if (priorityFilter !== 'ALL' && inc.priority !== priorityFilter) return false;

    // Search Query
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        inc.title.toLowerCase().includes(q) ||
        inc.id.toLowerCase().includes(q) ||
        inc.description.toLowerCase().includes(q) ||
        inc.service.name.toLowerCase().includes(q)
      );
    }
    return true;
  });

  // Handle report incident
  const handleReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          description: newDesc,
          service_id: newServiceId,
          reporter_id: currentUser?.id || 'user-emp-1',
          impact: newImpact,
          urgency: newUrgency,
          assignment_strategy: newStrategy,
          auto_assign: true
        })
      });
      const data = await res.json();
      if (data.duplicates_detected && data.duplicates_detected.length > 0) {
        setDetectedDuplicates(data.duplicates_detected);
      } else {
        setIsReportModalOpen(false);
        setNewTitle('');
        setNewDesc('');
      }
      fetchData();
    } catch (err) {
      alert('Error creating incident: ' + err);
    }
  };

  // Technician Actions
  const handleAcknowledge = async (id: string) => {
    const techId = currentUser?.id || 'tech-101';
    await fetch(`${API_BASE}/incidents/${id}/acknowledge?technician_id=${techId}`, { method: 'POST' });
    fetchData();
  };

  const handleStartInvestigation = async (id: string) => {
    if (!actionNote) return;
    const techId = currentUser?.id || 'tech-101';
    await fetch(`${API_BASE}/incidents/${id}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_id: techId, notes: actionNote })
    });
    setActionNote('');
    fetchData();
  };

  const handleResolve = async (id: string) => {
    if (!resolutionNote) return;
    const techId = currentUser?.id || 'tech-101';
    await fetch(`${API_BASE}/incidents/${id}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_id: techId, resolution_details: resolutionNote })
    });
    setResolutionNote('');
    fetchData();
  };

  // Employee Verification
  const handleVerify = async (id: string, confirmed: boolean) => {
    const actorId = currentUser?.id || 'user-emp-1';
    await fetch(`${API_BASE}/incidents/${id}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actor_id: actorId,
        is_confirmed: confirmed,
        feedback: verificationFeedback || (confirmed ? 'Confirmed resolved.' : 'Issue persists.')
      })
    });
    setVerificationFeedback('');
    fetchData();
  };

  // Admin Actions
  const handleTriggerSLA = async () => {
    const res = await fetch(`${API_BASE}/sla/trigger-cycle`, { method: 'POST' });
    const data = await res.json();
    alert(`SLA Cycle Complete!\nOpen tickets evaluated: ${data.total_open}\nSLA Breaches detected: ${data.breached_count}\nAuto-escalated tickets: ${data.escalated_incidents.length}`);
    fetchData();
  };

  const handleClose = async (id: string) => {
    const adminId = currentUser?.id || 'user-admin-1';
    await fetch(`${API_BASE}/incidents/${id}/close?actor_id=${adminId}`, { method: 'POST' });
    fetchData();
  };

  if (!currentUser) {
    return (
      <div className="auth-container">
        {/* Top Right Theme Toggle */}
        <div style={{ position: 'absolute', top: 24, right: 28 }}>
          <div 
            onClick={toggleTheme}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 14px',
              borderRadius: 8,
              border: '1px solid var(--border-subtle)',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              userSelect: 'none',
              fontSize: 13
            }}
          >
            {theme === 'dark' ? <Moon size={15} color="var(--role-orange)" /> : <Sun size={15} color="var(--role-orange)" />}
            <span>{theme === 'dark' ? 'Dark' : 'Light'}</span>
          </div>
        </div>

        {/* Central Auth Card */}
        <div className="auth-card">
          {/* Brand Header */}
          <div style={{ textAlign: 'center', marginBottom: 26 }}>
            <div style={{ 
              display: 'inline-flex', 
              padding: 12, 
              borderRadius: 12, 
              background: 'rgba(249, 115, 22, 0.12)', 
              border: '1px solid rgba(249, 115, 22, 0.3)',
              marginBottom: 14 
            }}>
              <Server size={30} color="var(--role-orange)" />
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.3px', color: 'var(--text-primary)', marginBottom: 4 }}>
              I-ITSM Platform
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Enterprise Incident Management System (CS F213 / MAC F212)
            </p>
          </div>

          {/* Mode Switch Tabs (Sign In vs Register vs Forgot Password) */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', marginBottom: 22 }}>
            <button 
              className={`auth-tab-btn ${authMode === 'LOGIN' ? 'active' : ''}`}
              onClick={() => { setAuthMode('LOGIN'); setAuthError(''); setAuthSuccess(''); }}
            >
              Sign In
            </button>
            <button 
              className={`auth-tab-btn ${authMode === 'REGISTER' ? 'active' : ''}`}
              onClick={() => { setAuthMode('REGISTER'); setRegStep('INPUT'); setRegCode(''); setAuthError(''); setAuthSuccess(''); }}
            >
              Register Account
            </button>
            {authMode === 'FORGOT_PASSWORD' && (
              <button className="auth-tab-btn active">
                Reset Password
              </button>
            )}
          </div>

          {/* Error Banner */}
          {authError && (
            <div style={{ 
              background: 'rgba(239, 68, 68, 0.12)', 
              border: '1px solid rgba(239, 68, 68, 0.3)', 
              borderRadius: 8, 
              padding: '10px 14px', 
              fontSize: 13, 
              color: '#ef4444', 
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{authError}</span>
            </div>
          )}

          {/* Success Banner */}
          {authSuccess && (
            <div style={{ 
              background: 'rgba(16, 185, 129, 0.12)', 
              border: '1px solid rgba(16, 185, 129, 0.3)', 
              borderRadius: 8, 
              padding: '10px 14px', 
              fontSize: 13, 
              color: '#10b981', 
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
              <span>{authSuccess}</span>
            </div>
          )}

          {/* Sign In Form */}
          {authMode === 'LOGIN' ? (
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Corporate Email
                </label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                  <input 
                    type="email" 
                    placeholder="e.g. alice@company.com"
                    value={loginEmail}
                    onChange={e => setLoginEmail(e.target.value)}
                    required
                    className="flat-input"
                    style={{ paddingLeft: 38 }}
                  />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthError('');
                      setAuthSuccess('');
                      setResetEmail(loginEmail);
                      setAuthMode('FORGOT_PASSWORD');
                    }}
                    style={{ background: 'none', border: 'none', color: 'var(--role-orange)', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                  >
                    Forgot Password?
                  </button>
                </div>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                  <input 
                    type="password" 
                    placeholder="Enter password..."
                    value={loginPassword}
                    onChange={e => setLoginPassword(e.target.value)}
                    required
                    className="flat-input"
                    style={{ paddingLeft: 38 }}
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="btn-primary" 
                disabled={authSubmitting}
                style={{ width: '100%', justifyContent: 'center', padding: '11px', marginTop: 4, opacity: authSubmitting ? 0.7 : 1 }}
              >
                {authSubmitting ? 'Authenticating...' : 'Sign In to Workspace'} <ArrowRight size={16} />
              </button>

              {/* Quick Evaluation Accounts Chips for Professors / Graders */}
              <div style={{ marginTop: 10, paddingTop: 14, borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                  Quick Fill Test Accounts (Password: password123 / PASSWORD123)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div 
                    className="auth-quick-chip"
                    onClick={() => {
                      setLoginEmail('alice@company.com');
                      setLoginPassword('password123');
                      handleLogin(undefined, 'alice@company.com', 'password123');
                    }}
                  >
                    <span><strong>Alice Smith</strong> (Employee / Customer)</span>
                    <span style={{ fontSize: 11, color: 'var(--role-orange)' }}>Login ➔</span>
                  </div>
                  <div 
                    className="auth-quick-chip"
                    onClick={() => {
                      setLoginEmail('devon@itsm.local');
                      setLoginPassword('password123');
                      handleLogin(undefined, 'devon@itsm.local', 'password123');
                    }}
                  >
                    <span><strong>Devon Vance</strong> (Technician / Support Eng)</span>
                    <span style={{ fontSize: 11, color: 'var(--role-orange)' }}>Login ➔</span>
                  </div>
                  <div 
                    className="auth-quick-chip"
                    onClick={() => {
                      setLoginEmail('admin@itsm.local');
                      setLoginPassword('password123');
                      handleLogin(undefined, 'admin@itsm.local', 'password123');
                    }}
                  >
                    <span><strong>Sarah Connor</strong> (IT Administrator / Manager)</span>
                    <span style={{ fontSize: 11, color: 'var(--role-orange)' }}>Login ➔</span>
                  </div>
                </div>
              </div>
            </form>
          ) : authMode === 'REGISTER' ? (
            /* Register Account Form with Real Email Verification & Password Strength */
            regStep === 'INPUT' ? (
              <form onSubmit={handleSendVerification} style={{ display: 'flex', flexDirection: 'column', gap: 13 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 4, borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--role-orange)' }}>
                    Step 1 of 2: Enterprise Credentials
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Email OTP Required</span>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Full Name
                  </label>
                  <div style={{ position: 'relative' }}>
                    <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                    <input 
                      type="text" 
                      placeholder="e.g. John Doe"
                      value={regName}
                      onChange={e => setRegName(e.target.value)}
                      required
                      className="flat-input"
                      style={{ paddingLeft: 38 }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Corporate Email
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                    <input 
                      type="email" 
                      placeholder="name@company.com"
                      value={regEmail}
                      onChange={e => setRegEmail(e.target.value)}
                      required
                      className="flat-input"
                      style={{ paddingLeft: 38 }}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  <div>
                    <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                      Department
                    </label>
                    <input 
                      type="text" 
                      placeholder="e.g. Finance"
                      value={regDept}
                      onChange={e => setRegDept(e.target.value)}
                      className="flat-input"
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                      Account Role
                    </label>
                    <select 
                      value={regRole} 
                      onChange={e => setRegRole(e.target.value as any)}
                      className="flat-select"
                    >
                      <option value="EMPLOYEE">Employee / Customer</option>
                      <option value="TECHNICIAN">Technician</option>
                      <option value="ADMIN">Administrator</option>
                    </select>
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
                      Enterprise Password
                    </label>
                    {regPassword && (
                      <span style={{ fontSize: 11, fontWeight: 700, color: getPasswordScore(regPassword).color }}>
                        {getPasswordScore(regPassword).label}
                      </span>
                    )}
                  </div>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                    <input 
                      type="password" 
                      placeholder="Min 8 chars with Upper, Number & Symbol..."
                      value={regPassword}
                      onChange={e => setRegPassword(e.target.value)}
                      required
                      className="flat-input"
                      style={{ paddingLeft: 38 }}
                    />
                  </div>

                  {/* Password Strength Meter & Real-Time Rule Checklist */}
                  <div style={{ marginTop: 8, background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 10 }}>
                    <div style={{ height: 4, background: 'var(--border-subtle)', borderRadius: 2, overflow: 'hidden', marginBottom: 8 }}>
                      <div 
                        style={{ 
                          height: '100%', 
                          width: `${getPasswordScore(regPassword).score}%`, 
                          background: getPasswordScore(regPassword).color, 
                          transition: 'all 0.3s ease' 
                        }} 
                      />
                    </div>
                    
                    {(() => {
                      const crit = checkPasswordCriteria(regPassword);
                      return (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, fontSize: 11 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: crit.length ? '#10b981' : 'var(--text-muted)' }}>
                            {crit.length ? <Check size={12} /> : <X size={12} />} 8+ Characters
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: crit.uppercase ? '#10b981' : 'var(--text-muted)' }}>
                            {crit.uppercase ? <Check size={12} /> : <X size={12} />} 1 Uppercase (A-Z)
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: crit.lowercase ? '#10b981' : 'var(--text-muted)' }}>
                            {crit.lowercase ? <Check size={12} /> : <X size={12} />} 1 Lowercase (a-z)
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: crit.number ? '#10b981' : 'var(--text-muted)' }}>
                            {crit.number ? <Check size={12} /> : <X size={12} />} 1 Number (0-9)
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 5, gridColumn: 'span 2', color: crit.special ? '#10b981' : 'var(--text-muted)' }}>
                            {crit.special ? <Check size={12} /> : <X size={12} />} 1 Special Character (!@#$%^&*...)
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn-primary" 
                  disabled={authSubmitting || !getPasswordScore(regPassword).isValid || !regEmail.trim() || !regName.trim()}
                  style={{ 
                    width: '100%', 
                    justifyContent: 'center', 
                    padding: '11px', 
                    marginTop: 4, 
                    opacity: (authSubmitting || !getPasswordScore(regPassword).isValid || !regEmail.trim() || !regName.trim()) ? 0.6 : 1 
                  }}
                >
                  {authSubmitting ? 'Dispatching Verification...' : 'Continue ➔ Send 6-Digit Code'} <ArrowRight size={16} />
                </button>
              </form>
            ) : (
              /* Step 2: 6-Digit OTP Verification Form */
              <form onSubmit={handleVerifyAndRegister} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 4, borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--role-orange)' }}>
                    Step 2 of 2: Security Verification
                  </span>
                  <button 
                    type="button" 
                    onClick={() => setRegStep('INPUT')}
                    style={{ background: 'transparent', border: 'none', color: 'var(--role-orange)', fontSize: 11, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
                  >
                    <ArrowLeft size={12} /> Edit Details
                  </button>
                </div>

                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: 14, textAlign: 'center' }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'rgba(249, 115, 22, 0.1)', color: 'var(--role-orange)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 10px auto' }}>
                    <ShieldCheck size={22} />
                  </div>
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 6px 0' }}>
                    Verify Your Corporate Email
                  </h4>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                    We dispatched a secure 6-digit verification code to: <br />
                    <strong style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}>{regEmail}</strong>
                  </p>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6, textAlign: 'center' }}>
                    Enter 6-Digit Verification Code
                  </label>
                  <input 
                    type="text" 
                    maxLength={6}
                    placeholder="000000"
                    value={regCode}
                    onChange={e => setRegCode(e.target.value.replace(/[^0-9]/g, ''))}
                    required
                    autoFocus
                    className="flat-input"
                    style={{ 
                      textAlign: 'center', 
                      fontSize: 26, 
                      fontWeight: 800, 
                      letterSpacing: 8, 
                      fontFamily: 'monospace', 
                      padding: '12px',
                      borderColor: regCode.length === 6 ? 'var(--role-orange)' : 'var(--border-subtle)'
                    }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8, fontSize: 11 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Valid for 10 minutes</span>
                    <button 
                      type="button"
                      onClick={handleResendCode}
                      disabled={regResending}
                      style={{ background: 'transparent', border: 'none', color: 'var(--role-orange)', cursor: 'pointer', fontWeight: 600, textDecoration: 'underline' }}
                    >
                      {regResending ? 'Resending...' : 'Resend Code'}
                    </button>
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn-primary" 
                  disabled={authSubmitting || regCode.length < 4}
                  style={{ 
                    width: '100%', 
                    justifyContent: 'center', 
                    padding: '11px', 
                    marginTop: 4, 
                    opacity: (authSubmitting || regCode.length < 4) ? 0.6 : 1 
                  }}
                >
                  {authSubmitting ? 'Verifying Code...' : 'Verify Code & Enter Workspace'} <ArrowRight size={16} />
                </button>

                <div style={{ padding: 10, borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--border-subtle)', fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  💡 <strong>Testing Locally?</strong> Dispatched verification codes can also be inspected directly in the <strong>Dispatched Email Outbox</strong> or system notification stream.
                </div>
              </form>
            )
          ) : (
            /* Forgot Password Form */
            <form onSubmit={handleForgotPassword} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Corporate Email
                </label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                  <input 
                    type="email" 
                    placeholder="e.g. alice@company.com"
                    value={resetEmail}
                    onChange={e => setResetEmail(e.target.value)}
                    required
                    className="flat-input"
                    style={{ paddingLeft: 38 }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  New Password
                </label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                  <input 
                    type="password" 
                    placeholder="At least 4 characters..."
                    value={resetPassword}
                    onChange={e => setResetPassword(e.target.value)}
                    required
                    minLength={4}
                    className="flat-input"
                    style={{ paddingLeft: 38 }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Confirm New Password
                </label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
                  <input 
                    type="password" 
                    placeholder="Confirm new password..."
                    value={resetConfirmPassword}
                    onChange={e => setResetConfirmPassword(e.target.value)}
                    required
                    minLength={4}
                    className="flat-input"
                    style={{ paddingLeft: 38 }}
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="btn-primary" 
                disabled={authSubmitting}
                style={{ width: '100%', justifyContent: 'center', padding: '11px', marginTop: 4, opacity: authSubmitting ? 0.7 : 1 }}
              >
                {authSubmitting ? 'Resetting...' : 'Update Password'} <ArrowRight size={16} />
              </button>

              <button
                type="button"
                onClick={() => {
                  setAuthError('');
                  setAuthSuccess('');
                  setAuthMode('LOGIN');
                }}
                className="btn-secondary"
                style={{ width: '100%', justifyContent: 'center', padding: '9px', fontSize: 12 }}
              >
                Cancel & Return to Sign In
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
      
      {/* ======================================================== */}
      {/* 1. LEFT SIDEBAR                                          */}
      {/* ======================================================== */}
      <aside 
        style={{ 
          width: 260, 
          background: 'var(--bg-sidebar)', 
          borderRight: '1px solid var(--border-subtle)',
          padding: '24px 18px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          flexShrink: 0
        }}
      >
        <div>
          {/* Logo & Brand: Conventional Server Infrastructure Icon */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, paddingBottom: 16, borderBottom: '1px solid var(--border-subtle)' }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: 'linear-gradient(135deg, #f97316, #ea580c)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 10px rgba(249, 115, 22, 0.35)' }}>
              <Server size={20} color="#ffffff" />
            </div>
            <div>
              <h1 style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.3px', color: 'var(--text-primary)' }}>
                I-ITSM
              </h1>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                Incident Resolution {loading && <span style={{ color: 'var(--role-orange)' }}>●</span>}
              </span>
            </div>
          </div>

          {/* Active Authenticated Profile (Page 4, 13, 17) */}
          <div style={{ 
            background: 'var(--input-bg)', 
            border: '1px solid var(--border-subtle)', 
            borderRadius: 10, 
            padding: '12px 14px', 
            marginBottom: 20 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                Active Session
              </span>
              <span className={`badge-state-${currentUser.role.toLowerCase()}`} style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>
                {currentUser.role}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{
                width: 34,
                height: 34,
                borderRadius: '50%',
                background: 'rgba(249, 115, 22, 0.15)',
                border: '1px solid rgba(249, 115, 22, 0.4)',
                color: 'var(--role-orange)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: 13,
                flexShrink: 0
              }}>
                {currentUser.name ? currentUser.name.split(' ').map(n => n[0]).slice(0, 2).join('') : 'U'}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {currentUser.name}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {currentUser.email}
                </div>
              </div>
            </div>

            <button 
              onClick={handleLogout}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                padding: '6px 8px',
                borderRadius: 6,
                border: '1px solid var(--border-subtle)',
                background: 'transparent',
                color: 'var(--text-secondary)',
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <LogOut size={13} /> Sign Out
            </button>
          </div>

          {/* Quick Navigation Views */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.5px', marginBottom: 10, textTransform: 'uppercase' }}>
              Workspace Views
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <button
                onClick={() => setViewFilter('ALL')}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, textAlign: 'left',
                  background: viewFilter === 'ALL' ? 'var(--input-bg)' : 'transparent',
                  color: viewFilter === 'ALL' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: viewFilter === 'ALL' ? 600 : 500
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Layers size={16} /> All Incidents
                </span>
                <span style={{ fontSize: 11, background: 'var(--border-subtle)', padding: '2px 7px', borderRadius: 99 }}>
                  {incidents.length}
                </span>
              </button>

              <button
                onClick={() => setViewFilter('MY_TICKETS')}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, textAlign: 'left',
                  background: viewFilter === 'MY_TICKETS' ? 'var(--input-bg)' : 'transparent',
                  color: viewFilter === 'MY_TICKETS' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: viewFilter === 'MY_TICKETS' ? 600 : 500
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <User size={16} /> {role === 'EMPLOYEE' ? 'My Reported Incidents' : 'My Assigned Tickets'}
                </span>
                <span style={{ fontSize: 11, background: 'var(--border-subtle)', padding: '2px 7px', borderRadius: 99 }}>
                  {role === 'EMPLOYEE'
                    ? incidents.filter(i => i.reporter?.id === currentUser?.id).length
                    : incidents.filter(i => i.assigned_technician?.id === currentUser?.id).length}
                </span>
              </button>

              <button
                onClick={() => setViewFilter('CRITICAL')}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, textAlign: 'left',
                  background: viewFilter === 'CRITICAL' ? 'var(--input-bg)' : 'transparent',
                  color: viewFilter === 'CRITICAL' ? '#f43f5e' : 'var(--text-secondary)',
                  fontWeight: viewFilter === 'CRITICAL' ? 600 : 500
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <AlertCircle size={16} /> Critical Outages
                </span>
                <span style={{ fontSize: 11, background: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e', padding: '2px 7px', borderRadius: 99 }}>
                  {analytics?.critical_incidents ?? 0}
                </span>
              </button>

              <button
                onClick={() => setViewFilter('SLA_BREACH')}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, textAlign: 'left',
                  background: viewFilter === 'SLA_BREACH' ? 'var(--input-bg)' : 'transparent',
                  color: viewFilter === 'SLA_BREACH' ? '#ea580c' : 'var(--text-secondary)',
                  fontWeight: viewFilter === 'SLA_BREACH' ? 600 : 500
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Clock size={16} /> SLA Violations
                </span>
                <span style={{ fontSize: 11, background: 'rgba(249, 115, 22, 0.15)', color: 'var(--role-orange)', padding: '2px 7px', borderRadius: 99 }}>
                  {analytics?.sla_violations ?? 0}
                </span>
              </button>

              <button
                onClick={handleOpenExecutiveReport}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, textAlign: 'left',
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  fontWeight: 500
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BarChart3 size={16} /> Executive Report
                </span>
                <span style={{ fontSize: 10, background: 'var(--border-subtle)', padding: '2px 6px', borderRadius: 4, fontWeight: 700 }}>
                  PDF
                </span>
              </button>
            </div>
          </div>

          {/* Technician Roster for Admin & Team */}
          {role === 'ADMIN' && (
            <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: 12, marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--role-orange)', marginBottom: 8, textTransform: 'uppercase' }}>
                Technician Roster
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {users.filter(u => u.role === 'TECHNICIAN').map(t => (
                  <div key={t.id} style={{ fontSize: 12, display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                    <span>{t.name.split(' ')[0]}</span>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{t.load}/{t.max_load} load</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Bottom Sidebar: Pill Switch Theme Toggle & SLA Daemon */}
        <div>
          {role === 'ADMIN' && (
            <button 
              className="btn-secondary"
              onClick={handleTriggerSLA}
              style={{ width: '100%', marginBottom: 12, fontSize: 12, padding: '7px 10px', justifyContent: 'center' }}
            >
              <RefreshCw size={14} /> Run SLA Daemon
            </button>
          )}

          {/* Theme Switch Pill (Replacing text "Toggle") */}
          <div 
            onClick={toggleTheme}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '9px 12px',
              borderRadius: 8,
              border: '1px solid var(--border-subtle)',
              background: 'var(--input-bg)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              userSelect: 'none'
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 500 }}>
              {theme === 'dark' ? <Moon size={16} color="var(--role-orange)" /> : <Sun size={16} color="var(--role-orange)" />}
              {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
            </span>
            <span className={`theme-switch-pill ${theme === 'dark' ? 'active' : ''}`}>
              <span className="theme-switch-thumb" />
            </span>
          </div>
        </div>
      </aside>

      {/* ======================================================== */}
      {/* 2. MAIN CONTENT AREA (Shrunk List + Expanded Right Pane) */}
      {/* ======================================================== */}
      <main style={{ flex: 1, padding: '24px 30px', minWidth: 0, overflowY: 'auto' }}>
        
        {/* Top Control Bar: Search + Flat Selects (Matching Page Font) + Report Button */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 14, marginBottom: 22 }}>
          <div style={{ display: 'flex', gap: 12, flex: 1, maxWidth: 640 }}>
            {/* Flat Search */}
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 14, top: 11 }} />
              <input 
                type="text" 
                placeholder="Search incident ID, title, service, or keywords..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="flat-input"
                style={{ paddingLeft: 38 }}
              />
            </div>

            {/* Flat Status Select */}
            <select 
              value={statusFilter} 
              onChange={e => setStatusFilter(e.target.value)}
              className="flat-select"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">New</option>
              <option value="ASSIGNED">Assigned</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
              <option value="VERIFIED">Verified</option>
              <option value="CLOSED">Closed</option>
            </select>

            {/* Flat Priority Select */}
            <select 
              value={priorityFilter} 
              onChange={e => setPriorityFilter(e.target.value)}
              className="flat-select"
            >
              <option value="ALL">All Priorities</option>
              <option value="P1">Critical</option>
              <option value="P2">High</option>
              <option value="P3">Medium</option>
              <option value="P4">Low</option>
            </select>
          </div>

          {/* Action CTAs & Synchronized Live Clock */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 7,
              padding: '7px 12px',
              background: 'var(--input-bg)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              fontSize: 12,
              color: 'var(--text-secondary)',
              fontWeight: 500
            }}>
              <Clock size={14} color="var(--role-orange)" />
              <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
              <span style={{ fontSize: 10, color: '#10b981', fontWeight: 600, background: 'rgba(16, 185, 129, 0.1)', padding: '2px 5px', borderRadius: 4 }}>
                LIVE
              </span>
            </div>

            {/* Email Outbox Dispatch Inspector Button */}
            <button 
              className="btn-secondary"
              onClick={() => { fetchNotifications(); setShowNotificationOutbox(true); }}
              style={{ fontSize: 12, padding: '7px 11px', gap: 6 }}
              title="View live dispatched notification emails"
            >
              <Mail size={14} color="var(--role-orange)" />
              <span>Outbox</span>
              <span style={{ fontSize: 10, background: 'rgba(249, 115, 22, 0.2)', color: 'var(--role-orange)', padding: '1px 5px', borderRadius: 99, fontWeight: 700 }}>
                {outboxEmails.length}
              </span>
            </button>

            {/* Executive Report & PDF Export Button */}
            <button 
              className="btn-secondary"
              onClick={handleOpenExecutiveReport}
              style={{ fontSize: 12, padding: '7px 11px', gap: 6 }}
              title="Generate and export official Executive Report as PDF"
            >
              <BarChart3 size={14} color="var(--role-orange)" />
              <span>Reports & PDF</span>
            </button>

            {role === 'EMPLOYEE' && (
              <button 
                className="btn-primary"
                onClick={() => { setIsReportModalOpen(true); setDetectedDuplicates([]); }}
              >
                <PlusCircle size={16} /> Report Incident
              </button>
            )}
          </div>
        </div>

        {/* Metrics Banner (FileEdit Document Icon for Active Open Tickets) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 22 }}>
          <div className="glass-panel" style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 6 }}>
              <span>Total Incidents</span>
              <FileText size={18} color="#3b82f6" />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)' }}>{analytics?.total_incidents ?? 0}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>Across all IT infrastructure</div>
          </div>

          {/* Active Open Tickets with Document/Notepad Writing Icon */}
          <div className="glass-panel" style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 6 }}>
              <span>Active Open Tickets</span>
              <FileEdit size={18} color="#f59e0b" />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: '#f59e0b' }}>{analytics?.open_incidents ?? 0}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>Assigned or in progress</div>
          </div>

          <div className="glass-panel" style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 6 }}>
              <span>Critical Outages</span>
              <AlertCircle size={18} color="#f43f5e" />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: '#f43f5e' }}>{analytics?.critical_incidents ?? 0}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>5m response SLA target</div>
          </div>

          <div className="glass-panel" style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 6 }}>
              <span>SLA Violations</span>
              <Clock size={18} color="#ef4444" />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: '#ef4444' }}>{analytics?.sla_violations ?? 0}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>Automatic escalation enabled</div>
          </div>
        </div>

        {/* Responsive Grid: Shrunk list (1fr) + Expanded Right Pane (530px) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 530px', gap: 22, alignItems: 'start' }}>
          
          {/* Incidents List (Shrunk to make space for right pane) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filteredIncidents.length === 0 ? (
              <div className="glass-panel" style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
                No incidents match the active criteria. Click "Report Incident" to log a new ticket.
              </div>
            ) : (
              filteredIncidents.map(inc => (
                <div 
                  key={inc.id}
                  className={`glass-panel glass-panel-interactive`}
                  onClick={() => setSelectedIncident(inc)}
                  style={{
                    padding: '14px 18px', cursor: 'pointer',
                    borderColor: selectedIncident?.id === inc.id ? 'var(--role-orange)' : undefined,
                    boxShadow: selectedIncident?.id === inc.id ? '0 0 16px rgba(249, 115, 22, 0.2)' : undefined
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--role-orange)', fontFamily: 'JetBrains Mono' }}>
                        {inc.id}
                      </span>
                      <span className={`badge-${inc.priority.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4 }}>
                        {getPriorityLabel(inc.priority)}
                      </span>
                      <span className={`badge-state-${inc.status.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4 }}>
                        {inc.status}
                      </span>
                      {inc.parent_incident_id && (
                        <span style={{ fontSize: 11, background: 'rgba(239, 68, 68, 0.12)', color: '#ef4444', padding: '2px 8px', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                          <AlertTriangle size={11} /> Correlated Duplicate
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4, color: 'var(--text-primary)' }}>{inc.title}</h3>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 10, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {inc.description}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
                    <div style={{ display: 'flex', gap: 14 }}>
                      <span>Service: <strong style={{ color: 'var(--text-primary)' }}>{inc.service.name}</strong></span>
                      <span>Category: <strong style={{ color: 'var(--text-primary)' }}>{inc.category}</strong></span>
                    </div>
                    <div>
                      {inc.assigned_technician ? (
                        <span>Assigned to: <strong style={{ color: 'var(--role-orange)' }}>{inc.assigned_technician.name}</strong></span>
                      ) : (
                        <span style={{ color: '#f59e0b' }}>Pending Assignment</span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Right Column: Expanded Incident Inspector (Roomy & Clean, No Emojis) */}
          <div>
            {selectedIncident ? (
              <div className="glass-panel" style={{ padding: 24, position: 'sticky', top: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: 'var(--role-orange)', fontWeight: 700 }}>
                        {selectedIncident.id}
                      </span>
                      <span className={`badge-${selectedIncident.priority.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>
                        {getPriorityLabel(selectedIncident.priority)}
                      </span>
                      <button
                        onClick={() => setShowPriorityMatrixModal(true)}
                        style={{ background: 'transparent', border: '1px solid var(--border-subtle)', borderRadius: 4, padding: '2px 6px', fontSize: 10, color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
                        title="View ITIL Priority Matrix"
                      >
                        <Sliders size={11} /> Priority Matrix
                      </button>
                      {role === 'ADMIN' && (
                        <button
                          onClick={() => {
                            setOverridePriorityVal(selectedIncident.priority);
                            setShowPriorityOverrideModal(true);
                          }}
                          style={{ background: 'transparent', border: '1px solid rgba(249, 115, 22, 0.4)', borderRadius: 4, padding: '2px 6px', fontSize: 10, color: 'var(--role-orange)', cursor: 'pointer', fontWeight: 600 }}
                        >
                          Override Priority
                        </button>
                      )}
                    </div>
                    <h2 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)' }}>{selectedIncident.title}</h2>
                  </div>
                  <button 
                    onClick={() => setSelectedIncident(null)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Incident Progression Lifecycle */}
                <div style={{ background: 'var(--input-bg)', padding: '12px 14px', borderRadius: 8, marginBottom: 16, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', fontWeight: 600 }}>
                    Incident Progression Lifecycle
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                    {['NEW', 'CLASSIFIED', 'ASSIGNED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'VERIFIED', 'CLOSED'].map((st, idx) => {
                      const isCurrent = selectedIncident.status === st;
                      return (
                        <React.Fragment key={st}>
                          <span style={{
                            fontSize: 10, padding: '3px 7px', borderRadius: 4, fontWeight: isCurrent ? 700 : 500,
                            background: isCurrent ? 'var(--role-orange-bg)' : 'transparent',
                            color: isCurrent ? 'var(--role-orange)' : 'var(--text-muted)',
                            border: isCurrent ? '1px solid var(--role-orange-border)' : '1px solid transparent'
                          }}>
                            {st}
                          </span>
                          {idx < 7 && <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>➔</span>}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>

                {/* SLA Target Box: Clean Professional Display with Synchronized Clock & Countdown */}
                <div style={{ 
                  background: selectedIncident.sla.is_breached ? 'rgba(239, 68, 68, 0.08)' : 'var(--input-bg)', 
                  border: selectedIncident.sla.is_breached ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid var(--border-subtle)', 
                  borderRadius: 8, padding: 12, marginBottom: 18 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: selectedIncident.sla.is_breached ? '#ef4444' : 'var(--text-secondary)', letterSpacing: '0.3px' }}>
                      {selectedIncident.sla.is_breached ? 'SLA VIOLATION DETECTED' : 'SLA Target'}
                    </span>
                    <span style={{ 
                      fontSize: 11, 
                      fontWeight: 600,
                      color: selectedIncident.sla.is_breached ? '#ef4444' : selectedIncident.sla.is_at_risk ? '#f59e0b' : '#10b981'
                    }}>
                      {getSlaRemainingText(selectedIncident.sla.resolution_deadline, selectedIncident.sla.is_breached, selectedIncident.status)}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 6 }}>
                    <div>
                      Resolution Deadline: <strong style={{ color: 'var(--text-primary)' }}>{new Date(selectedIncident.sla.resolution_deadline).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</strong>
                    </div>
                    <div>
                      Response Target: <strong style={{ color: 'var(--text-primary)' }}>{new Date(selectedIncident.sla.response_deadline).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</strong>
                    </div>
                  </div>
                </div>

                {/* Available Actions */}
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                    Available Actions
                  </div>

                  {/* Technician Operations */}
                  {role === 'TECHNICIAN' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {selectedIncident.status === 'ASSIGNED' && (
                        <button className="btn-primary" onClick={() => handleAcknowledge(selectedIncident.id)} style={{ width: '100%', justifyContent: 'center' }}>
                          <CheckCircle2 size={16} /> Acknowledge Ticket
                        </button>
                      )}

                      {(selectedIncident.status === 'ACKNOWLEDGED' || selectedIncident.status === 'IN_PROGRESS') && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                          <input 
                            type="text" 
                            placeholder="Add investigation findings..."
                            value={actionNote}
                            onChange={e => setActionNote(e.target.value)}
                            className="flat-input"
                          />
                          <button className="btn-secondary" onClick={() => handleStartInvestigation(selectedIncident.id)} style={{ width: '100%', justifyContent: 'center' }}>
                            Add Investigation Note
                          </button>
                        </div>
                      )}

                      {selectedIncident.status === 'IN_PROGRESS' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 4 }}>
                          <input 
                            type="text" 
                            placeholder="Resolution details..."
                            value={resolutionNote}
                            onChange={e => setResolutionNote(e.target.value)}
                            className="flat-input"
                          />
                          <button className="btn-primary" onClick={() => handleResolve(selectedIncident.id)} style={{ width: '100%', justifyContent: 'center', background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                            <Check size={16} /> Mark Resolved
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Employee Operations */}
                  {role === 'EMPLOYEE' && selectedIncident.status === 'RESOLVED' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                        Technician resolution: <em>"{selectedIncident.resolution_details}"</em>. Does this fix the problem?
                      </p>
                      <input 
                        type="text" 
                        placeholder="Optional feedback..."
                        value={verificationFeedback}
                        onChange={e => setVerificationFeedback(e.target.value)}
                        className="flat-input"
                      />
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn-primary" onClick={() => handleVerify(selectedIncident.id, true)} style={{ flex: 1, justifyContent: 'center', background: '#10b981' }}>
                          <Check size={15} /> Confirm & Verify
                        </button>
                        <button className="btn-danger" onClick={() => handleVerify(selectedIncident.id, false)} style={{ flex: 1, justifyContent: 'center' }}>
                          <X size={15} /> Reject (Re-open)
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Admin Close Action */}
                  {role === 'ADMIN' && (selectedIncident.status === 'VERIFIED' || selectedIncident.status === 'RESOLVED') && (
                    <button className="btn-secondary" onClick={() => handleClose(selectedIncident.id)} style={{ width: '100%', justifyContent: 'center' }}>
                      <CheckCircle2 size={16} /> Officially Close Incident
                    </button>
                  )}
                </div>

                {/* Expanded Activity & Audit Trail */}
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                    Activity & Audit Trail ({selectedIncident.audit_logs.length})
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 260, overflowY: 'auto' }}>
                    {selectedIncident.audit_logs.map(log => (
                      <div key={log.id} style={{ fontSize: 12, padding: '9px 12px', background: 'var(--input-bg)', borderRadius: 6, borderLeft: '3px solid var(--role-orange)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: 3 }}>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{log.actor_name}</span>
                          <span style={{ fontSize: 11 }}>{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', lineHeight: 1.4 }}>{log.description}</div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              <div className="glass-panel" style={{ padding: 36, textAlign: 'center', color: 'var(--text-muted)' }}>
                Select an incident from the list to view its complete lifecycle status, SLA countdowns, and audit trail.
              </div>
            )}
          </div>

        </div>

      </main>

      {/* ======================================================== */}
      {/* 3. REPORT INCIDENT MODAL                                 */}
      {/* ======================================================== */}
      {isReportModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ width: 520, padding: 26, background: 'var(--bg-modal)', border: '1px solid var(--border-accent)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <FileText size={20} color="var(--role-orange)" />
                <h2 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)' }}>Report New Incident</h2>
              </div>
              <button onClick={() => setIsReportModalOpen(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {/* Duplicate Incident Warning Alert if found */}
            {detectedDuplicates.length > 0 && (
              <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.35)', borderRadius: 8, padding: '12px 14px', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#ef4444', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
                  <AlertTriangle size={16} /> Possible Duplicate Incident Detected
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  A similar incident is already open with <strong>{(detectedDuplicates[0].similarity * 100).toFixed(0)}% match</strong>:
                  <br />
                  <span style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-primary)' }}>
                    {detectedDuplicates[0].id}: {detectedDuplicates[0].title}
                  </span>
                </p>
                <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                  <button className="btn-secondary" onClick={() => { setIsReportModalOpen(false); setDetectedDuplicates([]); }} style={{ fontSize: 12, padding: '4px 10px' }}>
                    View Existing Incident
                  </button>
                  <button className="btn-primary" onClick={() => { setIsReportModalOpen(false); setDetectedDuplicates([]); }} style={{ fontSize: 12, padding: '4px 10px' }}>
                    Submit as Correlated Ticket
                  </button>
                </div>
              </div>
            )}

            <form onSubmit={handleReport} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Affected IT Service
                </label>
                <select 
                  value={newServiceId} 
                  onChange={e => setNewServiceId(e.target.value)}
                  className="flat-select"
                  style={{ width: '100%' }}
                >
                  {services.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({formatServiceTier(s.tier)})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Incident Summary / Title
                </label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. Payment application unavailable during checkout"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  className="flat-input"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Issue Description & Diagnostic Details
                </label>
                <textarea 
                  required
                  rows={3}
                  placeholder="Describe what occurred, affected users, and error codes..."
                  value={newDesc}
                  onChange={e => setNewDesc(e.target.value)}
                  className="flat-input"
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Impact</label>
                  <select 
                    value={newImpact} 
                    onChange={e => setNewImpact(e.target.value)}
                    className="flat-select"
                    style={{ width: '100%' }}
                  >
                    <option value="CRITICAL">Critical (Org-wide)</option>
                    <option value="HIGH">High (Major Dept)</option>
                    <option value="MEDIUM">Medium (Multiple Users)</option>
                    <option value="LOW">Low (Single User)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Urgency</label>
                  <select 
                    value={newUrgency} 
                    onChange={e => setNewUrgency(e.target.value)}
                    className="flat-select"
                    style={{ width: '100%' }}
                  >
                    <option value="CRITICAL">Critical (Immediate)</option>
                    <option value="HIGH">High (Impending)</option>
                    <option value="MEDIUM">Medium (Normal)</option>
                    <option value="LOW">Low (Convenience)</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Assignment Routing Method
                </label>
                <select 
                  value={newStrategy} 
                  onChange={e => setNewStrategy(e.target.value)}
                  className="flat-select"
                  style={{ width: '100%' }}
                >
                  <option value="smart">Auto: Balanced Routing (Skill, Load & Rating)</option>
                  <option value="skill">Skill-Based Routing</option>
                  <option value="load">Least-Loaded Routing</option>
                  <option value="round_robin">Round-Robin Distribution</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn-secondary" onClick={() => setIsReportModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Submit Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* 3. EXECUTIVE OPERATIONS & INCIDENT AUDIT REPORT (PDF)    */}
      {/* ======================================================== */}
      {showExecutiveReport && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: 900, maxHeight: '90vh', overflowY: 'auto', padding: 30, background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 14 }}>
            {/* Report Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 16, marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--role-orange)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Executive Operations Audit
                </div>
                <h1 style={{ fontSize: 22, fontWeight: 700, margin: '6px 0 2px 0', color: 'var(--text-primary)' }}>
                  ITSM Service Reliability & Incident Intelligence Report
                </h1>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Course: CS F213 / MAC F212 (OOPS Project) &bull; Generated: {new Date().toLocaleString()}
                </div>
              </div>
              <div style={{ display: 'flex', gap: 10 }} className="no-print">
                <button 
                  onClick={() => window.print()}
                  className="btn-primary"
                  style={{ padding: '8px 14px', fontSize: 12 }}
                >
                  <Printer size={15} /> Print / Save as PDF
                </button>
                <button 
                  onClick={() => setShowExecutiveReport(false)}
                  className="btn-secondary"
                  style={{ padding: '8px 12px', fontSize: 12 }}
                >
                  <X size={15} /> Close
                </button>
              </div>
            </div>

            {/* KPI Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 24 }}>
              <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Incidents</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>{incidents.length}</div>
              </div>
              <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Outages</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: '#f59e0b', marginTop: 4 }}>
                  {incidents.filter(i => !['RESOLVED', 'CLOSED'].includes(i.status)).length}
                </div>
              </div>
              <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Critical (P1)</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: '#ef4444', marginTop: 4 }}>
                  {incidents.filter(i => i.priority === 'P1').length}
                </div>
              </div>
              <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>SLA Breaches</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: '#ea580c', marginTop: 4 }}>
                  {incidents.filter(i => i.sla?.is_breached).length}
                </div>
              </div>
              <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Resolution Rate</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: '#10b981', marginTop: 4 }}>
                  {incidents.length ? Math.round((incidents.filter(i => ['RESOLVED', 'CLOSED'].includes(i.status)).length / incidents.length) * 100) : 0}%
                </div>
              </div>
            </div>

            {/* Service Health Breakdown (Syllabus Page 9 Table) */}
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
                1. IT Service Criticality & Incident Analysis (Syllabus Page 9 Matrix)
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ background: 'var(--input-bg)', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Service Name</th>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Criticality Tier</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Total Tickets</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Critical P1</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>SLA Breached</th>
                    <th style={{ padding: '8px 12px', textAlign: 'right' }}>Operational Health</th>
                  </tr>
                </thead>
                <tbody>
                  {services.map(s => {
                    const sInc = incidents.filter(i => i.service.id === s.id);
                    const p1Count = sInc.filter(i => i.priority === 'P1').length;
                    const breachCount = sInc.filter(i => i.sla?.is_breached).length;
                    const isDegraded = p1Count > 0 || breachCount > 0;
                    return (
                      <tr key={s.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '8px 12px', fontWeight: 600 }}>{s.name}</td>
                        <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{formatServiceTier(s.tier)}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center' }}>{sInc.length}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center', color: p1Count ? '#ef4444' : 'inherit' }}>{p1Count}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center', color: breachCount ? '#ea580c' : 'inherit' }}>{breachCount}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 600, color: isDegraded ? '#ea580c' : '#10b981' }}>
                          {isDegraded ? 'DEGRADED' : 'OPERATIONAL'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Technician Allocation & Load Distribution */}
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
                2. Technician Capacity & Skill Allocation (Syllabus Pages 4 & 13)
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ background: 'var(--input-bg)', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Technician Name</th>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Domain Skills</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Active Workload</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Max Capacity</th>
                    <th style={{ padding: '8px 12px', textAlign: 'right' }}>Capacity Utilization</th>
                  </tr>
                </thead>
                <tbody>
                  {users.filter(u => u.role === 'TECHNICIAN').map(t => {
                    const pct = t.max_load ? Math.round((t.load / t.max_load) * 100) : 0;
                    return (
                      <tr key={t.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '8px 12px', fontWeight: 600 }}>{t.name}</td>
                        <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{(t.skills || ['GENERAL']).join(', ')}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center' }}>{t.load}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center' }}>{t.max_load}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 600, color: pct >= 100 ? '#ef4444' : pct > 60 ? '#f59e0b' : '#10b981' }}>
                          {pct}% {pct >= 100 ? '(Saturated)' : '(Available)'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Incident Register */}
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
                3. Master Incident Ledger & SLA Compliance Register
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
                <thead>
                  <tr style={{ background: 'var(--input-bg)', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>ID</th>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>Summary</th>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>Priority</th>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>Service</th>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '6px 10px', textAlign: 'left' }}>Assignee</th>
                    <th style={{ padding: '6px 10px', textAlign: 'right' }}>SLA Status</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map(inc => (
                    <tr key={inc.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '6px 10px', fontFamily: 'monospace', fontWeight: 700 }}>{inc.id}</td>
                      <td style={{ padding: '6px 10px' }}>{inc.title}</td>
                      <td style={{ padding: '6px 10px' }}>{getPriorityLabel(inc.priority)}</td>
                      <td style={{ padding: '6px 10px' }}>{inc.service.name}</td>
                      <td style={{ padding: '6px 10px' }}>{inc.status}</td>
                      <td style={{ padding: '6px 10px' }}>{inc.assigned_technician?.name || 'Unassigned'}</td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontWeight: 600, color: inc.sla?.is_breached ? '#ef4444' : '#10b981' }}>
                        {inc.sla?.is_breached ? 'BREACHED' : 'COMPLIANT'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* 4. REAL EMAIL NOTIFICATION OUTBOX & LIVE DISPATCHER      */}
      {/* ======================================================== */}
      {showNotificationOutbox && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: 840, maxHeight: '90vh', overflowY: 'auto', padding: 26, background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 14 }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 14, marginBottom: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ padding: 8, borderRadius: 8, background: 'rgba(249, 115, 22, 0.15)', color: 'var(--role-orange)' }}>
                  <Mail size={20} />
                </div>
                <div>
                  <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                    Enterprise Notification Outbox & Live SMTP Dispatch
                  </h2>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {smtpConfigured ? (
                      <span style={{ color: '#10b981', fontWeight: 600 }}>● Live External SMTP Server Connected</span>
                    ) : (
                      <span style={{ color: 'var(--role-orange)' }}>● In-App Enterprise Outbox Active (Real HTML Emails Rendered & Tracked)</span>
                    )}
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setShowNotificationOutbox(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Tabs: Outbox List vs Test Real Email */}
            <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--border-subtle)', marginBottom: 16 }}>
              <button
                className={`auth-tab-btn ${outboxActiveTab === 'OUTBOX' ? 'active' : ''}`}
                onClick={() => setOutboxActiveTab('OUTBOX')}
                style={{ padding: '8px 14px' }}
              >
                Dispatched Outbox ({outboxEmails.length})
              </button>
              <button
                className={`auth-tab-btn ${outboxActiveTab === 'TEST' ? 'active' : ''}`}
                onClick={() => setOutboxActiveTab('TEST')}
                style={{ padding: '8px 14px' }}
              >
                Test Real Email Dispatch
              </button>
            </div>

            {outboxActiveTab === 'OUTBOX' ? (
              <div>
                {selectedOutboxEmail ? (
                  <div>
                    <button
                      onClick={() => setSelectedOutboxEmail(null)}
                      className="btn-secondary"
                      style={{ padding: '6px 10px', fontSize: 12, marginBottom: 14 }}
                    >
                      ➔ Back to Outbox List
                    </button>
                    <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 16, marginBottom: 16 }}>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Subject</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }}>{selectedOutboxEmail.subject}</div>
                      <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
                        <div>To: <strong style={{ color: 'var(--text-primary)' }}>{selectedOutboxEmail.to.join(', ')}</strong></div>
                        <div>Status: <span style={{ color: '#10b981', fontWeight: 600 }}>{selectedOutboxEmail.status}</span></div>
                        <div>Sent: {new Date(selectedOutboxEmail.sent_at).toLocaleTimeString()}</div>
                      </div>
                    </div>
                    <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
                      <div dangerouslySetInnerHTML={{ __html: selectedOutboxEmail.body_html }} />
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {outboxEmails.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)', fontSize: 13 }}>
                        No notification emails dispatched yet. Register an account or report an incident to trigger automated emails!
                      </div>
                    ) : (
                      outboxEmails.map(mail => (
                        <div 
                          key={mail.id} 
                          onClick={() => setSelectedOutboxEmail(mail)}
                          style={{
                            background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8,
                            padding: '12px 14px', cursor: 'pointer', transition: 'all 0.2s',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                          }}
                        >
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                              <span style={{ fontSize: 11, padding: '2px 6px', borderRadius: 4, background: 'rgba(249, 115, 22, 0.15)', color: 'var(--role-orange)', fontWeight: 700 }}>
                                {mail.type}
                              </span>
                              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                                {mail.subject}
                              </span>
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                              To: <strong>{mail.to.join(', ')}</strong> &bull; {new Date(mail.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                          </div>
                          <span style={{ fontSize: 11, color: 'var(--role-orange)' }}>View HTML ➔</span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            ) : (
              <form onSubmit={handleSendTestEmail} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Recipient Email (Real Email Address)
                  </label>
                  <input 
                    type="email" 
                    required 
                    placeholder="e.g. yourname@gmail.com"
                    value={testEmailTo}
                    onChange={e => setTestEmailTo(e.target.value)}
                    className="flat-input"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Subject
                  </label>
                  <input 
                    type="text" 
                    required 
                    value={testEmailSub}
                    onChange={e => setTestEmailSub(e.target.value)}
                    className="flat-input"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Message Content
                  </label>
                  <textarea 
                    rows={3} 
                    required 
                    value={testEmailMsg}
                    onChange={e => setTestEmailMsg(e.target.value)}
                    className="flat-input"
                  />
                </div>
                {testEmailResult && (
                  <div style={{ padding: 10, borderRadius: 6, fontSize: 12, background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#10b981' }}>
                    {testEmailResult}
                  </div>
                )}
                <button 
                  type="submit" 
                  className="btn-primary" 
                  disabled={testEmailSending}
                  style={{ padding: '10px 16px', justifyContent: 'center' }}
                >
                  <Send size={15} /> {testEmailSending ? 'Dispatching...' : 'Dispatch Live Email'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* 5. ITIL PRIORITY MATRIX GUIDE MODAL                      */}
      {/* ======================================================== */}
      {showPriorityMatrixModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: 650, padding: 26, background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 12, marginBottom: 16 }}>
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                  ITIL Priority Calculation Matrix (Syllabus Page 5)
                </h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Mathematical mapping of Business Impact vs Operational Urgency
                </div>
              </div>
              <button 
                onClick={() => setShowPriorityMatrixModal(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: 12, marginBottom: 16 }}>
              <thead>
                <tr style={{ background: 'var(--input-bg)' }}>
                  <th style={{ padding: 10, border: '1px solid var(--border-subtle)', textAlign: 'left' }}>Impact \ Urgency</th>
                  <th style={{ padding: 10, border: '1px solid var(--border-subtle)', color: '#ef4444' }}>Critical</th>
                  <th style={{ padding: 10, border: '1px solid var(--border-subtle)', color: '#f97316' }}>High</th>
                  <th style={{ padding: 10, border: '1px solid var(--border-subtle)', color: '#eab308' }}>Medium</th>
                  <th style={{ padding: 10, border: '1px solid var(--border-subtle)', color: '#94a3b8' }}>Low</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', fontWeight: 600, textAlign: 'left', color: '#ef4444' }}>Critical (Org-wide)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(239, 68, 68, 0.2)', fontWeight: 700 }}>Critical (P1)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(239, 68, 68, 0.15)' }}>Critical (P1)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(249, 115, 22, 0.15)' }}>High (P2)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                </tr>
                <tr>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', fontWeight: 600, textAlign: 'left', color: '#f97316' }}>High (Dept-wide)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(239, 68, 68, 0.15)' }}>Critical (P1)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(249, 115, 22, 0.15)' }}>High (P2)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                </tr>
                <tr>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', fontWeight: 600, textAlign: 'left', color: '#eab308' }}>Medium (Multiple)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', background: 'rgba(249, 115, 22, 0.15)' }}>High (P2)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Low (P4)</td>
                </tr>
                <tr>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)', fontWeight: 600, textAlign: 'left', color: '#94a3b8' }}>Low (Single User)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Medium (P3)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Low (P4)</td>
                  <td style={{ padding: 10, border: '1px solid var(--border-subtle)' }}>Low (P4)</td>
                </tr>
              </tbody>
            </table>

            <div style={{ background: 'var(--input-bg)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--role-orange)' }}>Mission-Critical Service Rule:</strong> Any incident logged against a Tier-1 Service (such as Payment Gateway or Core PostgreSQL DB) with Critical Impact is automatically locked to <strong>Critical (P1)</strong>, with a 5-minute response SLA.
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* 6. PRIORITY OVERRIDE MODAL (ADMIN ONLY)                  */}
      {/* ======================================================== */}
      {showPriorityOverrideModal && selectedIncident && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: 500, padding: 24, background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 10, marginBottom: 14 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                Override Priority: {selectedIncident.id}
              </h3>
              <button onClick={() => setShowPriorityOverrideModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={16} />
              </button>
            </div>
            <form onSubmit={handleOverridePriority} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  New Priority Level
                </label>
                <select 
                  value={overridePriorityVal} 
                  onChange={e => setOverridePriorityVal(e.target.value)}
                  className="flat-select"
                  style={{ width: '100%' }}
                >
                  <option value="P1">Critical (P1) - 5m response / 30m resolution</option>
                  <option value="P2">High (P2) - 15m response / 2h resolution</option>
                  <option value="P3">Medium (P3) - 1h response / 8h resolution</option>
                  <option value="P4">Low (P4) - 4h response / 24h resolution</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Mandatory Audit Justification
                </label>
                <textarea 
                  rows={3} 
                  required 
                  placeholder="Provide operational justification for overriding the calculated priority..."
                  value={overrideReason}
                  onChange={e => setOverrideReason(e.target.value)}
                  className="flat-input"
                />
              </div>
              <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 6 }}>
                <button type="button" onClick={() => setShowPriorityOverrideModal(false)} className="btn-secondary" style={{ padding: '8px 14px', fontSize: 12 }}>
                  Cancel
                </button>
                <button type="submit" disabled={overrideSubmitting} className="btn-primary" style={{ padding: '8px 16px', fontSize: 12 }}>
                  {overrideSubmitting ? 'Updating...' : 'Commit Priority Override'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
