import { useEffect, useState } from 'react';

export default function Home() {
	const [logs, setLogs] = useState([]);
	const [isRunning, setIsRunning] = useState(false);
	const [message, setMessage] = useState('');
	const [repeatCount, setRepeatCount] = useState(1);

	// 🎲 Random identity generator
	async function createRedirect() {
		const res = await fetch('/api/create-redirect', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				targetUrl: message,
			}),
		});

		const data = await res.json();
		console.log(data);
	}

	return (
		<div style={{ padding: 20, fontFamily: 'monospace' }}>
			<h1>🕷️ Multi-Guestbook Scraper</h1>

			<div
				style={{
					display: 'flex',
					flexDirection: 'column',
					gap: '10px',
					marginBottom: '20px',
					width: '400px',
				}}>
				<textarea
					placeholder='Type your message here...'
					value={message}
					onChange={(e) => setMessage(e.target.value)}
					style={{ padding: 8, height: 120, fontFamily: 'monospace' }}
				/>

				<div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
					<label>Repeat count:</label>
					<input
						type='number'
						min={1}
						value={repeatCount}
						onChange={(e) => setRepeatCount(Number(e.target.value))}
						style={{ padding: 8, width: 80 }}
					/>
				</div>

				<button
					onClick={createRedirect}
					disabled={isRunning}
					style={{
						padding: '10px 16px',
						background: isRunning ? '#555' : '#008000',
						color: 'white',
						border: 'none',
						borderRadius: '5px',
						cursor: isRunning ? 'not-allowed' : 'pointer',
					}}>
					{isRunning ? '🚀 Scrapers Running...' : 'Start All Scrapers'}
				</button>
			</div>

			{/* <div
				style={{
					padding: 10,
					background: '#000',
					color: '#0f0',
					height: '60vh',
					overflowY: 'scroll',
					borderRadius: '6px',
				}}>
				{logs.length === 0 && (
					<div style={{ color: '#888' }}>Logs will appear here...</div>
				)}

				{logs.map((log, i) => (
					<div key={i}>
						{log.status === 'log' && <span>🟢 {log.message}</span>}
						{log.status === 'error' && (
							<span style={{ color: 'red' }}>❌ {log.message}</span>
						)}
						{log.status === 'status' && (
							<span style={{ color: 'orange' }}>🔄 {log.message}</span>
						)}
						{log.status === 'done' && (
							<span style={{ color: 'cyan' }}>{log.message}</span>
						)}
					</div>
				))}
			</div> */}
		</div>
	);
}
