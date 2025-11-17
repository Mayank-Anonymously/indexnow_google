// pages/api/indexer.js
import axios from 'axios';

export const config = {
	maxDuration: 300,
};

export default async function handler(req, res) {
	try {
		const { url } = req.query || req.body;

		if (!url) return res.status(400).json({ error: 'URL is required' });

		const safeGet = async (u, headers = {}) => {
			try {
				await axios.get(u, { timeout: 8000, headers });
				return { url: u, status: 'OK' };
			} catch (err) {
				return { url: u, status: 'FAIL', code: err.response?.status || null };
			}
		};

		const results = {};

		// ===================================================
		// 1. Google XML Ping
		// ===================================================
		results.xmlPing = await safeGet(
			`https://www.google.com/ping?sitemap=${encodeURIComponent(url)}`
		);

		// ===================================================
		// 2. Google URL Ping
		// ===================================================
		results.urlPing = await safeGet(
			`https://www.google.com/ping?url=${encodeURIComponent(url)}`
		);

		// ===================================================
		// 3. Web Cache Preload (404 = normal)
		// ===================================================
		results.cacheFetch = await safeGet(
			`https://webcache.googleusercontent.com/search?q=${encodeURIComponent(
				url
			)}`
		);

		// ===================================================
		// 4. Trigger Googlebot Crawl
		// ===================================================
		results.googlebot = await safeGet(url, {
			'User-Agent':
				'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
		});

		// ===================================================
		// 5. Trigger Googlebot Mobile
		// ===================================================
		results.googlebotMobile = await safeGet(url, {
			'User-Agent':
				'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 Chrome Mobile Safari/537.36 (compatible; Googlebot-Mobile/2.1; +http://www.google.com/bot.html)',
		});

		// ===================================================
		// 6. Trigger Googlebot Image
		// ===================================================
		results.googleImageBot = await safeGet(url, {
			'User-Agent': 'Googlebot-Image/1.0',
		});

		// ===================================================
		// 7. SafeBrowsing Lookup (forces Google internal fetch)
		// ===================================================
		results.safeBrowsing = await safeGet(
			`https://transparencyreport.google.com/safe-browsing/search?url=${encodeURIComponent(
				url
			)}`
		);

		// ===================================================
		// 8. AMP Cache (if site supports)
		// ===================================================
		results.ampCache = await safeGet(
			`https://cdn.ampproject.org/c/s/${url.replace('https://', '')}`
		);

		// ===================================================
		// 9. Check if Indexed
		// ===================================================
		const indexCheck = await checkIndexed(url);
		results.indexStatus = indexCheck;

		return res.status(200).json({
			message: 'Google Re-Crawl Signals Sent',
			url,
			results,
		});
	} catch (error) {
		return res.status(500).json({ error: error.toString() });
	}
}

/* --------------------------------------------------------
   INDEX CHECK FUNCTION
-------------------------------------------------------- */
async function checkIndexed(url) {
	try {
		const serp = await axios.get(
			`https://www.google.com/search?q=${encodeURIComponent('site:' + url)}`,
			{
				headers: {
					'User-Agent':
						'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
				},
			}
		);

		const html = serp.data;

		if (html.includes('did not match any documents')) {
			return { indexed: false, reason: 'Google reports no documents found' };
		}

		if (html.includes(url)) {
			return { indexed: true, reason: 'URL appears in Google search results' };
		}

		// fallback check
		return { indexed: 'unknown', reason: 'Google returned ambiguous data' };
	} catch (e) {
		return { indexed: 'error', error: e.toString() };
	}
}

