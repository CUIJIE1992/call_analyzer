// Cloudflare Workers 入口文件
// 服务静态文件和 HTML 页面

// CSS 样式内容
const CSS_CONTENT = `/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #2ed573;
    --warning-color: #ffa502;
    --danger-color: #ff4757;
    --text-primary: #2d3436;
    --text-secondary: #636e72;
    --bg-light: #f8f9fa;
    --bg-card: #ffffff;
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 20px;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
}

/* 头部样式 */
.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white;
    padding: 30px 40px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-icon {
    font-size: 3em;
}

.logo-text h1 {
    font-size: 1.8em;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 0.95em;
    opacity: 0.9;
}

.header-badge {
    display: flex;
    gap: 12px;
}

.badge-item {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9em;
    backdrop-filter: blur(10px);
}

/* 导航样式 */
.main-nav {
    background: rgba(0, 0, 0, 0.1);
    margin: 0 -40px -30px;
    padding: 15px 40px;
}

.nav-container {
    display: flex;
    gap: 10px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: var(--radius-md);
    color: white;
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-item:hover,
.nav-item.active {
    background: rgba(255, 255, 255, 0.2);
}

.nav-icon {
    font-size: 1.2em;
}

/* 模式选择 */
.mode-section {
    padding: 30px 40px 0;
}

.mode-tabs {
    display: flex;
    gap: 10px;
    border-bottom: 2px solid var(--bg-light);
}

.mode-tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 15px 25px;
    border: none;
    background: none;
    font-size: 1em;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.mode-tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.mode-icon {
    font-size: 1.2em;
}

/* 上传区域 */
.upload-section {
    padding: 30px 40px;
}

.upload-area {
    border: 3px dashed var(--primary-color);
    border-radius: var(--radius-lg);
    padding: 50px;
    text-align: center;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    transition: all 0.3s ease;
}

.upload-content h2 {
    font-size: 1.8em;
    margin-bottom: 10px;
    color: var(--text-primary);
}

.upload-subtitle {
    color: var(--text-secondary);
    margin-bottom: 25px;
}

.upload-icon-wrapper {
    position: relative;
    display: inline-block;
    margin-bottom: 20px;
}

.upload-icon {
    font-size: 4em;
    position: relative;
    z-index: 1;
}

.upload-icon-bg {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: 50%;
    opacity: 0.1;
}

.upload-info {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 20px;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
}

.info-icon {
    color: var(--success-color);
    font-weight: bold;
}

/* 按钮样式 */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    border: none;
    border-radius: var(--radius-md);
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.btn-secondary {
    background: var(--bg-light);
    color: var(--text-primary);
}

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid #ddd;
}

.btn-large {
    padding: 15px 30px;
    font-size: 1.1em;
}

.btn-icon {
    font-size: 1.2em;
}

/* 批量队列 */
.batch-queue-section {
    padding: 0 40px 30px;
}

.batch-queue-card {
    background: var(--bg-light);
    border-radius: var(--radius-md);
    padding: 25px;
}

.batch-queue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.batch-queue-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.2em;
    font-weight: 600;
}

.batch-queue-actions {
    display: flex;
    gap: 10px;
}

.empty-queue {
    text-align: center;
    padding: 40px;
    color: var(--text-secondary);
}

/* 批量进度 */
.batch-progress-section {
    padding: 0 40px 30px;
}

.batch-progress-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border-radius: var(--radius-md);
    padding: 25px;
}

.batch-progress-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}

.batch-progress-title {
    font-size: 1.2em;
    font-weight: 600;
}

.batch-progress-bar-wrapper {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.batch-progress-bar {
    flex: 1;
    height: 8px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.batch-progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    border-radius: 4px;
    transition: width 0.3s ease;
}

.batch-progress-percent {
    font-weight: 600;
    color: var(--primary-color);
}

.batch-progress-text {
    color: var(--text-secondary);
    margin-bottom: 10px;
}

.batch-current-file {
    font-size: 0.9em;
    color: var(--text-secondary);
}

/* 批量结果 */
.batch-summary-section {
    padding: 0 40px 40px;
}

.batch-summary-card {
    background: var(--bg-light);
    border-radius: var(--radius-md);
    padding: 25px;
}

.batch-summary-header {
    margin-bottom: 20px;
}

.batch-summary-footer {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}

/* 历史页面和仪表盘 */
.history-section,
.dashboard-section {
    padding: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }
    
    .header {
        padding: 20px;
    }
    
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }
    
    .header-badge {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .main-nav {
        margin: 0 -20px -20px;
        padding: 10px 20px;
    }
    
    .nav-container {
        justify-content: center;
    }
    
    .upload-section,
    .batch-queue-section,
    .batch-progress-section,
    .batch-summary-section {
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .upload-area {
        padding: 30px 20px;
    }
    
    .upload-info {
        flex-direction: column;
        gap: 10px;
    }
}`;

