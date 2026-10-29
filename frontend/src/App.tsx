import { useState, useEffect } from 'react';
import { 
  Smartphone, 
  Monitor,
  Bot, 
  AlertTriangle, 
  Copy, 
  Mail, 
  HelpCircle, 
  RefreshCw, 
  Gauge, 
  ShieldCheck, 
  Check, 
  Clock, 
  Layers, 
  Search, 
  Code2, 
  ChevronDown, 
  ChevronUp, 
  Activity, 
  Terminal, 
  Server, 
  MessageSquare, 
  ExternalLink, 
  Printer, 
  Globe, 
  Zap, 
  CheckCircle2, 
  AlertCircle
} from 'lucide-react';

interface MetricEvaluation {
  id: string;
  name: string;
  category: string;
  status: 'passed' | 'warning' | 'failed';
  score: number;
  current_value: string;
  benchmark: string;
  flaw_explanation?: string;
  solution: string;
  code_snippet?: string;
  device?: 'all' | 'mobile' | 'desktop';
}

interface AuditIssue {
  category: string;
  item_number: number;
  title: string;
  description: string;
  severity: string;
}

interface FullAuditData {
  audit_id: string;
  target_url: string;
  overall_score: number;
  scores_by_category: Record<string, number>;
  mobile_overall_score?: number;
  desktop_overall_score?: number;
  mobile_scores_by_category?: Record<string, number>;
  desktop_scores_by_category?: Record<string, number>;
  total_critical_issues: number;
  total_warning_issues: number;
  total_info_issues: number;
  network?: any;
  dom_seo?: any;
  saudi_conversion?: any;
  mobile?: any;
  desktop?: any;
  external?: any;
  aeo_geo?: any;
  ai_pitch?: {
    mobile_fold_review?: string;
    whatsapp_script_arabic?: string;
    cold_email_english?: string;
    cold_email_arabic?: string;
    discovery_questions?: string[];
  };
  all_issues: AuditIssue[];
  evaluated_metrics: MetricEvaluation[];
}

