const runBtn = document.getElementById('runBtn');
const refreshBtn = document.getElementById('refreshBtn');
const runLog = document.getElementById('runLog');
const summaryTable = document.getElementById('summaryTable');

const resultEmpty = document.getElementById('resultEmpty');
const resultContent = document.getElementById('resultContent');
const traceId = document.getElementById('traceId');
const product = document.getElementById('product');
const bestStore = document.getElementById('bestStore');
const bestPrice = document.getElementById('bestPrice');
const mdLink = document.getElementById('mdLink');
const pdfLink = document.getElementById('pdfLink');

function setLatest(summary) {
  console.log('setLatest called with:', summary);
  if (!summary || !summary.trace_id) {
    console.log('No summary or no trace_id, showing empty state');
    resultEmpty.classList.remove('hidden');
    resultContent.classList.add('hidden');
    return;
  }

  console.log('Showing result content');
  resultEmpty.classList.add('hidden');
  resultContent.classList.remove('hidden');

  traceId.textContent = summary.trace_id || '-';
  product.textContent = summary.product_name || '-';
  bestStore.textContent = summary.best_store || '-';
  bestPrice.textContent = summary.best_price !== '' ? String(summary.best_price) : '-';
  console.log('Updated display: traceId=%s, product=%s, bestStore=%s, bestPrice=%s', summary.trace_id, summary.product_name, summary.best_store, summary.best_price);

  if (summary.md_report_url) {
    mdLink.href = summary.md_report_url;
    mdLink.style.pointerEvents = 'auto';
    mdLink.style.opacity = '1';
  } else {
    mdLink.removeAttribute('href');
    mdLink.style.pointerEvents = 'none';
    mdLink.style.opacity = '0.4';
  }

  if (summary.pdf_report_url) {
    pdfLink.href = summary.pdf_report_url;
    pdfLink.style.pointerEvents = 'auto';
    pdfLink.style.opacity = '1';
  } else {
    pdfLink.removeAttribute('href');
    pdfLink.style.pointerEvents = 'none';
    pdfLink.style.opacity = '0.4';
  }
}

function renderSummaries(items) {
  if (!items || items.length === 0) {
    summaryTable.innerHTML = '<tr><td colspan="5">No run summaries found.</td></tr>';
    return;
  }

  const rows = items.map((item) => {
    const md = item.md_report_url ? `<a href="${item.md_report_url}" target="_blank" rel="noopener">MD</a>` : '-';
    const pdf = item.pdf_report_url ? `<a href="${item.pdf_report_url}" target="_blank" rel="noopener">PDF</a>` : '-';

    return `
      <tr>
        <td>${item.trace_id || '-'}</td>
        <td>${item.product_name || '-'}</td>
        <td>${item.best_store || '-'}</td>
        <td>${item.best_price ?? '-'}</td>
        <td>${md} / ${pdf}</td>
      </tr>
    `;
  });

  summaryTable.innerHTML = rows.join('');
}

async function loadSummaries() {
  summaryTable.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

  try {
    const response = await fetch('/api/summaries');
    const data = await response.json();
    console.log('Summaries loaded:', data);
    const summaries = data.summaries || [];
    console.log('Total summaries:', summaries.length);
    renderSummaries(summaries);
    if (summaries.length > 0) {
      setLatest(summaries[0]);
    }
  } catch (error) {
    console.error('Failed to load summaries:', error);
    summaryTable.innerHTML = `<tr><td colspan="5">Failed to load summaries: ${String(error)}</td></tr>`;
  }
}

async function runPipeline() {
  const requestValue = document.getElementById('request').value.trim();
  const modelValue = document.getElementById('model').value.trim();

  runBtn.disabled = true;
  runLog.textContent = 'Running pipeline... please wait.';

  try {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request: requestValue || 'Compare prices for coconut',
        model: modelValue || 'llama3:8b',
      }),
    });

    const data = await response.json();
    console.log('API Response:', data);

    if (!response.ok || !data.ok) {
      const stderr = data.stderr ? `\n\nSTDERR:\n${data.stderr}` : '';
      runLog.textContent = `Run failed: ${data.error || 'Unknown error'}${stderr}`;
      return;
    }

    runLog.textContent = data.stdout || 'Run completed successfully.';
    console.log('Setting latest with summary:', data.summary);
    setLatest(data.summary || null);
    console.log('Loading summaries...');
    await loadSummaries();
  } catch (error) {
    console.error('Pipeline error:', error);
    runLog.textContent = `Run failed: ${String(error)}`;
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener('click', runPipeline);
refreshBtn.addEventListener('click', loadSummaries);

loadSummaries();
