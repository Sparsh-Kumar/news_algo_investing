const API_URL = '/api/llm-responses/today';

let autoRefreshInterval = null;
let isAutoRefreshOn = false;
let isLoading = false; // Prevent concurrent requests

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  updateDateDisplay();
  loadResponses();
  setupEventListeners();
});

function setupEventListeners() {
  document.getElementById('refresh-btn').addEventListener('click', () => {
    loadResponses(true); // true = manual refresh
  });
  document.getElementById('auto-refresh-btn').addEventListener('click', toggleAutoRefresh);
}

function updateDateDisplay() {
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  document.getElementById('date-display').textContent = dateStr;
}

function toggleAutoRefresh() {
  const btn = document.getElementById('auto-refresh-btn');
  isAutoRefreshOn = !isAutoRefreshOn;

  if (isAutoRefreshOn) {
    btn.textContent = 'Auto-refresh: ON';
    btn.classList.add('active');
    // Start auto-refresh immediately, then every 30 seconds
    loadResponses(false); // Trigger immediately
    autoRefreshInterval = setInterval(() => {
      loadResponses(false); // false = auto refresh (less intrusive)
    }, 30000);
  } else {
    btn.textContent = 'Auto-refresh: OFF';
    btn.classList.remove('active');
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
  }
}

async function loadResponses(isManualRefresh = false) {
  // Prevent concurrent requests
  if (isLoading) {
    console.log('Request already in progress, skipping...');
    return;
  }

  const loadingEl = document.getElementById('loading');
  const errorEl = document.getElementById('error');
  const containerEl = document.getElementById('responses-container');

  isLoading = true;

  // For manual refresh, show loading and clear content immediately
  // For auto-refresh, be less intrusive (don't clear content, show subtle indicator)
  if (isManualRefresh) {
    loadingEl.classList.add('show');
    containerEl.innerHTML = '';
  } else {
    // For auto-refresh, add a subtle indicator without clearing content
    loadingEl.textContent = 'Refreshing...';
    loadingEl.classList.add('show');
    loadingEl.style.opacity = '0.7';
  }

  errorEl.classList.remove('show');

  try {
    const response = await fetch(API_URL);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch responses');
    }

    // Update the display
    updateCountDisplay(data.count);

    // Clear and rebuild content
    containerEl.innerHTML = '';

    if (data.count === 0) {
      containerEl.innerHTML = `
        <div class="empty-state">
          <h2>No Responses Today</h2>
          <p>There are no LLM request/response records for today.</p>
        </div>
      `;
    } else {
      data.data.forEach((record, index) => {
        containerEl.appendChild(createResponseCard(record, index + 1));
      });
    }

    // Hide loading indicator
    loadingEl.classList.remove('show');
    loadingEl.style.opacity = '1'; // Reset opacity
    loadingEl.textContent = 'Loading...'; // Reset text
  } catch (error) {
    loadingEl.classList.remove('show');
    loadingEl.style.opacity = '1'; // Reset opacity
    loadingEl.textContent = 'Loading...'; // Reset text
    
    // Only show error for manual refreshes or if container is empty
    if (isManualRefresh || containerEl.innerHTML === '') {
      errorEl.textContent = `Error: ${error.message}`;
      errorEl.classList.add('show');
    } else {
      // For auto-refresh errors, log but don't disrupt the UI
      console.error('Auto-refresh error:', error);
      // Show a subtle notification that refresh failed
      const errorMsg = document.createElement('div');
      errorMsg.className = 'auto-refresh-error';
      errorMsg.textContent = 'Auto-refresh failed. Click Refresh to try again.';
      errorMsg.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #fee; color: #c33; padding: 12px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 1000; font-size: 14px;';
      document.body.appendChild(errorMsg);
      setTimeout(() => errorMsg.remove(), 5000);
    }
  } finally {
    isLoading = false;
  }
}

function updateCountDisplay(count) {
  document.getElementById('count-display').textContent = `${count} response${count !== 1 ? 's' : ''}`;
}

function createResponseCard(record, index) {
  const card = document.createElement('div');
  card.className = 'response-card';

  const createdAt = record.created_at
    ? new Date(record.created_at).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    : 'Unknown time';

  const recordId = record._id || 'N/A';

  card.innerHTML = `
    <div class="response-header">
      <div>
        <div class="response-time">${createdAt}</div>
        <div class="response-id">ID: ${recordId}</div>
      </div>
    </div>
    <div class="section">
      <div class="section-title">
        <span>📝</span>
        <span>Prompt</span>
      </div>
      <div class="section-content">${escapeHtml(record.prompt || 'No prompt available')}</div>
    </div>
    <div class="section">
      <div class="section-title">
        <span>🤖</span>
        <span>Response</span>
      </div>
      <div class="section-content">${formatResponse(record.prompt_response || 'No response available')}</div>
    </div>
  `;

  return card;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatResponse(text) {
  // Try to parse as JSON and format it nicely
  try {
    const json = JSON.parse(text);
    return escapeHtml(JSON.stringify(json, null, 2));
  } catch (e) {
    // If not JSON, just escape and return
    return escapeHtml(text);
  }
}

