// LoL Analytics Agent - Frontend JavaScript
// Optional: set window.API_BASE_URL = 'https://your-backend.example.com' on static hosts
const API_BASE = (typeof window !== 'undefined' && window.API_BASE_URL) ? window.API_BASE_URL : '';

let currentPUUID = null;
let currentInsights = null;

// DOM Elements
const searchForm = document.getElementById('searchForm');
const gameNameInput = document.getElementById('gameName');
const tagLineInput = document.getElementById('tagLine');
const yearEndBtn = document.getElementById('yearEndBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const insightsContainer = document.getElementById('insightsContainer');
const errorAlert = document.getElementById('errorAlert');
const downloadCard = document.getElementById('downloadCard');

// Event Listeners
searchForm.addEventListener('submit', handleSearch);
yearEndBtn.addEventListener('click', handleYearEndReport);
downloadCard.addEventListener('click', handleDownloadCard);

// Handle player search
async function handleSearch(e) {
    e.preventDefault();
    
    const gameName = gameNameInput.value.trim();
    const tagLine = tagLineInput.value.trim();
    
    if (!gameName || !tagLine) {
        showError('Please enter both game name and tag line');
        return;
    }
    
    showLoading(true);
    hideError();
    insightsContainer.style.display = 'none';
    
    try {
        // Step 1: Lookup player
        const playerData = await lookupPlayer(gameName, tagLine);
        currentPUUID = playerData.puuid;
        
        // Step 2: Generate insights
        const insights = await generateInsights(currentPUUID, `${gameName}#${tagLine}`);
        currentInsights = insights;
        
        // Step 3: Display insights
        displayInsights(insights);
        
        // Enable year-end button
        yearEndBtn.disabled = false;
        
    } catch (error) {
        showError(error.message || 'Failed to generate insights');
    } finally {
        showLoading(false);
    }
}

// Handle year-end report generation
async function handleYearEndReport() {
    if (!currentPUUID) {
        showError('Please search for a player first');
        return;
    }
    
    showLoading(true);
    hideError();
    
    try {
        const report = await generateYearEndReport(currentPUUID, currentInsights.player_name);
        currentInsights = report;
        displayInsights(report, true);
    } catch (error) {
        showError(error.message || 'Failed to generate year-end report');
    } finally {
        showLoading(false);
    }
}

// Handle social card download
async function handleDownloadCard() {
    if (!currentInsights) {
        showError('No insights to download');
        return;
    }
    
    try {
    const response = await fetch(`${API_BASE}/api/visualizations/social-card`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentInsights),
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate social card');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lol-stats-${currentInsights.player_name}.jpg`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        showError('Failed to download social card');
    }
}

// API Calls
async function lookupPlayer(gameName, tagLine) {
    const response = await fetch(`${API_BASE}/api/player/lookup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ game_name: gameName, tag_line: tagLine }),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Player not found');
    }
    
    return await response.json();
}

async function generateInsights(puuid, playerName) {
    const response = await fetch(`${API_BASE}/api/player/${puuid}/insights`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName, max_matches: 100 }),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to generate insights');
    }
    
    return await response.json();
}

async function generateYearEndReport(puuid, playerName) {
    const response = await fetch(`${API_BASE}/api/player/${puuid}/year-end-report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName }),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to generate report');
    }
    
    return await response.json();
}

