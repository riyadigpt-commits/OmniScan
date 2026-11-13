let html5QrCode = null;
let isScanning = false;
let isProcessingScan = false;

function isURL(value) {
	try {
		const url = new URL(value);
		return url.protocol === 'http:' || url.protocol === 'https:';
	} catch (_) {
		return false;
	}
}

function showResult(dataResult, scanType) {
	playBeepSound();

	const resultCard = document.getElementById('result-card');
	const resultText = document.getElementById('result-text');
	const resultType = document.getElementById('result-type');
	const buttonNavigate = document.getElementById('btn-nav');
	const reader = document.getElementById('reader');

	resultText.innerText = dataResult;
	resultType.innerText = `Tipe: ${scanType}`;
	resultCard.classList.remove('d-none');

	if (isURL(dataResult)) {
		buttonNavigate.href = dataResult;
		buttonNavigate.classList.remove('d-none');
	} else {
		buttonNavigate.classList.add('d-none');
	}

	reader.classList.add('scan-success-border');
	setTimeout(() => reader.classList.remove('scan-success-border'), 1500);
	resultCard.scrollIntoView({ behavior: 'smooth' });
}

async function saveScan(dataResult, scanType) {
	const response = await fetch('/api/scan/save', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ scan_type: scanType, data_result: dataResult })
	});
	return readJSONResponse(response, 'Hasil scan gagal disimpan.');
}

async function stopCamera() {
	if (!html5QrCode || !isScanning) return;

	try {
		await html5QrCode.stop();
	} catch (error) {
		console.error('Gagal menghentikan kamera:', error);
	} finally {
		isScanning = false;
		document.getElementById('btn-start-cam').classList.remove('d-none');
		document.getElementById('btn-stop-cam').classList.add('d-none');
	}
}

function initScanner() {
	const startButton = document.getElementById('btn-start-cam');
	const stopButton = document.getElementById('btn-stop-cam');
	const selectButton = document.getElementById('btn-select-file');
	const fileInput = document.getElementById('file-input');
	const copyButton = document.getElementById('btn-copy');

	if (!startButton || !stopButton || !fileInput) return;

	selectButton.addEventListener('click', () => fileInput.click());

	startButton.addEventListener('click', async () => {
		if (isScanning || isProcessingScan || typeof Html5Qrcode === 'undefined') return;
		if (!html5QrCode) html5QrCode = new Html5Qrcode('reader');

		try {
			await html5QrCode.start(
				{ facingMode: 'environment' },
				{ fps: 10, qrbox: { width: 250, height: 250 } },
				async (decodedText, decodedResult) => {
					if (isProcessingScan) return;
					isProcessingScan = true;
					const codeType = decodedResult?.result?.format?.formatName || 'QR_CODE';
					await stopCamera();
					try {
						await saveScan(decodedText, codeType);
					} catch (error) {
						alert(error.message);
					} finally {
						showResult(decodedText, codeType);
						isProcessingScan = false;
					}
				},
				() => {}
			);
			isScanning = true;
			startButton.classList.add('d-none');
			stopButton.classList.remove('d-none');
		} catch (error) {
			alert(`Gagal mengakses kamera: ${error}`);
		}
	});

	stopButton.addEventListener('click', stopCamera);
	document.getElementById('upload-tab').addEventListener('click', stopCamera);

	fileInput.addEventListener('change', async event => {
		const file = event.target.files[0];
		if (!file) return;

		const formData = new FormData();
		formData.append('file', file);
		try {
			const response = await fetch('/api/scan/upload', { method: 'POST', body: formData });
			const data = await readJSONResponse(response, 'Gambar gagal diproses.');
			showResult(data.data_result, data.scan_type);
		} catch (error) {
			alert(error.message || 'Terjadi kesalahan saat memproses gambar.');
		} finally {
			fileInput.value = '';
		}
	});

	copyButton.addEventListener('click', async () => {
		try {
			await navigator.clipboard.writeText(document.getElementById('result-text').innerText);
			alert('Teks berhasil disalin!');
		} catch (_) {
			alert('Teks tidak dapat disalin otomatis.');
		}
	});
}

document.addEventListener('DOMContentLoaded', initScanner);