// HTML 页面内容
const INDEX_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>购房意向智能分析系统</title>
    <style>${CSS_CONTENT}</style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <span class="logo-icon">🏠</span>
                    <div class="logo-text">
                        <h1>购房意向智能分析系统</h1>
                        <p class="subtitle">AI驱动的房产销售洞察与客户跟进策略</p>
                    </div>
                </div>
                <div class="header-badge">
                    <span class="badge-item">🎯 客户评级</span>
                    <span class="badge-item">📊 意向分析</span>
                    <span class="badge-item">💡 跟进策略</span>
                </div>
            </div>
            <nav class="main-nav">
                <div class="nav-container">
                    <a href="/" class="nav-item active">
                        <span class="nav-icon">🏠</span>
                        <span>首页</span>
                    </a>
                    <a href="/history" class="nav-item">
                        <span class="nav-icon">📋</span>
                        <span>历史记录</span>
                    </a>
                    <a href="/dashboard" class="nav-item">
                        <span class="nav-icon">📊</span>
                        <span>统计仪表盘</span>
                    </a>
                </div>
            </nav>
        </header>

        <!-- 模式选择 -->
        <div class="mode-section">
            <div class="mode-tabs">
                <button class="mode-tab active" data-mode="file">
                    <span class="mode-icon">📁</span>
                    <span>上传文件</span>
                </button>
                <button class="mode-tab" data-mode="text">
                    <span class="mode-icon">📝</span>
                    <span>文本分析</span>
                </button>
            </div>
        </div>

        <!-- 上传区域 -->
        <div class="upload-section" id="uploadSection">
            <div class="upload-area" id="uploadArea">
                <div class="upload-content">
                    <div class="upload-icon-wrapper">
                        <div class="upload-icon">📁</div>
                        <div class="upload-icon-bg"></div>
                    </div>
                    <h2>拖放MP3文件到这里</h2>
                    <p class="upload-subtitle">或者点击下方按钮选择文件（支持多选）</p>
                    <input type="file" id="fileInput" accept=".mp3" multiple style="display: none;">
                    <button class="btn btn-primary btn-large" id="selectBtn">
                        <span class="btn-icon">📂</span>
                        <span>选择文件</span>
                    </button>
                    <div class="upload-info">
                        <div class="info-item">
                            <span class="info-icon">✓</span>
                            <span>支持格式：MP3</span>
                        </div>
                        <div class="info-item">
                            <span class="info-icon">✓</span>
                            <span>最大文件：50MB</span>
                        </div>
                        <div class="info-item">
                            <span class="info-icon">✓</span>
                            <span>支持批量上传</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 批量上传文件队列 -->
        <div class="batch-queue-section" id="batchQueueSection">
            <div class="batch-queue-card">
                <div class="batch-queue-header">
                    <div class="batch-queue-title">
                        <span class="batch-queue-title-icon">📋</span>
                        <span>文件队列</span>
                    </div>
                    <div class="batch-queue-actions">
                        <button class="btn btn-primary" onclick="alert('功能开发中...')">
                            <span>🚀</span> 开始批量处理
                        </button>
                        <button class="btn btn-ghost" onclick="alert('功能开发中...')">
                            <span>🗑️</span> 清空队列
                        </button>
                    </div>
                </div>
                <div class="batch-file-list" id="batchFileList">
                    <div class="empty-queue">暂无文件，请选择或拖拽文件到上传区域</div>
                </div>
            </div>
        </div>
        
        <!-- 批量处理进度 -->
        <div class="batch-progress-section" id="batchProgressSection">
            <div class="batch-progress-card">
                <div class="batch-progress-header">
                    <span class="batch-progress-icon">⚙️</span>
                    <h3 class="batch-progress-title">批量处理进度</h3>
                </div>
                <div class="batch-progress-bar-wrapper">
                    <div class="batch-progress-bar">
                        <div class="batch-progress-fill" id="batchProgressFill"></div>
                    </div>
                    <span class="batch-progress-percent" id="batchProgressPercent">0%</span>
                </div>
                <p class="batch-progress-text" id="batchProgressText">准备中...</p>
                <div class="batch-current-file">
                    <span class="batch-current-file-label">当前处理：</span>
                    <span class="batch-current-file-name" id="batchCurrentFile">-</span>
                </div>
            </div>
        </div>
        
        <!-- 批量结果摘要 -->
        <div class="batch-summary-section" id="batchSummarySection">
            <div class="batch-summary-card">
                <div class="batch-summary-header">
                    <h3>📊 批量处理结果</h3>
                </div>
                <div id="batchSummaryList"></div>
                <div class="batch-summary-footer">
                    <button class="btn btn-primary btn-large" onclick="alert('功能开发中...')">
                        <span>📥</span> 导出批量报告
                    </button>
                    <button class="btn btn-secondary btn-large" onclick="alert('功能开发中...')">
                        <span>🔄</span> 处理新文件
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 简单的文件选择功能
        document.getElementById('selectBtn').addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
        
        document.getElementById('fileInput').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                alert('已选择 ' + e.target.files.length + ' 个文件，功能开发中...');
            }
        });
    </script>
