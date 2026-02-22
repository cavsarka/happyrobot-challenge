function parseTranscript(transcription) {
  if (!transcription) return [];

  try {
    const parsed = JSON.parse(transcription);
    return parsed
      .filter(msg => msg.content && msg.role !== 'tool')
      .map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content
      }));
  } catch {
    return transcription.split('\n').filter(Boolean).map(line => ({
      role: line.startsWith('Alex:') ? 'assistant' : 'user',
      content: line.startsWith('Alex:')
        ? line.replace('Alex:', '').trim()
        : line.replace('Caller:', '').trim()
    }));
  }
}

export default function TranscriptPanel({ transcription }) {
  if (!transcription) {
    return <p className="text-sm text-muted italic py-4 px-6">No transcript available</p>;
  }

  const messages = parseTranscript(transcription);

  return (
    <div className="max-h-64 overflow-y-auto p-6 bg-background font-mono text-sm space-y-2">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`p-2 ${
            msg.role === 'assistant'
              ? 'border-l-2 border-accent pl-3 mr-16'
              : 'bg-border/30 ml-16 text-right'
          }`}
        >
          {msg.role === 'assistant' ? 'Alex: ' : 'Caller: '}{msg.content}
        </div>
      ))}
    </div>
  );
}