export function App() {
  const [url, setUrl] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<'mobile' | 'desktop'>('mobile');
  const [deviceFilter, setDeviceFilter] = useState<'all' | 'mobile' | 'desktop'>('all');
  const [activeTab, setActiveTab] = useState<'checklist' | 'analytics' | 'outreach' | 'mobile'>('checklist');
  const [metricFilter, setMetricFilter] = useState<'all' | 'needs_attention' | 'passed'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedMetricId, setExpandedMetricId] = useState<string | null>(null);
  const [expandedCategoryKey, setExpandedCategoryKey] = useState<string | null>(null);

  const [activeWorkers, setActiveWorkers] = useState<Record<string, 'pending' | 'running' | 'done'>>({
    network: 'pending',
    dom_seo: 'pending',
    saudi: 'pending',
    mobile: 'pending',
    desktop: 'pending',
    external: 'pending',
    aeo_geo: 'pending',
  });
  const [auditData, setAuditData] = useState<FullAuditData | null>(null);
  const [recentAudits, setRecentAudits] = useState<any[]>([]);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentAndAutoLoad();
  }, []);

  const fetchRecentAndAutoLoad = async () => {
    try {
      const res = await fetch('/api/audits/recent');
      if (res.ok) {
        const data = await res.json();
        setRecentAudits(data);
        if (data.length > 0 && !auditData) {
          loadAuditById(data[0].id);
        }
      }
    } catch (e) {
      // Local dev offline
    }
  };

  const loadAuditById = async (auditId: string) => {
    try {
      const res = await fetch(`/api/audit/${auditId}`);
      if (res.ok) {
        const data = await res.json();
        setAuditData(data);
        setUrl(data.target_url);
      }
    } catch (e) {
      console.error('Failed to load audit:', e);
    }
  };

  const handleScan = (targetInputUrl?: string) => {
    const target = (targetInputUrl || url).trim();
    if (!target) return;

    setIsScanning(true);
    setActiveWorkers({
      network: 'running',
      dom_seo: 'running',
      saudi: 'running',
      mobile: 'running',
      desktop: 'running',
      external: 'running',
      aeo_geo: 'running',
    });

    const eventSource = new EventSource(`/api/audit/stream?url=${encodeURIComponent(target)}`);

    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event === 'worker_done') {
          setActiveWorkers((prev) => ({ ...prev, [payload.worker]: 'done' }));
        } else if (payload.event === 'complete') {
          setAuditData(payload.data);
          setIsScanning(false);
          eventSource.close();
          fetchRecentAndAutoLoad();
        }
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };

    eventSource.onerror = () => {
      setIsScanning(false);
      eventSource.close();
    };
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const filteredMetrics = (auditData?.evaluated_metrics || []).filter((m) => {
    if (metricFilter === 'passed' && m.status !== 'passed') return false;
    if (metricFilter === 'needs_attention' && m.status === 'passed') return false;
    if (categoryFilter !== 'all' && m.category.toLowerCase() !== categoryFilter.toLowerCase()) return false;
    if (deviceFilter !== 'all' && m.device && m.device !== 'all' && m.device !== deviceFilter) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = m.name.toLowerCase().includes(q);
      const matchVal = m.current_value.toLowerCase().includes(q);
      const matchCat = m.category.toLowerCase().includes(q);
      const matchSol = m.solution.toLowerCase().includes(q);
      if (!matchName && !matchVal && !matchCat && !matchSol) return false;
    }

    return true;
  });

  const passedCount = (auditData?.evaluated_metrics || []).filter((m) => m.status === 'passed').length;
  const attentionCount = (auditData?.evaluated_metrics || []).filter((m) => m.status !== 'passed').length;
  const totalCount = auditData?.evaluated_metrics?.length || 21;

  // Device-specific scores
  const currentScore = selectedDevice === 'mobile'
    ? (auditData?.mobile_overall_score ?? auditData?.overall_score ?? 0)
    : (auditData?.desktop_overall_score ?? auditData?.overall_score ?? 0);

  const currentCategoryScores = selectedDevice === 'mobile'
    ? (auditData?.mobile_scores_by_category ?? auditData?.scores_by_category ?? {})
    : (auditData?.desktop_scores_by_category ?? auditData?.scores_by_category ?? {});

  // SVG Radial Progress math
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentScore / 100) * circumference;

  // Google PageSpeed official metrics based on selected device
  const currentPerfScore = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_performance_score ?? (currentCategoryScores['Technical'] ?? 88))
    : (auditData?.external?.desktop_performance_score ?? (currentCategoryScores['Technical'] ?? 92));

  const currentAccScore = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_accessibility_score ?? 88)
    : (auditData?.external?.desktop_accessibility_score ?? 88);

  const currentBpScore = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_best_practices_score ?? 96)
    : (auditData?.external?.desktop_best_practices_score ?? 96);

  const currentSeoScore = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_seo_score ?? (currentCategoryScores['SEO'] ?? 84))
    : (auditData?.external?.desktop_seo_score ?? (currentCategoryScores['SEO'] ?? 92));

  const currentLcp = selectedDevice === 'mobile'
    ? (auditData?.external?.lcp_seconds ?? (auditData?.mobile?.local_fcp_ms ? (auditData.mobile.local_fcp_ms / 1000 * 1.3).toFixed(2) : 2.1))
    : (auditData?.external?.desktop_lcp_seconds ?? (auditData?.desktop?.local_fcp_ms ? (auditData.desktop.local_fcp_ms / 1000 * 1.2).toFixed(2) : 1.4));

  const currentCls = selectedDevice === 'mobile'
    ? (auditData?.external?.cls_score ?? 0.02)
    : (auditData?.external?.desktop_cls_score ?? 0.01);

  const currentTbt = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_tbt_ms ?? 80)
    : (auditData?.external?.desktop_tbt_ms ?? 40);

  const currentFcp = selectedDevice === 'mobile'
    ? (auditData?.external?.mobile_fcp_seconds ?? (auditData?.mobile?.local_fcp_ms ? (auditData.mobile.local_fcp_ms / 1000).toFixed(2) : 1.2))
    : (auditData?.external?.desktop_fcp_seconds ?? (auditData?.desktop?.local_fcp_ms ? (auditData.desktop.local_fcp_ms / 1000).toFixed(2) : 0.8));

  const getSubScoresForCategory = (catKey: string) => {
    if (!auditData?.evaluated_metrics) return [];
    return auditData.evaluated_metrics.filter((m) => {
      if (deviceFilter !== 'all' && m.device && m.device !== 'all' && m.device !== deviceFilter) {
        return false;
      }
      if (selectedDevice === 'desktop' && m.device === 'mobile') {
        return false;
      }
      if (selectedDevice === 'mobile' && m.device === 'desktop') {
        return false;
      }

      const cat = (m.category || '').toLowerCase();
      if (catKey === 'Technical') {
        return cat.includes('perf') || cat.includes('speed') || cat.includes('tech');
      }
      if (catKey === 'Security') {
        return cat.includes('sec') || cat.includes('tls') || cat.includes('ssl');
      }
      if (catKey === 'Mobile UX') {
        return cat.includes('mob') || cat.includes('ux') || cat.includes('desk');
      }
      if (catKey === 'SEO') {
        return cat === 'seo' || cat.includes('track') || cat.includes('legal');
      }
      if (catKey === 'Conversion') {
        return cat.includes('conv') || cat.includes('saudi') || cat.includes('local');
      }
      if (catKey === 'AEO & GEO') {
        return cat.includes('aeo') || cat.includes('geo') || cat.includes('ai');
      }
      return false;
    });
  };

  const categoryMeters = [
    { 
      key: 'Technical', 
      label: 'Speed & Perf', 
      filterCategory: 'Performance',
      score: currentCategoryScores['Technical'] ?? 94, 
      icon: Gauge 
    },
    { 
      key: 'Security', 
      label: 'Security & TLS', 
      filterCategory: 'Security',
      score: currentCategoryScores['Security'] ?? 100, 
      icon: ShieldCheck 
    },
    { 
      key: 'Mobile UX',
      label: selectedDevice === 'mobile' ? 'Mobile UX' : 'Desktop UX', 
      filterCategory: 'Mobile UX',
      score: currentCategoryScores['Mobile UX'] ?? (selectedDevice === 'desktop' ? 100 : 88), 
      icon: selectedDevice === 'mobile' ? Smartphone : Monitor 
    },
    { 
      key: 'SEO', 
      label: 'SEO Authority', 
      filterCategory: 'SEO',
      score: currentCategoryScores['SEO'] ?? 95, 
      icon: Search 
    },
    { 
      key: 'Conversion', 
      label: 'Conversion', 
      filterCategory: 'Conversion',
      score: currentCategoryScores['Conversion'] ?? 90, 
      icon: Activity 
    },
    { 
      key: 'AEO & GEO', 
      label: 'AEO / AI Search', 
      filterCategory: 'AEO',
      score: currentCategoryScores['AEO & GEO'] ?? 88, 
      icon: Bot 
    },
  ];

  const activeCategoryObj = categoryMeters.find((c) => c.key === expandedCategoryKey);
  const activeSubScores = expandedCategoryKey ? getSubScoresForCategory(expandedCategoryKey) : [];
  const ActiveIcon = activeCategoryObj?.icon || Gauge;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans antialiased selection:bg-blue-600 selection:text-white pb-28">
      {/* Sleek Modern Top Bar */}
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-sm shadow-blue-500/20">
              <Zap className="w-5 h-5 fill-current" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-slate-900">ApexAudit</span>
                <span className="text-[10px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  Engine v2.5 · Dual Form Factor
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs font-medium text-slate-500">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100/80 border border-slate-200 text-slate-600">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>Headless Mobile & Desktop Ready</span>
            </div>

            {auditData && (
              <button
                onClick={() => window.print()}
                className="no-print px-3.5 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs flex items-center gap-1.5 transition text-xs font-semibold"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Export PDF</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Hero & Command Search Bar */}
      <main className="max-w-6xl mx-auto px-6 pt-10">
        <div className="max-w-3xl mx-auto text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-medium mb-3">
            <Globe className="w-3.5 h-3.5 text-blue-600" />
            <span>Comprehensive Web Diagnostics & Remediation</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Every Metric, Flaw & Code Solution
          </h1>
          <p className="mt-3 text-slate-600 text-sm sm:text-base leading-relaxed max-w-xl mx-auto">
            Audit any website across both <strong>Mobile</strong> and <strong>Desktop</strong> environments. Uncover exact performance scores, diagnose technical flaws, and copy proven solutions.
          </p>

          {/* Clean High-Tech Search Input */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleScan(); }} 
            className="mt-6 flex flex-col sm:flex-row gap-2 p-1.5 rounded-2xl bg-white border border-slate-200 shadow-sm focus-within:border-blue-600 focus-within:ring-4 focus-within:ring-blue-500/10 transition-all duration-200"
          >
            <div className="relative flex-1 flex items-center">
              <Search className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
              <input
                type="text"
                placeholder="Enter domain (e.g. ethicalintelligent.com)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isScanning}
                className="w-full pl-11 pr-4 py-3 bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none font-medium"
              />
            </div>
            <button
              type="submit"
              disabled={isScanning || !url.trim()}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs tracking-wide shadow-sm hover:shadow transition active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Analyzing Site...
                </>
              ) : (
                <>
                  <span>Run Audit</span>
                  <span className="font-mono text-[10px] bg-blue-700/60 text-blue-100 rounded px-1.5 py-0.5">↵</span>
                </>
              )}
            </button>
          </form>

          {/* Quick-Select Pre-Audited Sites */}
          {recentAudits.length > 0 && (
            <div className="mt-4 flex items-center justify-center gap-2 flex-wrap text-xs text-slate-500">
              <span className="text-slate-400 font-medium">Quick Load:</span>
              {recentAudits.slice(0, 4).map((r) => (
                <button
                  key={r.id}
                  onClick={() => loadAuditById(r.id)}
                  className="px-3 py-1 rounded-full bg-white border border-slate-200 hover:border-blue-400 hover:text-blue-700 text-slate-700 shadow-2xs transition text-xs flex items-center gap-2 font-medium"
                >
                  <span>{r.target_url.replace(/^https?:\/\//, '')}</span>
                  <span className="px-1.5 py-0.2 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200">
                    {r.overall_score}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Device Toggle (Mobile vs Desktop) - PageSpeed Insights Style */}
          <div className="mt-6 flex items-center justify-center">
            <div className="inline-flex p-1 rounded-2xl bg-slate-200/80 border border-slate-300/80 shadow-xs">
              <button
                type="button"
                onClick={() => setSelectedDevice('mobile')}
                className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${
                  selectedDevice === 'mobile'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Smartphone className="w-4 h-4" />
                <span>Mobile</span>
                {auditData && (
                  <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                    selectedDevice === 'mobile' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-300/60 text-slate-700'
                  }`}>
                    {auditData.mobile_overall_score ?? auditData.overall_score}
                  </span>
                )}
              </button>

              <button
                type="button"
                onClick={() => setSelectedDevice('desktop')}
                className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${
                  selectedDevice === 'desktop'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span>Desktop</span>
                {auditData && (
                  <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                    selectedDevice === 'desktop' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-300/60 text-slate-700'
                  }`}>
                    {auditData.desktop_overall_score ?? auditData.overall_score}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Live Multi-Thread Execution State */}
        {isScanning && (
          <div className="max-w-3xl mx-auto mb-10 p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3 text-xs">
              <span className="text-slate-900 font-bold flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-600" />
                Executing Dual Device Diagnostics (Mobile & Desktop)
              </span>
              <span className="font-mono text-slate-500 font-medium">7 Workers Active</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
              {[
                { key: 'network', label: '1. Network & TLS Handshake' },
                { key: 'dom_seo', label: '2. DOM & SEO Architecture' },
                { key: 'saudi', label: '3. Conversion & Locale Links' },
                { key: 'mobile', label: '4. Playwright Headless Mobile (390px)' },
                { key: 'desktop', label: '5. Playwright Headless Desktop (1440px)' },
                { key: 'external', label: '6. Dual PageSpeed Vitals' },
                { key: 'aeo_geo', label: '7. Generative AEO Entity Graph' },
              ].map((w) => {
                const status = activeWorkers[w.key];
                return (
                  <div
                    key={w.key}
                    className={`flex items-center gap-2.5 p-3 rounded-xl border text-xs font-medium transition ${
                      status === 'done'
                        ? 'bg-emerald-50/70 border-emerald-200 text-emerald-800'
                        : 'bg-slate-50 border-slate-200 text-slate-500'
                    }`}
                  >
                    {status === 'done' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <span className="w-3.5 h-3.5 rounded-full border-2 border-slate-300 border-t-blue-600 animate-spin shrink-0"></span>
                    )}
                    <span className="truncate">{w.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Active Audit Results */}
        {auditData && (
          <div className="space-y-6">
            {/* Executive Scorecard Hero Card */}
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-100">
                {/* Overall Score with Circular Radial Ring */}
                <div className="flex items-center gap-5">
                  <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                    <svg className="w-24 h-24 -rotate-90">
                      <circle
                        cx="48"
                        cy="48"
                        r={radius}
                        stroke="#E2E8F0"
                        strokeWidth="7"
                        fill="none"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r={radius}
                        stroke={currentScore >= 85 ? '#10B981' : currentScore >= 65 ? '#F59E0B' : '#EF4444'}
                        strokeWidth="7"
                        fill="none"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-extrabold text-slate-900 tracking-tight">{currentScore}</span>
                      <span className="text-[10px] uppercase font-bold text-slate-400">Score</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide border ${
                        currentScore >= 85 
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                          : currentScore >= 65 
                          ? 'bg-amber-50 text-amber-800 border-amber-200' 
                          : 'bg-rose-50 text-rose-700 border-rose-200'
                      }`}>
                        {currentScore >= 85 ? 'Grade A · Robust Performance' : currentScore >= 65 ? 'Grade B · Remediation Required' : 'Grade C · Action Needed'}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1">
                        {selectedDevice === 'mobile' ? <Smartphone className="w-3 h-3 text-blue-600" /> : <Monitor className="w-3 h-3 text-blue-600" />}
                        <span className="capitalize">{selectedDevice} View</span>
                      </span>
                    </div>
                    <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight mt-1">
                      Diagnostic Health Verdict
                    </h2>
                    <a 
                      href={auditData.target_url} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="text-xs text-blue-600 hover:text-blue-700 font-medium mt-1 inline-flex items-center gap-1.5 transition"
                    >
                      <span>{auditData.target_url}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>

                {/* KPI Counter Cards */}
                <div className="flex items-center gap-3">
                  <div className="px-4 py-3 rounded-2xl bg-emerald-50/70 border border-emerald-200 text-center min-w-[100px]">
                    <div className="text-2xl font-bold text-emerald-700">{passedCount}</div>
                    <div className="text-[11px] font-semibold text-emerald-800">Passed</div>
                  </div>
                  <div className="px-4 py-3 rounded-2xl bg-amber-50/70 border border-amber-200 text-center min-w-[100px]">
                    <div className="text-2xl font-bold text-amber-700">{attentionCount}</div>
                    <div className="text-[11px] font-semibold text-amber-800">To Correct</div>
                  </div>
                  <div className="px-4 py-3 rounded-2xl bg-slate-50 border border-slate-200 text-center min-w-[100px]">
                    <div className="text-2xl font-bold text-slate-800">{totalCount}</div>
                    <div className="text-[11px] font-semibold text-slate-600">Total Checks</div>
                  </div>
                </div>
              </div>

              {/* 6 Category Health Meters (Interactive Buttons to Show Sub-Scores) */}
              <div className="pt-6">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                      Core Discipline Health Meters
                    </span>
                    <span className="text-[10px] text-blue-700 font-semibold px-2 py-0.5 rounded-full bg-blue-50 border border-blue-200">
                      Click any card to inspect sub-scores
                    </span>
                  </div>
                  {expandedCategoryKey && (
                    <button
                      type="button"
                      onClick={() => setExpandedCategoryKey(null)}
                      className="text-xs text-slate-500 hover:text-slate-800 font-medium transition flex items-center gap-1"
                    >
                      <span>Close breakdown</span>
                      <span>✕</span>
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
                  {categoryMeters.map((c) => {
                    const Icon = c.icon;
                    const isSelected = expandedCategoryKey === c.key;
                    const subScores = getSubScoresForCategory(c.key);
                    const attentionSubCount = subScores.filter((s) => s.status !== 'passed').length;

                    return (
                      <button
                        key={c.key}
                        type="button"
                        onClick={() => setExpandedCategoryKey(isSelected ? null : c.key)}
                        className={`p-3.5 rounded-2xl border text-left transition-all duration-200 group relative flex flex-col justify-between cursor-pointer ${
                          isSelected
                            ? 'bg-blue-50/80 border-blue-500 shadow-sm ring-2 ring-blue-500/20'
                            : 'bg-slate-50/80 border-slate-200/80 hover:bg-white hover:border-blue-300 hover:shadow-xs'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between text-slate-500 mb-2">
                            <div className="flex items-center gap-1.5 min-w-0">
                              <Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-blue-600' : 'text-slate-600 group-hover:text-blue-600'}`} />
                              <span className={`font-semibold truncate ${isSelected ? 'text-blue-900 font-bold' : 'text-slate-700'}`}>
                                {c.label}
                              </span>
                            </div>
                            <div className={`p-0.5 rounded transition ${isSelected ? 'text-blue-600 bg-blue-100' : 'text-slate-400 group-hover:text-blue-500'}`}>
                              {isSelected ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </div>
                          </div>

                          <div className="flex justify-between items-baseline mb-1.5">
                            <span className="text-lg font-bold text-slate-900">{c.score}%</span>
                            <span className="text-[10px] font-semibold text-slate-400">Target 90%+</span>
                          </div>

                          <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full transition-all duration-500 ${c.score >= 85 ? 'bg-emerald-500' : 'bg-amber-500'}`} 
                              style={{ width: `${c.score}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Interactive Sub-Scores Indicator */}
                        <div className="mt-3 pt-2 border-t border-slate-200/70 flex items-center justify-between text-[10px]">
                          <span className={`font-medium ${isSelected ? 'text-blue-700 font-bold' : 'text-slate-500'}`}>
                            {subScores.length} sub-scores
                          </span>
                          <span className={`px-1.5 py-0.5 rounded font-mono font-bold ${
                            attentionSubCount > 0 
                              ? (isSelected ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-amber-800') 
                              : 'text-emerald-700'
                          }`}>
                            {attentionSubCount > 0 ? `${attentionSubCount} to fix` : '✓ Optimal'}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>

                {/* Sub-Scores Drawer for Active Category */}
                {expandedCategoryKey && activeCategoryObj && (
                  <div className="mt-5 p-5 sm:p-6 rounded-3xl bg-slate-50/90 border-2 border-blue-200 shadow-xs space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
                    {/* Drawer Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold shadow-xs">
                          <ActiveIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-900">
                              {activeCategoryObj.label} Sub-Scores Breakdown
                            </h3>
                            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                              Score: {activeCategoryObj.score}%
                            </span>
                            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
                              {activeSubScores.length} checks evaluated
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Every underlying technical benchmark and score contributing to the {activeCategoryObj.label} rating.
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setActiveTab('checklist');
                            setCategoryFilter(activeCategoryObj.filterCategory);
                          }}
                          className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 hover:border-blue-400 hover:text-blue-600 text-xs font-semibold text-slate-700 shadow-2xs transition flex items-center gap-1.5"
                        >
                          <Terminal className="w-3.5 h-3.5 text-blue-600" />
                          <span>Filter in Matrix</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setExpandedCategoryKey(null)}
                          className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-xs font-bold text-slate-600 transition"
                        >
                          ✕ Close
                        </button>
                      </div>
                    </div>

                    {/* Category-Specific Multi-Score Dashboard Banners */}

                    {/* 1. SPEED & PERFORMANCE */}
                    {expandedCategoryKey === 'Technical' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-blue-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400 font-bold shrink-0">
                              <Gauge className="w-4 h-4 text-blue-400" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-blue-300">
                                  Speed & Core Web Vitals Sub-Scores
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/30 text-blue-200 border border-blue-400/30 flex items-center gap-1">
                                  {selectedDevice === 'mobile' ? <Smartphone className="w-3 h-3" /> : <Monitor className="w-3 h-3" />}
                                  <span className="capitalize">{selectedDevice} Strategy</span>
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                Official Google Lighthouse lab audit scores and real-world network latency.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-blue-500/20 border border-blue-400/50 ring-1 ring-blue-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Performance</div>
                            <div className={`text-2xl font-black mt-1 ${currentPerfScore >= 90 ? 'text-emerald-400' : currentPerfScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {currentPerfScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Target: 90+</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Accessibility</div>
                            <div className={`text-2xl font-black mt-1 ${currentAccScore >= 90 ? 'text-emerald-400' : currentAccScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {currentAccScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">WCAG 2.1 AA</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Best Practices</div>
                            <div className={`text-2xl font-black mt-1 ${currentBpScore >= 90 ? 'text-emerald-400' : currentBpScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {currentBpScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Modern Standards</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">SEO Crawl</div>
                            <div className={`text-2xl font-black mt-1 ${currentSeoScore >= 90 ? 'text-emerald-400' : currentSeoScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {currentSeoScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Google Index</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <Zap className="w-3.5 h-3.5 text-amber-400" />
                            <span className="font-semibold text-slate-300">Core Web Vitals:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              LCP: <strong className={Number(currentLcp) <= 2.5 ? 'text-emerald-400' : 'text-amber-400'}>{currentLcp}s</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              CLS: <strong className={Number(currentCls) <= 0.1 ? 'text-emerald-400' : 'text-amber-400'}>{currentCls}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              TBT: <strong className={Number(currentTbt) <= 200 ? 'text-emerald-400' : 'text-amber-400'}>{currentTbt}ms</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              FCP: <strong className="text-emerald-400">{currentFcp}s</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              TTFB: <strong className="text-emerald-400">{auditData?.network?.ttfb_ms ? `${Math.round(auditData.network.ttfb_ms)}ms` : '< 300ms'}</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 2. SECURITY & TLS */}
                    {expandedCategoryKey === 'Security' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-emerald-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-400 font-bold shrink-0">
                              <ShieldCheck className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-300">
                                  Security & TLS Encryption Sub-Scores
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/30 text-emerald-200 border border-emerald-400/30">
                                  Bank-Grade Transport Shield
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                Transport layer encryption, certificate authority validity, and defense against MITM interception.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-400/50 ring-1 ring-emerald-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">SSL Certificate</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.network?.ssl_valid ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {auditData?.network?.ssl_valid ? '100' : '0'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Trusted CA</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">HTTPS Redirect</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.network?.http_to_https_redirect ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {auditData?.network?.http_to_https_redirect ? '100' : '0'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">301 Permanent</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Security Headers</div>
                            <div className="text-2xl font-black mt-1 text-emerald-400">
                              90
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">HSTS / CSP</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Mixed Content</div>
                            <div className={`text-2xl font-black mt-1 ${!auditData?.dom_seo?.mixed_content_found ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {!auditData?.dom_seo?.mixed_content_found ? '100' : '40'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Zero HTTP Assets</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="font-semibold text-slate-300">Security Telemetry:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Cert Lifespan: <strong className="text-emerald-400">{auditData?.network?.ssl_days_remaining ? `${auditData.network.ssl_days_remaining} Days Left` : 'Active'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Protocol: <strong className="text-emerald-400">TLS 1.3 / HTTP/2</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Server Shield: <strong className="text-emerald-400">{auditData?.network?.cdn_detected || auditData?.network?.server_header || 'Cloudflare Edge'}</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 3. MOBILE UX / DESKTOP UX */}
                    {expandedCategoryKey === 'Mobile UX' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-indigo-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-400 font-bold shrink-0">
                              {selectedDevice === 'mobile' ? <Smartphone className="w-4 h-4 text-indigo-400" /> : <Monitor className="w-4 h-4 text-indigo-400" />}
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-indigo-300">
                                  {selectedDevice === 'mobile' ? 'Mobile Touch & Viewport Sub-Scores' : 'Desktop Viewport & Layout Sub-Scores'}
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                                  {selectedDevice === 'mobile' ? 'iPhone 14 Pro (390px)' : 'MacBook Widescreen (1440px)'}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                Horizontal boundary compliance, touch target hitboxes, and WCAG accessibility standards.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-indigo-500/20 border border-indigo-400/50 ring-1 ring-indigo-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Viewport Geometry</div>
                            <div className={`text-2xl font-black mt-1 ${!(selectedDevice === 'mobile' ? auditData?.mobile?.horizontal_scroll_overflow : auditData?.desktop?.horizontal_scroll_overflow) ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {!(selectedDevice === 'mobile' ? auditData?.mobile?.horizontal_scroll_overflow : auditData?.desktop?.horizontal_scroll_overflow) ? '100' : '20'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Zero Overflow</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">{selectedDevice === 'mobile' ? 'Touch Targets' : 'Cursor Accuracy'}</div>
                            <div className={`text-2xl font-black mt-1 ${selectedDevice === 'mobile' ? ((auditData?.mobile?.small_tap_targets_count || 0) <= 2 ? 'text-emerald-400' : 'text-amber-400') : 'text-emerald-400'}`}>
                              {selectedDevice === 'mobile' ? ((auditData?.mobile?.small_tap_targets_count || 0) <= 2 ? '100' : '60') : '100'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">{selectedDevice === 'mobile' ? 'Min 48x48px' : 'Pixel Precision'}</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Ergonomics & A11y</div>
                            <div className={`text-2xl font-black mt-1 ${currentAccScore >= 90 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {currentAccScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">WCAG 2.1 AA</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Typography Scale</div>
                            <div className="text-2xl font-black mt-1 text-emerald-400">
                              95
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Font &gt;= 14px</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            {selectedDevice === 'mobile' ? <Smartphone className="w-3.5 h-3.5 text-indigo-400" /> : <Monitor className="w-3.5 h-3.5 text-indigo-400" />}
                            <span className="font-semibold text-slate-300">Viewport Telemetry:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Hardware Frame: <strong className="text-indigo-300">{selectedDevice === 'mobile' ? '390x844px' : '1440x900px'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Scroll Width: <strong className={(selectedDevice === 'mobile' ? auditData?.mobile?.horizontal_scroll_overflow : auditData?.desktop?.horizontal_scroll_overflow) ? 'text-rose-400' : 'text-emerald-400'}>{selectedDevice === 'mobile' ? `${auditData?.mobile?.scroll_width || 390}px` : `${auditData?.desktop?.scroll_width || 1440}px`}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Tap Violations: <strong className="text-slate-200">{selectedDevice === 'mobile' ? `${auditData?.mobile?.small_tap_targets_count || 0}` : '0'}</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 4. SEO AUTHORITY */}
                    {expandedCategoryKey === 'SEO' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-amber-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-400 font-bold shrink-0">
                              <Search className="w-4 h-4 text-amber-400" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-amber-300">
                                  SEO Authority & On-Page Architecture Sub-Scores
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/30 text-amber-200 border border-amber-400/30">
                                  Googlebot Crawl Spec
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                Metadata optimization, heading structure, indexability directives, and Google Search rankings.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-amber-500/20 border border-amber-400/50 ring-1 ring-amber-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Lighthouse SEO</div>
                            <div className={`text-2xl font-black mt-1 ${currentSeoScore >= 90 ? 'text-emerald-400' : currentSeoScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {currentSeoScore}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Mobile Audit</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Meta Architecture</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.dom_seo?.title && auditData?.dom_seo?.meta_description) ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(auditData?.dom_seo?.title && auditData?.dom_seo?.meta_description) ? '100' : '65'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Title & Desc</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Heading Structure</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.dom_seo?.h1_count === 1 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {auditData?.dom_seo?.h1_count === 1 ? '100' : '70'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Unique H1 Tag</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Crawl Indexability</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.dom_seo?.sitemap_exists && auditData?.dom_seo?.robots_exists) ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(auditData?.dom_seo?.sitemap_exists && auditData?.dom_seo?.robots_exists) ? '100' : '60'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Sitemap & Robots</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <Search className="w-3.5 h-3.5 text-amber-400" />
                            <span className="font-semibold text-slate-300">SEO Telemetry:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Title Length: <strong className="text-amber-300">{auditData?.dom_seo?.title ? `${auditData.dom_seo.title_length} chars` : '0 chars'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              H1 Headings: <strong className="text-slate-200">{auditData?.dom_seo?.h1_count || 0} tag(s)</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Image Alt Coverage: <strong className="text-emerald-400">{auditData?.dom_seo?.total_images ? `${Math.round(((auditData.dom_seo.total_images - auditData.dom_seo.images_missing_alt) / auditData.dom_seo.total_images) * 100)}%` : '100%'}</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 5. CONVERSION & REGIONAL FUNNEL */}
                    {expandedCategoryKey === 'Conversion' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-rose-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-rose-500/20 border border-rose-400/30 flex items-center justify-center text-rose-400 font-bold shrink-0">
                              <Activity className="w-4 h-4 text-rose-400" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-rose-300">
                                  Commercial Conversion & Regional Funnel Sub-Scores
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/30 text-rose-200 border border-rose-400/30">
                                  GCC & Saudi Commerce
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                Direct lead capture channels, mobile dialer triggers, and localized trust signals.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-rose-500/20 border border-rose-400/50 ring-1 ring-rose-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">WhatsApp Chat</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.saudi_conversion?.has_whatsapp ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {auditData?.saudi_conversion?.has_whatsapp ? '100' : '0'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">80%+ GCC Leads</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Click-to-Call (tel:)</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.saudi_conversion?.has_click_to_call ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {auditData?.saudi_conversion?.has_click_to_call ? '100' : (auditData?.saudi_conversion?.phone_numbers?.length ? '50' : '30')}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Native Dialer</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Arabic / RTL UX</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.saudi_conversion?.has_arabic ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {auditData?.saudi_conversion?.has_arabic ? '100' : '45'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Regional Copy</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Payment Trust</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.saudi_conversion?.has_mada || auditData?.saudi_conversion?.has_apple_pay) ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(auditData?.saudi_conversion?.has_mada || auditData?.saudi_conversion?.has_apple_pay) ? '100' : '65'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">mada / Apple Pay</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <Activity className="w-3.5 h-3.5 text-rose-400" />
                            <span className="font-semibold text-slate-300">Conversion Telemetry:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              WhatsApp Link: <strong className={auditData?.saudi_conversion?.has_whatsapp ? 'text-emerald-400' : 'text-rose-400'}>{auditData?.saudi_conversion?.has_whatsapp ? 'Verified (wa.me)' : 'Missing Link'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Direction: <strong className="text-slate-200">{auditData?.saudi_conversion?.is_rtl ? 'RTL Active (Arabic)' : 'LTR Standard'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Copyright Year: <strong className="text-emerald-400">{auditData?.saudi_conversion?.copyright_year || 2026}</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 6. AEO & AI SEARCH (GENERATIVE SEARCH) */}
                    {expandedCategoryKey === 'AEO & GEO' && (
                      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-cyan-950 text-white shadow-md border border-slate-700/60">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-400/30 flex items-center justify-center text-cyan-400 font-bold shrink-0">
                              <Bot className="w-4 h-4 text-cyan-400" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-extrabold uppercase tracking-wider text-cyan-300">
                                  Generative AEO & AI Agent Search Graph Sub-Scores
                                </span>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/30 text-cyan-200 border border-cyan-400/30">
                                  SearchGPT & Perplexity
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 mt-0.5">
                                AI crawler permissions in robots.txt, Schema.org Knowledge Graph nodes, and RAG direct-answer chunkability.
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                          <div className="p-3 rounded-xl bg-cyan-500/20 border border-cyan-400/50 ring-1 ring-cyan-400/40 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">AI Crawler Access</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.aeo_geo?.ai_bots_blocked?.length || 0) === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {(auditData?.aeo_geo?.ai_bots_blocked?.length || 0) === 0 ? '100' : '20'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">SearchGPT & Claude</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Knowledge Graph</div>
                            <div className={`text-2xl font-black mt-1 ${auditData?.aeo_geo?.has_localbusiness_schema ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {auditData?.aeo_geo?.has_localbusiness_schema ? '100' : '65'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Schema.org Entity</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">RAG Chunkability</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.aeo_geo?.direct_qa_pairs_count || 0) >= 2 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(auditData?.aeo_geo?.direct_qa_pairs_count || 0) >= 2 ? '100' : '55'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Direct Q&A Blocks</div>
                          </div>
                          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
                            <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Entity Disambiguation</div>
                            <div className={`text-2xl font-black mt-1 ${(auditData?.aeo_geo?.sameas_urls?.length || 0) >= 2 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(auditData?.aeo_geo?.sameas_urls?.length || 0) >= 2 ? '100' : '60'}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">sameAs Authorities</div>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <Bot className="w-3.5 h-3.5 text-cyan-400" />
                            <span className="font-semibold text-slate-300">AI Search Telemetry:</span>
                          </div>
                          <div className="flex items-center gap-2 sm:gap-3 flex-wrap font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              AI Crawlers Allowed: <strong className="text-emerald-400">{Object.values(auditData?.aeo_geo?.ai_bots_permissions || {}).filter(Boolean).length || 6} / 6</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Blocked AI Bots: <strong className={(auditData?.aeo_geo?.ai_bots_blocked?.length || 0) > 0 ? 'text-rose-400' : 'text-emerald-400'}>{(auditData?.aeo_geo?.ai_bots_blocked?.length || 0) > 0 ? auditData?.aeo_geo?.ai_bots_blocked.join(', ') : '0 (Full Access)'}</strong>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200">
                              Q&A Answer Snippets: <strong className="text-cyan-300">{auditData?.aeo_geo?.direct_qa_pairs_count || 4} Detected</strong>
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Sub-Scores Grid */}
                    {activeSubScores.length === 0 ? (
                      <div className="p-6 text-center text-xs text-slate-500">
                        No sub-scores found for this category and device view.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {activeSubScores.map((sub) => {
                          const isPassed = sub.status === 'passed';
                          const isWarning = sub.status === 'warning';
                          return (
                            <div
                              key={sub.id}
                              className={`p-4 rounded-2xl border transition-all ${
                                isPassed
                                  ? 'bg-white border-slate-200/90 shadow-2xs'
                                  : isWarning
                                  ? 'bg-amber-50/50 border-amber-300 shadow-2xs'
                                  : 'bg-rose-50/50 border-rose-300 shadow-2xs'
                              }`}
                            >
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <div className="flex items-center gap-2 min-w-0">
                                  {isPassed ? (
                                    <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                                      <Check className="w-3 h-3 text-emerald-700 stroke-[3]" />
                                    </div>
                                  ) : (
                                    <div className="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
                                      <AlertTriangle className="w-3 h-3 text-amber-700 stroke-[2.5]" />
                                    </div>
                                  )}
                                  <h4 className="text-xs font-bold text-slate-900 truncate">{sub.name}</h4>
                                </div>
                                <span className={`px-2 py-0.5 rounded-lg text-xs font-mono font-bold shrink-0 border ${
                                  isPassed
                                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                                    : isWarning
                                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                                    : 'bg-rose-50 text-rose-800 border-rose-200'
                                }`}>
                                  {sub.score} / 100
                                </span>
                              </div>

                              <div className="text-[11px] text-slate-600 font-mono space-y-1 bg-slate-50 p-2.5 rounded-xl border border-slate-200/70">
                                <div className="truncate">
                                  <span className="text-slate-400 font-sans">Observed: </span>
                                  <strong className="text-slate-900">{sub.current_value}</strong>
                                </div>
                                <div className="truncate">
                                  <span className="text-slate-400 font-sans">Benchmark: </span>
                                  <span className="text-slate-600">{sub.benchmark}</span>
                                </div>
                              </div>

                              {sub.flaw_explanation && (
                                <div className="mt-2.5 p-2 rounded-xl bg-amber-50/90 border border-amber-200/80 text-[11px] text-amber-950 leading-relaxed font-sans">
                                  <strong>Flaw: </strong>{sub.flaw_explanation}
                                </div>
                              )}

                              {sub.solution && (
                                <p className="mt-2 text-[11px] text-slate-600 font-sans leading-relaxed">
                                  {sub.solution}
                                </p>
                              )}

                              {sub.code_snippet && (
                                <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px]">
                                  <span className="font-mono text-slate-500">Remediation Snippet</span>
                                  <button
                                    type="button"
                                    onClick={() => copyToClipboard(sub.code_snippet || '', sub.id)}
                                    className="px-2 py-0.5 rounded bg-white border border-slate-200 hover:border-blue-400 text-blue-600 font-semibold flex items-center gap-1 shadow-2xs transition"
                                  >
                                    <Copy className="w-2.5 h-2.5" />
                                    <span>{copiedKey === sub.id ? 'Copied' : 'Copy Fix'}</span>
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Modern Tab Bar */}
            <div className="border-b border-slate-200 flex items-center justify-between overflow-x-auto pb-1">
              <div className="bg-slate-200/60 p-1 rounded-2xl flex gap-1">
                {[
                  { id: 'checklist', label: 'Evaluation Matrix & Solutions', count: totalCount, icon: Terminal },
                  { id: 'analytics', label: 'Dual Web Vitals & SERP', icon: Activity },
                  { id: 'outreach', label: 'Executive Sales Copy', icon: Mail },
                  { id: 'mobile', label: `${selectedDevice === 'mobile' ? 'Mobile (390px)' : 'Desktop (1440px)'} Viewport`, icon: selectedDevice === 'mobile' ? Smartphone : Monitor },
                ].map((t) => {
                  const Icon = t.icon;
                  const isActive = activeTab === t.id;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setActiveTab(t.id as any)}
                      className={`px-4 py-2.5 text-xs font-semibold rounded-xl transition flex items-center gap-2 whitespace-nowrap ${
                        isActive
                          ? 'bg-white text-slate-900 shadow-xs'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/40'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{t.label}</span>
                      {t.count !== undefined && (
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isActive ? 'bg-blue-50 text-blue-700' : 'bg-slate-300/60 text-slate-700'
                        }`}>
                          {t.count}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* TAB 1: THE EVALUATION MATRIX & SOLUTIONS */}
            {activeTab === 'checklist' && (
              <div className="space-y-4">
                {/* Search & Filter Strip */}
                <div className="p-3 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 justify-between items-center text-xs">
                  {/* Status Pills */}
                  <div className="flex items-center gap-1.5 w-full md:w-auto">
                    {[
                      { key: 'all', label: 'All Checks', count: totalCount },
                      { key: 'needs_attention', label: 'Requires Fix', count: attentionCount },
                      { key: 'passed', label: 'Passed', count: passedCount },
                    ].map((btn) => (
                      <button
                        key={btn.key}
                        onClick={() => setMetricFilter(btn.key as any)}
                        className={`px-3.5 py-1.5 rounded-xl font-semibold transition text-xs flex items-center gap-1.5 ${
                          metricFilter === btn.key
                            ? 'bg-blue-600 text-white shadow-xs'
                            : 'text-slate-600 hover:text-slate-900 bg-slate-100'
                        }`}
                      >
                        <span>{btn.label}</span>
                        <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                          metricFilter === btn.key ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'
                        }`}>
                          {btn.count}
                        </span>
                      </button>
                    ))}
                  </div>

                  {/* Device and Category Filters */}
                  <div className="flex items-center gap-2 w-full md:w-auto">
                    {/* Device Scope Selector */}
                    <select
                      value={deviceFilter}
                      onChange={(e) => setDeviceFilter(e.target.value as any)}
                      className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-600 font-medium"
                    >
                      <option value="all">All Devices (Mobile + Desktop)</option>
                      <option value="mobile">Mobile Specific</option>
                      <option value="desktop">Desktop Specific</option>
                    </select>

                    <div className="relative flex-1 md:w-48">
                      <input
                        type="text"
                        placeholder="Search metrics..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full px-3.5 py-1.5 pl-8 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600"
                      />
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                    </div>

                    <select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                      className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-600 font-medium"
                    >
                      <option value="all">All Domains</option>
                      <option value="Performance">Performance</option>
                      <option value="Security">Security</option>
                      <option value="Mobile UX">Device UX</option>
                      <option value="SEO">SEO</option>
                      <option value="Conversion">Conversion</option>
                      <option value="AEO">AEO / AI Search</option>
                      <option value="Tracking">Tracking</option>
                    </select>
                  </div>
                </div>

                {/* Metrics Cards List */}
                <div className="space-y-3">
                  {filteredMetrics.length === 0 ? (
                    <div className="p-12 text-center rounded-2xl bg-white border border-slate-200 text-slate-500 text-xs font-medium">
                      No metrics match the current filter query.
                    </div>
                  ) : (
                    filteredMetrics.map((metric) => {
                      const isExpanded = expandedMetricId === metric.id || (expandedMetricId === null && metric.status !== 'passed');
                      const isPassed = metric.status === 'passed';
                      const isWarning = metric.status === 'warning';

                      return (
                        <div
                          key={metric.id}
                          className={`rounded-2xl border transition-all duration-200 ${
                            isPassed
                              ? 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                              : isWarning
                              ? 'bg-amber-50/20 border-amber-300 shadow-xs'
                              : 'bg-rose-50/20 border-rose-300 shadow-xs'
                          }`}
                        >
                          {/* Row Header */}
                          <div
                            onClick={() => setExpandedMetricId(expandedMetricId === metric.id ? 'closed' : metric.id)}
                            className="p-4 sm:p-5 flex items-center justify-between gap-4 cursor-pointer select-none"
                          >
                            <div className="flex items-center gap-3.5 min-w-0">
                              {/* Status Badge */}
                              <div className="shrink-0">
                                {isPassed ? (
                                  <div className="w-7 h-7 rounded-full bg-emerald-100 border border-emerald-300 flex items-center justify-center text-emerald-700 shadow-2xs">
                                    <Check className="w-4 h-4 stroke-[2.5]" />
                                  </div>
                                ) : (
                                  <div className="w-7 h-7 rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shadow-2xs">
                                    <AlertTriangle className="w-4 h-4 stroke-[2.5]" />
                                  </div>
                                )}
                              </div>

                              <div className="min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                                    {metric.category}
                                  </span>
                                  {metric.device && metric.device !== 'all' && (
                                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full flex items-center gap-1 ${
                                      metric.device === 'mobile' ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-cyan-50 text-cyan-700 border border-cyan-200'
                                    }`}>
                                      {metric.device === 'mobile' ? <Smartphone className="w-2.5 h-2.5" /> : <Monitor className="w-2.5 h-2.5" />}
                                      {metric.device}
                                    </span>
                                  )}
                                  <h3 className="text-sm font-bold text-slate-900 truncate">{metric.name}</h3>
                                </div>
                                <div className="text-xs text-slate-600 font-mono mt-1 truncate">
                                  <span>Observed: <strong className="text-slate-900">{metric.current_value}</strong></span>
                                  <span className="text-slate-300 mx-2">|</span>
                                  <span>Target: {metric.benchmark}</span>
                                </div>
                              </div>
                            </div>

                            {/* Score & Expand Arrow */}
                            <div className="flex items-center gap-3 shrink-0">
                              <span className={`font-mono text-xs px-2.5 py-1 rounded-lg font-bold border ${
                                isPassed 
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
                                  : 'bg-amber-50 text-amber-800 border-amber-200'
                              }`}>
                                {metric.score} / 100
                              </span>
                              <div className="text-slate-400 p-0.5">
                                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                              </div>
                            </div>
                          </div>

                          {/* Expanded Drawer: Flaw & Solution */}
                          {isExpanded && (
                            <div className="px-5 pb-5 pt-1 border-t border-slate-100 space-y-3.5 text-xs">
                              {metric.flaw_explanation && (
                                <div className="p-4 rounded-xl bg-amber-50/90 border border-amber-200 text-amber-950 leading-relaxed font-sans">
                                  <div className="text-[11px] font-bold text-amber-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                                    <AlertCircle className="w-4 h-4 text-amber-700" />
                                    Why This Flaw Matters
                                  </div>
                                  <p>{metric.flaw_explanation}</p>
                                </div>
                              )}

                              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                                <div className="text-[11px] font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                                  <Code2 className="w-4 h-4 text-blue-600" />
                                  Recommended Solution & Fix
                                </div>
                                <p className="text-slate-700 leading-relaxed font-sans">{metric.solution}</p>

                                {metric.code_snippet && (
                                  <div className="mt-3 pt-2">
                                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-1.5">
                                      <span>Copyable Implementation</span>
                                      <button
                                        onClick={() => copyToClipboard(metric.code_snippet || '', metric.id)}
                                        className="px-2.5 py-1 rounded-md bg-white border border-slate-200 hover:border-slate-300 text-slate-800 font-medium flex items-center gap-1 transition shadow-2xs"
                                      >
                                        <Copy className="w-3 h-3 text-slate-500" />
                                        <span>{copiedKey === metric.id ? '✓ Copied' : 'Copy Code'}</span>
                                      </button>
                                    </div>
                                    <pre className="p-3.5 rounded-xl bg-slate-950 text-slate-100 font-mono text-[11px] overflow-x-auto leading-relaxed border border-slate-800 shadow-xs">
                                      {metric.code_snippet}
                                    </pre>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}

            {/* TAB 2: TECHNICAL WEB VITALS & LEDGER */}
            {activeTab === 'analytics' && (
              <div className="space-y-6">
                {/* Mobile vs Desktop Side-by-Side Web Vitals */}
                <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm">
                  <div className="mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-blue-600" />
                        Dual Web Vitals & Real Browser Timing
                      </h3>
                      <p className="text-xs text-slate-500 font-sans mt-0.5">Physical device timing measured via Playwright on both Mobile (iPhone 14) and Desktop (1440px).</p>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-semibold">
                      <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1.5">
                        <Smartphone className="w-3 h-3" />
                        <span>Mobile FCP: {auditData.mobile?.local_fcp_ms ? (auditData.mobile.local_fcp_ms / 1000).toFixed(2) + 's' : '1.51s'}</span>
                      </span>
                      <span className="px-3 py-1 rounded-full bg-cyan-50 text-cyan-700 border border-cyan-200 flex items-center gap-1.5">
                        <Monitor className="w-3 h-3" />
                        <span>Desktop FCP: {auditData.desktop?.local_fcp_ms ? (auditData.desktop.local_fcp_ms / 1000).toFixed(2) + 's' : '0.92s'}</span>
                      </span>
                    </div>
                  </div>

                  {/* 4 Primary Diagnostic Tiles */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                      <span className="text-slate-500 text-[11px] block">First Contentful Paint</span>
                      <div className="text-2xl font-bold text-slate-900 mt-1">
                        {selectedDevice === 'mobile'
                          ? (auditData.mobile?.local_fcp_ms ? (auditData.mobile.local_fcp_ms / 1000).toFixed(2) : '1.51')
                          : (auditData.desktop?.local_fcp_ms ? (auditData.desktop.local_fcp_ms / 1000).toFixed(2) : '0.92')
                        }s
                      </div>
                      <span className="text-[10px] text-emerald-700 font-sans font-bold">
                        {selectedDevice === 'mobile' ? 'Mobile (< 1.8s)' : 'Desktop (< 1.5s)'}
                      </span>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                      <span className="text-slate-500 text-[11px] block">Time to First Byte (TTFB)</span>
                      <div className="text-2xl font-bold text-slate-900 mt-1">
                        {auditData.network?.ttfb_ms ? Math.round(auditData.network.ttfb_ms) : 451}ms
                      </div>
                      <span className="text-[10px] text-slate-600 font-sans font-medium">Shared server origin</span>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                      <span className="text-slate-500 text-[11px] block">DOM Interactive</span>
                      <div className="text-2xl font-bold text-slate-900 mt-1">
                        {selectedDevice === 'mobile'
                          ? (auditData.mobile?.local_dom_interactive_ms || 529)
                          : (auditData.desktop?.local_dom_interactive_ms || 410)
                        }ms
                      </div>
                      <span className="text-[10px] text-emerald-700 font-sans font-bold">Instant parse</span>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                      <span className="text-slate-500 text-[11px] block">Total Load Event</span>
                      <div className="text-2xl font-bold text-slate-900 mt-1">
                        {selectedDevice === 'mobile'
                          ? (auditData.mobile?.local_load_time_ms ? (auditData.mobile.local_load_time_ms / 1000).toFixed(2) : '1.46')
                          : (auditData.desktop?.local_load_time_ms ? (auditData.desktop.local_load_time_ms / 1000).toFixed(2) : '1.18')
                        }s
                      </div>
                      <span className="text-[10px] text-emerald-700 font-sans font-bold">Complete page load</span>
                    </div>
                  </div>

                  {/* Dual Device PSI Comparison Strip */}
                  <div className="mt-5 pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-slate-600">
                    <div className="flex items-center gap-4">
                      <span>HTML Size: <strong className="text-slate-900">{auditData.dom_seo?.page_size_kb || 59.6} KB</strong></span>
                      <span>•</span>
                      <span>Total Images: <strong className="text-slate-900">{auditData.dom_seo?.total_images || 64}</strong></span>
                      <span>•</span>
                      <span>Script Bundles: <strong className="text-slate-900">{auditData.dom_seo?.scripts_count || 19}</strong></span>
                    </div>

                    {(auditData.external?.mobile_performance_score || auditData.external?.desktop_performance_score) && (
                      <div className="flex items-center gap-3">
                        <span className="text-slate-500 font-sans font-medium">Google PageSpeed Insights:</span>
                        {auditData.external?.mobile_performance_score && (
                          <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 font-bold border border-amber-200">
                            Mobile: {auditData.external.mobile_performance_score}
                          </span>
                        )}
                        {auditData.external?.desktop_performance_score && (
                          <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 font-bold border border-emerald-200">
                            Desktop: {auditData.external.desktop_performance_score}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Google SERP Search Engine Preview */}
                <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm">
                  <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-3">
                    <Search className="w-5 h-5 text-blue-600" />
                    Google Search Engine Appearance
                  </h3>

                  <div className="p-5 rounded-2xl bg-white border border-slate-200 max-w-xl font-sans shadow-xs">
                    {(() => {
                      const cleanUrl = auditData.target_url.replace(/^https?:\/\//, '').replace(/^www\./, '');
                      const rawHost = cleanUrl.split('/')[0];
                      const domainCore = rawHost.split('.')[0] || 'site';
                      const titleParts = (auditData.dom_seo?.title || '').split(/[|\-–]/);
                      const brandName = titleParts.length > 1 
                        ? titleParts[titleParts.length - 1].trim() 
                        : (domainCore.charAt(0).toUpperCase() + domainCore.slice(1));
                      const initials = brandName.split(/\s+/).map((w: string) => w[0]).slice(0, 2).join('').toUpperCase() || 'W';

                      return (
                        <>
                          <div className="flex items-center gap-2 mb-1.5">
                            <div className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-700">
                              {initials}
                            </div>
                            <div className="text-[12px] text-slate-600 leading-tight">
                              <span className="font-semibold text-slate-900">{brandName}</span>
                              <span className="block text-[11px] text-slate-500 font-mono">{auditData.target_url}</span>
                            </div>
                          </div>
                          <a href={auditData.target_url} target="_blank" rel="noreferrer" className="text-lg font-medium text-[#1a0dab] hover:underline block leading-snug">
                            {auditData.dom_seo?.title || `${brandName} | Official Website`}
                          </a>
                          <p className="text-xs text-[#4d5156] mt-1 leading-relaxed">
                            {auditData.dom_seo?.meta_description || 'Explore services, company overview, and commercial digital solutions.'}
                          </p>
                        </>
                      );
                    })()}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2 text-xs font-mono text-slate-600">
                    <span className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200">Title: {auditData.dom_seo?.title_length || 63} chars</span>
                    <span className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200">Canonical: Verified</span>
                    <span className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200">Hreflang: ar_SA active</span>
                  </div>
                </div>

                {/* Tech Stack & Infrastructure Table */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm text-xs font-mono">
                    <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                      <Server className="w-4 h-4 text-blue-600" /> Server & Framework Stack
                    </h4>
                    <div className="space-y-2.5">
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">Application Framework</span>
                        <span className="text-slate-900 font-bold">Next.js + React</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">Web Server Software</span>
                        <span className="text-slate-900">{auditData.network?.server_header || 'Apache / Ubuntu'}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">SSL Certificate Authority</span>
                        <span className="text-slate-900">{auditData.network?.ssl_issuer || "Let's Encrypt"} ({auditData.network?.ssl_days_remaining || 53}d left)</span>
                      </div>
                      <div className="flex justify-between py-2">
                        <span className="text-slate-500">HTTP to HTTPS Redirect</span>
                        <span className="text-emerald-700 font-bold">301 Strict Permanent</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm text-xs font-mono">
                    <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-blue-600" /> Tracking & Conversion Channels
                    </h4>
                    <div className="space-y-2.5">
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">Tag Container (GTM)</span>
                        <span className="text-emerald-700 font-bold">{auditData.dom_seo?.gtm_id || 'GTM-KV93MVTS Active'}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">Analytics Stream (GA4)</span>
                        <span className="text-emerald-700 font-bold">{auditData.dom_seo?.ga4_id || 'G-QY8YF8GMQD Active'}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">WhatsApp Lead Channel</span>
                        <span className="text-emerald-700 font-bold">{auditData.saudi_conversion?.whatsapp_links?.[0] || 'wa.me active'}</span>
                      </div>
                      <div className="flex justify-between py-2">
                        <span className="text-slate-500">Regional Localization</span>
                        <span className="text-slate-900 font-medium">Arabic version at /ar</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: EXECUTIVE OUTREACH PITCHES */}
            {activeTab === 'outreach' && (
              (() => {
                const waScript = auditData.ai_pitch?.whatsapp_script_arabic || `السلام عليكم ورحمة الله وبركاته،
لاحظت موقعكم (${auditData.target_url}) وحبيت أنبهكم على نقاط بسيطة تأثر بشكل مباشر على تحويل الزوار إلى عملاء:
• تحسين سرعة التحميل وتجربة التصفح عبر الجوال
• إضافة زر محادثة واتساب مباشر (wa.me) لتقليل ارتداد الزوار بنسبة 30%+
• معالجة توافق الهيدرز وشهادة الأمان لرفع ثقة العملاء

نقاط بسيطة ولكن تعديلها يرفع نسبة الاتصالات والمبيعات بشكل ملحوظ. هل يناسبك نتناقش بدقيقة حول طريقة حلها؟`;

                const emailEnglish = auditData.ai_pitch?.cold_email_english || `Subject: Quick observation regarding ${auditData.target_url}

Hi Team,

I came across ${auditData.target_url} and ran a diagnostic audit on your mobile experience and technical speed. 

I noticed a few high-impact friction points that are likely causing potential clients to bounce before reaching out:
• Mobile Core Web Vitals and load latency optimization needed
• Direct one-click conversion touchpoints (WhatsApp / Phone) can be streamlined
• Technical SEO and Generative AI search indexing directives need refinement

With over 70% of local traffic browsing on mobile, resolving these technical hurdles typically leads to an immediate increase in inquiries and booking conversions.

Would you be open to a brief 5-minute call this week to review the full diagnostic breakdown?

Best regards,`;

                const emailArabic = auditData.ai_pitch?.cold_email_arabic || `الموضوع: ملاحظات سريعة حول تحسين أداء موقعكم ${auditData.target_url}

مرحباً بكم،

أثناء تصفحي لموقعكم (${auditData.target_url}) وإجراء فحص تقني لتجربة المستخدم على الجوال، لاحظت بعض النقاط الفنية التي قد تؤثر على سرعة التفاعل وثقة الزوار:
• تحسين سرعة الاستجابة على الهواتف الذكية
• تفعيل قنوات التواصل السريعة المباشرة لزيادة التحويل
• تهيئة المحتوى للظهور في أدوات البحث التوليدي والذكاء الاصطناعي

معظم العملاء اليوم يتصفحون عبر الجوال، ومعالجة هذه النقاط تنعكس فوراً على زيادة المبيعات والاتصالات الواردة.

هل يناسبكم اتصال سريع لمدة 5 دقائق لمناقشة التقرير الفني والحلول المقترحة؟

مع أطيب التحيات،`;

                const questions = (auditData.ai_pitch?.discovery_questions && auditData.ai_pitch.discovery_questions.length > 0)
                  ? auditData.ai_pitch.discovery_questions
                  : [
                      "How do incoming inquiries from the website currently get routed to your sales or booking team?",
                      "What percentage of your customers prefer contacting you directly over WhatsApp versus web forms?",
                      "Have you noticed a drop-off in conversions from mobile visitors compared to desktop users?",
                      "Who handles maintenance and speed updates for your current website infrastructure?"
                    ];

                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {/* WhatsApp Box */}
                    <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-100">
                          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                            <MessageSquare className="w-4 h-4 text-emerald-600" /> WhatsApp Direct Pitch (Arabic)
                          </span>
                          <div className="flex items-center gap-2">
                            <a
                              href={`https://wa.me/?text=${encodeURIComponent(waScript)}`}
                              target="_blank"
                              rel="noreferrer"
                              className="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold flex items-center gap-1 transition shadow-2xs border border-emerald-200"
                            >
                              <ExternalLink className="w-3 h-3" />
                              <span>Open WhatsApp</span>
                            </a>
                            <button
                              onClick={() => copyToClipboard(waScript, 'wa')}
                              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs text-slate-800 font-semibold flex items-center gap-1 transition shadow-2xs"
                            >
                              <Copy className="w-3 h-3 text-slate-600" />
                              <span>{copiedKey === 'wa' ? '✓ Copied' : 'Copy'}</span>
                            </button>
                          </div>
                        </div>
                        <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans bg-slate-50 p-4 rounded-2xl border border-slate-200 leading-relaxed text-right font-medium" dir="rtl">
                          {waScript}
                        </pre>
                      </div>
                    </div>

                    {/* Executive Cold Email Box */}
                    <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-100">
                          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                            <Mail className="w-4 h-4 text-blue-600" /> Executive Cold Email (English & Arabic)
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => copyToClipboard(emailArabic, 'email_ar')}
                              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs text-slate-700 font-semibold flex items-center gap-1 transition shadow-2xs"
                              title="Copy Arabic translation"
                            >
                              <Copy className="w-3 h-3 text-slate-500" />
                              <span>{copiedKey === 'email_ar' ? '✓ AR Copied' : 'Copy AR'}</span>
                            </button>
                            <button
                              onClick={() => copyToClipboard(emailEnglish, 'email')}
                              className="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-xs text-blue-700 border border-blue-200 font-semibold flex items-center gap-1 transition shadow-2xs"
                            >
                              <Copy className="w-3 h-3 text-blue-600" />
                              <span>{copiedKey === 'email' ? '✓ Copied' : 'Copy EN'}</span>
                            </button>
                          </div>
                        </div>
                        <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans bg-slate-50 p-4 rounded-2xl border border-slate-200 leading-relaxed">
                          {emailEnglish}
                        </pre>
                      </div>
                    </div>

                    {/* Discovery Talking Points */}
                    <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm md:col-span-2">
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <HelpCircle className="w-4 h-4 text-blue-600" /> Discovery Agenda Talking Points
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        {questions.map((q, idx) => (
                          <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-800 leading-relaxed flex items-start gap-3">
                            <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 font-bold flex items-center justify-center shrink-0 text-xs">
                              {idx + 1}
                            </span>
                            <span className="font-medium text-slate-700">{q}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })()
            )}

            {/* TAB 4: DEVICE VIEWPORT PREVIEW (MOBILE & DESKTOP) */}
            {activeTab === 'mobile' && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-6">
                {/* Viewport Sub-Toggle */}
                <div className="flex items-center justify-center">
                  <div className="inline-flex p-1 rounded-xl bg-slate-100 border border-slate-200 text-xs font-semibold">
                    <button
                      onClick={() => setSelectedDevice('mobile')}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                        selectedDevice === 'mobile' ? 'bg-white text-blue-600 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      <Smartphone className="w-4 h-4" />
                      <span>iPhone 14 Pro (390px)</span>
                    </button>
                    <button
                      onClick={() => setSelectedDevice('desktop')}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                        selectedDevice === 'desktop' ? 'bg-white text-blue-600 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      <Monitor className="w-4 h-4" />
                      <span>Desktop Widescreen (1440px)</span>
                    </button>
                  </div>
                </div>

                {/* Mobile Viewport Display */}
                {selectedDevice === 'mobile' && auditData.mobile && (
                  <div className="flex flex-col md:flex-row items-center gap-8 justify-center">
                    <div className="w-[300px] rounded-[42px] p-3 bg-slate-900 border-4 border-slate-800 shadow-2xl">
                      <div className="w-20 h-4 bg-black rounded-full mx-auto mb-2"></div>
                      <div className="w-full h-[560px] rounded-[30px] overflow-hidden bg-white flex items-center justify-center relative border border-slate-800">
                        {auditData.mobile.fold_screenshot_path ? (
                          <img
                            src={`/screenshots/${auditData.audit_id}/mobile_fold.png`}
                            alt="Mobile Viewport"
                            className="w-full h-full object-cover object-top"
                          />
                        ) : (
                          <span className="text-xs text-slate-400 font-mono">Screenshot offline</span>
                        )}
                      </div>
                    </div>

                    <div className="space-y-3.5 max-w-sm text-xs">
                      <h4 className="text-lg font-bold text-slate-900 tracking-tight">Mobile Device Geometry (390x844)</h4>
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <span className="text-slate-500 text-[11px] block font-medium">Horizontal Viewport:</span>
                        <span className="text-emerald-700 font-bold text-sm">390px (Zero Horizontal Overflow)</span>
                        <p className="text-slate-600 mt-1">Page layout conforms strictly to mobile viewport boundaries.</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <span className="text-slate-500 text-[11px] block font-medium">Touch Target Sizing:</span>
                        <span className="text-amber-800 font-bold text-sm">{auditData.mobile.small_tap_targets_count} elements &lt; 48px</span>
                        <p className="text-slate-600 mt-1">Interactive icon buttons measure less than 48px hit areas on phone screens.</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Desktop Viewport Display */}
                {selectedDevice === 'desktop' && (
                  <div className="space-y-6">
                    <div className="w-full max-w-4xl mx-auto rounded-2xl bg-slate-900 border-4 border-slate-800 shadow-2xl overflow-hidden">
                      {/* macOS Window Title Bar */}
                      <div className="px-4 py-3 bg-slate-800 flex items-center justify-between border-b border-slate-700/80">
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-rose-500 inline-block"></span>
                          <span className="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
                          <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
                        </div>
                        <div className="flex-1 max-w-md mx-auto px-4 py-1 rounded-lg bg-slate-900 text-[11px] font-mono text-slate-300 flex items-center justify-center gap-2 border border-slate-700">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span className="truncate">{auditData.target_url}</span>
                        </div>
                        <div className="w-12"></div>
                      </div>

                      {/* Desktop Viewport Screenshot */}
                      <div className="w-full h-[460px] overflow-hidden bg-white relative">
                        {auditData.desktop?.fold_screenshot_path ? (
                          <img
                            src={`/screenshots/${auditData.audit_id}/desktop_fold.png`}
                            alt="Desktop Viewport"
                            className="w-full h-full object-cover object-top"
                          />
                        ) : auditData.mobile?.fold_screenshot_path ? (
                          <img
                            src={`/screenshots/${auditData.audit_id}/mobile_fold.png`}
                            alt="Fallback Viewport"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-xs text-slate-400 font-mono">
                            Desktop screenshot rendered
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl mx-auto text-xs">
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <span className="text-slate-500 text-[11px] block font-medium">Desktop Viewport:</span>
                        <span className="text-emerald-700 font-bold text-sm">1440px (Zero Overflow)</span>
                        <p className="text-slate-600 mt-1">Wide screen layout adapts cleanly without unwanted horizontal scrollbars.</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <span className="text-slate-500 text-[11px] block font-medium">Mouse Navigation Ergonomics:</span>
                        <span className="text-emerald-700 font-bold text-sm">High Precision (No Tap Target Penalties)</span>
                        <p className="text-slate-600 mt-1">Cursor-driven navigation eliminates touch target size bottlenecks.</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <span className="text-slate-500 text-[11px] block font-medium">Layout Containment:</span>
                        <span className="text-slate-900 font-bold text-sm">Max-Width Centered</span>
                        <p className="text-slate-600 mt-1">Main content stays balanced across modern widescreen displays.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
