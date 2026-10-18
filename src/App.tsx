import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import {
  Bot,
  Vote,
  Bell,
  Shield,
  Clock,
  Code2,
  Copy,
  Check,
  Terminal,
  ChevronDown,
  Zap,
  RefreshCw,
  Target,
  Users,
  Github,
  ArrowRight,
  Sparkles,
  Server,
  MessageSquare,
  Settings,
  Eye,
  Palette,
} from 'lucide-react';
import { mainBotCode, requirementsTxt, envExample, setupInstructions } from './data/botCode';

// ─── Constants ───────────────────────────────────────────────────────────────

const VOTE_GOAL = 250;

// ─── Utility Functions ───────────────────────────────────────────────────────

function formatRelativeTime(seconds: number): string {
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function formatCountdown(elapsedSeconds: number): string {
  const SCRAPE_INTERVAL = 180;
  const remaining = Math.max(0, SCRAPE_INTERVAL - (elapsedSeconds % SCRAPE_INTERVAL));
  if (remaining < 60) return `${remaining}s`;
  const minutes = Math.floor(remaining / 60);
  const secs = remaining % 60;
  return `${minutes}m ${secs}s`;
}

// ─── Components ──────────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white text-xs font-medium transition-all border border-white/10"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}

function CodeBlock({ code, language = 'python' }: { code: string; language?: string }) {
  return (
    <div className="relative group rounded-xl overflow-hidden border border-white/[0.06] bg-[#0c0c0e]">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
          </div>
          <span className="text-[11px] text-gray-500 font-mono uppercase ml-2">{language}</span>
        </div>
        <CopyButton text={code} />
      </div>
      <pre className="p-4 overflow-x-auto text-[13px] leading-[1.7] max-h-[500px] overflow-y-auto">
        <code className="text-gray-400 font-mono whitespace-pre">{code}</code>
      </pre>
    </div>
  );
}

// ─── Navigation ──────────────────────────────────────────────────────────────

function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#09090b]/80 backdrop-blur-xl border-b border-white/[0.06]' : ''
      }`}
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
            <Bot size={16} className="text-black" />
          </div>
          <span className="font-bold text-white text-sm">VoteParty Bot</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
          <a href="#tracker" className="text-sm text-gray-400 hover:text-white transition-colors">Live Demo</a>
          <a href="#code" className="text-sm text-gray-400 hover:text-white transition-colors">Source Code</a>
          <a href="#setup" className="text-sm text-gray-400 hover:text-white transition-colors">Setup</a>
        </div>
        <a
          href="#code"
          className="px-4 py-2 rounded-lg bg-white text-black text-sm font-semibold hover:bg-gray-200 transition-colors"
        >
          Get Started
        </a>
      </div>
    </motion.nav>
  );
}

// ─── Hero Section ────────────────────────────────────────────────────────────

function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-yellow-500/[0.07] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/[0.05] rounded-full blur-[128px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/[0.03] rounded-full blur-[128px]" />
      </div>
      
      {/* Grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative max-w-5xl mx-auto px-6 text-center pt-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-sm font-medium mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Production Ready • Python 3.10+
          </motion.div>

          {/* Main heading */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-white tracking-tight leading-[0.9] mb-6">
            <span className="block">Vote Party</span>
            <span className="block mt-2 bg-gradient-to-r from-yellow-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
              Tracker Bot
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
            A production-ready Discord bot that auto-scrapes vote counts, manages
            vote party cycles, and notifies your community — all in a single elegant embed.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap justify-center gap-4 mb-16">
            <a
              href="#code"
              className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white text-black font-semibold text-sm hover:bg-gray-100 transition-all"
            >
              <Code2 size={16} />
              View Source Code
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </a>
            <a
              href="#setup"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white/[0.06] text-white font-semibold text-sm border border-white/[0.1] hover:bg-white/[0.1] transition-all"
            >
              <Terminal size={16} />
              Setup Guide
            </a>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto">
            {[
              { label: 'Vote Goal', value: '250', icon: Target },
              { label: 'Scrape Rate', value: '3 min', icon: Clock },
              { label: 'Vote Sites', value: '3', icon: Vote },
              { label: 'Ping At', value: '≤30', icon: Bell },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="relative p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] group hover:bg-white/[0.05] transition-all"
              >
                <stat.icon size={16} className="text-gray-500 mb-2 mx-auto" />
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-xs text-gray-500 mt-0.5">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <ChevronDown size={20} className="text-gray-600" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── Features Section ────────────────────────────────────────────────────────

function Features() {
  const features = [
    {
      icon: RefreshCw,
      title: 'Auto-Scraping Engine',
      description: 'Scrapes vote counts from 3 sites every 3 minutes with multiple selector strategies and regex fallbacks for reliability.',
      gradient: 'from-yellow-500/20 to-amber-500/20',
      iconColor: 'text-yellow-400',
    },
    {
      icon: Target,
      title: 'Smart Cycle Detection',
      description: 'Automatically detects when 250 votes are reached, triggers the party, and resets for the next cycle.',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      iconColor: 'text-blue-400',
    },
    {
      icon: Bell,
      title: 'Role Notifications',
      description: 'Pings the VP role when remaining votes drop to 30 or below. Members toggle notifications with a persistent button.',
      gradient: 'from-red-500/20 to-rose-500/20',
      iconColor: 'text-red-400',
    },
    {
      icon: Shield,
      title: 'Admin Slash Commands',
      description: 'Full command suite: setup tracker, set remaining votes, reset baseline, force updates, and more.',
      gradient: 'from-emerald-500/20 to-green-500/20',
      iconColor: 'text-emerald-400',
    },
    {
      icon: Zap,
      title: 'Single Embed Editing',
      description: 'Edits one message in-place — never spams the channel. Survives bot restarts via JSON persistence.',
      gradient: 'from-purple-500/20 to-violet-500/20',
      iconColor: 'text-purple-400',
    },
    {
      icon: Palette,
      title: 'Dynamic Color Coding',
      description: 'Premium embed with accent bar that shifts color based on remaining votes with contextual status messages.',
      gradient: 'from-orange-500/20 to-amber-500/20',
      iconColor: 'text-orange-400',
    },
  ];

  return (
    <section id="features" className="relative py-32">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-xs font-medium mb-4">
            <Sparkles size={12} />
            Features
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Everything you need
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Built with clean modular code, proper error handling, and designed for zero-maintenance operation.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="group relative p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-300"
            >
              <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4`}>
                <feature.icon size={20} className={feature.iconColor} />
              </div>
              <h3 className="text-base font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Live Tracker Demo ───────────────────────────────────────────────────────

