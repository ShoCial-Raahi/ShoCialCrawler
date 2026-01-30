

// Restore state on load
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('vendor_import_config');
    if (saved) {
        const config = JSON.parse(saved);
        if (config.vendorName) document.getElementById('vendorName').value = config.vendorName;
        if (config.baseUrl) document.getElementById('baseUrl').value = config.baseUrl;
        if (config.startUrl) document.getElementById('startUrl').value = config.startUrl;
        if (config.pageLimit) document.getElementById('pageLimit').value = config.pageLimit;
    }
});

document.getElementById('crawlForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const vendorName = document.getElementById('vendorName').value;
    const baseUrl = document.getElementById('baseUrl').value;
    const startUrl = document.getElementById('startUrl').value;
    const pageLimit = parseInt(document.getElementById('pageLimit').value);

    // Save to localStorage
    localStorage.setItem('vendor_import_config', JSON.stringify({
        vendorName, baseUrl, startUrl, pageLimit
    }));

    // Toggle UI
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('loadingBtn').style.display = 'flex';
    document.getElementById('statusPanel').classList.remove('hidden');

    try {
        const res = await fetch('/api/crawl/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor_name: vendorName,
                base_url: baseUrl,
                start_urls: [startUrl],
                page_limit: pageLimit
            })
        });

        const data = await res.json();
        const sessionId = data.session_id;

        // Start polling
        pollStatus(sessionId);

    } catch (err) {
        console.error(err);
        alert('Failed to start crawl');
        document.getElementById('startBtn').style.display = 'block';
        document.getElementById('loadingBtn').style.display = 'none';
    }
});

async function pollStatus(sessionId) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/api/crawl/status/${sessionId}`);
            if (!res.ok) return; // Wait for next tick if 404 momentarily

            const stats = await res.json();

            // Update DOM
            document.getElementById('statDiscovered').innerText = stats.discovered;
            document.getElementById('statExtracted').innerText = stats.extracted;
            document.getElementById('statFailed').innerText = stats.failed;

            // Progress Bar (Heuristic based on page discovery vs extracted + failed)
            // If we don't know total pages initially, we can just use discovered as a base
            // or just animate it loosely.

            document.getElementById('statusText').innerText = `Status: ${stats.status.toUpperCase()}`;
            document.getElementById('progressText').innerText = `${stats.extracted} products extracted`;

            if (stats.status === 'completed' || stats.status === 'failed') {
                clearInterval(interval);
                document.getElementById('progressBar').style.width = '100%';
                document.getElementById('progressBar').classList.remove('bg-indigo-600');

                if (stats.status === 'completed') {
                    document.getElementById('progressBar').classList.add('bg-green-600');
                } else {
                    document.getElementById('progressBar').classList.add('bg-red-600');
                }

                // Show Preview Link
                const link = document.getElementById('previewLink');
                link.href = `/vendor-import/preview?session_id=${sessionId}`;
                link.classList.remove('hidden');

                // Reset Button state
                document.getElementById('startBtn').style.display = 'block';
                document.getElementById('loadingBtn').style.display = 'none';
            } else {
                // Determine progress %
                // If discovered > 0, we can estimate progress = (extracted + failed) / discovered * 100
                if (stats.discovered > 0) {
                    const progress = ((stats.extracted + stats.failed) / stats.discovered) * 100;
                    document.getElementById('progressBar').style.width = `${Math.min(progress, 95)}%`;
                }
            }

        } catch (e) {
            console.error(e);
        }
    }, 2000); // Poll every 2 seconds
}
