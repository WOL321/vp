import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
  Ticket,
  Globe,
  Award,
  TrendingUp,
  Gamepad2,
  Music,
  Calendar,
  Map,
  Sword,
  Heart,
  Star,
  Gift,
  Activity,
  Ban,
  FileText,
  Mic,
  Volume2,
  Coins,
  ShoppingBag,
  Briefcase,
  PartyPopper,
  Trophy,
  Flag,
  Scroll,
  Hammer,
  Wrench,
} from 'lucide-react';

// ─── Constants ───────────────────────────────────────────────────────────────

const VOTE_GOAL = 250;

// ─── Components ──────────────────────────────────────────────────────────────

function FeatureCard({ icon: Icon, title, description, color, delay = 0 }: {
  icon: any;
  title: string;
  description: string;
  color: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="group relative p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-300"
    >
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
        <Icon size={24} className="text-white" />
      </div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </motion.div>
  );
}

function DiscordEmbed({ title, description, color, fields = [] }: {
  title: string;
  description: string;
  color: number;
  fields?: Array<{ name: string; value: string }>;
}) {
  return (
    <div className="rounded-lg bg-[#2b2d31] border-l-4 overflow-hidden" style={{ borderColor: `#${color.toString(16).padStart(6, '0')}` }}>
      <div className="p-4">
        <h3 className="text-white font-bold mb-2">{title}</h3>
        <div className="text-gray-300 text-sm whitespace-pre-line mb-3">{description}</div>
        {fields.map((field, i) => (
          <div key={i} className="mb-2">
            <div className="text-white font-semibold text-sm mb-1">{field.name}</div>
            <div className="text-gray-400 text-xs">{field.value}</div>
          </div>
        ))}
      </div>
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
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
            <Bot size={16} className="text-black" />
          </div>
          <span className="font-bold text-white text-sm">Nariño Bot</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-400 font-medium">v1.0</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
          <a href="#vote-party" className="text-sm text-gray-400 hover:text-white transition-colors">Vote Party</a>
          <a href="#nation" className="text-sm text-gray-400 hover:text-white transition-colors">Nation</a>
          <a href="#economy" className="text-sm text-gray-400 hover:text-white transition-colors">Economy</a>
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
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-yellow-500/[0.07] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/[0.05] rounded-full blur-[128px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/[0.03] rounded-full blur-[128px]" />
      </div>
      
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative max-w-6xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-sm font-medium mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Named after Antonio Nariño • Colombian Independence Leader
          </motion.div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-white tracking-tight leading-[0.9] mb-6">
            <span className="block">Nariño Bot</span>
            <span className="block mt-2 bg-gradient-to-r from-yellow-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
              DiplomaticaMC Integration
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
            The ultimate Discord bot for <span className="text-white font-semibold">DiplomaticaMC</span> with deep Towny integration, 
            Gold Standard economy, SiegeWar support, live map & market links, and 25,000+ player community features.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-16">
            <a
              href="#features"
              className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white text-black font-semibold text-sm hover:bg-gray-100 transition-all"
            >
              <Sparkles size={16} />
              Explore All Features
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </a>
            <a
              href="#setup"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white/[0.06] text-white font-semibold text-sm border border-white/[0.1] hover:bg-white/[0.1] transition-all"
            >
              <Terminal size={16} />
              Quick Setup
            </a>
          </div>

          {/* Feature count stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {[
              { label: 'Server Players', value: '25K+', icon: Users, color: 'from-yellow-500/20 to-amber-500/20' },
              { label: 'Discord Members', value: '1.3K', icon: MessageSquare, color: 'from-blue-500/20 to-cyan-500/20' },
              { label: 'Earth Scale', value: '1:450', icon: Globe, color: 'from-green-500/20 to-emerald-500/20' },
              { label: 'Vote Sites', value: '3', icon: Vote, color: 'from-purple-500/20 to-violet-500/20' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="relative p-5 rounded-xl bg-white/[0.03] border border-white/[0.06] group hover:bg-white/[0.05] transition-all"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center mb-3 mx-auto`}>
                  <stat.icon size={20} className="text-white" />
                </div>
                <div className="text-3xl font-black text-white">{stat.value}</div>
                <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
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

// ─── Features Overview ───────────────────────────────────────────────────────

function FeaturesOverview() {
  const features = [
    {
      icon: Vote,
      title: 'Vote Party System',
      description: '99%+ accuracy scraper with triple-layer extraction, 3 votes per cycle limit, leaderboards, and advanced analytics.',
      color: 'from-yellow-500 to-amber-500',
    },
    {
      icon: Users,
      title: 'Welcome Messages',
      description: 'Colombian-themed welcome embeds with auto-detection for new members and links to all features.',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Shield,
      title: 'Role Requests',
      description: 'Button-based system for Citizenship, Ally, and VP Pings with leadership review workflow.',
      color: 'from-purple-500 to-violet-500',
    },
    {
      icon: Ticket,
      title: 'Support Tickets',
      description: 'Private ticket channels with staff assignment, response tracking, and archive system.',
      color: 'from-red-500 to-rose-500',
    },
    {
      icon: Coins,
      title: 'Economy System',
      description: 'Virtual currency (Pesos), daily rewards, work commands, shop, and transaction tracking.',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: Globe,
      title: 'Diplomacy',
      description: 'Alliance tracking, war declarations, peace treaties, and diplomatic relations management.',
      color: 'from-indigo-500 to-blue-500',
    },
    {
      icon: Activity,
      title: 'Activity Tracking',
      description: 'XP system for messages and voice, levels, leaderboards, and inactive member cleanup.',
      color: 'from-orange-500 to-amber-500',
    },
    {
      icon: Ban,
      title: 'Moderation',
      description: 'Auto-mod, warning system, temp mute/ban, mod logs, and comprehensive moderation tools.',
      color: 'from-red-600 to-red-500',
    },
    {
      icon: Calendar,
      title: 'Events System',
      description: 'Giveaways, tournaments, attendance tracking, and event announcements.',
      color: 'from-pink-500 to-rose-500',
    },
    {
      icon: Map,
      title: 'Town Management',
      description: 'Town creation, leaderboards, town-specific channels, and mayor roles.',
      color: 'from-teal-500 to-cyan-500',
    },
    {
      icon: Gamepad2,
      title: 'Minecraft Integration',
      description: 'Server status display, role sync between Discord and MC, player verification.',
      color: 'from-lime-500 to-green-500',
    },
    {
      icon: Trophy,
      title: 'Leaderboards',
      description: 'Multiple leaderboards for votes, activity, economy, and custom categories.',
      color: 'from-yellow-500 to-orange-500',
    },
    {
      icon: Gift,
      title: 'Giveaways',
      description: 'Reaction-based giveaways with winner selection, rerolls, and duration tracking.',
      color: 'from-fuchsia-500 to-pink-500',
    },
    {
      icon: Sword,
      title: 'War System',
      description: 'Declare wars, track battles, manage alliances, and diplomatic relations.',
      color: 'from-red-700 to-red-500',
    },
    {
      icon: Scroll,
      title: 'Custom Commands',
      description: 'Admin-created custom commands with variables and dynamic responses.',
      color: 'from-violet-500 to-purple-500',
    },
    {
      icon: FileText,
      title: 'Logging System',
      description: 'Comprehensive logs for joins, leaves, bans, message edits, and role changes.',
      color: 'from-gray-500 to-slate-500',
    },
    {
      icon: Heart,
      title: 'Birthday Tracking',
      description: 'Track member birthdays, send announcements, and special birthday roles.',
      color: 'from-pink-400 to-rose-400',
    },
    {
      icon: Star,
      title: 'Fun Features',
      description: 'Colombia trivia, fun facts, memes, and interactive entertainment commands.',
      color: 'from-amber-500 to-yellow-500',
    },
  ];

  return (
    <section id="features" className="relative py-32">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-gray-400 text-xs font-medium mb-4">
            <Sparkles size={12} />
            18+ Features
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Everything You Need
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            A complete nation management solution with vote tracking, economy, diplomacy, moderation, and much more.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              color={feature.color}
              delay={i * 0.05}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Vote Party Deep Dive ────────────────────────────────────────────────────

function VotePartySection() {
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
    <section id="vote-party" className="relative py-32 bg-gradient-to-b from-transparent via-yellow-500/[0.02] to-transparent">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-medium mb-4">
            <Vote size={12} />
            Vote Party System
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            99%+ Accuracy Vote Tracking
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Triple-layer extraction with BeautifulSoup, Regex, and Playwright. 4 retry attempts, user-agent rotation, and advanced analytics.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Live Demo */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="max-w-2xl"
          >
            <div className="rounded-xl bg-[#313338] border border-white/[0.04] overflow-hidden shadow-2xl shadow-black/50">
              <div className="px-5 pt-5 pb-1 flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot size={18} className="text-black" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[15px] font-semibold text-white">Nariño</span>
                    <span className="px-1 py-0.5 rounded text-[10px] bg-[#5865f2] text-white font-medium">BOT</span>
                    <span className="text-xs text-gray-500">Today at {timeStr}</span>
                  </div>

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

              <div className="px-5 pb-4 pt-1 pl-[72px]">
                <div className="flex flex-wrap gap-2">
                  <button className="py-1.5 px-3 rounded-sm bg-[#248046] hover:bg-[#1a6334] text-white text-[13px] font-medium transition-colors">
                    ✅ I Voted!
                  </button>
                  <button className="py-1.5 px-3 rounded-sm bg-[#5865f2] hover:bg-[#4752c4] text-white text-[13px] font-medium transition-colors">
                    🔔 Get Notified
                  </button>
                  <button className="py-1.5 px-3 rounded-sm bg-[#4e5058] hover:bg-[#6d6f78] text-white text-[13px] font-medium transition-colors">
                    🏆 Leaderboard
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Features List */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            {[
              { icon: Zap, title: 'Triple-Layer Extraction', desc: 'BeautifulSoup + Regex + Playwright for 99%+ accuracy' },
              { icon: RefreshCw, title: '4 Retry Attempts', desc: 'Exponential backoff (1s → 2s → 4s → 8s)' },
              { icon: Target, title: '3 Votes Per Cycle', desc: 'Prevents farming, resets automatically' },
              { icon: TrendingUp, title: 'Advanced Analytics', desc: 'Voting rate, completion estimates, health tracking' },
              { icon: Award, title: 'Leaderboards', desc: 'Personal stats, cycle rankings, all-time records' },
              { icon: Bell, title: 'Smart Notifications', desc: 'Auto-ping VP role at threshold, DM reminders' },
              { icon: Eye, title: 'Auto-Delete Confirmations', desc: 'Clean chat with 1-second message deletion' },
              { icon: Globe, title: 'Bilingual Support', desc: 'Full EN/ES translations with auto-detection' },
            ].map((feature, i) => (
              <div key={feature.title} className="flex gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] transition-all">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <feature.icon size={20} className="text-yellow-400" />
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-1">{feature.title}</h4>
                  <p className="text-sm text-gray-400">{feature.desc}</p>
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ─── Nation Features ─────────────────────────────────────────────────────────

function NationFeatures() {
  return (
    <section id="nation" className="relative py-32">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-4">
            <Flag size={12} />
            Nation Management
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Complete Nation System
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Everything you need to manage your nation: welcome messages, role requests, diplomacy, towns, and more.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Welcome Messages */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <Users size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Interactive Onboarding</h3>
            </div>
            <DiscordEmbed
              title="🇨🇴 ¡Bienvenido a Colombia, NewMember!"
              description="**Welcome Streak:** 🔥 47 members
**Member #1,247**

Comrade, you have reached our shores. Whether you come to build a home, stand alongside our people, or speak on behalf of another nation, there is a place for you here.

🌟 **Quick Start Guide**
1️⃣ Read our rules in #rules
2️⃣ Introduce yourself in #introductions
3️⃣ Request citizenship below
4️⃣ Join the conversation!

— Nariño 🇨🇴"
              color={0xF1C40F}
            />
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="px-3 py-1.5 rounded-lg bg-[#4e5058] hover:bg-[#6d6f78] text-white text-xs font-medium transition-colors">📜 Read Rules</button>
              <button className="px-3 py-1.5 rounded-lg bg-[#5865f2] hover:bg-[#4752c4] text-white text-xs font-medium transition-colors">🏠 Request Citizenship</button>
              <button className="px-3 py-1.5 rounded-lg bg-[#248046] hover:bg-[#1a6334] text-white text-xs font-medium transition-colors">💬 Introduce Yourself</button>
              <button className="px-3 py-1.5 rounded-lg bg-[#4e5058] hover:bg-[#6d6f78] text-white text-xs font-medium transition-colors">🎁 Claim Gift</button>
            </div>
            <div className="mt-3 p-3 rounded-lg bg-gradient-to-r from-yellow-500/10 to-transparent border border-yellow-500/20">
              <p className="text-xs text-yellow-400 font-semibold mb-1">🎊 MILESTONE WELCOME!</p>
              <p className="text-xs text-gray-400">NewMember is member #1,247! +500 Pesos bonus • Exclusive role • Featured in #hall-of-fame</p>
            </div>
          </motion.div>

          {/* Role Requests */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-500 flex items-center justify-center">
                <Shield size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Advanced Role System</h3>
            </div>
            <DiscordEmbed
              title="🇨🇴 Colombia Role Requests"
              description="Choose a role below. Citizenship and Ally requests go to leadership review with multi-step verification.

**Request format:**
Minecraft username · Nation · Town · Nation role

**Verification Process:**
1️⃣ Submit application
2️⃣ Leadership review (24-48h)
3️⃣ Interview (if required)
4️⃣ Trial period (7 days)
5️⃣ Full citizenship"
              color={0xF1C40F}
            />
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="px-4 py-2 rounded-lg bg-[#5865f2] text-white text-sm font-medium">🏠 Request Citizenship</button>
              <button className="px-4 py-2 rounded-lg bg-[#4e5058] text-white text-sm font-medium">🤝 Request Ally</button>
              <button className="px-4 py-2 rounded-lg bg-[#4e5058] text-white text-sm font-medium">🌐 Foreign Diplomat</button>
              <button className="px-4 py-2 rounded-lg bg-[#248046] text-white text-sm font-medium">🔔 Toggle VP Pings</button>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2">
              <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                <div className="text-lg font-bold text-white">24</div>
                <div className="text-xs text-gray-400">Pending</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                <div className="text-lg font-bold text-emerald-400">156</div>
                <div className="text-xs text-gray-400">Approved</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                <div className="text-lg font-bold text-red-400">8</div>
                <div className="text-xs text-gray-400">Denied</div>
              </div>
            </div>
          </motion.div>

          {/* Diplomacy */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center">
                <Globe size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Advanced Diplomacy</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gradient-to-r from-emerald-500/10 to-transparent border border-emerald-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-400 text-lg">🤝</span>
                    <span className="text-white font-bold text-sm">Alliance with Brazil</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded bg-emerald-500/20 text-emerald-400">Active</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">Trade agreement • Mutual defense • 500+ members</p>
                <div className="flex gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 transition-colors">View Terms</button>
                  <button className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 transition-colors">Trade Stats</button>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-gradient-to-r from-red-500/10 to-transparent border border-red-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-red-400 text-lg">⚔️</span>
                    <span className="text-white font-bold text-sm">War with Peru</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 animate-pulse">Active</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">Declared 3 days ago • 2 battles • 150 casualties</p>
                <div className="flex gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors">Battle Log</button>
                  <button className="text-xs px-2 py-1 rounded bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 transition-colors">Propose Peace</button>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-400 text-lg">🕊️</span>
                    <span className="text-white font-bold text-sm">Peace Treaty - Ecuador</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400">Pending Vote</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">Proposed yesterday • 12/15 votes • Needs 3 more</p>
                <div className="w-full bg-white/5 rounded-full h-2 mb-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{width: '80%'}}></div>
                </div>
                <button className="text-xs px-2 py-1 rounded bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 transition-colors">View Treaty</button>
              </div>
            </div>
          </motion.div>

          {/* Town Management */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center">
                <Map size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Town Management</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-3 rounded-lg bg-white/[0.02]">
                <span className="text-white text-sm font-medium">🏰 Bogotá</span>
                <span className="text-gray-400 text-xs">45 members</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-white/[0.02]">
                <span className="text-white text-sm font-medium">🌴 Cartagena</span>
                <span className="text-gray-400 text-xs">32 members</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-white/[0.02]">
                <span className="text-white text-sm font-medium">⛰️ Medellín</span>
                <span className="text-gray-400 text-xs">28 members</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ─── Economy & Activity ──────────────────────────────────────────────────────

function EconomySection() {
  return (
    <section id="economy" className="relative py-32 bg-gradient-to-b from-transparent via-green-500/[0.02] to-transparent">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-medium mb-4">
            <Coins size={12} />
            Gold Standard Economy
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            DiplomaticaMC Gold Economy
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Real gold-based economy matching DiplomaticaMC's Gold Standard. Town creation (64 gold), nation creation (1024 gold), 
            chunk claiming (16 gold), and full Towny integration.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Economy */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-amber-500 flex items-center justify-center mb-4">
              <Coins size={24} className="text-white" />
            </div>
            <h3 className="text-lg font-bold text-white mb-3">Gold Standard Economy</h3>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gradient-to-r from-yellow-500/10 to-transparent border border-yellow-500/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-semibold text-sm">🪙 Gold Balance</span>
                  <span className="text-yellow-400 font-bold">1,247 gold</span>
                </div>
                <div className="text-xs text-gray-400">19 stacks + 31 ingots</div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                  <div className="text-xs text-gray-400 mb-1">🏰 Town Creation</div>
                  <div className="text-sm font-bold text-yellow-400">64 gold</div>
                </div>
                <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                  <div className="text-xs text-gray-400 mb-1">🌍 Nation Creation</div>
                  <div className="text-sm font-bold text-yellow-400">1024 gold</div>
                </div>
                <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                  <div className="text-xs text-gray-400 mb-1">🗺️ Chunk Claim</div>
                  <div className="text-sm font-bold text-yellow-400">16 gold</div>
                </div>
                <div className="p-2 rounded-lg bg-white/[0.02] text-center">
                  <div className="text-xs text-gray-400 mb-1">📅 Daily Reward</div>
                  <div className="text-sm font-bold text-emerald-400">16 gold</div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 px-3 py-2 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 text-xs font-medium transition-colors">🏰 Towny</button>
                <button className="flex-1 px-3 py-2 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs font-medium transition-colors">🗺️ Map</button>
                <button className="flex-1 px-3 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 text-xs font-medium transition-colors">📊 Market</button>
              </div>
            </div>
          </motion.div>

          {/* Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center mb-4">
              <Activity size={24} className="text-white" />
            </div>
            <h3 className="text-lg font-bold text-white mb-3">Activity Tracking</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Message XP</span>
                <span className="text-white font-semibold">1 XP per message</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Voice XP</span>
                <span className="text-white font-semibold">5 XP per minute</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Level Up</span>
                <span className="text-white font-semibold">Every 100 XP</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Inactive Cleanup</span>
                <span className="text-white font-semibold">30 days</span>
              </div>
            </div>
          </motion.div>

          {/* Leaderboards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center mb-4">
              <Trophy size={24} className="text-white" />
            </div>
            <h3 className="text-lg font-bold text-white mb-3">Leaderboards</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-yellow-400">🥇</span>
                <span className="text-white">Player1</span>
                <span className="text-gray-400 ml-auto">1,234 XP</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">🥈</span>
                <span className="text-white">Player2</span>
                <span className="text-gray-400 ml-auto">1,100 XP</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-orange-400">🥉</span>
                <span className="text-white">Player3</span>
                <span className="text-gray-400 ml-auto">987 XP</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ─── DiplomaticaMC Integration ───────────────────────────────────────────────

function DiplomaticaMCSection() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-transparent via-blue-500/[0.02] to-transparent">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-4">
            <Globe size={12} />
            DiplomaticaMC Integration
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Deep Server Integration
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Built specifically for DiplomaticaMC with Towny, SiegeWar, Gold Standard economy, and live map/market integration.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Towny Integration */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 flex items-center justify-center">
                <Map size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Towny Integration</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gradient-to-r from-emerald-500/10 to-transparent border border-emerald-500/20">
                <div className="text-white font-semibold text-sm mb-2">🏰 Town Management</div>
                <div className="space-y-1 text-xs text-gray-400">
                  <div className="flex justify-between">
                    <span>Create Town</span>
                    <span className="text-yellow-400 font-semibold">64 gold</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Claim Chunk</span>
                    <span className="text-yellow-400 font-semibold">16 gold</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Town Treasury</span>
                    <span className="text-white">Shared gold</span>
                  </div>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20">
                <div className="text-white font-semibold text-sm mb-2">🌍 Nation System</div>
                <div className="space-y-1 text-xs text-gray-400">
                  <div className="flex justify-between">
                    <span>Create Nation</span>
                    <span className="text-yellow-400 font-semibold">1024 gold</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Nation Treasury</span>
                    <span className="text-white">Shared gold</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Member Towns</span>
                    <span className="text-white">Unlimited</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 px-3 py-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 text-xs font-medium transition-colors">/town</button>
                <button className="flex-1 px-3 py-2 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs font-medium transition-colors">/nation</button>
              </div>
            </div>
          </motion.div>

          {/* SiegeWar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center">
                <Sword size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">SiegeWar System</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gradient-to-r from-red-500/10 to-transparent border border-red-500/20">
                <div className="text-white font-semibold text-sm mb-2">⚔️ Weekend Warfare</div>
                <div className="text-xs text-gray-400 space-y-1">
                  <div>✓ Opt-in battles only</div>
                  <div>✓ Non-destructive (no griefing)</div>
                  <div>✓ Zero upkeep costs</div>
                  <div>✓ Zero plundering</div>
                  <div>✓ Saturday-Sunday only</div>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-white/[0.02]">
                <div className="text-white font-semibold text-sm mb-2">🛡️ Active Sieges</div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-red-400">🏰 Bogotá</span>
                    <span className="text-gray-400">vs Lima</span>
                    <span className="text-yellow-400">Day 2/3</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-blue-400">🏰 Cartagena</span>
                    <span className="text-gray-400">vs Quito</span>
                    <span className="text-emerald-400">Defending</span>
                  </div>
                </div>
              </div>
              <button className="w-full px-3 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 text-xs font-medium transition-colors">/siege status</button>
            </div>
          </motion.div>

          {/* Live Map */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <Map size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Live Interactive Map</h3>
            </div>
            <div className="space-y-3">
              <div className="rounded-lg overflow-hidden border border-white/[0.06]">
                <img 
                  src="https://diplomaticamc.com/img/map-overview.jpg" 
                  alt="Live Map" 
                  className="w-full h-32 object-cover"
                />
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>✓ Real-time player tracking</div>
                <div>✓ Town & nation borders</div>
                <div>✓ Capital markers</div>
                <div>✓ Siege zones</div>
                <div>✓ Mobile responsive</div>
              </div>
              <a 
                href="https://map.diplomaticamc.com/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="block w-full px-3 py-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 text-xs font-medium transition-colors text-center"
              >
                Open Live Map →
              </a>
            </div>
          </motion.div>

          {/* Live Market */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                <TrendingUp size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Live Market</h3>
            </div>
            <div className="space-y-3">
              <div className="rounded-lg overflow-hidden border border-white/[0.06]">
                <img 
                  src="https://diplomaticamc.com/img/market-overview.jpg" 
                  alt="Live Market" 
                  className="w-full h-32 object-cover"
                />
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>✓ Real-time price tracking</div>
                <div>✓ Trade volume analytics</div>
                <div>✓ Stock levels</div>
                <div>✓ Price trends</div>
                <div>✓ Supply & demand</div>
              </div>
              <a 
                href="https://market.diplomaticamc.com/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="block w-full px-3 py-2 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 text-xs font-medium transition-colors text-center"
              >
                Open Live Market →
              </a>
            </div>
          </motion.div>
        </div>

        {/* Server Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 p-6 rounded-2xl bg-gradient-to-r from-yellow-500/10 via-blue-500/10 to-red-500/10 border border-white/[0.06]"
        >
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">🇨🇴 DiplomaticaMC Server Info</h3>
            <p className="text-gray-400 text-sm">The ultimate Earth-scale geopolitics sandbox</p>
          </div>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-black text-white">25K+</div>
              <div className="text-xs text-gray-400">Total Players</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white">12K+</div>
              <div className="text-xs text-gray-400">Unique Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white">1:450</div>
              <div className="text-xs text-gray-400">Earth Scale</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white">1.21+</div>
              <div className="text-xs text-gray-400">MC Version</div>
            </div>
          </div>
          <div className="mt-6 text-center">
            <div className="inline-block px-6 py-3 rounded-lg bg-white/[0.05] border border-white/[0.1]">
              <div className="text-xs text-gray-400 mb-1">Server IP</div>
              <div className="text-lg font-mono font-bold text-white">diplomaticamc.com</div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── Events & Tournaments ────────────────────────────────────────────────────

function EventsSection() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-transparent via-purple-500/[0.02] to-transparent">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-medium mb-4">
            <Calendar size={12} />
            Events & Tournaments
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Epic Community Events
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Multi-stage tournaments, battle royales, scavenger hunts, trivia championships, and more.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Active Tournament */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <Trophy size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Build Competition</h3>
                  <p className="text-xs text-purple-400">Stage 2 of 3 • 47 participants</p>
                </div>
              </div>
              <span className="px-2 py-1 rounded bg-purple-500/20 text-purple-400 text-xs font-semibold animate-pulse">LIVE</span>
            </div>
            
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-white/[0.02]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white text-sm font-semibold">🏆 Prize Pool</span>
                  <span className="text-yellow-400 font-bold">5,000 Pesos</span>
                </div>
                <div className="flex gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400">🥇 2,500</span>
                  <span className="text-xs px-2 py-1 rounded bg-gray-500/20 text-gray-400">🥈 1,500</span>
                  <span className="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-400">🥉 1,000</span>
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-white/[0.02]">
                <div className="text-white text-sm font-semibold mb-2">📅 Timeline</div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-emerald-400">✓</span>
                    <span className="text-gray-400">Registration (7 days ago)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-emerald-400">✓</span>
                    <span className="text-gray-400">Round 1: Qualifiers (3 days ago)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-purple-400 animate-pulse">●</span>
                    <span className="text-white font-semibold">Round 2: Semi-finals (Now)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-gray-500">○</span>
                    <span className="text-gray-500">Round 3: Finals (in 2 days)</span>
                  </div>
                </div>
              </div>
              
              <button className="w-full px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 text-sm font-medium transition-colors">
                View Leaderboard
              </button>
            </div>
          </motion.div>

          {/* Upcoming Events */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                <Calendar size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Upcoming Events</h3>
            </div>
            
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gradient-to-r from-red-500/10 to-transparent border border-red-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">⚔️</span>
                    <span className="text-white font-semibold text-sm">PvP Tournament</span>
                  </div>
                  <span className="text-xs text-red-400">in 3 days</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">1v1 elimination bracket • 64 players max</p>
                <div className="flex gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors">Register</button>
                  <button className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 transition-colors">Rules</button>
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🧠</span>
                    <span className="text-white font-semibold text-sm">Trivia Championship</span>
                  </div>
                  <span className="text-xs text-blue-400">in 5 days</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">5 rounds • Colombia history & culture</p>
                <div className="flex gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 transition-colors">Register</button>
                  <button className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 transition-colors">Practice</button>
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-gradient-to-r from-green-500/10 to-transparent border border-green-500/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🗺️</span>
                    <span className="text-white font-semibold text-sm">Scavenger Hunt</span>
                  </div>
                  <span className="text-xs text-green-400">in 7 days</span>
                </div>
                <p className="text-xs text-gray-400 mb-2">Team event • Find hidden items across the map</p>
                <div className="flex gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-green-500/20 hover:bg-green-500/30 text-green-300 transition-colors">Form Team</button>
                  <button className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 transition-colors">Details</button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
              <Bot size={16} className="text-black" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Nariño Bot</div>
              <div className="text-xs text-gray-500">The Ultimate Colombia Nation Bot • v1.0.0</div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-xs text-gray-600">18+ Features • 50+ Commands • Bilingual</span>
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
      <FeaturesOverview />
      <VotePartySection />
      <NationFeatures />
      <EconomySection />
      <DiplomaticaMCSection />
      <EventsSection />
      <Footer />
    </div>
  );
}
