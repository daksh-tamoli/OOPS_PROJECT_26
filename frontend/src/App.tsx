import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, CheckCircle2, Clock, Search, Shield, User, Wrench, 
  PlusCircle, RefreshCw, Activity, Check, X, FileText, Sparkles
} from 'lucide-react';

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

export function App() {
  const [role, setRole] = useState<'EMPLOYEE' | 'TECHNICIAN' | 'ADMIN'>('EMPLOYEE');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [services, setServices] = useState<ITService[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
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

  const API_BASE = 'http://localhost:8000/api';

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

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  // Filtered incidents
  const filteredIncidents = incidents.filter(inc => {
    if (role === 'EMPLOYEE' && inc.reporter.id !== 'user-emp-1' && statusFilter === 'MY_TICKETS') return false;
    if (role === 'TECHNICIAN' && inc.assigned_technician?.id !== 'tech-101' && statusFilter === 'MY_ASSIGNED') return false;
    if (statusFilter !== 'ALL' && statusFilter !== 'MY_TICKETS' && statusFilter !== 'MY_ASSIGNED' && inc.status !== statusFilter) return false;
    if (priorityFilter !== 'ALL' && inc.priority !== priorityFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return inc.title.toLowerCase().includes(q) || inc.id.toLowerCase().includes(q) || inc.description.toLowerCase().includes(q);
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
          reporter_id: 'user-emp-1',
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
    await fetch(`${API_BASE}/incidents/${id}/acknowledge?technician_id=tech-101`, { method: 'POST' });
    fetchData();
  };

  const handleStartInvestigation = async (id: string) => {
    if (!actionNote) return;
    await fetch(`${API_BASE}/incidents/${id}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_id: 'tech-101', notes: actionNote })
    });
    setActionNote('');
    fetchData();
  };

  const handleResolve = async (id: string) => {
    if (!resolutionNote) return;
    await fetch(`${API_BASE}/incidents/${id}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_id: 'tech-101', resolution_details: resolutionNote })
    });
    setResolutionNote('');
    fetchData();
  };

  // Employee Verification
  const handleVerify = async (id: string, confirmed: boolean) => {
    await fetch(`${API_BASE}/incidents/${id}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actor_id: 'user-emp-1',
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
    await fetch(`${API_BASE}/incidents/${id}/close?actor_id=user-admin-1`, { method: 'POST' });
    fetchData();
  };

  return (
    <div style={{ maxWidth: 1440, margin: '0 auto', padding: '24px 32px' }}>
      
      {/* Top Navigation Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28, paddingBottom: 20, borderBottom: '1px solid var(--border-subtle)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Shield size={24} color="#fff" />
            </div>
            <div>
              <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.5px' }}>
                I-ITSM Platform {loading && <span style={{ fontSize: 11, color: '#38bdf8', fontWeight: 500 }}>● syncing</span>}
              </h1>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Intelligent Incident Lifecycle & Resolution Management</p>
            </div>
          </div>
        </div>

        {/* Role Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, background: 'rgba(255,255,255,0.05)', padding: '6px 8px', borderRadius: 12, border: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8, fontWeight: 600 }}>ACTIVE ROLE:</span>
          
          <button 
            onClick={() => setRole('EMPLOYEE')}
            style={{ 
              display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: role === 'EMPLOYEE' ? 'rgba(6, 182, 212, 0.2)' : 'transparent',
              color: role === 'EMPLOYEE' ? '#38bdf8' : 'var(--text-secondary)',
              fontWeight: role === 'EMPLOYEE' ? 600 : 500, fontSize: 13
            }}
          >
            <User size={15} /> Employee (Alice)
          </button>

          <button 
            onClick={() => setRole('TECHNICIAN')}
            style={{ 
              display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: role === 'TECHNICIAN' ? 'rgba(234, 179, 8, 0.2)' : 'transparent',
              color: role === 'TECHNICIAN' ? '#fde047' : 'var(--text-secondary)',
              fontWeight: role === 'TECHNICIAN' ? 600 : 500, fontSize: 13
            }}
          >
            <Wrench size={15} /> Technician (Devon)
          </button>

          <button 
            onClick={() => setRole('ADMIN')}
            style={{ 
              display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: role === 'ADMIN' ? 'rgba(168, 85, 247, 0.2)' : 'transparent',
              color: role === 'ADMIN' ? '#d8b4fe' : 'var(--text-secondary)',
              fontWeight: role === 'ADMIN' ? 600 : 500, fontSize: 13
            }}
          >
            <Shield size={15} /> Admin (Sarah)
          </button>
        </div>
      </header>

      {/* Metrics Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
        <div className="glass-panel" style={{ padding: '18px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 8 }}>
            <span>Total Incidents</span>
            <FileText size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{analytics?.total_incidents ?? 0}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Across all IT infrastructure</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 8 }}>
            <span>Active Open Tickets</span>
            <Activity size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#fcd34d' }}>{analytics?.open_incidents ?? 0}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>In investigation / assigned</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 8 }}>
            <span>Critical P1 Outages</span>
            <AlertTriangle size={18} color="#f43f5e" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#fda4af' }}>{analytics?.critical_incidents ?? 0}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>5 min response SLA target</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 13, marginBottom: 8 }}>
            <span>SLA Violations</span>
            <Clock size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#ef4444' }}>{analytics?.sla_violations ?? 0}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Automated escalation triggered</div>
        </div>
      </div>

      {/* Technician Roster for Administrator & Team visibility */}
      {role === 'ADMIN' && (
        <div className="glass-panel" style={{ padding: '12px 18px', marginBottom: 20, display: 'flex', gap: 16, alignItems: 'center' }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#a855f7' }}>TECHNICIAN ROSTER:</span>
          {users.filter(u => u.role === 'TECHNICIAN').map(t => (
            <span key={t.id} style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              <strong style={{ color: '#fff' }}>{t.name}</strong> ({t.load}/{t.max_load} load)
            </span>
          ))}
        </div>
      )}

      {/* Main Content Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 24 }}>
        
        {/* Left Column: Incidents List & Controls */}
        <div>
          {/* Action Header & Search */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', gap: 12, flex: 1, maxWidth: 500 }}>
              <div style={{ position: 'relative', width: '100%' }}>
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 11 }} />
                <input 
                  type="text" 
                  placeholder="Search incident ID, title, or service..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%', padding: '9px 12px 9px 36px', borderRadius: 8,
                    background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)',
                    color: '#fff', fontSize: 13, outline: 'none'
                  }}
                />
              </div>

              <select 
                value={statusFilter} 
                onChange={e => setStatusFilter(e.target.value)}
                style={{
                  background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)',
                  color: '#fff', padding: '8px 12px', borderRadius: 8, fontSize: 13, outline: 'none'
                }}
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

              <select 
                value={priorityFilter} 
                onChange={e => setPriorityFilter(e.target.value)}
                style={{
                  background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)',
                  color: '#fff', padding: '8px 12px', borderRadius: 8, fontSize: 13, outline: 'none'
                }}
              >
                <option value="ALL">All Priorities</option>
                <option value="P1">P1 - Critical</option>
                <option value="P2">P2 - High</option>
                <option value="P3">P3 - Medium</option>
                <option value="P4">P4 - Low</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              {role === 'EMPLOYEE' && (
                <button 
                  className="btn-primary"
                  onClick={() => { setIsReportModalOpen(true); setDetectedDuplicates([]); }}
                >
                  <PlusCircle size={16} /> Report Incident
                </button>
              )}

              {role === 'ADMIN' && (
                <button 
                  className="btn-secondary"
                  onClick={handleTriggerSLA}
                  title="Executes SLA evaluation & hierarchical auto-escalation"
                >
                  <RefreshCw size={15} /> Run SLA Daemon
                </button>
              )}
            </div>
          </div>

          {/* Incidents List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
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
                    padding: '16px 20px', cursor: 'pointer',
                    borderColor: selectedIncident?.id === inc.id ? 'var(--accent-blue)' : undefined,
                    boxShadow: selectedIncident?.id === inc.id ? '0 0 20px rgba(59, 130, 246, 0.25)' : undefined
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-cyan)', fontFamily: 'JetBrains Mono' }}>{inc.id}</span>
                      <span className={`badge-${inc.priority.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4 }}>
                        {inc.priority}
                      </span>
                      <span className={`badge-state-${inc.status.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4 }}>
                        {inc.status}
                      </span>
                      {inc.parent_incident_id && (
                        <span style={{ fontSize: 11, background: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', padding: '2px 8px', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                          <AlertTriangle size={11} /> Correlated Duplicate
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>{inc.title}</h3>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {inc.description}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
                    <div style={{ display: 'flex', gap: 16 }}>
                      <span>Service: <strong style={{ color: '#e2e8f0' }}>{inc.service.name}</strong></span>
                      <span>Category: <strong style={{ color: '#e2e8f0' }}>{inc.category}</strong></span>
                    </div>
                    <div>
                      {inc.assigned_technician ? (
                        <span>Assigned to: <strong style={{ color: '#38bdf8' }}>{inc.assigned_technician.name}</strong></span>
                      ) : (
                        <span style={{ color: '#f59e0b' }}>Pending Assignment</span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Detailed Incident Inspector & Audit History */}
        <div>
          {selectedIncident ? (
            <div className="glass-panel" style={{ padding: 24, position: 'sticky', top: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                      {selectedIncident.id}
                    </span>
                    <span className={`badge-${selectedIncident.priority.toLowerCase()}`} style={{ fontSize: 11, fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>
                      {selectedIncident.priority}
                    </span>
                  </div>
                  <h2 style={{ fontSize: 17, fontWeight: 700 }}>{selectedIncident.title}</h2>
                </div>
                <button 
                  onClick={() => setSelectedIncident(null)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                >
                  <X size={18} />
                </button>
              </div>

              {/* State Machine Visualizer */}
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px 14px', borderRadius: 8, marginBottom: 18, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', fontWeight: 600 }}>
                  Lifecycle State Machine (State Pattern)
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                  {['NEW', 'CLASSIFIED', 'ASSIGNED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'VERIFIED', 'CLOSED'].map((st, idx) => {
                    const isCurrent = selectedIncident.status === st;
                    return (
                      <React.Fragment key={st}>
                        <span style={{
                          fontSize: 10, padding: '2px 6px', borderRadius: 4, fontWeight: isCurrent ? 700 : 500,
                          background: isCurrent ? 'rgba(59, 130, 246, 0.3)' : 'rgba(255,255,255,0.05)',
                          color: isCurrent ? '#60a5fa' : 'var(--text-muted)',
                          border: isCurrent ? '1px solid #3b82f6' : '1px solid transparent'
                        }}>
                          {st}
                        </span>
                        {idx < 7 && <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>➔</span>}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

              {/* SLA Target Box */}
              <div style={{ background: selectedIncident.sla.is_breached ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255,255,255,0.03)', border: selectedIncident.sla.is_breached ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid var(--border-subtle)', borderRadius: 8, padding: 12, marginBottom: 18 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: selectedIncident.sla.is_breached ? '#ef4444' : '#94a3b8' }}>
                    {selectedIncident.sla.is_breached ? '🚨 SLA VIOLATION DETECTED' : '⏱️ SLA Deadlines'}
                  </span>
                  {selectedIncident.sla.is_at_risk && !selectedIncident.sla.is_breached && (
                    <span style={{ fontSize: 11, color: '#f59e0b', fontWeight: 600 }}>⚠️ Resolution At Risk (&gt;70%)</span>
                  )}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  Resolution Deadline: {new Date(selectedIncident.sla.resolution_deadline).toLocaleTimeString()}
                </div>
              </div>

              {/* Role Contextual Actions */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                  Available Role Operations
                </div>

                {/* Technician Actions */}
                {role === 'TECHNICIAN' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {selectedIncident.status === 'ASSIGNED' && (
                      <button className="btn-primary" onClick={() => handleAcknowledge(selectedIncident.id)}>
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
                          style={{ padding: '8px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                        />
                        <button className="btn-secondary" onClick={() => handleStartInvestigation(selectedIncident.id)}>
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
                          style={{ padding: '8px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                        />
                        <button className="btn-primary" onClick={() => handleResolve(selectedIncident.id)} style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                          <Check size={16} /> Mark Resolved
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Employee Actions */}
                {role === 'EMPLOYEE' && selectedIncident.status === 'RESOLVED' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                      Technician resolved this issue: <em>"{selectedIncident.resolution_details}"</em>. Does this solve your problem?
                    </p>
                    <input 
                      type="text" 
                      placeholder="Optional feedback..."
                      value={verificationFeedback}
                      onChange={e => setVerificationFeedback(e.target.value)}
                      style={{ padding: '8px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                    />
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button className="btn-primary" onClick={() => handleVerify(selectedIncident.id, true)} style={{ flex: 1, background: '#10b981' }}>
                        <Check size={15} /> Confirm & Verify
                      </button>
                      <button className="btn-danger" onClick={() => handleVerify(selectedIncident.id, false)} style={{ flex: 1 }}>
                        <X size={15} /> Reject (Re-open)
                      </button>
                    </div>
                  </div>
                )}

                {/* Admin Close Action */}
                {role === 'ADMIN' && (selectedIncident.status === 'VERIFIED' || selectedIncident.status === 'RESOLVED') && (
                  <button className="btn-secondary" onClick={() => handleClose(selectedIncident.id)}>
                    <CheckCircle2 size={16} /> Officially Close Incident
                  </button>
                )}
              </div>

              {/* Immutable Audit Log Trail (Observer Pattern) */}
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase' }}>
                  Immutable Audit Trail ({selectedIncident.audit_logs.length} entries)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 220, overflowY: 'auto' }}>
                  {selectedIncident.audit_logs.map(log => (
                    <div key={log.id} style={{ fontSize: 12, padding: '8px 10px', background: 'rgba(0,0,0,0.2)', borderRadius: 6, borderLeft: '3px solid #3b82f6' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: 2 }}>
                        <span><strong>{log.actor_name}</strong></span>
                        <span>{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                      </div>
                      <div style={{ color: 'var(--text-secondary)' }}>{log.description}</div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            <div className="glass-panel" style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>
              Select an incident from the list to view its complete OOP State Lifecycle, SLA countdown timers, and immutable Audit Trail.
            </div>
          )}
        </div>

      </div>

      {/* Report Incident Modal */}
      {isReportModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ width: 540, padding: 28, background: '#111827', border: '1px solid var(--border-accent)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Sparkles size={20} color="var(--accent-cyan)" />
                <h2 style={{ fontSize: 18, fontWeight: 700 }}>Report IT Incident</h2>
              </div>
              <button onClick={() => setIsReportModalOpen(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {/* Duplicate Incident Warning Alert if found */}
            {detectedDuplicates.length > 0 && (
              <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: 8, padding: '12px 16px', marginBottom: 18 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#fca5a5', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
                  <AlertTriangle size={16} /> Intelligent Duplicate Detection Triggered!
                </div>
                <p style={{ fontSize: 12, color: '#fecdd3' }}>
                  The system detected an existing active incident with <strong>{(detectedDuplicates[0].similarity * 100).toFixed(1)}% similarity</strong>:
                  <br />
                  <span style={{ fontFamily: 'JetBrains Mono' }}>{detectedDuplicates[0].id}: {detectedDuplicates[0].title}</span>
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
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                >
                  {services.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.tier})</option>
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
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Detailed Description (NLP Auto-Categorization Enabled)
                </label>
                <textarea 
                  required
                  rows={3}
                  placeholder="Describe the failure, affected users, and error messages..."
                  value={newDesc}
                  onChange={e => setNewDesc(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Impact</label>
                  <select 
                    value={newImpact} 
                    onChange={e => setNewImpact(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
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
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
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
                  Technician Assignment Strategy (Strategy Pattern)
                </label>
                <select 
                  value={newStrategy} 
                  onChange={e => setNewStrategy(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: 13 }}
                >
                  <option value="smart">Composite Smart Assignment (Skill + Load + Rating)</option>
                  <option value="skill">Skill-Based Assignment</option>
                  <option value="load">Least-Loaded Assignment</option>
                  <option value="round_robin">Round-Robin Assignment</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
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

    </div>
  );
}

export default App;
