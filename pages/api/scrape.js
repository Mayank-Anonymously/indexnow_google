import { spawn } from 'child_process';
import path from 'path';

let runningProcesses = [];
let logs = [];

export default async function handler(req, res) {
	if (req.method === 'POST') {
		// ✅ Instead of blocking with 409, allow new run safely
		if (runningProcesses.some((p) => p.exitCode === null)) {
			console.log('⚠️ Another scraper run still active. Restarting new batch.');
			runningProcesses.forEach((p) => {
				try {
					p.kill();
				} catch {}
			});
			runningProcesses = [];
		}

		const jsonPayload = req.body;
		const repeatCount = jsonPayload.repeatCount || 1;

		const scripts = [
			// path.join(process.cwd(), 'scraper', 'barricella.py'),
			path.join(process.cwd(), 'scraper', 'florida.py'),
			path.join(process.cwd(), 'scraper', 'creazion.py'),
			path.join(process.cwd(), 'scraper', 'submit_form.py'),
			path.join(process.cwd(), 'scraper', 'guestpost_headless.py'),
			// path.join(process.cwd(), 'scraper', 'kphotography.py'), // include only if file exists

			// path.join(process.cwd(), 'scraper', 'lebanon.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'thefollowing.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'abhira.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'thsen.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'pinlap.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'sappertask.py'), // include only if file exists
			// path.join(process.cwd(), 'scraper', 'hallbook.py'), // include only if file exists
		].filter((script) => {
			try {
				require('fs').accessSync(script);
				return true;
			} catch {
				console.warn(`⚠️ Skipping missing script: ${script}`);
				return false;
			}
		});

		logs = [];
		logs.push({ type: 'status', message: 'Starting scraper batch...' });

		let iteration = 0;

		const runIteration = () => {
			if (iteration >= repeatCount) {
				logs.push({
					type: 'done',
					message: `✅ All ${repeatCount} iterations completed.`,
				});
				runningProcesses = [];
				return;
			}

			iteration++;
			logs.push({
				type: 'status',
				message: `🔁 Running iteration ${iteration} of ${repeatCount}`,
			});

			runningProcesses = scripts.map((scriptPath) => {
				const proc = spawn('python3', [scriptPath]);
				proc.stdin.write(JSON.stringify(jsonPayload));
				proc.stdin.end();

				proc.stdout.on('data', (data) => {
					const msg = data.toString().trim();
					logs.push({
						type: 'log',
						message: `[${path.basename(scriptPath)}] ${msg}`,
					});
				});

				proc.stderr.on('data', (data) => {
					const msg = data.toString().trim();
					logs.push({
						type: 'error',
						message: `[${path.basename(scriptPath)}] ${msg}`,
					});
				});

				proc.on('close', (code) => {
					logs.push({
						type: 'status',
						message: `[${path.basename(scriptPath)}] exited with code ${code}`,
					});

					// Proceed when all scripts are done for this iteration
					if (
						runningProcesses.every(
							(p) => p.exitCode !== null && p.exitCode !== undefined
						)
					) {
						runIteration();
					}
				});

				return proc;
			});
		};

		runIteration();
		return res
			.status(200)
			.json({ message: `Scraper started (${repeatCount}×)` });
	}

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
