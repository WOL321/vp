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
  FileCode,
  Settings,
  ChevronRight,
  ExternalLink,
  Zap,
  RefreshCw,
  Target,
  Users,
} from 'lucide-react';
import { mainBotCode, requirementsTxt, envExample, setupInstructions } from './data/botCode';

const VOTE_GOAL = 250;

// Simple Colombian color palette
const COLORS = {
  yellow: '#FCD116',
  blue: '#003893',
  red: '#CE1126',
  dark: '#0a0a0a',
  gray: '#1a1a1a',
  lightGray: '#2a2a2a',
  text: '#ffffff',
  textMuted: '#a0a0a0',
};

// Helper function to format relative time
function formatRelativeTime(seconds: number): string {
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds} seconds ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
  const days = Math.floor(hours / 24);
  return `${days} ${days === 1 ? 'day' : 'days'} ago`;
}

// Helper function to format countdown to next update (every 3 minutes = 180 seconds)
function formatCountdown(elapsedSeconds: number): string {
  const SCRAPE_INTERVAL = 180; // 3 minutes in seconds
  const remaining = Math.max(0, SCRAPE_INTERVAL - (elapsedSeconds % SCRAPE_INTERVAL));
  if (remaining < 60) return `${remaining} seconds`;
  const minutes = Math.floor(remaining / 60);
  const secs = remaining % 60;
  return `${minutes}m ${secs}s`;
}

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
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white text-sm transition-all border border-gray-700"
    >
      {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}

