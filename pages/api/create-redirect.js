import fs from 'fs';
import path from 'path';
import https from 'https';

export default async function handler(req, res) {
	try {
		if (req.method !== 'POST') {
			return res.status(405).json({ error: 'Method not allowed' });
		}

		const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
		const { targetUrl } = body;

		if (!targetUrl) {
			return res.status(400).json({ error: 'Missing targetUrl' });
		}

		// Ensure redirects folder exists
		const redirectDir = path.join(process.cwd(), 'public', 'redirects');
		fs.mkdirSync(redirectDir, { recursive: true });

		// Create unique file name
		const id = Date.now();
		const filename = `r_${id}.html`;
		const filePath = path.join(redirectDir, filename);

		// HTML redirect content
		const html = `
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="0; url=${targetUrl}" />
<link rel="canonical" href="${targetUrl}" />
</head>
<body>
Redirecting to <a href="${targetUrl}">${targetUrl}</a>
</body>
</html>
`;

		fs.writeFileSync(filePath, html);

		const redirectUrl = `https://travelcation.com/redirects/${filename}`;

		// -------- Update Sitemap ----------
		const sitemapPath = path.join(process.cwd(), 'public', 'sitemap.xml');

		let sitemap = fs.readFileSync(sitemapPath, 'utf8');

		const newEntry = `
  <url>
    <loc>${redirectUrl}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
  </url>
`;

		// Insert entry BEFORE </urlset>
		sitemap = sitemap.replace('</urlset>', `${newEntry}</urlset>`);
		fs.writeFileSync(sitemapPath, sitemap);

		// -------- Ping Google -------------
		const sitemapPing = encodeURIComponent(
			'https://travelcation.com/sitemap.xml'
		);
		https.get(`https://www.google.com/ping?sitemap=${sitemapPing}`, () => {
			console.log('📡 Google pinged');
		});

		return res.status(200).json({
			message: 'Redirect created & Google notified',
			redirectUrl,
			filename,
		});
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: err.message });
	}
}
