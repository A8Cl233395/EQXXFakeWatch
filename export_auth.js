// 认证信息导出工具
// F12 → Console 粘贴运行，按提示操作
(function() {
  function extractSToken() {
    var sources = [
      (window.globalConfig || {}).wdyp,
      (window.globalConfig || {}).zsdjndUrl,
      (window.globalConfig || {}).ThirdPartyInterfaces,
      localStorage.getItem('temp_topath')
    ].filter(Boolean);
    for (var i = 0; i < sources.length; i++) {
      var m = sources[i].match(/stoken=([^&]+)/);
      if (m) return decodeURIComponent(m[1]);
    }
    return '';
  }

  var data = {
    auth: {
      x_token: localStorage.getItem('x-token'),
      s_token: extractSToken(),
      system: 's1',
      cookies: document.cookie,
      user_id: localStorage.getItem('userId'),
      username: localStorage.getItem('username'),
      user_name: localStorage.getItem('uName')
    },
    sign_config: {
      secret_key: 'nheam-sign-key-2024'
    },
    export_time: Date.now()
  };

  var jsonStr = JSON.stringify(data);
  var mergedJsonStr = '';

  // ========== 弹窗 ==========
  var overlay = document.createElement('div');
  overlay.id = '__exportOverlay';
  overlay.style.cssText =
    'position:fixed;top:0;left:0;width:100%;height:100%;' +
    'background:rgba(0,0,0,0.7);z-index:2147483647;' +
    'display:flex;justify-content:center;align-items:center;' +
    'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;';

  var box = document.createElement('div');
  box.style.cssText =
    'background:#fff;padding:28px 32px;border-radius:12px;' +
    'max-width:600px;width:92%;max-height:88vh;overflow-y:auto;' +
    'box-shadow:0 20px 60px rgba(0,0,0,0.3);line-height:1.6;color:#1a1a1a;font-size:14px;';

  // ---------- 标题 ----------
  var h1 = document.createElement('h2');
  h1.textContent = '认证信息导出';
  h1.style.cssText = 'margin:0 0 6px 0;font-size:22px;color:#c0392b;font-weight:700;';

  var sub = document.createElement('p');
  sub.textContent = '已自动获取: x-token, s-token, user_id, MoodleSession';
  sub.style.cssText = 'margin:0 0 18px 0;font-size:13px;color:#666;';

  // ---------- 步骤2：JSESSIONID ----------
  var secTitle = document.createElement('h3');
  secTitle.textContent = '还需要手动获取 JSESSIONID';
  secTitle.style.cssText = 'margin:0 0 10px 0;font-size:16px;color:#e67e22;font-weight:600;';

  var why = document.createElement('div');
  why.style.cssText =
    'background:#fff3cd;border-left:4px solid #f39c12;padding:10px 14px;' +
    'border-radius:4px;margin-bottom:14px;font-size:13px;color:#856404;';
  why.innerHTML = '<b>为什么需要手动获取？</b><br>JSESSIONID 是 HttpOnly Cookie，JavaScript 没有权限读取它，但它又是所有 API 请求必需的。';

  var steps = document.createElement('ol');
  steps.style.cssText = 'margin:0 0 14px 0;padding-left:20px;font-size:13px;line-height:2;';
  steps.innerHTML =
    '<li>打开浏览器 <b>F12 → Application（应用程序）</b> 标签页</li>' +
    '<li>左侧面板找到 <b>Storage → Cookies → https://eqx.shzhzj.cn</b></li>' +
    '<li>在右侧表格中找到 <b>Name 为 JSESSIONID</b> 的那一行</li>' +
    '<li>双击那一行的 <b>Value 列</b>，全选并复制（Ctrl+C）</li>' +
    '<li>将复制的值粘贴到下方输入框中</li>';

  var inputRow = document.createElement('div');
  inputRow.style.cssText = 'display:flex;gap:8px;margin-bottom:14px;align-items:center;';

  var input = document.createElement('input');
  input.id = '__jsidInput';
  input.placeholder = '在此粘贴 JSESSIONID 的值';
  input.style.cssText =
    'flex:1;padding:10px 12px;font-size:14px;border:2px solid #ddd;' +
    'border-radius:6px;outline:none;transition:border-color .2s;';
  input.onfocus = function() { this.style.borderColor = '#3498db'; };
  input.onblur = function() { this.style.borderColor = '#ddd'; };

  var mergeBtn = document.createElement('button');
  mergeBtn.textContent = '合并';
  mergeBtn.style.cssText =
    'padding:10px 24px;background:#2196F3;color:#fff;border:none;' +
    'border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;' +
    'transition:background .2s;white-space:nowrap;';
  mergeBtn.onmouseenter = function() { this.style.background = '#1976D2'; };
  mergeBtn.onmouseleave = function() { this.style.background = '#2196F3'; };

  inputRow.appendChild(input);
  inputRow.appendChild(mergeBtn);

  // ---------- 结果区域 ----------
  var result = document.createElement('div');
  result.id = '__resultArea';
  result.style.cssText = 'display:none;';

  var resTitle = document.createElement('h3');
  resTitle.textContent = '请复制下方 JSON';
  resTitle.style.cssText = 'margin:0 0 6px 0;font-size:16px;color:#27ae60;font-weight:600;';

  var info = document.createElement('p');
  info.id = '__infoText';
  info.style.cssText = 'margin:0 0 10px 0;font-size:13px;color:#666;';

  var textarea = document.createElement('textarea');
  textarea.id = '__output';
  textarea.readOnly = true;
  textarea.style.cssText =
    'width:100%;height:220px;font-size:12px;font-family:"SF Mono",Consolas,monospace;' +
    'border:2px solid #27ae60;border-radius:6px;padding:12px;resize:vertical;' +
    'background:#f9fbfd;color:#333;box-sizing:border-box;';

  var btnRow = document.createElement('div');
  btnRow.style.cssText = 'margin-top:10px;display:flex;gap:10px;align-items:center;';

  var copyBtn = document.createElement('button');
  copyBtn.textContent = '点击复制';
  copyBtn.style.cssText =
    'padding:10px 24px;background:#4CAF50;color:#fff;border:none;' +
    'border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;transition:background .2s;';
  copyBtn.onmouseenter = function() { this.style.background = '#388E3C'; };
  copyBtn.onmouseleave = function() { this.style.background = '#4CAF50'; };

  var status = document.createElement('span');
  status.id = '__copyStatus';
  status.style.cssText = 'color:#27ae60;font-size:14px;font-weight:600;display:none;';

  btnRow.appendChild(copyBtn);
  btnRow.appendChild(status);

  result.appendChild(resTitle);
  result.appendChild(info);
  result.appendChild(textarea);
  result.appendChild(btnRow);

  // ---------- 底部关闭 ----------
  var closeBtn = document.createElement('button');
  closeBtn.textContent = '关闭窗口';
  closeBtn.style.cssText =
    'display:block;width:100%;margin-top:18px;padding:10px;' +
    'background:#e74c3c;color:#fff;border:none;border-radius:6px;' +
    'font-size:14px;font-weight:600;cursor:pointer;transition:background .2s;';
  closeBtn.onmouseenter = function() { this.style.background = '#c0392b'; };
  closeBtn.onmouseleave = function() { this.style.background = '#e74c3c'; };
  closeBtn.onclick = function() {
    document.body.removeChild(overlay);
  };

  // ========== 组装 DOM ==========
  box.appendChild(h1);
  box.appendChild(sub);
  box.appendChild(secTitle);
  box.appendChild(why);
  box.appendChild(steps);
  box.appendChild(inputRow);
  box.appendChild(result);
  box.appendChild(closeBtn);
  overlay.appendChild(box);
  document.body.appendChild(overlay);

  // ========== 事件绑定 ==========
  mergeBtn.onclick = function() {
    var jsid = input.value.trim();
    if (!jsid) {
      input.style.borderColor = '#e74c3c';
      setTimeout(function() { input.style.borderColor = '#ddd'; }, 1500);
      return;
    }
    // 合并 cookies
    data.auth.cookies = 'JSESSIONID=' + jsid + '; ' + data.auth.cookies;
    mergedJsonStr = JSON.stringify(data);
    textarea.value = mergedJsonStr;
    info.textContent = 'JSESSIONID 已合并到 cookies 字段中';
    result.style.display = 'block';
    textarea.select();

    // 尝试自动复制
    try {
      document.execCommand('copy');
      status.textContent = '已自动复制！';
      status.style.display = 'inline';
    } catch(e) {
      status.textContent = '请点击"点击复制"按钮';
      status.style.display = 'inline';
    }

    // 滚动到结果区
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  copyBtn.onclick = function() {
    textarea.select();
    try {
      document.execCommand('copy');
      status.textContent = '已复制！';
      status.style.display = 'inline';
    } catch(e) {
      status.textContent = '复制失败，请手动 Ctrl+C';
      status.style.display = 'inline';
    }
    setTimeout(function() { status.style.display = 'none'; }, 3000);
  };

  // Enter 键提交
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') mergeBtn.click();
  });

  // 自动聚焦输入框
  setTimeout(function() { input.focus(); }, 200);

  console.log('%c✅ 认证信息已就绪', 'color:green;font-size:14px;');
  console.log(data);
  console.log('%c⚠️ 请根据弹窗提示手动获取 JSESSIONID', 'color:orange;');

  return data;
})();