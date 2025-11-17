import { useState } from 'react';

export default function Home() {
	const [url, setUrl] = useState('');
	const [repeat, setRepeat] = useState(1);
	const [loading, setLoading] = useState(false);
	const [logs, setLogs] = useState([]);
	const [error, setError] = useState('');

	async function fireReindex() {
		setLoading(true);
		setLogs([]);
		setError('');

		for (let i = 0; i < repeat; i++) {
			try {
				const res = await fetch('/api/bot', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ url }),
				});

				const data = await res.json();

				if (!res.ok) {
					throw new Error(data.error || 'Unknown error');
				}

				setLogs((prev) => [
					...prev,
					{
						success: true,
						msg: `#${i + 1} — DONE: Googlebot triggers fired`,
						results: data.results,
					},
				]);
			} catch (err) {
				setLogs((prev) => [
					...prev,
					{
						success: false,
						msg: `#${i + 1} — ERROR: ${err.message}`,
					},
				]);
			}
		}

		setLoading(false);
	}

	return (
		<div style={{ padding: 20, fontFamily: 'monospace' }}>
			<h1>⚡ Googlebot Forced Re-Crawl Tool</h1>

			<div
				style={{
					width: 450,
					display: 'flex',
					flexDirection: 'column',
					gap: 12,
				}}>
				<input
					type='text'
					placeholder='Enter URL to reindex...'
					value={url}
					onChange={(e) => setUrl(e.target.value)}
					style={{
						padding: 10,
						fontSize: 15,
						border: '1px solid #aaa',
						borderRadius: 6,
						fontFamily: 'monospace',
					}}
				/>

				<label style={{ fontSize: 14 }}>Repeat Count:</label>
				<input
					type='number'
					min={1}
					value={repeat}
					onChange={(e) => setRepeat(Number(e.target.value))}
					style={{
						padding: 8,
						width: 120,
						borderRadius: 6,
						border: '1px solid #aaa',
						fontFamily: 'monospace',
					}}
				/>

				<button
					disabled={loading}
					onClick={fireReindex}
					style={{
						background: loading ? '#777' : '#0066ff',
						color: 'white',
						padding: '12px 15px',
						border: 'none',
						borderRadius: 6,
						cursor: loading ? 'not-allowed' : 'pointer',
						fontSize: 16,
					}}>
					{loading ? '⏳ Firing Googlebot...' : '🚀 Trigger Googlebot Fetch'}
				</button>

				{error && <div style={{ color: 'red', marginTop: 10 }}>❌ {error}</div>}

				{/* {logs.length > 0 && (
					<div style={{ marginTop: 20 }}>
						<h3>📜 Execution Logs</h3>

						<div
							style={{
								background: '#000',
								color: '#0f0',
								padding: 10,
								borderRadius: 6,
								height: 250,
								overflowY: 'scroll',
								fontSize: 14,
							}}>
							{logs.map((item, i) => (
								<div
									key={i}
									style={{ marginBottom: 8 }}>
									<span style={{ color: item.success ? '#0f0' : 'red' }}>
										{item.msg}
									</span>

									{item.results && (
										<div style={{ marginLeft: 10, color: '#6cf' }}>
											{Object.entries(item.results).map(([k, v]) => (
												<div key={k}>
													➡ {k}: {v}
												</div>
											))}
										</div>
									)}
								</div>
							))}
						</div>
					</div>
				)} */}
			</div>
		</div>
	);
}
