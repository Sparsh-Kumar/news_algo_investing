const API_URL = '/api/llm-responses/today';

let autoRefreshInterval = null;
let isAutoRefreshOn = false;
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  updateDateDisplay();
  loadResponses();
  setupEventListeners();
});

function setupEventListeners() {
  document.getElementById('refresh-btn').addEventListener('click', () => {
    loadResponses(true);
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
  const btnText = btn.querySelector('.btn-text');
  isAutoRefreshOn = !isAutoRefreshOn;

  if (isAutoRefreshOn) {
    btnText.textContent = 'Auto-refresh: ON';
    btn.classList.add('active');
    loadResponses(false);
    autoRefreshInterval = setInterval(() => {
      loadResponses(false);
    }, 30000);
  } else {
    btnText.textContent = 'Auto-refresh: OFF';
    btn.classList.remove('active');
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
  }
}

async function loadResponses(isManualRefresh = false) {
  if (isLoading) {
    console.log('Request already in progress, skipping...');
    return;
  }

  const loadingEl = document.getElementById('loading');
  const errorEl = document.getElementById('error');
  const containerEl = document.getElementById('responses-container');

  isLoading = true;

  if (isManualRefresh) {
    loadingEl.classList.add('show');
    containerEl.innerHTML = '';
  } else {
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

    updateCountDisplay(data.count);
    containerEl.innerHTML = '';

    if (data.count === 0) {
      containerEl.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📊</div>
          <h2>No Recommendations Today</h2>
          <p>There are no trading recommendations available for today.</p>
        </div>
      `;
    } else {
      // Process each record
      data.data.forEach((record, recordIndex) => {
        const recommendations = parseRecommendations(record.prompt_response);
        
        if (recommendations && recommendations.length > 0) {
          // Display recommendations
          recommendations.forEach((rec, index) => {
            containerEl.appendChild(createRecommendationCard(rec, recordIndex, index));
          });
        } else {
          // If no valid recommendations, show the raw response record
          containerEl.appendChild(createResponseRecordCard(record, recordIndex));
        }
      });
    }

    loadingEl.classList.remove('show');
    loadingEl.style.opacity = '1';
  } catch (error) {
    loadingEl.classList.remove('show');
    loadingEl.style.opacity = '1';
    
    if (isManualRefresh || containerEl.innerHTML === '') {
      errorEl.textContent = `Error: ${error.message}`;
      errorEl.classList.add('show');
    } else {
      console.error('Auto-refresh error:', error);
      showNotification('Auto-refresh failed. Click Refresh to try again.', 'error');
    }
  } finally {
    isLoading = false;
  }
}

function parseRecommendations(responseText) {
  if (!responseText) return null;
  
  try {
    // Try to parse as JSON
    const json = JSON.parse(responseText);
    
    // Check if it's an array
    if (Array.isArray(json) && json.length > 0) {
      return json;
    }
    
    // Check if it's wrapped in markdown code blocks
    const codeBlockMatch = responseText.match(/```(?:json)?\s*(\[.*?\])\s*```/s);
    if (codeBlockMatch) {
      return JSON.parse(codeBlockMatch[1]);
    }
    
    return null;
  } catch (e) {
    // Try to extract JSON array from text
    const arrayMatch = responseText.match(/\[[\s\S]*\]/);
    if (arrayMatch) {
      try {
        return JSON.parse(arrayMatch[0]);
      } catch (e2) {
        console.error('Failed to parse recommendations:', e2);
        return null;
      }
    }
    return null;
  }
}

function createRecommendationCard(recommendation, recordIndex, index) {
  const card = document.createElement('div');
  card.className = 'recommendation-card';

  const newsType = recommendation.news_summary_segment || 'MARKET_NEWS';
  const confidence = recommendation.confidence_on_trading_idea || 0;
  const tradingIdea = recommendation.trading_idea || '';
  const newsRef = recommendation.news_summary_referenced || '';

  // Determine if it's BUY or SELL
  const isBuy = tradingIdea.toUpperCase().includes('BUY');
  const isSell = tradingIdea.toUpperCase().includes('SELL');

  // Confidence level
  let confidenceClass = 'low';
  if (confidence >= 7) confidenceClass = 'high';
  else if (confidence >= 4) confidenceClass = 'medium';

  // Format trading idea (remove BUY/SELL prefix for cleaner display)
  const tradingIdeaText = tradingIdea
    .replace(/^(BUY|SELL):\s*/i, '')
    .trim();

  card.innerHTML = `
    <div class="card-header">
      <div class="card-meta">
        <div class="card-time">Recommendation #${index + 1}</div>
        <span class="news-type-badge ${newsType === 'MARKET_NEWS' ? 'market' : 'political'}">
          ${newsType === 'MARKET_NEWS' ? 'Market News' : 'Political News'}
        </span>
      </div>
      <div class="confidence-score">
        <span>Confidence</span>
        <div class="confidence-bar">
          <div class="confidence-fill ${confidenceClass}" style="width: ${confidence * 10}%"></div>
        </div>
        <span>${confidence}/10</span>
      </div>
    </div>
    <div class="card-content">
      <div class="trading-idea ${isBuy ? 'buy' : isSell ? 'sell' : ''}">
        <span class="trading-idea-label">${isBuy ? 'BUY' : isSell ? 'SELL' : 'TRADE'}</span>
        ${escapeHtml(tradingIdeaText)}
      </div>
      ${newsRef ? `
        <div class="news-reference">
          <div class="news-reference-label">Referenced News</div>
          ${escapeHtml(newsRef)}
        </div>
      ` : ''}
    </div>
  `;

  return card;
}

function createResponseRecordCard(record, index) {
  const card = document.createElement('div');
  card.className = 'response-record-card';

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
    <div class="response-record-header">
      <div>
        <div class="response-record-time">${createdAt}</div>
        <div class="response-record-id">ID: ${recordId}</div>
      </div>
    </div>
    <div class="response-section">
      <div class="response-section-title">Prompt</div>
      <div class="response-section-content">${escapeHtml(record.prompt || 'No prompt available')}</div>
    </div>
    <div class="response-section">
      <div class="response-section-title">Response</div>
      <div class="response-section-content">${formatResponse(record.prompt_response || 'No response available')}</div>
    </div>
  `;

  return card;
}

function updateCountDisplay(count) {
  document.getElementById('count-display').textContent = count;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatResponse(text) {
  try {
    const json = JSON.parse(text);
    return escapeHtml(JSON.stringify(json, null, 2));
  } catch (e) {
    return escapeHtml(text);
  }
}

function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'error' ? '#fee' : '#e0f2fe'};
    color: ${type === 'error' ? '#991b1b' : '#0c4a6e'};
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    font-size: 14px;
    font-weight: 500;
    animation: slideIn 0.3s ease;
  `;
  
  document.body.appendChild(notification);
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

