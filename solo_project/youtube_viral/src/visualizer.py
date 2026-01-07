import json
from datetime import datetime
from pathlib import Path

class TrendVisualizer:
    def __init__(self, output_path="dashboard.html"):
        self.output_path = output_path
        self.template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Viral Radar Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-primary: #38bdf8;
            --accent-secondary: #818cf8;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --danger: #ef4444;
            --success: #10b981;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 40px;
            border-bottom: 1px solid #334155;
            padding-bottom: 20px;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .timestamp {
            color: var(--text-dim);
            font-size: 0.95rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .card {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--accent-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        .table-card {
            grid-column: span 1;
            overflow: hidden;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th {
            text-align: left;
            padding: 12px;
            color: var(--text-dim);
            border-bottom: 1px solid #334155;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #334155;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-power { background: rgba(56, 189, 248, 0.2); color: var(--accent-primary); }
        .badge-recent { background: rgba(16, 185, 129, 0.2); color: var(--success); }

        .highlights {
            display: flex;
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-box {
            flex: 1;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #334155;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            display: block;
            margin-top: 5px;
        }

        .stat-label {
            color: var(--text-dim);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>YVR Dashboard <small style="font-size: 1rem; font-weight: 400; color: var(--text-dim)">v2.5 Snapshot</small></h1>
                <p style="margin: 5px 0 0 0; color: var(--text-dim)">AI-Powered YouTube Viral Radar</p>
            </div>
            <div class="timestamp">Last Updated: <span id="update-time"></span></div>
        </header>

        <div class="highlights" id="top-highlights">
            <!-- Dynamic Main Stats -->
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">🚀 Topic Share Index (%)</div>
                <div class="chart-container">
                    <canvas id="shareChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">🔥 Trend Power Score</div>
                <div class="chart-container">
                    <canvas id="powerChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">👁️ Average View Count</div>
                <div class="chart-container">
                    <canvas id="viewChart"></canvas>
                </div>
            </div>
            <div class="card table-card">
                <div class="card-title">💎 Recent Analysis Snapshot</div>
                <table id="analysisTable">
                    <thead>
                        <tr>
                            <th>Keyword</th>
                            <th>Avg. Views</th>
                            <th>Power</th>
                            <th>Recent(%)</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const data = {{DATA_JSON}};

        document.getElementById('update-time').textContent = data.timestamp;

        // 1. Highlights
        const highBox = document.getElementById('top-highlights');
        const topPower = data.analysis.sort((a,b) => b.power_score - a.power_score)[0];
        const totalVols = data.analysis.reduce((a,b) => a + (b.total_vols || 0), 0);
        
        highBox.innerHTML = `
            <div class="stat-box">
                <span class="stat-label">Hot Topic</span>
                <span class="stat-value" style="color: var(--accent-primary)">${topPower ? topPower.keyword : '-'}</span>
            </div>
            <div class="stat-box">
                <span class="stat-label">Analyzed Videos</span>
                <span class="stat-value">${totalVols.toLocaleString()}</span>
            </div>
            <div class="stat-box">
                <span class="stat-label">Avg. Recent Density</span>
                <span class="stat-value" style="color: var(--success)">
                    ${(data.analysis.reduce((a,b) => a + b.recent_ratio, 0) / data.analysis.length * 100).toFixed(1)}%
                </span>
            </div>
        `;

        // 2. Share Chart
        new Chart(document.getElementById('shareChart'), {
            type: 'bar',
            data: {
                labels: data.analysis.map(d => d.keyword),
                datasets: [{
                    label: 'Share %',
                    data: data.analysis.map(d => d.topic_share),
                    backgroundColor: '#38bdf8',
                    borderRadius: 8
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, 
                scales: { y: { beginAtZero: true, grid: { color: '#334155' } }, x: { grid: { display : false } } },
                plugins: { legend: { display: false } }
            }
        });

        // 3. Power Chart (Horizontal)
        new Chart(document.getElementById('powerChart'), {
            type: 'bar',
            data: {
                labels: data.analysis.map(d => d.keyword),
                datasets: [{
                    label: 'Power Score',
                    data: data.analysis.map(d => d.power_score),
                    backgroundColor: '#818cf8',
                    borderRadius: 8
                }]
            },
            options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                scales: { x: { grid: { color: '#334155' } }, y: { grid: { display : false } } },
                plugins: { legend: { display: false } }
            }
        });

        // 4. Average View Chart
        new Chart(document.getElementById('viewChart'), {
            type: 'line',
            data: {
                labels: data.analysis.map(d => d.keyword),
                datasets: [{
                    label: 'Avg Views',
                    data: data.analysis.map(d => d.avg_views),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, grid: { color: '#334155' } }, x: { grid: { display : false } } },
                plugins: { legend: { display: false } }
            }
        });

        // 5. Table
        const tbody = document.querySelector('#analysisTable tbody');
        data.analysis.forEach(d => {
            const row = `<tr>
                <td style="font-weight: 600">${d.keyword}</td>
                <td>${Math.round(d.avg_views).toLocaleString()}</td>
                <td><span class="badge badge-power">${Math.round(d.power_score).toLocaleString()}</span></td>
                <td><span class="badge badge-recent">${(d.recent_ratio*100).toFixed(0)}%</span></td>
            </tr>`;
            tbody.innerHTML += row;
        });
    </script>
</body>
</html>
"""

    def generate(self, analysis_data: list):
        """데이터를 주입하여 HTML 파일을 생성합니다."""
        if not analysis_data: return

        data_payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": analysis_data
        }

        html_content = self.template.replace("{{DATA_JSON}}", json.dumps(data_payload, ensure_ascii=False))
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"📊 Dashboard updated: {self.output_path}")