// Display Functions
function displayInsights(insights, isYearEnd = false) {
    const stats = insights.overall_stats || {};
    const championStats = insights.champion_stats || {};
    const playstyle = insights.playstyle || {};
    const strengths = insights.strengths || {};
    const weaknesses = insights.weaknesses || {};
    const coachingTips = insights.coaching_tips || [];
    const achievements = insights.achievements || [];
    
    // Player Name
    document.getElementById('playerName').textContent = insights.player_name;
    
    // Overall Stats
    displayOverallStats(stats);
    
    // Champions
    displayChampions(championStats);
    
    // Playstyle
    displayPlaystyle(playstyle);
    
    // Strengths
    displayStrengths(strengths);
    
    // Weaknesses
    displayWeaknesses(weaknesses);
    
    // Coaching Tips
    displayCoachingTips(coachingTips);
    
    // Achievements
    displayAchievements(achievements);
    
    // Show insights container
    insightsContainer.style.display = 'block';
    
    // Scroll to insights
    insightsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayOverallStats(stats) {
    const statsRow = document.getElementById('statsRow');
    statsRow.innerHTML = `
        <div class="col-md-3">
            <div class="stats-card text-center">
                <div class="stat-value">${stats.win_rate || 0}%</div>
                <div class="stat-label">Win Rate</div>
                <small>${stats.wins || 0}W ${stats.losses || 0}L</small>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card text-center">
                <div class="stat-value">${stats.avg_kda || 0}</div>
                <div class="stat-label">Avg KDA</div>
                <small>${stats.avg_kills || 0}/${stats.avg_deaths || 0}/${stats.avg_assists || 0}</small>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card text-center">
                <div class="stat-value">${stats.total_games || 0}</div>
                <div class="stat-label">Total Games</div>
                <small>${stats.total_time_played_hours || 0}h played</small>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card text-center">
                <div class="stat-value">${formatNumber(stats.avg_damage_dealt || 0)}</div>
                <div class="stat-label">Avg Damage</div>
                <small>Max: ${formatNumber(stats.max_damage_dealt || 0)}</small>
            </div>
        </div>
    `;
}

function displayChampions(championStats) {
    const championsList = document.getElementById('championsList');
    const bestChampions = championStats.best_champions || [];
    
    if (bestChampions.length === 0) {
        championsList.innerHTML = '<p class="text-muted">No champion data available</p>';
        return;
    }
    
    let html = '';
    bestChampions.slice(0, 5).forEach((champ, index) => {
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
        html += `
            <div class="champion-item">
                <div>
                    <strong>${medal} ${champ.champion}</strong>
                    <br><small>${champ.games} games</small>
                </div>
                <div class="text-end">
                    <div>${champ.win_rate}% WR</div>
                    <small>${champ.avg_kda} KDA</small>
                </div>
            </div>
        `;
    });
    
    championsList.innerHTML = html;
}

function displayPlaystyle(playstyle) {
    const playstyleInfo = document.getElementById('playstyleInfo');
    
    playstyleInfo.innerHTML = `
        <p><strong>Style:</strong> ${playstyle.primary_style || 'Unknown'}</p>
        <p><strong>Aggression Score:</strong> ${playstyle.aggression_score || 0}/100</p>
        <p><strong>Damage Type:</strong> ${playstyle.damage_preference || 'Balanced'}</p>
        <p><strong>Avg Game Length:</strong> ${playstyle.avg_game_length_minutes || 0} min</p>
        ${playstyle.preferred_day ? `<p><strong>Most Active:</strong> ${playstyle.preferred_day}</p>` : ''}
    `;
}

function displayStrengths(strengths) {
    const strengthsList = document.getElementById('strengthsList');
    const strengthsArray = Object.values(strengths);
    
    if (strengthsArray.length === 0) {
        strengthsList.innerHTML = '<p class="text-muted">Keep playing to identify your strengths!</p>';
        return;
    }
    
    let html = '';
    strengthsArray.forEach(strength => {
        html += `
            <div class="coaching-tip">
                <strong>${strength.metric}:</strong> ${strength.value}
                <br><small>${strength.description}</small>
            </div>
        `;
    });
    
    strengthsList.innerHTML = html;
}

function displayWeaknesses(weaknesses) {
    const weaknessesList = document.getElementById('weaknessesList');
    const weaknessesArray = Object.values(weaknesses);
    
    if (weaknessesArray.length === 0) {
        weaknessesList.innerHTML = '<p class="text-success">No major weaknesses identified! Keep it up!</p>';
        return;
    }
    
    let html = '';
    weaknessesArray.forEach(weakness => {
        html += `
            <div class="weakness-item">
                <strong>${weakness.metric}:</strong> ${weakness.value}
                <br><small><i class="fas fa-lightbulb"></i> ${weakness.suggestion}</small>
            </div>
        `;
    });
    
    weaknessesList.innerHTML = html;
}

function displayCoachingTips(tips) {
    const coachingTipsContainer = document.getElementById('coachingTips');
    
    if (!tips || tips.length === 0) {
        coachingTipsContainer.innerHTML = '<p class="text-muted">No specific tips at this time</p>';
        return;
    }
    
    let html = '<ol>';
    tips.forEach(tip => {
        html += `<li class="mb-2">${tip}</li>`;
    });
    html += '</ol>';
    
    coachingTipsContainer.innerHTML = html;
}

function displayAchievements(achievements) {
    const achievementsList = document.getElementById('achievementsList');
    
    if (!achievements || achievements.length === 0) {
        achievementsList.innerHTML = '<p class="text-muted">Keep playing to unlock achievements!</p>';
        return;
    }
    
    let html = '';
    achievements.forEach(achievement => {
        html += `
            <div class="achievement-badge">
                ${achievement.icon || '⭐'} ${achievement.title}
            </div>
        `;
    });
    
    achievementsList.innerHTML = html;
}

// Utility Functions
function showLoading(show) {
    loadingSpinner.style.display = show ? 'block' : 'none';
}

function showError(message) {
    errorAlert.textContent = message;
    errorAlert.style.display = 'block';
}

function hideError() {
    errorAlert.style.display = 'none';
}

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    }
    return Math.round(num);
}
