document.addEventListener('DOMContentLoaded', () => {
	const themeToggleBtn = document.getElementById('theme-toggle');
	const themeIcon = document.getElementById('theme-icon');
	const htmlElement = document.documentElement;

	if (themeToggleBtn && themeIcon) {
		const currentTheme = localStorage.getItem('omniscan_theme') || 'light';
		htmlElement.setAttribute('data-bs-theme', currentTheme);
		updateThemeIcon(currentTheme, themeIcon);

		themeToggleBtn.addEventListener('click', () => {
			const newTheme = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
			htmlElement.setAttribute('data-bs-theme', newTheme);
			localStorage.setItem('omniscan_theme', newTheme);
			updateThemeIcon(newTheme, themeIcon);
		});
	}

	const currentYear = document.getElementById('current-year');
	if (currentYear) currentYear.textContent = new Date().getFullYear();

	initGenerator();
});

const scanAudio = new Audio('/static/audio/beep.mp3');
scanAudio.preload = 'auto';

function playBeepSound() {
	scanAudio.currentTime = 0;
	scanAudio.play().catch(() => {
		// Browser may block audio until the user interacts with the page.
	});
}

function updateThemeIcon(theme, icon) {
	icon.className = theme === 'dark'
		? 'fa-solid fa-sun text-warning'
		: 'fa-solid fa-moon';
}

async function readJSONResponse(response, fallbackMessage) {
	const contentType = response.headers.get('content-type') || '';
	const data = contentType.includes('application/json') ? await response.json() : null;
	if (!response.ok || !data || data.status !== 'success') {
		throw new Error(data?.message || fallbackMessage);
	}
	return data;
}

function initGenerator() {
	const textForm = document.getElementById('form-text-qr');
	const fileForm = document.getElementById('form-file-qr');
	const resultCard = document.getElementById('qr-result-card');
	const qrImage = document.getElementById('qr-image');
	const downloadButton = document.getElementById('btn-download-qr');

	if (!textForm || !fileForm || !resultCard || !qrImage || !downloadButton) return;

	const submitForm = async (form, endpoint, fallbackMessage) => {
		const button = form.querySelector('button[type="submit"]');
		button.disabled = true;
		try {
			const response = await fetch(endpoint, { method: 'POST', body: new FormData(form) });
			const data = await readJSONResponse(response, fallbackMessage);
			qrImage.src = data.qr_url;
			downloadButton.href = data.qr_url;
			resultCard.classList.remove('d-none');
			resultCard.scrollIntoView({ behavior: 'smooth' });
		} catch (error) {
			alert(error.message || fallbackMessage);
		} finally {
			button.disabled = false;
		}
	};

	textForm.addEventListener('submit', event => {
		event.preventDefault();
		submitForm(textForm, '/api/generate/text', 'Gagal membuat QR Code.');
	});

	fileForm.addEventListener('submit', event => {
		event.preventDefault();
		submitForm(fileForm, '/api/generate/file', 'Gagal mengunggah berkas.');
	});
}
