document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  function safeCreateIcons() {
    try {
      if (typeof lucide !== 'undefined' && lucide && typeof lucide.createIcons === 'function') {
        lucide.createIcons();
      }
    } catch (e) {
      console.warn('Lucide error:', e);
    }
  }
  safeCreateIcons();

  // State
  let currentComparison = null;
  let activeTab = 'matches'; // 'matches' | 'p1' | 'p2'
  let currentSearchQuery = '';
  let distributionChart = null;

  // DOM Elements
  const compareForm = document.getElementById('compare-form');
  const btnSubmit = document.getElementById('btn-submit');
  const btnText = document.getElementById('btn-text');
  const btnSpinner = document.getElementById('btn-spinner');
  const errorBox = document.getElementById('error-box');
  const errorMessage = document.getElementById('error-message');
  const resultsSection = document.getElementById('results-section');
  const btnFillSampleUrls = document.getElementById('btn-fill-sample-urls');
  const btnClearInputs = document.getElementById('btn-clear-inputs');

  const url1Input = document.getElementById('url1');
  const url2Input = document.getElementById('url2');

  // Tab buttons
  const tabBtnMatches = document.getElementById('tab-btn-matches');
  const tabBtnP1 = document.getElementById('tab-btn-p1');
  const tabBtnP2 = document.getElementById('tab-btn-p2');

  const trackSearchInput = document.getElementById('track-search-input');
  const tracksTableBody = document.getElementById('tracks-table-body');
  const tableEmptyState = document.getElementById('table-empty-state');
  const filteredTracksCount = document.getElementById('filtered-tracks-count');

  // Export buttons
  const btnCopyMatches = document.getElementById('btn-copy-matches');
  const btnExportTxt = document.getElementById('btn-export-txt');
  const btnExportCsv = document.getElementById('btn-export-csv');

  // Pre-fill test sample URLs
  const SAMPLE_URL_1 = "https://music.yandex.ru/playlists/lk.0ce106d6-e6c0-4dd0-8173-3dba3e82cad6?utm_source=web&utm_medium=copy_link";
  const SAMPLE_URL_2 = "https://music.yandex.ru/users/sasha-music/playlists/1005";

  if (btnFillSampleUrls) {
    btnFillSampleUrls.addEventListener('click', () => {
      url1Input.value = SAMPLE_URL_1;
      url2Input.value = SAMPLE_URL_2;
      showToast("Тестовые ссылки вставлены!", "check-circle");
    });
  }

  if (btnClearInputs) {
    btnClearInputs.addEventListener('click', () => {
      url1Input.value = '';
      url2Input.value = '';
      hideError();
    });
  }

  // Run comparison logic
  async function runComparison(u1, u2) {
    u1 = (u1 || '').trim();
    u2 = (u2 || '').trim();

    if (!u1 || !u2) {
      showError("Пожалуйста, укажите ссылки на оба плейлиста.");
      return;
    }

    setLoading(true);
    hideError();

    try {
      const apiEndpoint = window.location.pathname.startsWith('/taste-of-music')
        ? '/taste-of-music/api/compare'
        : '/api/compare';

      const resp = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url1: u1, url2: u2 })
      });

      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || 'Не удалось выполнить сравнение плейлистов.');
      }

      currentComparison = data;
      renderDashboard(data);
      showToast("Сравнение успешно завершено!", "check-circle");
    } catch (err) {
      showError(err.message || 'Произошла непредвиденная ошибка при запросе к серверу.');
    } finally {
      setLoading(false);
    }
  }

  // Form Submit Handler
  if (compareForm) {
    compareForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const u1 = url1Input ? url1Input.value : '';
      const u2 = url2Input ? url2Input.value : '';
      await runComparison(u1, u2);
    });
  }

  // Auto-run if URL query parameters exist (e.g. from previous GET refresh)
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const q1 = urlParams.get('url1');
    const q2 = urlParams.get('url2');
    if (q1 && q2) {
      if (url1Input) url1Input.value = q1;
      if (url2Input) url2Input.value = q2;
      runComparison(q1, q2);
    }
  } catch (e) {
    console.warn('URL params parsing error:', e);
  }

  function setLoading(isLoading) {
    if (isLoading) {
      btnSubmit.disabled = true;
      btnSpinner.classList.remove('hidden');
      btnText.textContent = "Анализируем треки...";
    } else {
      btnSubmit.disabled = false;
      btnSpinner.classList.add('hidden');
      btnText.textContent = "Сравнить плейлисты";
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorBox.classList.remove('hidden');
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function hideError() {
    errorBox.classList.add('hidden');
    errorMessage.textContent = '';
  }

  // Client-side Mojibake detector & fixer
  function fixMojibakeClient(str) {
    if (!str || typeof str !== 'string') return '';
    if (str.includes('Ð') || str.includes('Ñ') || str.includes('Ã')) {
      try {
        const bytes = new Uint8Array([...str].map(c => c.charCodeAt(0)));
        const decoded = new TextDecoder('utf-8').decode(bytes);
        if (decoded && !decoded.includes('\uFFFD')) {
          return decoded;
        }
      } catch (e) {}
    }
    return str;
  }

  // Render Full Dashboard
  function renderDashboard(data) {
    resultsSection.classList.remove('hidden');

    const p1 = data.playlist1;
    const p2 = data.playlist2;
    const stats = data.stats;

    // Playlist 1 Card
    const p1Title = fixMojibakeClient(p1.title) || 'Плейлист 1';
    const p1Owner = fixMojibakeClient(p1.owner);
    document.getElementById('p1-title').textContent = p1Title;
    document.getElementById('p1-title').title = p1Title;
    document.getElementById('p1-owner').textContent = p1Owner ? `Автор: ${p1Owner}` : 'Пользовательский плейлист';
    document.getElementById('p1-count').textContent = p1.total_tracks;
    const p1Cover = document.getElementById('p1-cover');
    p1Cover.src = p1.cover || 'https://avatars.yandex.net/get-music-user-playlist/11418140/favorit-playlist-cover.bb48fdb9b9f4/400x400';
    p1Cover.onerror = () => { 
      p1Cover.src = 'https://avatars.yandex.net/get-music-user-playlist/11418140/favorit-playlist-cover.bb48fdb9b9f4/400x400'; 
    };

    // Playlist 2 Card
    const p2Title = fixMojibakeClient(p2.title) || 'Плейлист 2';
    const p2Owner = fixMojibakeClient(p2.owner);
    document.getElementById('p2-title').textContent = p2Title;
    document.getElementById('p2-title').title = p2Title;
    document.getElementById('p2-owner').textContent = p2Owner ? `Автор: ${p2Owner}` : 'Пользовательский плейлист';
    document.getElementById('p2-count').textContent = p2.total_tracks;
    const p2Cover = document.getElementById('p2-cover');
    p2Cover.src = p2.cover || 'https://avatars.yandex.net/get-music-user-playlist/11418140/favorit-playlist-cover.bb48fdb9b9f4/400x400';
    p2Cover.onerror = () => { 
      p2Cover.src = 'https://avatars.yandex.net/get-music-user-playlist/11418140/favorit-playlist-cover.bb48fdb9b9f4/400x400'; 
    };

    // Score gauge animation
    const scoreVal = stats.jaccard_score;
    const scoreNum = document.getElementById('score-number');
    animateNumber(scoreNum, 0, Math.round(scoreVal), 1000, '%');

    const circle = document.getElementById('score-circle');
    const circumference = 2 * Math.PI * 42; // ~264
    const offset = circumference - (scoreVal / 100) * circumference;
    setTimeout(() => {
      circle.style.strokeDashoffset = offset;
    }, 50);

    document.getElementById('verdict-title').textContent = stats.verdict;
    document.getElementById('verdict-desc').textContent = stats.verdict_desc;

    // KPI Cards
    document.getElementById('metric-matches').textContent = stats.matching_tracks_count;
    document.getElementById('metric-artists').textContent = stats.shared_artists_count;
    document.getElementById('metric-duration').textContent = stats.total_shared_duration_fmt;
    document.getElementById('metric-pct1').textContent = `${p1.match_percent}%`;
    document.getElementById('metric-pct2').textContent = `${p2.match_percent}%`;

    // Distribution Legend
    document.getElementById('legend-u1').textContent = stats.unique_to_p1;
    document.getElementById('legend-shared').textContent = stats.matching_tracks_count;
    document.getElementById('legend-u2').textContent = stats.unique_to_p2;

    // Render Distribution Donut Chart
    renderChart(stats.unique_to_p1, stats.matching_tracks_count, stats.unique_to_p2);

    // Shared Artists Leaderboard
    renderSharedArtists(data.shared_artists);

    // Badges on Tabs
    document.getElementById('tab-matches-badge').textContent = stats.matching_tracks_count;
    document.getElementById('tab-p1-badge').textContent = p1.total_tracks;
    document.getElementById('tab-p2-badge').textContent = p2.total_tracks;

    // Set default tab to matches
    setTab('matches');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    safeCreateIcons();
  }

  // Animate numeric counters
  function animateNumber(element, start, end, duration, suffix = '') {
    const startTime = performance.now();
    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.floor(start + (end - start) * progress);
      element.textContent = `${current}${suffix}`;
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    requestAnimationFrame(update);
  }

  // Render Distribution Chart
  function renderChart(unique1, shared, unique2) {
    const ctx = document.getElementById('chart-distribution').getContext('2d');
    if (distributionChart) {
      distributionChart.destroy();
    }

    distributionChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Уникальные в Плейлисте 1', 'Общие совпадения', 'Уникальные в Плейлисте 2'],
        datasets: [{
          data: [unique1, shared, unique2],
          backgroundColor: [
            'rgba(255, 204, 0, 0.85)',
            'rgba(16, 185, 129, 0.85)',
            'rgba(139, 92, 246, 0.85)'
          ],
          borderColor: '#12141c',
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.85)',
            titleColor: '#fff',
            bodyColor: '#ddd',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8
          }
        },
        cutout: '68%'
      }
    });
  }

  // Render Shared Artists List
  function renderSharedArtists(sharedArtists) {
    const container = document.getElementById('shared-artists-list');
    const counter = document.getElementById('shared-artists-counter');
    container.innerHTML = '';
    counter.textContent = `${sharedArtists.length} найдено`;

    if (!sharedArtists || sharedArtists.length === 0) {
      container.innerHTML = `
        <div class="text-center py-6 text-gray-500 text-xs">
          Общих исполнителей не обнаружено
        </div>
      `;
      return;
    }

    sharedArtists.forEach((item, index) => {
      const el = document.createElement('div');
      el.className = 'flex items-center justify-between p-2.5 rounded-lg bg-black/30 border border-white/5 hover:border-purple-400/30 transition text-xs';
      
      const sample1 = item.sample_titles_1.slice(0, 2).map(fixMojibakeClient).join(', ');
      const sample2 = item.sample_titles_2.slice(0, 2).map(fixMojibakeClient).join(', ');
      const artistName = fixMojibakeClient(item.name);

      el.innerHTML = `
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-6 h-6 rounded-full bg-purple-500/20 text-purple-300 font-bold flex items-center justify-center text-[10px]">
            ${index + 1}
          </div>
          <div class="min-w-0">
            <div class="font-bold text-white truncate">${escapeHtml(artistName)}</div>
            <div class="text-[10px] text-gray-400 truncate" title="Пл.1: ${escapeHtml(sample1)} | Пл.2: ${escapeHtml(sample2)}">
              <span class="text-yellow-400">#1:</span> ${item.tracks_in_p1} трек. • <span class="text-purple-400">#2:</span> ${item.tracks_in_p2} трек.
            </div>
          </div>
        </div>
        <div class="flex-shrink-0 ml-2">
          <span class="badge badge-purple">${item.total_tracks} в сумме</span>
        </div>
      `;
      container.appendChild(el);
    });
  }

  // Tabs Handling
  tabBtnMatches.addEventListener('click', () => setTab('matches'));
  tabBtnP1.addEventListener('click', () => setTab('p1'));
  tabBtnP2.addEventListener('click', () => setTab('p2'));

  function setTab(tab) {
    activeTab = tab;
    [tabBtnMatches, tabBtnP1, tabBtnP2].forEach(b => {
      b.classList.remove('active', 'text-yellow-400', 'border-yellow-400');
      b.classList.add('text-gray-400', 'border-transparent');
    });

    if (tab === 'matches') {
      tabBtnMatches.classList.add('active', 'text-yellow-400', 'border-yellow-400');
      tabBtnMatches.classList.remove('text-gray-400', 'border-transparent');
    } else if (tab === 'p1') {
      tabBtnP1.classList.add('active', 'text-yellow-400', 'border-yellow-400');
      tabBtnP1.classList.remove('text-gray-400', 'border-transparent');
    } else if (tab === 'p2') {
      tabBtnP2.classList.add('active', 'text-yellow-400', 'border-yellow-400');
      tabBtnP2.classList.remove('text-gray-400', 'border-transparent');
    }

    renderCurrentTable();
  }

  // Search input handler
  trackSearchInput.addEventListener('input', (e) => {
    currentSearchQuery = e.target.value.toLowerCase().trim();
    renderCurrentTable();
  });

  // Table rendering with safe cover markup
  function renderCurrentTable() {
    if (!currentComparison) return;

    let tracks = [];
    if (activeTab === 'matches') {
      tracks = currentComparison.matching_tracks || [];
    } else if (activeTab === 'p1') {
      tracks = currentComparison.playlist1.tracks || [];
    } else if (activeTab === 'p2') {
      tracks = currentComparison.playlist2.tracks || [];
    }

    // Set of matched IDs for highlighting
    const matchedIdSet = new Set((currentComparison.matching_tracks || []).map(t => String(t.id)));

    // Apply search filter
    let filtered = tracks;
    if (currentSearchQuery) {
      filtered = tracks.filter(t => {
        const title = fixMojibakeClient(t.title || '').toLowerCase();
        const artist = fixMojibakeClient(t.artist || (t.artists ? t.artists.join(' ') : '')).toLowerCase();
        const album = fixMojibakeClient(t.album || '').toLowerCase();
        return title.includes(currentSearchQuery) || artist.includes(currentSearchQuery) || album.includes(currentSearchQuery);
      });
    }

    filteredTracksCount.textContent = filtered.length;
    tracksTableBody.innerHTML = '';

    if (filtered.length === 0) {
      tableEmptyState.classList.remove('hidden');
    } else {
      tableEmptyState.classList.add('hidden');
    }

    filtered.forEach((track, idx) => {
      const isMatched = matchedIdSet.has(String(track.id)) || activeTab === 'matches';
      const duration = track.duration_fmt || formatDuration(track.duration_sec || 0);
      const rawArtists = track.artist || (track.artists ? track.artists.join(', ') : 'Неизвестный исполнитель');
      const artistsStr = fixMojibakeClient(rawArtists);
      const titleStr = fixMojibakeClient(track.title || 'Без названия');
      const albumStr = fixMojibakeClient(track.album || '');
      const coverUrl = track.cover || '';

      const tr = document.createElement('tr');
      tr.className = `track-row ${isMatched ? 'is-matched' : ''}`;

      tr.innerHTML = `
        <td class="py-3 px-4 text-center font-mono text-gray-500">${idx + 1}</td>
        <td class="py-3 px-4">
          <div class="relative w-10 h-10 rounded-md overflow-hidden bg-zinc-800 border border-white/10 flex-shrink-0 flex items-center justify-center shadow-sm">
            ${coverUrl ? `
              <img 
                src="${escapeHtml(coverUrl)}" 
                alt="Cover" 
                class="w-full h-full object-cover"
                onerror="this.style.display='none'; this.nextElementSibling.classList.remove('hidden');"
              >
              <div class="hidden w-full h-full flex items-center justify-center text-yellow-400 bg-zinc-800">
                <i data-lucide="disc" class="w-5 h-5"></i>
              </div>
            ` : `
              <div class="w-full h-full flex items-center justify-center text-yellow-400 bg-zinc-800">
                <i data-lucide="disc" class="w-5 h-5"></i>
              </div>
            `}
          </div>
        </td>
        <td class="py-3 px-4">
          <div class="font-semibold text-white flex items-center gap-2">
            <span>${escapeHtml(titleStr)}</span>
            ${isMatched && activeTab !== 'matches' ? '<span class="badge badge-yellow text-[9px] px-1.5 py-0.2">Совпадение</span>' : ''}
          </div>
          ${track.match_type ? `<div class="text-[10px] text-emerald-400 mt-0.5">${track.match_type}</div>` : ''}
        </td>
        <td class="py-3 px-4 text-gray-300 font-medium">${escapeHtml(artistsStr)}</td>
        <td class="py-3 px-4 text-gray-400 hidden md:table-cell truncate max-w-[200px]" title="${escapeHtml(albumStr)}">
          ${escapeHtml(albumStr || '—')}
        </td>
        <td class="py-3 px-4 text-center font-mono text-gray-400">${duration}</td>
        <td class="py-3 px-4 text-center">
          ${track.url ? `
            <a 
              href="${track.url}" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-yellow-400/10 hover:bg-yellow-400/20 text-yellow-300 border border-yellow-400/20 font-semibold text-[11px] transition"
            >
              <span>Слушать</span>
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          ` : `
            <span class="text-gray-600 text-xs">—</span>
          `}
        </td>
      `;

      tracksTableBody.appendChild(tr);
    });

    safeCreateIcons();
  }

  // Export functions
  btnCopyMatches.addEventListener('click', () => {
    if (!currentComparison || !currentComparison.matching_tracks.length) {
      showToast("Нет совпадающих треков для копирования", "alert-circle");
      return;
    }
    const lines = currentComparison.matching_tracks.map((t, i) => {
      const art = fixMojibakeClient(t.artist || (t.artists ? t.artists.join(', ') : ''));
      const title = fixMojibakeClient(t.title || '');
      return `${i + 1}. ${art} - ${title}`;
    });
    navigator.clipboard.writeText(lines.join('\n'))
      .then(() => showToast(`Скопировано ${lines.length} треков в буфер!`, "copy"))
      .catch(() => showToast("Не удалось скопировать", "alert-circle"));
  });

  btnExportTxt.addEventListener('click', () => {
    if (!currentComparison || !currentComparison.matching_tracks.length) {
      showToast("Нет совпадающих треков", "alert-circle");
      return;
    }
    const lines = [
      `=== Совпадающие треки Яндекс Музыки ===`,
      `Плейлист 1: ${fixMojibakeClient(currentComparison.playlist1.title)}`,
      `Плейлист 2: ${fixMojibakeClient(currentComparison.playlist2.title)}`,
      `Совпадений: ${currentComparison.stats.matching_tracks_count}`,
      `Совпадение вкуса: ${currentComparison.stats.jaccard_score}%`,
      `---------------------------------------`,
      ...currentComparison.matching_tracks.map((t, i) => {
        const art = fixMojibakeClient(t.artist || (t.artists ? t.artists.join(', ') : ''));
        const title = fixMojibakeClient(t.title || '');
        const album = fixMojibakeClient(t.album || 'Сингл');
        return `${i + 1}. ${art} - ${title} [${album}] (${t.duration_fmt || ''}) ${t.url || ''}`;
      })
    ];
    downloadFile(lines.join('\n'), 'matching_tracks.txt', 'text/plain;charset=utf-8');
    showToast("Файл matching_tracks.txt скачан!", "download");
  });

  btnExportCsv.addEventListener('click', () => {
    if (!currentComparison || !currentComparison.matching_tracks.length) {
      showToast("Нет совпадающих треков", "alert-circle");
      return;
    }
    const headers = ["Index", "Title", "Artist", "Album", "Duration", "URL"];
    const rows = currentComparison.matching_tracks.map((t, i) => [
      i + 1,
      `"${fixMojibakeClient(t.title || '').replace(/"/g, '""')}"`,
      `"${fixMojibakeClient(t.artist || (t.artists ? t.artists.join(', ') : '')).replace(/"/g, '""')}"`,
      `"${fixMojibakeClient(t.album || '').replace(/"/g, '""')}"`,
      `"${t.duration_fmt || ''}"`,
      `"${t.url || ''}"`
    ]);
    const csvContent = "\uFEFF" + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    downloadFile(csvContent, 'matching_tracks.csv', 'text/csv;charset=utf-8');
    showToast("Файл matching_tracks.csv скачан!", "file-spreadsheet");
  });

  function downloadFile(content, fileName, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Toast Notification
  function showToast(message, iconName = 'check-circle') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    toastMsg.textContent = message;
    toastIcon.setAttribute('data-lucide', iconName);
    safeCreateIcons();

    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
      toast.classList.add('translate-y-20', 'opacity-0');
      toast.classList.remove('translate-y-0', 'opacity-100');
    }, 3200);
  }

  // Utilities
  function formatDuration(sec) {
    if (!sec) return '0:00';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

});
