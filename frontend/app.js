/* ================================================================
   PROJECT ARGUS — Frontend Application Logic
   Vanilla JS client connecting to the FastAPI backend API.
   ================================================================ */

(function () {
    'use strict';

    // ----------------------------------------------------------------
    // CONFIG
    // ----------------------------------------------------------------
    const API_BASE = 'http://localhost:8000';

    // ----------------------------------------------------------------
    // DOM CACHE
    // ----------------------------------------------------------------
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    const navStatus = $('#nav-status');
    const statusDot = $('.status-dot', navStatus);
    const statusText = $('.status-text', navStatus);

    const modTabs = $$('.mod-tab');
    const inputPanels = $$('.input-panel');
    const navLinks = $$('.nav-link');

    const loadingOverlay = $('#loading-overlay');
    const loadingText = $('#loading-text');
    const resultsZone = $('#results-zone');
    const historyZone = $('#history-zone');

    // Trust meter
    const trustRingFill = $('#trust-ring-fill');
    const trustRingValue = $('#trust-ring-value');
    const trustVerdict = $('#trust-verdict');
    const riskBadge = $('#risk-badge');
    const predValue = $('#pred-value');
    const predConf = $('#pred-conf');
    const trustModel = $('#trust-model');

    // Result cards
    const factorsCard = $('#factors-card');
    const factorsList = $('#factors-list');
    const recommendationCard = $('#recommendation-card');
    const recommendationText = $('#recommendation-text');
    const limitationsCard = $('#limitations-card');
    const limitationsList = $('#limitations-list');
    const claimsCard = $('#claims-card');
    const claimsList = $('#claims-list');
    const forensicsCard = $('#forensics-card');
    const forensicsGrid = $('#forensics-grid');
    const metadataCard = $('#metadata-card');
    const metadataTable = $('#metadata-table');
    const rawJson = $('#raw-json');

    // ----------------------------------------------------------------
    // STATE
    // ----------------------------------------------------------------
    let currentModality = 'text';
    let currentSection = 'verify';
    let analysisHistory = JSON.parse(localStorage.getItem('argus_history') || '[]');
    let selectedFiles = { image: null, video: null, audio: null };

    // ----------------------------------------------------------------
    // BACKEND HEALTH CHECK
    // ----------------------------------------------------------------
    async function checkHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
            if (res.ok) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Backend Online';
                return true;
            }
        } catch (_) { /* ignore */ }
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Backend Offline';
        return false;
    }

    checkHealth();
    setInterval(checkHealth, 30000);

    // ----------------------------------------------------------------
    // MODALITY TABS
    // ----------------------------------------------------------------
    modTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const mod = tab.dataset.modality;
            currentModality = mod;

            modTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            inputPanels.forEach(p => p.classList.remove('active'));
            $(`#panel-${mod}`).classList.add('active');

            // Reset results
            resultsZone.style.display = 'none';
        });
    });

    // ----------------------------------------------------------------
    // NAV LINKS
    // ----------------------------------------------------------------
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            currentSection = section;

            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            if (section === 'verify') {
                historyZone.style.display = 'none';
                // show input zone and possibly results
                $('.input-zone').style.display = 'block';
                $('#hero').style.display = 'block';
                $('.modality-bar').style.display = 'flex';
            } else if (section === 'history') {
                historyZone.style.display = 'block';
                $('.input-zone').style.display = 'none';
                resultsZone.style.display = 'none';
                $('#hero').style.display = 'none';
                $('.modality-bar').style.display = 'none';
                renderHistory();
            }
        });
    });

    // ----------------------------------------------------------------
    // FILE UPLOAD HANDLING
    // ----------------------------------------------------------------
    function setupUpload(modality, accept, maxMB) {
        const dropzone = $(`#${modality}-dropzone`);
        const fileInput = $(`#${modality}-file`);
        const previewEl = $(`#${modality}-preview`);
        const clearBtn = $(`#${modality}-clear`);
        const analyzeBtn = $(`#btn-analyze-${modality}`);

        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) handleFile(fileInput.files[0]);
        });

        clearBtn.addEventListener('click', () => {
            selectedFiles[modality] = null;
            previewEl.style.display = 'none';
            dropzone.style.display = 'block';
            analyzeBtn.disabled = true;
            fileInput.value = '';
        });

        function handleFile(file) {
            if (file.size > maxMB * 1024 * 1024) {
                alert(`File too large. Maximum size is ${maxMB}MB.`);
                return;
            }
            selectedFiles[modality] = file;
            dropzone.style.display = 'none';
            previewEl.style.display = 'flex';
            analyzeBtn.disabled = false;

            // Show preview
            if (modality === 'image') {
                const reader = new FileReader();
                reader.onload = (e) => { $('#image-preview-img').src = e.target.result; };
                reader.readAsDataURL(file);
            } else if (modality === 'video') {
                const url = URL.createObjectURL(file);
                $('#video-preview-el').src = url;
            } else if (modality === 'audio') {
                const url = URL.createObjectURL(file);
                $('#audio-preview-el').src = url;
            }
        }
    }

    setupUpload('image', '.jpg,.jpeg,.png,.webp,.bmp', 10);
    setupUpload('video', '.mp4,.avi,.mov,.mkv', 50);
    setupUpload('audio', '.wav,.mp3,.ogg,.flac', 25);

    // ----------------------------------------------------------------
    // ANALYSIS FUNCTIONS
    // ----------------------------------------------------------------
    function showLoading(text) {
        loadingText.textContent = text;
        loadingOverlay.style.display = 'flex';
    }

    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }

    // TEXT
    $('#btn-analyze-text').addEventListener('click', async () => {
        const title = $('#text-title').value.trim();
        const content = $('#text-content').value.trim();
        if (!content) {
            alert('Please enter article content.');
            return;
        }

        showLoading('Analyzing text for misinformation…');
        try {
            const res = await fetch(`${API_BASE}/analyze/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title || 'Untitled',
                    content,
                    verify_claims: $('#text-verify-claims').checked
                })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }

            const data = await res.json();
            displayResults(data, 'text', title || content.substring(0, 50));
        } catch (err) {
            alert(`Analysis failed: ${err.message}`);
        } finally {
            hideLoading();
        }
    });

    // IMAGE
    $('#btn-analyze-image').addEventListener('click', async () => {
        if (!selectedFiles.image) return;
        showLoading('Running image forensics & deepfake detection…');
        try {
            const form = new FormData();
            form.append('file', selectedFiles.image);
            const res = await fetch(`${API_BASE}/analyze/image`, { method: 'POST', body: form });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            displayResults(data, 'image', selectedFiles.image.name);
        } catch (err) {
            alert(`Analysis failed: ${err.message}`);
        } finally {
            hideLoading();
        }
    });

    // VIDEO
    $('#btn-analyze-video').addEventListener('click', async () => {
        if (!selectedFiles.video) return;
        showLoading('Extracting frames & analyzing for deepfakes…');
        try {
            const form = new FormData();
            form.append('file', selectedFiles.video);
            const res = await fetch(`${API_BASE}/analyze/video`, { method: 'POST', body: form });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            displayResults(data, 'video', selectedFiles.video.name);
        } catch (err) {
            alert(`Analysis failed: ${err.message}`);
        } finally {
            hideLoading();
        }
    });

    // AUDIO
    $('#btn-analyze-audio').addEventListener('click', async () => {
        if (!selectedFiles.audio) return;
        showLoading('Analyzing audio waveform for synthetic artifacts…');
        try {
            const form = new FormData();
            form.append('file', selectedFiles.audio);
            const res = await fetch(`${API_BASE}/analyze/audio`, { method: 'POST', body: form });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            displayResults(data, 'audio', selectedFiles.audio.name);
        } catch (err) {
            alert(`Analysis failed: ${err.message}`);
        } finally {
            hideLoading();
        }
    });

    // URL
    $('#btn-analyze-url').addEventListener('click', async () => {
        const url = $('#url-input').value.trim();
        if (!url) {
            alert('Please enter a URL.');
            return;
        }

        showLoading('Fetching URL content & verifying claims…');
        try {
            const res = await fetch(`${API_BASE}/analyze/url`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url,
                    verify_claims: $('#url-verify-claims').checked
                })
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            displayResults(data, 'url', url);
        } catch (err) {
            alert(`Analysis failed: ${err.message}`);
        } finally {
            hideLoading();
        }
    });

    // ----------------------------------------------------------------
    // DISPLAY RESULTS
    // ----------------------------------------------------------------
    function displayResults(data, modality, label) {
        // Store raw
        rawJson.textContent = JSON.stringify(data, null, 2);

        // Trust Score
        const trustScore = data.trust_score;
        const trustObj = data.trust || {};
        const score = trustScore ?? trustObj.score ?? null;
        const verdict = data.verdict || trustObj.verdict || 'UNKNOWN';
        const risk = data.risk_level || trustObj.risk || 'UNKNOWN';
        const prediction = data.prediction || '—';
        const confidence = data.confidence ?? 0;
        const model = data.model || (data.processing && data.processing.model) || 'ARGUS';

        // Animate trust ring
        if (score !== null && score !== undefined) {
            const circumference = 2 * Math.PI * 52; // r=52
            const offset = circumference - (score / 100) * circumference;
            trustRingFill.style.strokeDashoffset = offset;
            trustRingValue.textContent = Math.round(score);
        } else {
            trustRingFill.style.strokeDashoffset = 326.73;
            trustRingValue.textContent = '?';
        }

        // SVG gradient for trust ring (inject dynamically)
        let defs = $('defs', trustRingFill.closest('svg'));
        if (!defs) {
            defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            trustRingFill.closest('svg').prepend(defs);
        }
        defs.innerHTML = `
            <linearGradient id="trustGradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="${getRiskColor(risk)}"/>
                <stop offset="100%" stop-color="#6366f1"/>
            </linearGradient>
        `;
        trustRingFill.setAttribute('stroke', `url(#trustGradient)`);

        // Verdict
        trustVerdict.textContent = verdict;
        trustVerdict.style.color = getVerdictColor(verdict);

        // Risk badge
        riskBadge.textContent = risk;
        riskBadge.className = 'risk-badge ' + risk.toLowerCase().replace('_', '-');
        if (['LOW'].includes(risk)) riskBadge.className = 'risk-badge low';
        else if (['MEDIUM'].includes(risk)) riskBadge.className = 'risk-badge medium';
        else if (['HIGH'].includes(risk)) riskBadge.className = 'risk-badge high';
        else if (['CRITICAL'].includes(risk)) riskBadge.className = 'risk-badge critical';
        else riskBadge.className = 'risk-badge unknown';

        // Prediction
        predValue.textContent = prediction;
        predConf.textContent = `${(confidence * 100).toFixed(1)}%`;
        trustModel.textContent = `Model: ${model}`;

        // Factors
        const factors = data.factors || trustObj.factors || [];
        if (factors.length) {
            factorsCard.style.display = 'block';
            factorsList.innerHTML = factors.map(f => {
                const cls = getFactorClass(f);
                const icon = getFactorIcon(f);
                const text = typeof f === 'string' ? f : (f.description || f.text || JSON.stringify(f));
                return `<div class="factor-item ${cls}">
                    <span class="factor-icon">${icon}</span>
                    <span class="factor-text">${escapeHtml(text)}</span>
                </div>`;
            }).join('');
        } else {
            factorsCard.style.display = 'none';
        }

        // Recommendation
        const rec = data.recommendation || trustObj.recommendation || '';
        if (rec) {
            recommendationCard.style.display = 'block';
            recommendationText.textContent = rec;
        } else {
            recommendationCard.style.display = 'none';
        }

        // Limitations
        const lims = data.limitations || trustObj.limitations || [];
        if (lims.length) {
            limitationsCard.style.display = 'block';
            limitationsList.innerHTML = lims.map(l => `<li>${escapeHtml(l)}</li>`).join('');
        } else {
            limitationsCard.style.display = 'none';
        }

        // Claims
        const claims = data.claims || [];
        if (claims.length) {
            claimsCard.style.display = 'block';
            claimsList.innerHTML = claims.map(renderClaim).join('');
        } else {
            claimsCard.style.display = 'none';
        }

        // Forensics
        const forensics = data.forensics || {};
        if (Object.keys(forensics).length) {
            forensicsCard.style.display = 'block';
            forensicsGrid.innerHTML = renderForensics(forensics);
        } else {
            forensicsCard.style.display = 'none';
        }

        // Metadata
        const meta = data.metadata || {};
        if (Object.keys(meta).length) {
            metadataCard.style.display = 'block';
            metadataTable.innerHTML = renderMetadata(meta);
        } else {
            metadataCard.style.display = 'none';
        }

        // Show results
        resultsZone.style.display = 'block';
        resultsZone.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Add to history
        addToHistory({
            modality,
            label,
            verdict,
            score,
            risk,
            prediction,
            confidence,
            timestamp: new Date().toISOString(),
            data
        });
    }

    // ----------------------------------------------------------------
    // RENDER HELPERS
    // ----------------------------------------------------------------
    function renderClaim(claim) {
        const text = claim.claim_text || claim.text || claim.claim || '—';
        const verdict = (claim.verdict || claim.claim_verdict || 'UNVERIFIED').toUpperCase();
        const sources = claim.sources || [];

        let verdictClass = 'unverified';
        if (verdict === 'SUPPORTED') verdictClass = 'supported';
        else if (verdict === 'CONTRADICTED') verdictClass = 'contradicted';
        else if (verdict === 'MIXED') verdictClass = 'mixed';

        let sourcesHtml = '';
        if (sources.length) {
            sourcesHtml = `<div class="claim-sources">${sources.map(s => {
                const quality = (s.source_quality || s.quality || 'unknown').toLowerCase();
                const domain = s.domain || new URL(s.url || 'https://unknown').hostname;
                return `<div class="source-item">
                    <span class="source-quality-dot ${quality}"></span>
                    <span>${escapeHtml(s.title || domain)}</span>
                    ${s.url ? `<a class="source-link" href="${escapeHtml(s.url)}" target="_blank" rel="noopener">${escapeHtml(domain)}</a>` : ''}
                </div>`;
            }).join('')}</div>`;
        }

        return `<div class="claim-card">
            <div class="claim-header">
                <span class="claim-text">${escapeHtml(text)}</span>
                <span class="claim-verdict-badge ${verdictClass}">${verdict}</span>
            </div>
            ${sourcesHtml}
        </div>`;
    }

    function renderForensics(forensics) {
        return Object.entries(flattenObject(forensics)).map(([key, val]) => {
            let display = val;
            if (typeof val === 'number') display = val.toFixed(4);
            if (typeof val === 'boolean') display = val ? '✓ Yes' : '✗ No';
            return `<div class="forensic-item">
                <div class="forensic-label">${escapeHtml(key.replace(/_/g, ' '))}</div>
                <div class="forensic-value">${escapeHtml(String(display))}</div>
            </div>`;
        }).join('');
    }

    function renderMetadata(meta) {
        return Object.entries(flattenObject(meta)).map(([key, val]) => {
            return `<span class="meta-key">${escapeHtml(key.replace(/_/g, ' '))}</span>
                    <span class="meta-val">${escapeHtml(String(val))}</span>`;
        }).join('');
    }

    function flattenObject(obj, prefix = '') {
        const result = {};
        for (const [key, val] of Object.entries(obj)) {
            const fullKey = prefix ? `${prefix}.${key}` : key;
            if (val && typeof val === 'object' && !Array.isArray(val)) {
                Object.assign(result, flattenObject(val, fullKey));
            } else if (Array.isArray(val)) {
                result[fullKey] = val.join(', ');
            } else {
                result[fullKey] = val;
            }
        }
        return result;
    }

    function getRiskColor(risk) {
        switch ((risk || '').toUpperCase()) {
            case 'LOW': return '#22c55e';
            case 'MEDIUM': return '#f59e0b';
            case 'HIGH': return '#f97316';
            case 'CRITICAL': return '#ef4444';
            default: return '#64748b';
        }
    }

    function getVerdictColor(verdict) {
        const v = (verdict || '').toUpperCase();
        if (['REAL', 'AUTHENTIC', 'SUPPORTED', 'VERIFIED'].includes(v)) return '#22c55e';
        if (['FAKE', 'MANIPULATED', 'CONTRADICTED'].includes(v)) return '#ef4444';
        if (['SUSPICIOUS', 'MIXED', 'UNCERTAIN'].includes(v)) return '#f59e0b';
        return '#94a3b8';
    }

    function getFactorClass(factor) {
        const text = (typeof factor === 'string' ? factor : (factor.description || factor.text || '')).toLowerCase();
        if (text.includes('no ') || text.includes('not ') || text.includes('low') || text.includes('normal') || text.includes('consistent') || text.includes('genuine')) return 'positive';
        if (text.includes('high') || text.includes('suspicious') || text.includes('anomal') || text.includes('synthetic') || text.includes('fake') || text.includes('manipulat')) return 'negative';
        return 'neutral';
    }

    function getFactorIcon(factor) {
        const cls = getFactorClass(factor);
        if (cls === 'positive') return '✓';
        if (cls === 'negative') return '⚠';
        return 'ℹ';
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ----------------------------------------------------------------
    // NEW ANALYSIS BUTTON
    // ----------------------------------------------------------------
    $('#btn-new-analysis').addEventListener('click', () => {
        resultsZone.style.display = 'none';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ----------------------------------------------------------------
    // HISTORY
    // ----------------------------------------------------------------
    function addToHistory(entry) {
        analysisHistory.unshift(entry);
        if (analysisHistory.length > 50) analysisHistory.pop();
        try {
            localStorage.setItem('argus_history', JSON.stringify(analysisHistory));
        } catch (_) { /* quota */ }
    }

    function renderHistory() {
        const list = $('#history-list');
        if (!analysisHistory.length) {
            list.innerHTML = '<p class="history-empty">No analyses yet. Start by verifying content above.</p>';
            return;
        }

        list.innerHTML = analysisHistory.map((h, i) => {
            const scoreDisplay = h.score !== null && h.score !== undefined ? h.score : '?';
            const scoreColor = getRiskColor(h.risk);
            const time = new Date(h.timestamp).toLocaleString();
            return `<div class="history-item" data-index="${i}">
                <span class="history-type">${escapeHtml(h.modality)}</span>
                <span class="history-summary">${escapeHtml(h.label)}</span>
                <span class="history-score" style="color:${scoreColor}">${scoreDisplay}</span>
                <span class="history-time">${time}</span>
            </div>`;
        }).join('');

        // Click to re-display
        $$('.history-item', list).forEach(item => {
            item.addEventListener('click', () => {
                const idx = parseInt(item.dataset.index, 10);
                const entry = analysisHistory[idx];
                if (entry && entry.data) {
                    // Switch to verify view
                    navLinks.forEach(l => l.classList.remove('active'));
                    $$('.nav-link').find(l => l.dataset.section === 'verify')?.classList.add('active');
                    historyZone.style.display = 'none';
                    $('.input-zone').style.display = 'block';
                    $('#hero').style.display = 'block';
                    $('.modality-bar').style.display = 'flex';
                    displayResults(entry.data, entry.modality, entry.label);
                }
            });
        });
    }

    $('#btn-clear-history').addEventListener('click', () => {
        analysisHistory = [];
        localStorage.removeItem('argus_history');
        renderHistory();
    });

})();