</body>
</html>`;

const HISTORY_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>历史记录 - 购房意向智能分析系统</title>
    <style>${CSS_CONTENT}</style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <span class="logo-icon">🏠</span>
                    <div class="logo-text">
                        <h1>购房意向智能分析系统</h1>
                        <p class="subtitle">AI驱动的房产销售洞察与客户跟进策略</p>
                    </div>
                </div>
            </div>
            <nav class="main-nav">
                <div class="nav-container">
                    <a href="/" class="nav-item">
                        <span class="nav-icon">🏠</span>
                        <span>首页</span>
                    </a>
                    <a href="/history" class="nav-item active">
                        <span class="nav-icon">📋</span>
                        <span>历史记录</span>
                    </a>
                    <a href="/dashboard" class="nav-item">
                        <span class="nav-icon">📊</span>
                        <span>统计仪表盘</span>
                    </a>
                </div>
            </nav>
        </header>
        
        <div class="history-section">
            <h2>📋 历史记录</h2>
            <p>功能开发中...</p>
        </div>
    </div>
</body>
</html>`;

const DASHBOARD_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>统计仪表盘 - 购房意向智能分析系统</title>
    <style>${CSS_CONTENT}</style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <span class="logo-icon">🏠</span>
                    <div class="logo-text">
                        <h1>购房意向智能分析系统</h1>
                        <p class="subtitle">AI驱动的房产销售洞察与客户跟进策略</p>
                    </div>
                </div>
            </div>
            <nav class="main-nav">
                <div class="nav-container">
                    <a href="/" class="nav-item">
                        <span class="nav-icon">🏠</span>
                        <span>首页</span>
                    </a>
                    <a href="/history" class="nav-item">
                        <span class="nav-icon">📋</span>
                        <span>历史记录</span>
                    </a>
                    <a href="/dashboard" class="nav-item active">
                        <span class="nav-icon">📊</span>
                        <span>统计仪表盘</span>
                    </a>
                </div>
            </nav>
        </header>
        
        <div class="dashboard-section">
            <h2>📊 统计仪表盘</h2>
            <p>功能开发中...</p>
        </div>
    </div>
</body>
</html>`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // 服务 CSS 文件
    if (pathname.startsWith('/static/css/')) {
      return new Response(CSS_CONTENT, {
        headers: {
          'Content-Type': 'text/css',
          'Cache-Control': 'public, max-age=31536000',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // 服务 HTML 页面
    if (pathname === '/' || pathname === '/index.html') {
      return new Response(INDEX_HTML, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8'
        }
      });
    }
    
    if (pathname === '/history' || pathname === '/history.html') {
      return new Response(HISTORY_HTML, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8'
        }
      });
    }
    
    if (pathname === '/dashboard' || pathname === '/dashboard.html') {
      return new Response(DASHBOARD_HTML, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8'
        }
      });
    }
    
    // 默认返回首页
    return new Response(INDEX_HTML, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8'
      }
    });
  }
};
