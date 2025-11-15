import { spawn } from 'child_process';
import path from 'path';

let runningProcess = null;
let logs = [];

export default function handler(req, res) {
	if (req.method === 'POST') {
		const { seedsFile, resultsFile, name, email, message } = req.body;

		if (runningProcess) {
			return res.status(409).json({ error: 'Scraper already running' });
		}

		const scriptPath = path.join(
			process.cwd(),
			'scraper',
			'guestpost_headless.py'
		);

		const args = [
			scriptPath,
			seedsFile || 'seeds.txt',
			resultsFile || 'results.csv',
			name,
			email,
			message,
		];

		console.log('Starting scraper:', args);

		runningProcess = spawn('python3', args);
		logs = [];

		runningProcess.stdout.on('data', (data) => {
			const message = data.toString().trim();
			logs.push({ type: 'log', message });
			console.log('[Python STDOUT]:', message);
		});

		runningProcess.stderr.on('data', (data) => {
			const message = data.toString().trim();
			logs.push({ type: 'error', message });
			console.error('[Python STDERR]:', message);
		});

		runningProcess.on('close', (code) => {
			logs.push({ type: 'done', exitCode: code });
			runningProcess = null;
		});

		return res.status(200).json({ message: 'Scraper started' });
	}

	if (req.method === 'GET') {
		res.writeHead(200, {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			Connection: 'keep-alive',
		});

		let sent = 0;

		const interval = setInterval(() => {
			if (sent < logs.length) {
				for (let i = sent; i < logs.length; i++) {
					res.write(`data: ${JSON.stringify(logs[i])}\n\n`);
				}
				sent = logs.length;
			}
		}, 500);

		req.on('close', () => {
			clearInterval(interval);
			res.end();
		});
	} else {
		res.status(405).json({ error: 'Method Not Allowed' });
	}
}
