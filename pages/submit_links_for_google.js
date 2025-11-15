import { useEffect, useState } from 'react';

export default function Home() {
	const [logs, setLogs] = useState([]);
	const [isRunning, setIsRunning] = useState(false);
	const [message, setMessage] = useState('');
	const [repeatCount, setRepeatCount] = useState(1);
	const path = __dirname;

	// 🎲 Random identity generator
	const generateRandomIdentity = () => {
		const randomNum = Math.floor(Math.random() * 100000);
		const name = `GuestPoster_${randomNum}`;
		const email = `guest${randomNum}@example.com`;
		const website = `https://guest${randomNum}.example.com`;
		const title = `Greetings ${randomNum}`;
		const pwd = 'Mayankk2';
		return { name, email, website, title, pwd };
	};

	const startScraping = async () => {
		const timestamp = moment().format('DD:MM:YYYYTHH:MM:SS');
		console.log(timestamp);
		// const IMAGE_DIR = path.join(__dirname, 'images');
		// if (!existsSync(IMAGE_DIR)) {
		// 	mkdirSync(IMAGE_DIR, { recursive: true });
		// }

		// if (!message.trim()) return alert('Please enter a message first.');
		// if (repeatCount < 1) return alert('Repeat count must be at least 1.');

		// setIsRunning(true);
		// setLogs([]);

		// setLogs((prev) => [
		// 	...prev,
		// 	{ status: 'status', message: '🔄 Starting all scrapers...' },
		// ]);

		// // Start backend scraper
		// await fetch('/api/scrape', {
		// 	method: 'POST',
		// 	headers: { 'Content-Type': 'application/json' },
		// 	body: JSON.stringify({
		// 		message,
		// 		repeatCount,
		// 	}),
		// });

		// // 👂 Open Server-Sent Events stream for live logs
		// const eventSource = new EventSource('/api/scrape');

		// eventSource.onmessage = (event) => {
		// 	const log = JSON.parse(event.data);
		// 	setLogs((prev) => [
		// 		...prev,
		// 		{
		// 			status:
		// 				log.type === 'error'
		// 					? 'error'
		// 					: log.type === 'done'
		// 					? 'done'
		// 					: 'log',
		// 			message: log.message,
		// 		},
		// 	]);

		// 	// Auto-stop when all done
		// 	if (log.type === 'done') {
		// 		eventSource.close();
		// 		setIsRunning(false);
		// 	}
		// };

		// eventSource.onerror = (err) => {
		// 	console.error('SSE error:', err);
		// 	eventSource.close();
		// 	setIsRunning(false);
		// };
	};

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
					onClick={startScraping}
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

			<div
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
			</div>
		</div>
	);
}