function LiveTracker() {
  const [votes, setVotes] = useState(103);
  const [elapsed, setElapsed] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(0);
  const [siteVotes, setSiteVotes] = useState([
    { name: 'Minecraft-MP', votes: 4441, dot: '🟡' },
    { name: 'MinecraftServers.org', votes: 4745, dot: '🔷' },
    { name: 'Minecraft-Server-List', votes: 4495, dot: '🔴' },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
      setLastUpdate((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Simulate vote changes
  useEffect(() => {
    const voteInterval = setInterval(() => {
      setVotes((prev) => {
        const change = Math.random() > 0.5 ? 1 : 0;
        return Math.min(VOTE_GOAL, prev + change);
      });
      setSiteVotes((prev) =>
        prev.map((site) => {
          const delta = Math.floor(Math.random() * 5) - 1;
          return { ...site, votes: Math.max(0, site.votes + delta) };
        })
      );
    }, 8000);
    return () => clearInterval(voteInterval);
  }, []);

  const remaining = VOTE_GOAL - votes;
  const progress = (votes / VOTE_GOAL) * 100;
  const filledBlocks = Math.round((progress / 100) * 10);
  const emptyBlocks = 10 - filledBlocks;
  const progressBar = '🟨'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);

  const getMotivational = () => {
    if (remaining <= 10) return '🔥 Almost there! Party imminent!';
    if (remaining <= 30) return '⚡ Getting close! Notify the server!';
    if (remaining <= 100) return '💪 Good progress! Keep it up!';
    return '🗳️ Vote party in progress';
  };

  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });

  return (
    <section id="tracker" className="relative py-32">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-xs font-medium mb-4">
            <Eye size={12} />
            Live Preview
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            See it in action
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            This is a live simulation of what the tracker embed looks like in your Discord channel.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-lg mx-auto"
        >
          {/* Discord embed mockup */}
          <div className="rounded-2xl bg-[#2b2d31] border border-white/[0.06] overflow-hidden shadow-2xl shadow-black/50">
            {/* Discord message header */}
            <div className="px-4 pt-4 pb-2 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
                <Bot size={18} className="text-black" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">VoteParty Bot</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#5865f2] text-white font-medium">BOT</span>
                </div>
                <span className="text-xs text-gray-500">Today at {timeStr}</span>
              </div>
            </div>

            {/* Embed content */}
            <div className="mx-4 mb-4 rounded-lg overflow-hidden bg-[#1e1f22] border-l-4 border-yellow-400">
              <div className="p-4 font-mono text-[13px] leading-[1.8]">
                {/* Title */}
                <div className="text-white font-bold text-sm mb-1">
                  🇨🇴 Colombia Vote Party
                </div>

                {/* Remaining */}
                <div className="text-gray-300 mb-1">
                  <span className="font-semibold text-white">{remaining}</span> votes remaining
                </div>

                {/* Progress bar */}
                <div className="text-[12px] tracking-wider mb-0.5">
                  {progressBar} <span className="text-gray-400">{progress.toFixed(1)}%</span>
                </div>

                {/* Votes collected */}
                <div className="text-gray-400 text-[12px] mb-2">
                  {votes} / {VOTE_GOAL} votes collected
                </div>

                {/* Motivational */}
                <div className="text-gray-300 text-[12px] mb-3">
                  {getMotivational()}
                </div>

                {/* Divider */}
                <div className="text-gray-600 text-[12px] mb-2 select-none">
                  ━━━━━━━━━━━━━━━━━━━━
                </div>

                {/* Vote Counts header */}
                <div className="text-gray-300 text-[12px] mb-1.5">
                  🗳️ Vote Counts
                </div>

                {/* Site votes */}
                <div className="space-y-0.5 mb-2">
                  {siteVotes.map((site) => (
                    <div key={site.name} className="text-[12px]">
                      <span>{site.dot}</span>{' '}
                      <span className="text-gray-300">{site.name}</span>{' '}
                      <span className="text-gray-500">—</span>{' '}
                      <span className="text-white font-semibold">{site.votes.toLocaleString()}</span>
                    </div>
                  ))}
                </div>

                {/* Vote Now header */}
                <div className="text-yellow-400 text-[12px] font-semibold mb-1">
                  🔗 Vote Now!
                </div>

                {/* Vote links */}
                <div className="space-y-0.5 mb-3">
                  {siteVotes.map((site, i) => (
                    <div key={site.name} className="text-[12px] text-[#00aff4] hover:underline cursor-pointer">
                      {i + 1}. Vote on {site.name}
                    </div>
                  ))}
                </div>

                {/* Divider */}
                <div className="text-gray-600 text-[12px] mb-1 select-none">
                  ━━━━━━━━━━━━━━━━
                </div>

                {/* Footer */}
                <div className="text-gray-500 text-[11px]">
                  Updates every 15s • Today at {timeStr}
                </div>
              </div>
            </div>

            {/* Notification button */}
            <div className="px-4 pb-4">
              <button className="w-full py-2 rounded-lg bg-[#4e5058] hover:bg-[#6d6f78] text-white text-xs font-medium transition-colors flex items-center justify-center gap-2">
                <Bell size={12} />
                Get Notified When Close
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── Source Code Section ─────────────────────────────────────────────────────

function SourceCode() {
  const [activeTab, setActiveTab] = useState<'bot' | 'requirements' | 'env'>('bot');

  const tabs = [
    { id: 'bot' as const, label: 'bot.py', icon: FileCodeIcon },
    { id: 'requirements' as const, label: 'requirements.txt', icon: ListIcon },
    { id: 'env' as const, label: '.env.example', icon: Settings },
  ];

  const getCode = () => {
    switch (activeTab) {
      case 'bot': return mainBotCode;
      case 'requirements': return requirementsTxt;
      case 'env': return envExample;
    }
  };

  const getLanguage = () => {
    switch (activeTab) {
      case 'bot': return 'python';
      case 'requirements': return 'text';
      case 'env': return 'env';
    }
  };

  return (
    <section id="code" className="relative py-32">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-xs font-medium mb-4">
            <Code2 size={12} />
            Source Code
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Clean, documented code
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Production-ready Python code with comprehensive comments, error handling, and modular design.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          {/* Tab bar */}
          <div className="flex gap-1 p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] mb-4 w-fit">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white/[0.08] text-white'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                <tab.icon size={14} />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Code display */}
          <CodeBlock code={getCode()} language={getLanguage()} />
        </motion.div>
      </div>
    </section>
  );
}

function FileCodeIcon({ size }: { size: number }) {
  return <Code2 size={size} />;
}

function ListIcon({ size }: { size: number }) {
  return <Server size={size} />;
}

// ─── Setup Section ───────────────────────────────────────────────────────────

function Setup() {
  const steps = [
    {
      number: '01',
      title: 'Clone & Install',
      description: 'Clone the repository and install Python dependencies.',
      code: 'pip install -r requirements.txt',
    },
    {
      number: '02',
      title: 'Configure Environment',
      description: 'Create a .env file with your Discord bot token and server settings.',
      code: 'cp .env.example .env\n# Edit .env with your values',
    },
    {
      number: '03',
      title: 'Create Discord Bot',
      description: 'Create a bot at discord.com/developers and invite it to your server with appropriate permissions.',
      code: '# Required permissions:\n# - Send Messages\n# - Embed Links\n# - Manage Roles\n# - Use Slash Commands',
    },
    {
      number: '04',
      title: 'Run the Bot',
      description: 'Start the bot and use /setup to initialize the vote tracker in your channel.',
      code: 'python bot.py\n# Then in Discord: /setup',
    },
  ];

  return (
    <section id="setup" className="relative py-32">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-xs font-medium mb-4">
            <Terminal size={12} />
            Setup Guide
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Get started in minutes
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Four simple steps to get your vote party tracker running.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-4">
          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group relative p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl font-black text-white/[0.06] group-hover:text-white/[0.1] transition-colors">
                  {step.number}
                </div>
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-white mb-1">{step.title}</h3>
                  <p className="text-sm text-gray-500 mb-3">{step.description}</p>
                  <pre className="text-xs font-mono text-gray-400 bg-black/40 rounded-lg p-3 border border-white/[0.04]">
                    <code>{step.code}</code>
                  </pre>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Commands reference */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <MessageSquare size={18} className="text-yellow-400" />
            Slash Commands
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {[
              { cmd: '/setup', desc: 'Initialize vote tracker in channel' },
              { cmd: '/setremaining', desc: 'Manually set remaining votes' },
              { cmd: '/reset', desc: 'Reset vote cycle baseline' },
              { cmd: '/forceupdate', desc: 'Force immediate scrape update' },
              { cmd: '/status', desc: 'Show current bot status' },
              { cmd: '/help', desc: 'Show all available commands' },
            ].map((item) => (
              <div key={item.cmd} className="flex items-center gap-3 p-2.5 rounded-lg bg-white/[0.02]">
                <code className="text-xs font-mono text-yellow-400 bg-yellow-400/10 px-2 py-1 rounded">
                  {item.cmd}
                </code>
                <span className="text-xs text-gray-500">{item.desc}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-12">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
              <Bot size={16} className="text-black" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Colombia Vote Party Bot</div>
              <div className="text-xs text-gray-500">DiplomaticaMC • Colombia Nation</div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-xs text-gray-600">Built with Python & discord.py</span>
            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-600">🇨🇴</span>
              <span className="text-xs text-gray-500">Made for Colombia</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ─── Main App ────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <div className="min-h-screen bg-[#09090b] text-white font-[Inter,system-ui,sans-serif]">
      <Navbar />
      <Hero />
      <Features />
      <LiveTracker />
      <SourceCode />
      <Setup />
      <Footer />
    </div>
  );
}
