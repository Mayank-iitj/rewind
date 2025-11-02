// Copied from static/js/app.js for static hosting (Netlify/Vercel)
// Optional: set window.API_BASE_URL = 'https://your-backend.example.com'
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

searchForm.addEventListener('submit', handleSearch);
yearEndBtn.addEventListener('click', handleYearEndReport);
downloadCard.addEventListener('click', handleDownloadCard);

async function handleSearch(e) {
  e.preventDefault();
  const gameName = gameNameInput.value.trim();
  const tagLine = tagLineInput.value.trim();
  if (!gameName || !tagLine) { return showError('Please enter both game name and tag line'); }
  showLoading(true); hideError(); insightsContainer.style.display = 'none';
  try {
    const playerData = await lookupPlayer(gameName, tagLine);
    currentPUUID = playerData.puuid;
    const insights = await generateInsights(currentPUUID, `${gameName}#${tagLine}`);
    currentInsights = insights; displayInsights(insights); yearEndBtn.disabled = false;
  } catch (err) { showError(err.message || 'Failed to generate insights'); } finally { showLoading(false); }
}

async function handleYearEndReport() {
  if (!currentPUUID) return showError('Please search for a player first');
  showLoading(true); hideError();
  try {
    const report = await generateYearEndReport(currentPUUID, currentInsights.player_name);
    currentInsights = report; displayInsights(report, true);
  } catch (err) { showError(err.message || 'Failed to generate year-end report'); } finally { showLoading(false); }
}

async function handleDownloadCard() {
  if (!currentInsights) return showError('No insights to download');
  try {
    const res = await fetch(`${API_BASE}/api/visualizations/social-card`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(currentInsights) });
    if (!res.ok) throw new Error('Failed to generate social card');
    const blob = await res.blob(); const url = window.URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = `lol-stats-${currentInsights.player_name}.jpg`; document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); document.body.removeChild(a);
  } catch { showError('Failed to download social card'); }
}

async function lookupPlayer(gameName, tagLine) {
  const res = await fetch(`${API_BASE}/api/player/lookup`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ game_name: gameName, tag_line: tagLine }) });
  if (!res.ok) { const err = await res.json().catch(()=>({})); throw new Error(err.error || 'Player not found'); }
  return res.json();
}

async function generateInsights(puuid, playerName) {
  const res = await fetch(`${API_BASE}/api/player/${puuid}/insights`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ player_name: playerName, max_matches: 100 }) });
  if (!res.ok) { const err = await res.json().catch(()=>({})); throw new Error(err.error || 'Failed to generate insights'); }
  return res.json();
}

async function generateYearEndReport(puuid, playerName) {
  const res = await fetch(`${API_BASE}/api/player/${puuid}/year-end-report`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ player_name: playerName }) });
  if (!res.ok) { const err = await res.json().catch(()=>({})); throw new Error(err.error || 'Failed to generate report'); }
  return res.json();
}

function displayInsights(insights) {
  const stats = insights.overall_stats || {}; const championStats = insights.champion_stats || {}; const playstyle = insights.playstyle || {}; const strengths = insights.strengths || {}; const weaknesses = insights.weaknesses || {}; const tips = insights.coaching_tips || []; const achievements = insights.achievements || [];
  document.getElementById('playerName').textContent = insights.player_name; displayOverallStats(stats); displayChampions(championStats); displayPlaystyle(playstyle); displayStrengths(strengths); displayWeaknesses(weaknesses); displayCoachingTips(tips); displayAchievements(achievements); insightsContainer.style.display = 'block'; insightsContainer.scrollIntoView({ behavior:'smooth', block:'start' });
}

function displayOverallStats(stats){const r=document.getElementById('statsRow');r.innerHTML=`
<div class="col-md-3"><div class="stats-card text-center"><div class="stat-value">${stats.win_rate||0}%</div><div class="stat-label">Win Rate</div><small>${stats.wins||0}W ${stats.losses||0}L</small></div></div>
<div class="col-md-3"><div class="stats-card text-center"><div class="stat-value">${stats.avg_kda||0}</div><div class="stat-label">Avg KDA</div><small>${stats.avg_kills||0}/${stats.avg_deaths||0}/${stats.avg_assists||0}</small></div></div>
<div class="col-md-3"><div class="stats-card text-center"><div class="stat-value">${stats.total_games||0}</div><div class="stat-label">Total Games</div><small>${stats.total_time_played_hours||0}h played</small></div></div>
<div class="col-md-3"><div class="stats-card text-center"><div class="stat-value">${formatNumber(stats.avg_damage_dealt||0)}</div><div class="stat-label">Avg Damage</div><small>Max: ${formatNumber(stats.max_damage_dealt||0)}</small></div></div>`}

function displayChampions(championStats){const list=document.getElementById('championsList');const best=championStats.best_champions||[];if(best.length===0){list.innerHTML='<p class="text-muted">No champion data available</p>';return;}let html='';best.slice(0,5).forEach((c,i)=>{const m=i===0?'🥇':i===1?'🥈':i===2?'🥉':'';html+=`<div class="champion-item"><div><strong>${m} ${c.champion}</strong><br><small>${c.games} games</small></div><div class="text-end"><div>${c.win_rate}% WR</div><small>${c.avg_kda} KDA</small></div></div>`});list.innerHTML=html}

function displayPlaystyle(p){document.getElementById('playstyleInfo').innerHTML=`<p><strong>Style:</strong> ${p.primary_style||'Unknown'}</p><p><strong>Aggression Score:</strong> ${p.aggression_score||0}/100</p><p><strong>Damage Type:</strong> ${p.damage_preference||'Balanced'}</p><p><strong>Avg Game Length:</strong> ${p.avg_game_length_minutes||0} min</p>${p.preferred_day?`<p><strong>Most Active:</strong> ${p.preferred_day}</p>`:''}`}

function displayStrengths(s){const el=document.getElementById('strengthsList');const arr=Object.values(s);if(arr.length===0){el.innerHTML='<p class="text-muted">Keep playing to identify your strengths!</p>';return;}let html='';arr.forEach(x=>{html+=`<div class="coaching-tip"><strong>${x.metric}:</strong> ${x.value}<br><small>${x.description}</small></div>`});el.innerHTML=html}

function displayWeaknesses(w){const el=document.getElementById('weaknessesList');const arr=Object.values(w);if(arr.length===0){el.innerHTML='<p class="text-success">No major weaknesses identified! Keep it up!</p>';return;}let html='';arr.forEach(x=>{html+=`<div class="weakness-item"><strong>${x.metric}:</strong> ${x.value}<br><small><i class="fas fa-lightbulb"></i> ${x.suggestion}</small></div>`});el.innerHTML=html}

function displayCoachingTips(t){const el=document.getElementById('coachingTips');if(!t||t.length===0){el.innerHTML='<p class="text-muted">No specific tips at this time</p>';return;}el.innerHTML='<ol>'+t.map(x=>`<li class="mb-2">${x}</li>`).join('')+'</ol>'}

function displayAchievements(a){const el=document.getElementById('achievementsList');if(!a||a.length===0){el.innerHTML='<p class="text-muted">Keep playing to unlock achievements!</p>';return;}el.innerHTML=a.map(x=>`<div class="achievement-badge">${x.icon||'⭐'} ${x.title}</div>`).join('')}

function showLoading(s){loadingSpinner.style.display=s?'block':'none'}
function showError(m){errorAlert.textContent=m; errorAlert.style.display='block'}
function hideError(){errorAlert.style.display='none'}
function formatNumber(n){if(n>=1000){return (n/1000).toFixed(1)+'k'} return Math.round(n)}