function CodeBlock({ code, language = 'python' }: { code: string; language?: string }) {
  return (
    <div className="relative group">
      <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity z-10">
        <CopyButton text={code} />
      </div>
      <div className="absolute top-3 left-4 text-xs text-gray-500 font-mono uppercase">
        {language}
      </div>
      <pre className="bg-gray-900 rounded-lg p-4 pt-10 overflow-x-auto text-sm leading-relaxed border border-gray-800">
        <code className="text-gray-300 font-mono whitespace-pre">{code}</code>
      </pre>
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden bg-black">
      <div className="relative max-w-6xl mx-auto px-6 py-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gray-900 border border-gray-800 text-gray-300 text-sm font-medium mb-8">
            <Bot size={16} />
            Discord Bot • Python 3.10+
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            🇨🇴 Colombia{' '}
            <span className="text-yellow-400">
              Vote Party
            </span>{' '}
            Bot
          </h1>

          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            A production-ready Discord bot that automatically tracks vote progress across
            3 Minecraft server list sites, manages vote party cycles, and notifies your
            community when the party is close.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <a
              href="#code"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-yellow-400 hover:bg-yellow-300 text-black font-semibold transition-all"
            >
              <Code2 size={18} />
              View Source Code
            </a>
            <a
              href="#setup"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gray-900 hover:bg-gray-800 text-white font-semibold border border-gray-800 transition-colors"
            >
              <Terminal size={18} />
              Setup Guide
            </a>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 max-w-4xl mx-auto"
        >
          {[
            { label: 'Vote Goal', value: '250', icon: Target, color: COLORS.yellow },
            { label: 'Scrape Interval', value: '3 min', icon: Clock, color: COLORS.blue },
            { label: 'Vote Sites', value: '3', icon: Vote, color: COLORS.red },
            { label: 'Ping Threshold', value: '30', icon: Bell, color: COLORS.yellow },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-gray-900 rounded-xl p-4 border border-gray-800"
            >
              <stat.icon size={20} className="mx-auto mb-2" style={{ color: stat.color }} />
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function Features() {
  const features = [
    {
      icon: RefreshCw,
      title: 'Robust Auto-Scraping',
      description:
        'Scrapes vote counts from 3 sites every 3 minutes with multiple selector strategies and regex fallbacks.',
      color: COLORS.yellow,
    },
    {
      icon: Target,
      title: 'Smart Cycle Detection',
      description:
        'Automatically detects when 250 votes are reached and resets for the next vote party cycle.',
      color: COLORS.blue,
    },
    {
      icon: Bell,
      title: 'Role Notifications',
      description:
        'Pings the VP role when remaining votes drop to 30 or below. Members toggle notifications with a button.',
      color: COLORS.red,
    },
    {
      icon: Shield,
      title: 'Admin Controls',
      description:
        'Full slash command suite: setup tracker, set remaining votes, reset baseline, force updates.',
      color: COLORS.yellow,
    },
    {
      icon: Zap,
      title: 'Persistent Single Embed',
      description:
        'Edits one message in-place — never spams the channel. Survives bot restarts via JSON persistence.',
      color: COLORS.blue,
    },
    {
      icon: Users,
      title: 'Dynamic Color-Coded Embed',
      description:
        'Premium embed with accent bar that changes color based on remaining votes with status messages.',
      color: COLORS.red,
    },
  ];

  return (
    <section className="max-w-6xl mx-auto px-6 py-20 bg-black">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-14"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Feature-Rich & Production-Ready
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Everything you need to run a vote party tracker, built with clean modular code
          and proper error handling.
        </p>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="bg-gray-900 rounded-xl p-6 border border-gray-800"
          >
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
              style={{ backgroundColor: feature.color + '20' }}
            >
              <feature.icon size={20} style={{ color: feature.color }} />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

function Commands() {
  const commands = [
    {
      name: '/voteparty setup',
      description: 'Post or update the tracker embed in the current channel',
      permission: 'Administrator',
      color: COLORS.yellow,
    },
    {
      name: '/voteparty setremaining <number>',
      description: 'Manually set the number of remaining votes (0-250)',
      permission: 'Administrator',
      color: COLORS.blue,
    },
    {
      name: '/voteparty setbaseline',
      description: 'Set the current total vote sum as the new baseline',
      permission: 'Administrator',
      color: COLORS.red,
    },
    {
      name: '/voteparty forceupdate',
      description: 'Force an immediate scrape of all sites and update the embed',
      permission: 'Administrator',
      color: COLORS.yellow,
    },
  ];

  return (
    <section className="max-w-6xl mx-auto px-6 py-20 bg-black">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-14"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Slash Commands
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          All commands are slash-only and require Administrator permission.
        </p>
      </motion.div>

      <div className="space-y-3">
        {commands.map((cmd, i) => (
          <motion.div
            key={cmd.name}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="bg-gray-900 rounded-xl p-5 border border-gray-800 flex flex-col md:flex-row md:items-center gap-3"
          >
            <div className="flex items-center gap-3 md:w-96 shrink-0">
              <ChevronRight size={16} style={{ color: cmd.color }} />
              <code className="font-mono text-sm font-semibold" style={{ color: cmd.color }}>
                {cmd.name}
              </code>
            </div>
            <p className="text-gray-400 text-sm flex-1">{cmd.description}</p>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 text-xs font-medium border border-red-500/20 shrink-0">
              <Shield size={12} />
              {cmd.permission}
            </span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

function CodeViewer() {
  const [activeTab, setActiveTab] = useState('bot.py');

  const tabs = [
    { name: 'bot.py', icon: FileCode, content: mainBotCode, language: 'python' },
    { name: 'requirements.txt', icon: FileCode, content: requirementsTxt, language: 'text' },
    { name: '.env.example', icon: Settings, content: envExample, language: 'bash' },
  ];

  const activeFile = tabs.find((t) => t.name === activeTab)!;

  return (
    <section id="code" className="max-w-6xl mx-auto px-6 py-20 bg-black">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-14"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Source Code
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Complete, production-ready code. Copy and customize for your own server.
        </p>
      </motion.div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        {/* Tab bar */}
        <div className="flex items-center gap-1 px-4 py-3 bg-gray-950 border-b border-gray-800 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.name}
              onClick={() => setActiveTab(tab.name)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab.name
                  ? 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <tab.icon size={14} />
              {tab.name}
            </button>
          ))}
          <div className="ml-auto">
            <CopyButton text={activeFile.content} />
          </div>
        </div>

        {/* Code content */}
        <div className="p-6 max-h-[600px] overflow-y-auto">
          <pre className="text-sm leading-relaxed">
            <code className="text-gray-300 font-mono whitespace-pre">
              {activeFile.content}
            </code>
          </pre>
        </div>
      </div>
    </section>
  );
}

function SetupGuide() {
  const steps = [
    {
      title: 'Create a Discord Bot',
      color: COLORS.yellow,
      description: (
        <>
          Go to{' '}
          <a
            href="https://discord.com/developers/applications"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline inline-flex items-center gap-1"
          >
            Discord Developer Portal <ExternalLink size={12} />
          </a>
          , create a new application, go to the Bot tab, enable{' '}
          <strong>Server Members Intent</strong> and{' '}
          <strong>Message Content Intent</strong>, then copy the bot token.
        </>
      ),
    },
    {
      title: 'Invite the Bot',
      color: COLORS.blue,
      description:
        'Use the OAuth2 URL Generator with scopes: bot + applications.commands. Select permissions: Send Messages, Embed Links, Manage Messages, Manage Roles, Read Message History, Use Slash Commands.',
    },
    {
      title: 'Create the VP Role',
      color: COLORS.red,
      description:
        'In Server Settings → Roles, create a role named exactly "VP". Ensure the bot\'s role is above VP in the hierarchy.',
    },
    {
      title: 'Install & Run',
      color: COLORS.yellow,
      description: (
        <div className="mt-3 space-y-2">
          <CodeBlock
            code={`pip install -r requirements.txt
export DISCORD_BOT_TOKEN='your_token_here'
python bot.py`}
            language="bash"
          />
        </div>
      ),
    },
    {
      title: 'Initialize the Tracker',
      color: COLORS.blue,
      description:
        'In your desired channel, run /voteparty setup. The tracker embed will appear with the 🔔 Get Notified button.',
    },
  ];

  return (
    <section id="setup" className="max-w-6xl mx-auto px-6 py-20 bg-black">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-14"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Setup Guide
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Get up and running in under 5 minutes.
        </p>
      </motion.div>

      <div className="space-y-6">
        {steps.map((step, i) => (
          <motion.div
            key={step.title}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="flex gap-5"
          >
            <div className="flex flex-col items-center">
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                style={{ backgroundColor: step.color }}
              >
                {i + 1}
              </div>
              {i < steps.length - 1 && (
                <div className="w-0.5 flex-1 bg-gray-800 mt-2" />
              )}
            </div>
            <div className="pb-8">
              <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
              <div className="text-gray-400 text-sm leading-relaxed">
                {step.description}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

function EmbedPreview() {
  const [previewState, setPreviewState] = useState<'yellow' | 'blue' | 'red'>('yellow');
  const [lastUpdateSeconds, setLastUpdateSeconds] = useState(21);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdateSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const states = {
    yellow: { remaining: 120, color: COLORS.yellow, label: 'Early Stage', status: '✅ **All good! Let\'s get started!**' },
    blue: { remaining: 47, color: COLORS.blue, label: 'Mid Stage', status: '⚡ **Getting close! Keep voting!**' },
    red: { remaining: 23, color: COLORS.red, label: 'Final Push', status: '🔥 **Final push! Almost there!**' },
  };

  const current = states[previewState];
  const progress = VOTE_GOAL - current.remaining;
  const percentage = (progress / VOTE_GOAL) * 100;
  const filled = Math.round(percentage / 5);
  const empty = 20 - filled;

  return (
    <section className="max-w-6xl mx-auto px-6 py-24 bg-black">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-16"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Live Preview
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-10">
          This is exactly what the bot sends to Discord. The timestamp updates in real-time.
        </p>

        <div className="flex flex-wrap justify-center gap-3">
          {Object.entries(states).map(([key, state]) => (
            <button
              key={key}
              onClick={() => {
                setPreviewState(key as 'yellow' | 'blue' | 'red');
                setLastUpdateSeconds(21);
              }}
              className={`px-5 py-2.5 rounded-md text-sm font-semibold transition-all ${
                previewState === key
                  ? 'text-white shadow-lg'
                  : 'bg-gray-900 text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
              style={previewState === key ? {
                backgroundColor: state.color,
                boxShadow: `0 10px 25px -5px ${state.color}40`,
              } : {}}
            >
              <span
                className="inline-block w-2.5 h-2.5 rounded-full mr-2"
                style={{ backgroundColor: previewState === key ? 'white' : state.color }}
              />
              {state.label}
            </button>
          ))}
        </div>
      </motion.div>

      <motion.div
        key={previewState}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
        className="max-w-2xl mx-auto"
      >
        {/* Discord message - exact replica */}
        <div className="bg-[#313338] rounded-lg p-4">
          {/* Message with embed */}
          <div className="flex gap-4">
            {/* Bot avatar */}
            <div className="w-10 h-10 rounded-full bg-[#5865F2] flex items-center justify-center shrink-0">
              <Bot size={20} className="text-white" />
            </div>

            {/* Message body */}
            <div className="flex-1 min-w-0">
              {/* Username line */}
              <div className="flex items-baseline gap-2 mb-1">
                <span className="font-medium text-white">Colombia Vote Party</span>
                <span className="bg-[#5865F2] text-white text-[0.625rem] font-semibold px-1 py-0.5 rounded flex items-center gap-0.5">
                  <svg width="6" height="6" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M14.5 2L6.5 10L1.5 5L0 6.5L6.5 13L16 3.5L14.5 2Z"/>
                  </svg>
                  BOT
                </span>
                <span className="text-xs text-[#949ba4]">
                  Today at {new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                </span>
              </div>

              {/* Embed */}
              <div className="mt-0.5 flex">
                {/* Accent bar */}
                <div 
                  className="w-1 shrink-0 rounded-l"
                  style={{ backgroundColor: current.color }}
                />
                
                {/* Embed content */}
                <div className="bg-[#2b2d31] rounded-r-sm flex-1 overflow-hidden">
                  {/* Header with gradient */}
                  <div 
                    className="px-5 py-4"
                    style={{ 
                      background: `linear-gradient(135deg, ${current.color}15 0%, transparent 100%)`,
                      borderBottom: `1px solid ${current.color}20`
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-white font-bold text-lg">
                        🇨🇴 Colombia Vote Party
                      </div>
                      <div 
                        className="text-xs font-bold px-2 py-1 rounded"
                        style={{ 
                          backgroundColor: `${current.color}20`,
                          color: current.color
                        }}
                      >
                        {percentage.toFixed(0)}% Complete
                      </div>
                    </div>
                    
                    {/* Big number */}
                    <div className="flex items-baseline gap-2 mb-3">
                      <span 
                        className="text-5xl font-black"
                        style={{ color: current.color }}
                      >
                        {current.remaining}
                      </span>
                      <span className="text-[#b5bac1] text-lg">
                        votes to go
                      </span>
                    </div>

                    {/* Modern progress bar */}
                    <div className="relative h-2 bg-[#1e1f22] rounded-full overflow-hidden mb-2">
                      <div 
                        className="absolute left-0 top-0 h-full rounded-full transition-all duration-500"
                        style={{ 
                          width: `${percentage}%`,
                          background: `linear-gradient(90deg, ${current.color}, ${current.color}dd)`,
                          boxShadow: `0 0 10px ${current.color}60`
                        }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-[#949ba4]">
                      <span><span className="text-white font-semibold">{progress}</span> / 250 votes</span>
                      <span className="font-semibold" style={{ color: current.color }}>{percentage.toFixed(1)}%</span>
                    </div>
                  </div>

                  {/* Content sections */}
                  <div className="px-5 py-4 space-y-4">
                    {/* Status message */}
                    <div 
                      className="text-sm font-bold px-3 py-2 rounded"
                      style={{ 
                        backgroundColor: `${current.color}10`,
                        color: current.color,
                        border: `1px solid ${current.color}30`
                      }}
                    >
                      {current.status}
                    </div>

                    {/* Vote Counts */}
                    <div>
                      <div className="text-white font-semibold text-sm mb-2 flex items-center gap-2">
                        <span>🗳️</span>
                        <span>Vote Counts</span>
                      </div>
                      <div className="space-y-1.5">
                        {[
                          { name: 'Minecraft-MP', votes: 89 },
                          { name: 'MinecraftServers.org', votes: 67 },
                          { name: 'Minecraft-Server-List', votes: 47 },
                        ].map((site) => (
                          <div key={site.name} className="flex items-center justify-between text-sm bg-[#1e1f22] px-3 py-2 rounded">
                            <span className="text-[#dbdee1] font-medium">{site.name}</span>
                            <span className="font-bold text-white">{site.votes}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Vote Links */}
                    <div>
                      <div className="text-white font-semibold text-sm mb-2 flex items-center gap-2">
                        <span>🔗</span>
                        <span>Vote Now</span>
                      </div>
                      <div className="space-y-1">
                        {[
                          { name: 'Minecraft-MP', url: 'https://minecraft-mp.com/server-s349345' },
                          { name: 'MinecraftServers.org', url: 'https://minecraftservers.org/server/679302' },
                          { name: 'Minecraft-Server-List', url: 'https://minecraft-server-list.com/server/513054/vote/' },
                        ].map((site, i) => (
                          <a 
                            key={site.name}
                            href={site.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-[#00a8fc] hover:text-[#00d4ff] hover:underline transition-colors group"
                          >
                            <span className="text-[#949ba4] group-hover:text-[#00a8fc] transition-colors">{i + 1}.</span>
                            <span>Vote on {site.name}</span>
                            <ExternalLink size={12} className="opacity-50 group-hover:opacity-100 transition-opacity" />
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div 
                    className="px-5 py-3 border-t"
                    style={{ borderColor: `${current.color}20` }}
                  >
                    <div className="flex items-center gap-2 text-xs text-[#949ba4]">
                      <Clock size={12} />
                      <span>
                        Updated <span className="text-white font-medium">{formatRelativeTime(lastUpdateSeconds)}</span>
                      </span>
                      <span className="text-[#4e5058]">•</span>
                      <span>Next update in <span className="text-white font-medium">{formatCountdown(lastUpdateSeconds)}</span></span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Button */}
              <div className="mt-3">
                <button 
                  className="flex items-center gap-2 text-white text-sm font-semibold px-4 py-2 rounded transition-all hover:scale-105"
                  style={{ 
                    backgroundColor: current.color,
                    boxShadow: `0 4px 12px ${current.color}40`
                  }}
                >
                  <Bell size={14} />
                  <span>Get Notified</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-gray-800 mt-10 bg-black">
      <div className="max-w-6xl mx-auto px-6 py-10 text-center">
        <p className="text-gray-500 text-sm mb-4">
          🇨🇴 Colombia Vote Party Bot • Built for DiplomaticaMC • Python + discord.py 2.x
        </p>
        <div className="flex flex-wrap justify-center gap-4 mb-6">
          <a
            href="https://railway.app"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-400 text-black rounded-lg hover:bg-yellow-300 transition-colors text-sm font-semibold"
          >
            🚀 Deploy on Railway
          </a>
          <a
            href="QUICKSTART.md"
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-semibold"
          >
            📖 Quick Start Guide
          </a>
        </div>
        <div className="flex flex-wrap justify-center gap-6">
          <a
            href="https://discord.com/developers/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-yellow-400 text-sm transition-colors"
          >
            Discord.py Docs
          </a>
          <a
            href="https://minecraft-mp.com/server-s349345"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-blue-400 text-sm transition-colors"
          >
            Minecraft-MP
          </a>
          <a
            href="https://minecraftservers.org/server/679302"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-red-400 text-sm transition-colors"
          >
            MinecraftServers.org
          </a>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <div className="min-h-screen text-white bg-black">
      <Hero />
      <Features />
      <Commands />
      <EmbedPreview />
      <CodeViewer />
      <SetupGuide />
      <Footer />
    </div>
  );
}
