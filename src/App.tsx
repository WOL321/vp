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
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#2b2d31] hover:bg-[#35373c] text-gray-300 hover:text-white text-sm transition-all border border-[#3f4147]"
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
      <pre className="bg-[#1e1f22] rounded-lg p-4 pt-10 overflow-x-auto text-sm leading-relaxed border border-[#2b2d31]">
        <code className="text-gray-300 font-mono whitespace-pre">{code}</code>
      </pre>
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#5865F2]/20 via-[#1e1f22] to-[#1e1f22]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[#5865F2]/10 rounded-full blur-3xl" />

      <div className="relative max-w-6xl mx-auto px-6 py-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#5865F2]/10 border border-[#5865F2]/30 text-[#5865F2] text-sm font-medium mb-8">
            <Bot size={16} />
            Discord Bot • Python 3.10+
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            🇨🇴 Colombia{' '}
            <span className="bg-gradient-to-r from-[#5865F2] to-[#EB459E] text-transparent bg-clip-text">
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
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#5865F2] hover:bg-[#4752C4] text-white font-semibold transition-colors"
            >
              <Code2 size={18} />
              View Source Code
            </a>
            <a
              href="#setup"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#2b2d31] hover:bg-[#35373c] text-white font-semibold border border-[#3f4147] transition-colors"
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
            { label: 'Vote Goal', value: '250', icon: Target },
            { label: 'Scrape Interval', value: '3 min', icon: Clock },
            { label: 'Vote Sites', value: '3', icon: Vote },
            { label: 'Ping Threshold', value: '30', icon: Bell },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-[#2b2d31]/80 backdrop-blur rounded-xl p-4 border border-[#3f4147]"
            >
              <stat.icon size={20} className="text-[#5865F2] mx-auto mb-2" />
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
        'Scrapes "Vote(s)" from Minecraft-MP, "Votes" from MinecraftServers.org, and monthly/all-time votes from Minecraft-Server-List. Uses multiple selector strategies + regex fallbacks.',
    },
    {
      icon: Target,
      title: 'Smart Cycle Detection',
      description:
        'Automatically detects when 250 votes are reached and resets for the next vote party cycle. No manual intervention needed.',
    },
    {
      icon: Bell,
      title: 'Role Notifications',
      description:
        'Pings the VP role when remaining votes drop to 30 or below (once per cycle). Members toggle notifications with a single button click.',
    },
    {
      icon: Shield,
      title: 'Admin Controls',
      description:
        'Full slash command suite: setup tracker, set remaining votes, reset baseline, force updates. All Administrator-only.',
    },
    {
      icon: Zap,
      title: 'Persistent Single Embed',
      description:
        'Edits one message in-place — never spams the channel. Survives bot restarts via JSON persistence. Professional and clean.',
    },
    {
      icon: Users,
      title: 'Dynamic Color-Coded Embed',
      description:
        'Premium embed with accent bar that changes color: yellow (>50 remaining), blue (31-50), red (≤30). Includes dynamic status messages and progress visualization.',
    },
  ];

  return (
    <section className="max-w-6xl mx-auto px-6 py-20">
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
            className="bg-[#2b2d31] rounded-xl p-6 border border-[#3f4147] hover:border-[#5865F2]/50 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-[#5865F2]/10 flex items-center justify-center mb-4">
              <feature.icon size={20} className="text-[#5865F2]" />
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
      name: '/voteparty action:setup',
      description: 'Post or update the tracker embed in the current channel',
      permission: 'Administrator',
    },
    {
      name: '/voteparty action:setremaining value:<number>',
      description: 'Manually set the number of remaining votes (0-250)',
      permission: 'Administrator',
    },
    {
      name: '/voteparty action:setbaseline',
      description: 'Set the current total vote sum as the new baseline',
      permission: 'Administrator',
    },
    {
      name: '/voteparty action:forceupdate',
      description: 'Force an immediate scrape of all sites and update the embed',
      permission: 'Administrator',
    },
  ];

  return (
    <section className="max-w-6xl mx-auto px-6 py-20">
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
            className="bg-[#2b2d31] rounded-xl p-5 border border-[#3f4147] flex flex-col md:flex-row md:items-center gap-3"
          >
            <div className="flex items-center gap-3 md:w-96 shrink-0">
              <ChevronRight size={16} className="text-[#5865F2]" />
              <code className="text-[#5865F2] font-mono text-sm font-semibold">
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
    <section id="code" className="max-w-6xl mx-auto px-6 py-20">
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

      <div className="bg-[#2b2d31] rounded-xl border border-[#3f4147] overflow-hidden">
        {/* Tab bar */}
        <div className="flex items-center gap-1 px-4 py-3 bg-[#1e1f22] border-b border-[#3f4147] overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.name}
              onClick={() => setActiveTab(tab.name)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.name
                  ? 'bg-[#2b2d31] text-white border border-[#3f4147]'
                  : 'text-gray-400 hover:text-white hover:bg-[#2b2d31]/50'
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
      description: (
        <>
          Go to{' '}
          <a
            href="https://discord.com/developers/applications"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#5865F2] hover:underline inline-flex items-center gap-1"
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
      description:
        'Use the OAuth2 URL Generator with scopes: bot + applications.commands. Select permissions: Send Messages, Embed Links, Manage Messages, Manage Roles, Read Message History, Use Slash Commands.',
    },
    {
      title: 'Create the VP Role',
      description:
        'In Server Settings → Roles, create a role named exactly "VP". Ensure the bot\'s role is above VP in the hierarchy.',
    },
    {
      title: 'Install & Run',
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
      description:
        'In your desired channel, run /voteparty action:setup. The tracker embed will appear with the 🔔 Get Notified button.',
    },
  ];

  return (
    <section id="setup" className="max-w-6xl mx-auto px-6 py-20">
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
              <div className="w-10 h-10 rounded-full bg-[#5865F2] flex items-center justify-center text-white font-bold text-sm shrink-0">
                {i + 1}
              </div>
              {i < steps.length - 1 && (
                <div className="w-0.5 flex-1 bg-[#3f4147] mt-2" />
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
  const [previewState, setPreviewState] = useState<'yellow' | 'blue' | 'red'>('blue');
  const [lastUpdateSeconds, setLastUpdateSeconds] = useState(21);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdateSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const states = {
    yellow: { remaining: 120, color: '#F1C40F', label: 'Early Stage', status: '✅ **All good! Let\'s get started!**' },
    blue: { remaining: 47, color: '#3498DB', label: 'Mid Stage', status: '⚡ **Getting close! Keep voting!**' },
    red: { remaining: 23, color: '#E74C3C', label: 'Final Push', status: '🔥 **Final push! Almost there!**' },
  };

  const current = states[previewState];
  const progress = VOTE_GOAL - current.remaining;
  const percentage = (progress / VOTE_GOAL) * 100;
  const filled = Math.round(percentage / 5);
  const empty = 20 - filled;

  return (
    <section className="max-w-6xl mx-auto px-6 py-24">
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
                  ? 'bg-[#5865F2] text-white'
                  : 'bg-[#2b2d31] text-gray-400 hover:text-white hover:bg-[#35373c]'
              }`}
            >
              <span
                className="inline-block w-2.5 h-2.5 rounded-full mr-2"
                style={{ backgroundColor: state.color }}
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
                  className="w-1 shrink-0"
                  style={{ backgroundColor: current.color }}
                />
                
                {/* Embed content */}
                <div className="bg-[#2b2d31] rounded-r-sm px-4 py-3 flex-1">
                  {/* Title */}
                  <div className="text-white font-semibold mb-2">
                    🇨🇴 Colombia Vote Party Tracker
                  </div>

                  {/* Description */}
                  <div className="text-[#dbdee1] text-sm leading-relaxed mb-3">
                    <div className="text-[1.375rem] font-bold text-white leading-tight mb-0.5">
                      {current.remaining} votes remaining
                    </div>
                    <div className="text-sm mb-2">
                      to reach <span className="font-bold">250!</span>
                    </div>

                    {/* Progress bar */}
                    <div className="font-mono text-sm mb-1">
                      <span style={{ color: current.color }}>
                        {'▰'.repeat(filled)}
                      </span>
                      <span className="text-[#4e5058]">
                        {'▱'.repeat(empty)}
                      </span>{' '}
                      <span className="font-bold text-white">{percentage.toFixed(1)}%</span>
                    </div>

                    <div className="text-xs text-[#b5bac1] mb-2">
                      <span className="font-bold text-white">{progress}</span> / 250 votes collected
                    </div>

                    {/* Status */}
                    <div className="text-sm font-bold" style={{ color: current.color }}>
                      {current.status}
                    </div>
                  </div>

                  {/* Vote Counts field */}
                  <div className="mt-3">
                    <div className="text-white font-semibold text-sm mb-1">
                      🗳️ Vote Counts
                    </div>
                    <div className="text-sm text-[#dbdee1] space-y-0.5">
                      <div>▸ <span className="font-bold text-white">Minecraft-MP</span> — 89 votes</div>
                      <div>▸ <span className="font-bold text-white">MinecraftServers.org</span> — 67 votes</div>
                      <div>▸ <span className="font-bold text-white">Minecraft-Server-List</span> — 47 votes</div>
                    </div>
                  </div>

                  {/* Vote Now field */}
                  <div className="mt-3">
                    <div className="text-white font-semibold text-sm mb-1">
                      🔗 Vote Now
                    </div>
                    <div className="text-sm space-y-0.5">
                      <div>▸ <a href="#" className="text-[#00a8fc] hover:underline">Vote on Minecraft-MP</a></div>
                      <div>▸ <a href="#" className="text-[#00a8fc] hover:underline">Vote on MinecraftServers.org</a></div>
                      <div>▸ <a href="#" className="text-[#00a8fc] hover:underline">Vote on Minecraft-Server-List</a></div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="mt-3 pt-2 border-t border-[#3f4147]">
                    <span className="text-[0.6875rem] text-[#949ba4]">
                      ⏱️ Updated {formatRelativeTime(lastUpdateSeconds)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Button */}
              <div className="mt-2">
                <button className="bg-[#4e505c] hover:bg-[#6d6f7b] text-white text-sm font-medium px-4 py-1.5 rounded-sm transition-colors">
                  🔔 Get Notified
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
    <footer className="border-t border-[#3f4147] mt-10">
      <div className="max-w-6xl mx-auto px-6 py-10 text-center">
        <p className="text-gray-500 text-sm">
          Colombia Vote Party Bot • Built for DiplomaticaMC • Python + discord.py 2.x
        </p>
        <div className="flex justify-center gap-6 mt-4">
          <a
            href="https://discord.com/developers/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-[#5865F2] text-sm transition-colors"
          >
            Discord.py Docs
          </a>
          <a
            href="https://minecraft-mp.com/server-s349345"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-[#5865F2] text-sm transition-colors"
          >
            Minecraft-MP
          </a>
          <a
            href="https://minecraftservers.org/server/679302"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-500 hover:text-[#5865F2] text-sm transition-colors"
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
    <div className="min-h-screen bg-[#1e1f22] text-white">
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
