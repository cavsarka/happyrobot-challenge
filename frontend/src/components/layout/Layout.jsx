import TopNav from './TopNav';

export default function Layout({ activeTab, onTabChange, children }) {
  return (
    <div className="min-h-screen bg-background">
      <TopNav activeTab={activeTab} onTabChange={onTabChange} />
      <main className="max-w-[1800px] mx-auto w-full px-6 xl:px-8 py-8">
        <div className="zoom-sim-75">
          {children}
        </div>
      </main>
    </div>
  );
}
