import happyRobotLogo from '../../assets/HappyRobot Logo.png';

export default function TopNav({ activeTab, onTabChange }) {
  const tabs = [
    { key: 'overview', label: 'Executive Overview' },
    { key: 'calls', label: 'Call Log' },
    { key: 'loads', label: 'Load Intelligence' },
    { key: 'carriers', label: 'Carrier CRM' },
  ];

  return (
    <nav className="sticky top-0 z-50 h-16 bg-surface border-b border-border flex items-center px-6 xl:px-8 justify-between">
      <div className="flex items-center gap-8">
        <button
          type="button"
          onClick={() => onTabChange('overview')}
          className="font-heading text-lg tracking-tight flex items-center gap-2 cursor-pointer"
        >
          <span className="font-bold text-primary">ACME Logistics</span>
          <span className="text-border">|</span>
          <img
            src={happyRobotLogo}
            alt="HappyRobot"
            className="h-[2.1rem] w-auto flex-none"
          />
        </button>
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => onTabChange(tab.key)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === tab.key
                  ? 'border-accent text-primary'
                  : 'border-transparent text-muted hover:text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted font-mono">
          {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
        <div className="w-8 h-8 bg-border flex items-center justify-center text-xs font-medium text-muted">
          AC
        </div>
      </div>
    </nav>
  );
}
