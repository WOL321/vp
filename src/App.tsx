import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
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
  Sparkles,
  Trophy,
  Globe,
  Timer,
  MessageSquare,
  TrendingUp,
  Award,
} from 'lucide-react';
import { mainBotCode, requirementsTxt, envExample, setupInstructions } from './data/botCode';

// ─── Constants ───────────────────────────────────────────────────────────────

const VOTE_GOAL = 250;

// ─── Utility Functions ───────────────────────────────────────────────────────

function formatCountdown(elapsedSeconds: number): string {
  const SCRAPE_INTERVAL = 15;
  const remaining = Math.max(0, SCRAPE_INTERVAL - (elapsedSeconds % SCRAPE_INTERVAL));
  return `${remaining}s`;
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
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-400 font-medium">v2</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
          <a href="#tracker" className="text-sm text-gray-400 hover:text-white transition-colors">Live Demo</a>
          <a href="#code" className="text-sm text-gray-400 hover:text-white transition-colors">Source Code</a>
          <a href="#setup" className="text-sm text-gray-400 hover:text-white transition-colors">Setup</a>
        </div>
        <a
          href="#setup"
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
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-yellow-500/[0.07] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/[0.05] rounded-full blur-[128px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/[0.03] rounded-full blur-[128px]" />
      </div>
      
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative max-w-5xl mx-auto px-6 text-center pt-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-sm font-medium mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Premium Edition • Python 3.10+ • Modular Architecture
          </motion.div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-white tracking-tight leading-[0.9] mb-6">
            <span className="block">Vote Party</span>
            <span className="block mt-2 bg-gradient-to-r from-yellow-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
              Tracker Bot
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
            A premium Discord bot with self-reporting votes, leaderboards, streaks,
            bilingual support, and a beautiful multi-state embed system.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-16">
            <a
              href="#code"
              className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white text-black font-semibold text-sm hover:bg-gray-100 transition-all"
            >
              <Code2 size={16} />
              View Source Code
            </a>
            <a
              href="#setup"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white/[0.06] text-white font-semibold text-sm border border-white/[0.1] hover:bg-white/[0.1] transition-all"
            >
              <Terminal size={16} />
              Setup Guide
            </a>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto">
            {[
              { label: 'Vote Goal', value: '250', icon: Target },
              { label: 'Scrape Rate', value: '15s', icon: Clock },
              { label: 'Languages', value: 'EN/ES', icon: Globe },
              { label: 'Modules', value: '7', icon: Code2 },
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
      icon: Sparkles,
      title: 'Multi-State Embeds',
      description: '6 distinct visual states: Normal, Momentum, Close, Final Push, Celebration, and Cooldown — each with unique colors and messaging.',
      gradient: 'from-yellow-500/20 to-amber-500/20',
      iconColor: 'text-yellow-400',
    },
    {
      icon: Trophy,
      title: 'Self-Report Votes',
      description: 'Players claim votes with "I Voted!" button. Includes 1hr cooldown, streak tracking, and per-site contribution counting.',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      iconColor: 'text-blue-400',
    },
    {
      icon: Award,
      title: 'Leaderboards & Stats',
      description: 'Cycle and all-time leaderboards. Personal stats with /myvotes. Historical tracking of fastest parties and voting rates.',
      gradient: 'from-purple-500/20 to-violet-500/20',
      iconColor: 'text-purple-400',
    },
    {
      icon: Globe,
      title: 'Bilingual Support',
      description: 'Full English and Spanish translations. Users switch with /language. All embeds, buttons, and messages are localized.',
      gradient: 'from-emerald-500/20 to-green-500/20',
      iconColor: 'text-emerald-400',
    },
    {
      icon: Zap,
      title: 'Premium Buttons',
      description: '5 persistent interactive buttons: I Voted, Get Notified, How to Vote, Remind Me Later, and Leaderboard.',
      gradient: 'from-orange-500/20 to-amber-500/20',
      iconColor: 'text-orange-400',
    },
    {
      icon: Timer,
      title: 'Smart Reminders',
      description: 'DM reminders after 30min. Voting rate calculation. Estimated completion time. Per-site contribution tracking.',
      gradient: 'from-red-500/20 to-rose-500/20',
      iconColor: 'text-red-400',
    },
    {
      icon: Shield,
      title: 'Admin Suite',
      description: 'Full /voteparty command group: setup, setremaining, setbaseline, forceupdate, reset. All with clean error handling.',
      gradient: 'from-indigo-500/20 to-blue-500/20',
      iconColor: 'text-indigo-400',
    },
    {
      icon: TrendingUp,
      title: 'Voting Analytics',
      description: 'Real-time voting rate, estimated completion, cycle duration tracking, and historical party statistics.',
      gradient: 'from-teal-500/20 to-cyan-500/20',
      iconColor: 'text-teal-400',
    },
    {
      icon: Users,
      title: 'Minecraft Linking',
      description: 'Players link their Minecraft IGN with /link. Required for vote claiming. Enables personalized experience.',
      gradient: 'from-pink-500/20 to-rose-500/20',
      iconColor: 'text-pink-400',
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
            Premium Features
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Everything you need
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            A complete rewrite with modular architecture, premium embeds, and engaging social features.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
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
  const [siteVotes, setSiteVotes] = useState([
    { name: 'Minecraft-MP', votes: 4441, emoji: '🟡', contribution: 12 },
    { name: 'MinecraftServers.org', votes: 4745, emoji: '🔵', contribution: 8 },
    { name: 'Minecraft-Server-List', votes: 4495, emoji: '🔴', contribution: 15 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const voteInterval = setInterval(() => {
      setVotes((prev) => {
        const change = Math.random() > 0.5 ? 1 : 0;
        return Math.min(VOTE_GOAL, prev + change);
      });
      setSiteVotes((prev) =>
        prev.map((site) => {
          const delta = Math.floor(Math.random() * 5) - 1;
          const newVotes = Math.max(0, site.votes + delta);
          const newContribution = delta > 0 ? site.contribution + 1 : site.contribution;
          return { ...site, votes: newVotes, contribution: newContribution };
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
            <Zap size={12} />
            Live Preview
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            See it in action
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            A live simulation of the premium tracker embed with interactive buttons.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          {/* Discord embed mockup */}
          <div className="rounded-xl bg-[#313338] border border-white/[0.04] overflow-hidden shadow-2xl shadow-black/50">
            <div className="px-5 pt-5 pb-1 flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot size={18} className="text-black" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[15px] font-semibold text-white">VoteParty Bot</span>
                  <span className="px-1 py-0.5 rounded text-[10px] bg-[#5865f2] text-white font-medium">BOT</span>
                  <span className="text-xs text-gray-500">Today at {timeStr}</span>
                </div>

                {/* Embed */}
                <div className="mt-2 rounded-md overflow-hidden bg-[#2b2d31] border-l-[3px] border-yellow-400">
                  <div className="px-4 py-3">
                    <div className="text-white font-bold text-[15px] mb-2">
                      🇨🇴 Colombia Vote Party
                    </div>

                    <div className="text-[#dbdee1] text-[14px] mb-0.5">
                      <span className="font-semibold text-white">{remaining}</span> votes remaining
                    </div>

                    <div className="text-[13px] tracking-wider mb-0.5 font-sans">
                      {progressBar} <span className="text-[#949ba4]">{progress.toFixed(1)}%</span>
                    </div>

                    <div className="text-[#949ba4] text-[13px] mb-1">
                      {votes} / {VOTE_GOAL} votes collected
                    </div>

                    <div className="text-[#dbdee1] text-[13px] mb-1">
                      {getMotivational()}
                    </div>

                    {/* Rate + estimate */}
                    <div className="text-[#949ba4] text-[12px] mb-2">
                      📈 4.2 votes/hour • 🕐 Est: ~38m
                    </div>

                    <div className="text-[#4e5058] text-[13px] mt-2 mb-1.5 select-none leading-none">
                      ━━━━━━━━━━━━━━━━━━━━
                    </div>

                    <div className="text-[#dbdee1] text-[13px] font-semibold mb-1">
                      🗳️ Vote Counts
                    </div>

                    <div className="space-y-0.5 mb-2">
                      {siteVotes.map((site) => (
                        <div key={site.name} className="text-[13px] leading-relaxed">
                          <span>{site.emoji}</span>{' '}
                          <span className="text-[#dbdee1]">{site.name}</span>{' '}
                          <span className="text-[#6d6f78]">—</span>{' '}
                          <span className="text-white font-semibold">{site.votes.toLocaleString()}</span>
                          {site.contribution > 0 && (
                            <span className="text-emerald-400 text-[11px] ml-1">(+{site.contribution})</span>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="text-[#dbdee1] text-[13px] font-semibold mb-1">
                      🔗 Vote Now!
                    </div>

                    <div className="space-y-0.5 mb-2">
                      {siteVotes.map((site, i) => (
                        <div key={site.name} className="text-[13px] text-[#00a8fc] hover:underline cursor-pointer leading-relaxed">
                          {i + 1}. Vote on {site.name}
                        </div>
                      ))}
                    </div>

                    <div className="text-[#6d6f78] text-[11px] mt-2">
                      Updates every 15s • Today at {timeStr}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive buttons */}
            <div className="px-5 pb-4 pt-1 pl-[72px]">
              <div className="flex flex-wrap gap-2">
                <button className="py-1.5 px-3 rounded-sm bg-[#248046] hover:bg-[#1a6334] text-white text-[13px] font-medium transition-colors">
                  ✅ I Voted!
                </button>
                <button className="py-1.5 px-3 rounded-sm bg-[#5865f2] hover:bg-[#4752c4] text-white text-[13px] font-medium transition-colors">
                  🔔 Get Notified
                </button>
                <button className="py-1.5 px-3 rounded-sm bg-[#4e5058] hover:bg-[#6d6f78] text-white text-[13px] font-medium transition-colors">
                  📖 How to Vote
                </button>
                <button className="py-1.5 px-3 rounded-sm bg-[#4e5058] hover:bg-[#6d6f78] text-white text-[13px] font-medium transition-colors">
                  ⏰ Remind Me
                </button>
                <button className="py-1.5 px-3 rounded-sm bg-[#4e5058] hover:bg-[#6d6f78] text-white text-[13px] font-medium transition-colors">
                  🏆 Leaderboard
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── Source Code Section ─────────────────────────────────────────────────────

function SourceCode() {
  const [activeTab, setActiveTab] = useState<'bot' | 'requirements' | 'env' | 'setup'>('bot');

  const tabs = [
    { id: 'bot' as const, label: 'bot.py' },
    { id: 'requirements' as const, label: 'requirements.txt' },
    { id: 'env' as const, label: '.env.example' },
    { id: 'setup' as const, label: 'Setup Guide' },
  ];

  const getCode = () => {
    switch (activeTab) {
      case 'bot': return mainBotCode;
      case 'requirements': return requirementsTxt;
      case 'env': return envExample;
      case 'setup': return setupInstructions;
    }
  };

  const getLanguage = () => {
    switch (activeTab) {
      case 'bot': return 'python';
      case 'requirements': return 'text';
      case 'env': return 'env';
      case 'setup': return 'markdown';
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
            Modular architecture
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            7 clean modules: bot.py, config.py, scraper.py, data_manager.py, embed_builder.py, views.py, commands.py, i18n.py
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
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
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          <CodeBlock code={getCode()} language={getLanguage()} />
        </motion.div>
      </div>
    </section>
  );
}

// ─── Setup Section ───────────────────────────────────────────────────────────

function Setup() {
  const steps = [
    {
      number: '01',
      title: 'Install Dependencies',
      description: 'Install all required Python packages.',
      code: 'pip install -r requirements.txt',
    },
    {
      number: '02',
      title: 'Configure Environment',
      description: 'Create .env with your Discord bot token.',
      code: 'cp .env.example .env\n# Edit .env with your token',
    },
    {
      number: '03',
      title: 'Create Discord Bot',
      description: 'Set up at discord.com/developers with required intents and permissions.',
      code: '# Required intents:\n# - MESSAGE CONTENT\n# - SERVER MEMBERS\n# Required perms:\n# - Send Messages, Embed Links\n# - Manage Roles, Slash Commands',
    },
    {
      number: '04',
      title: 'Run & Setup',
      description: 'Start the bot and use /voteparty setup to post the tracker.',
      code: 'python bot.py\n# Then in Discord:\n# /voteparty setup',
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
            Quick Setup
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Get started in minutes
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Four simple steps to get your premium vote party tracker running.
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
          className="mt-12 grid md:grid-cols-2 gap-4"
        >
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Users size={18} className="text-yellow-400" />
              User Commands
            </h3>
            <div className="space-y-2">
              {[
                { cmd: '/link <ign>', desc: 'Link your Minecraft username' },
                { cmd: '/myvotes', desc: 'View your personal vote stats' },
                { cmd: '/leaderboard', desc: 'View the vote leaderboard' },
                { cmd: '/stats', desc: 'View vote party statistics' },
                { cmd: '/language', desc: 'Set EN/ES preference' },
              ].map((item) => (
                <div key={item.cmd} className="flex items-center gap-3 p-2 rounded-lg bg-white/[0.02]">
                  <code className="text-xs font-mono text-yellow-400 bg-yellow-400/10 px-2 py-1 rounded">
                    {item.cmd}
                  </code>
                  <span className="text-xs text-gray-500">{item.desc}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Shield size={18} className="text-blue-400" />
              Admin Commands
            </h3>
            <div className="space-y-2">
              {[
                { cmd: '/voteparty setup', desc: 'Post/update tracker embed' },
                { cmd: '/voteparty setremaining', desc: 'Set remaining votes' },
                { cmd: '/voteparty setbaseline', desc: 'Reset cycle baseline' },
                { cmd: '/voteparty forceupdate', desc: 'Force immediate update' },
                { cmd: '/voteparty reset', desc: 'Reset all progress' },
              ].map((item) => (
                <div key={item.cmd} className="flex items-center gap-3 p-2 rounded-lg bg-white/[0.02]">
                  <code className="text-xs font-mono text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                    {item.cmd}
                  </code>
                  <span className="text-xs text-gray-500">{item.desc}</span>
                </div>
              ))}
            </div>
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
              <div className="text-xs text-gray-500">Premium Edition • DiplomaticaMC</div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-xs text-gray-600">Modular Python • discord.py • 7 modules</span>
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
