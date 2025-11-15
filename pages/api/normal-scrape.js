import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

let runningProcesses = [];
let logs = [];

export default async function handler(req, res) {
	if (req.method === 'POST') {
		// 🔹 Kill running processes
		runningProcesses.forEach((p) => {
			if (p.exitCode === null) {
				try {
					p.kill();
				} catch {}
			}
		});
		runningProcesses = [];

		const { url, message, repeatCount = 1 } = req.body;
		if (!url) return res.status(400).json({ error: 'Missing URL' });

		const scripts = [
			'letsdobookmark.py',
			'star_bookmarking.py',
			'ubookmarking.py',
			'letsdobookmark.py',
		];

		const scriptPaths = scripts
			.map((name) => path.join(process.cwd(), 'scraper', 'single_link', name))
			.filter(fs.existsSync);

		if (scriptPaths.length === 0)
			return res.status(404).json({ error: 'No valid scripts found' });

		logs = [];
		logs.push({
			type: 'status',
			message: `🚀 Running ${scriptPaths.length} scrapers in parallel...`,
		});

		let completedCount = 0;

		scriptPaths.forEach((scriptPath) => {
			const scriptName = path.basename(scriptPath);

			// 🧩 Each scraper gets its own environment + isolated stdin
			const proc = spawn('python3', [scriptPath], {
				stdio: ['pipe', 'pipe', 'pipe'], // ensure isolated pipes
				env: { ...process.env, PYTHONUNBUFFERED: '1' }, // force flush
			});

			// 🔸 Write JSON input after a small delay to ensure Python is ready
			setTimeout(() => {
				try {
					proc.stdin.write(
						JSON.stringify({ url, message, repeatCount }) + '\n'
					);
					proc.stdin.end();
				} catch (err) {
					console.error(`⚠️ Failed to send input to ${scriptName}:`, err);
				}
			}, 500);

			// 🔸 Handle stdout
			proc.stdout.on('data', (data) => {
				const lines = data.toString().split('\n').filter(Boolean);
				for (const line of lines) {
					logs.push({ type: 'log', script: scriptName, message: line });
				}
			});

			// 🔸 Handle stderr
			proc.stderr.on('data', (data) => {
				const msg = data.toString().trim();
				logs.push({ type: 'error', script: scriptName, message: msg });
			});

			// 🔸 Handle exit
			proc.on('close', (code) => {
				completedCount++;
				logs.push({
					type: 'status',
					script: scriptName,
					message: `💨 ${scriptName} exited with code ${code}`,
				});

				if (completedCount === scriptPaths.length) {
					logs.push({
						type: 'done',
						message: `✅ All ${scriptPaths.length} scrapers finished.`,
					});
					runningProcesses = [];
				}
			});

			runningProcesses.push(proc);
		});

		return res.status(200).json({
			message: `Started ${scriptPaths.length} scrapers successfully.`,
		});
	}

	// --- 🔹 Stream Logs (SSE) ---
	if (req.method === 'GET') {
		res.writeHead(200, {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache, no-transform',
			Connection: 'keep-alive',
		});

		let lastIndex = 0;
		const interval = setInterval(() => {
			while (lastIndex < logs.length) {
				const log = logs[lastIndex];
				res.write(`data: ${JSON.stringify(log)}\n\n`);
				lastIndex++;
			}
		}, 300);

		req.on('close', () => {
			clearInterval(interval);
			res.end();
		});
		return;
	}

	res.status(405).json({ error: 'Method Not Allowed' });
}
