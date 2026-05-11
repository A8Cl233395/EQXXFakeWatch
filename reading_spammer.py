#!/usr/bin/env python3
"""
Reading请求伪造工具 v9.0
"""

import sys, traceback
try:
    import json, time, hashlib, random, string, requests, threading
    from urllib.parse import quote
    from typing import Dict, List, Optional
except Exception as _startup_err:
    print(f"启动失败: {_startup_err}")
    traceback.print_exc()
    input("按回车退出...")
    sys.exit(1)

BASE = "https://eqx.shzhzj.cn/zhjxpthd"

class ReadingSpammer:
    def __init__(self, config: Dict):
        self.auth = config.get('auth', {})
        self.sc = config.get('sign_config', {})
        self.x_token = self.auth.get('x_token', '')
        self.s_token = self.auth.get('s_token', '')
        self.system = self.auth.get('system', 's1')
        self.user_id = self.auth.get('user_id', '')
        self.cookies = self._parse_cookies(self.auth.get('cookies', ''))
        self.secret_key = self.sc.get('secret_key', 'nheam-sign-key-2024')
        self.courses = []
        self.running = False

    def _parse_cookies(self, s: str) -> Dict:
        c = {}
        if s:
            for p in s.split(';'):
                if '=' in p:
                    k, v = p.strip().split('=', 1)
                    c[k] = v
        return c

    def _nonce(self) -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    def _ts(self) -> int:
        return int(time.time() * 1000)

    def _rg_bh(self) -> str:
        h = '0123456789abcdef'
        return '-'.join([''.join(random.choice(h) for _ in range(n)) for n in [8,4,4,4,12]])

    def _sign(self, params: Dict) -> Dict:
        ts = self._ts()
        nonce = self._nonce()
        f = {k: v for k, v in params.items() if k not in ('sign','timestamp','nonce')}
        keys = sorted(k for k in f if f[k] is not None and f[k] != '')
        qs = '&'.join(f"{k}={quote(str(f[k]))}" for k in keys)
        qs = (qs + '&' if qs else '') + f"timestamp={ts}&nonce={nonce}&key={self.secret_key}"
        s = hashlib.md5(qs.encode()).hexdigest().lower()
        return {'sign': s, 'timestamp': ts, 'nonce': nonce,
                'stamp': ts, 'x-sign': s, 'x-timestamp': str(ts), 'x-nonce': nonce}

    def _headers(self, sd: Dict) -> Dict:
        return {
            'Content-Type': 'application/json;charset=UTF-8',
            'x-token': self.x_token, 'system': self.system, 's-token': self.s_token,
            'stamp': str(sd['stamp']), 'x-sign': sd['x-sign'],
            'x-timestamp': sd['x-timestamp'], 'x-nonce': sd['x-nonce'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://eqx.shzhzj.cn/zhjxpt/', 'Origin': 'https://eqx.shzhzj.cn'
        }

    def _post(self, path: str, body: Dict, session: requests.Session) -> Optional[Dict]:
        sd = self._sign(body)
        try:
            r = session.post(f"{BASE}{path}", headers=self._headers(sd), json=body)
            if r.status_code == 200:
                d = r.json()
                if d.get('code') == 0:
                    return d.get('data')
        except:
            pass
        return None

    def fetch_courses(self) -> List[Dict]:
        """从API获取所有课程和章节"""
        session = requests.Session()
        session.cookies.update(self.cookies)

        print(f"  正在获取课程列表...")
        data = self._post('/JwBjxxFromMDLCourse/CourseCardVuenobk',
                          {'id': self.user_id, 'auth': 0}, session)
        if not data:
            print("  [-] 获取课程列表失败")
            return []
        raw = data.get('courseCardlist', [])
        print(f"  [+] 获取到 {len(raw)} 个课程")

        # 2. 获取每个课程的章节
        result = []
        for c in raw:
            cid = c['id']
            cname = c['fullname']
            sd = self._post('/mdlcoursesections/queryPageList3',
                            {'course': str(cid)}, session)
            sections = []
            if sd and isinstance(sd, list) and len(sd) > 0 and sd[0].get('list'):
                sections = [s for s in sd[0]['list'] if s]
                sections = [{
                    'section': s['section'],
                    'name': s.get('subname', ''),
                    'jxhdids': [int(x.strip()) for x in (s.get('sequence','')).split(',') if x.strip()]
                } for s in sections]
            result.append({
                'id': cid,
                'name': cname,
                'sections': sections
            })
            jcount = sum(len(s['jxhdids']) for s in sections)
            print(f"    {cname}: {len(sections)}章节, {jcount}课件")

        self.courses = result
        return result

    def _do_reading(self, session: requests.Session, url: str, course_id: int, jxhdid: int, rg_bh: str = None) -> bool:
        if rg_bh is None:
            rg_bh = self._rg_bh()
        body = {'rg_bh': rg_bh, 'rg_yhid': self.user_id, 'rg_kcid': course_id,
                'rg_jxhdid': jxhdid, 'rg_zylx': 'mp4', 'rg_pjbzbh': '', 'rg_sfkw': ''}
        return self._post(url, body, session) is not None

    def _spam_one(self, course_id, cname, jxhdid, sname, interval, idx, total):
        """每个课件独立线程：每20轮 finishRead + 重新 startRead"""
        label = f"[{idx}/{total}]"
        cycle = 0
        ok = err = 0

        session = requests.Session()
        session.cookies.update(self.cookies)

        # 同一周期内 startRead/reading/finishRead 共享同一个 rg_bh
        rg_bh = self._rg_bh()

        def _start():
            nonlocal ok, err, rg_bh
            rg_bh = self._rg_bh()
            o = self._do_reading(session, '/rzgkjl/startRead', course_id, jxhdid, rg_bh)
            if o: ok += 1; print(f"{label} startRead OK  | {sname}")
            else:  err += 1; print(f"{label} startRead FAIL | {sname}")

        def _finish():
            nonlocal ok, err
            o = self._do_reading(session, '/rzgkjl/finishRead', course_id, jxhdid, rg_bh)
            if o: ok += 1
            else:  err += 1

        _start()

        while self.running:
            o = self._do_reading(session, '/rzgkjl/reading', course_id, jxhdid, rg_bh)
            cycle += 1
            if o: ok += 1
            else:  err += 1

            if cycle % 10 == 0:
                print(f"{label} {sname} | req:{cycle} ok:{ok} err:{err}")

            if cycle % 20 == 0:
                _finish()
                print(f"{label} finishRead | {sname} | 开始新周期")
                _start()

            time.sleep(interval)

    def spam_course(self, course_id: int, interval: float):
        course = next((c for c in self.courses if c['id'] == course_id), None)
        if not course:
            print("[-] 课程不存在"); return

        # 收集所有课件
        all_items = []
        for s in course.get('sections', []):
            for j in s.get('jxhdids', []):
                all_items.append((j, s['name']))

        total = len(all_items)
        print(f"\n[+] 共 {total} 个课件，并行刷课")
        print("[+] 按 Ctrl+C 停止")

        self.running = True
        threads = []

        for idx, (jxhdid, sname) in enumerate(all_items, 1):
            t = threading.Thread(
                target=self._spam_one,
                args=(course_id, course['name'], jxhdid, sname, interval, idx, total),
                daemon=True
            )
            threads.append(t)
            t.start()

        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print("\n[+] 正在停止所有线程...")

    def run(self):
        print("=" * 60)
        print("  Reading v9.0")
        print("  全部课程列表、章节信息、请求签名均由本程序完成")
        print("=" * 60)

        self.fetch_courses()
        if not self.courses:
            print("[-] 获取课程列表失败，请检查认证信息是否过期")
            return

        print(f"\n{'─' * 40}")
        print(f"  共 {len(self.courses)} 个课程可选")
        print(f"{'─' * 40}")
        for i, c in enumerate(self.courses):
            total = sum(len(s['jxhdids']) for s in c['sections'])
            print(f"  {i+1:2d}. {c['name']}")
            print(f"       {len(c['sections'])} 个章节, {total} 个课件")

        while True:
            try:
                ch = input(f"\n请选择课程编号 (1-{len(self.courses)}, q退出): ").strip()
                if ch.lower() == 'q':
                    print("退出")
                    return
                idx = int(ch) - 1
                if 0 <= idx < len(self.courses):
                    c = self.courses[idx]
                    print(f"\n已选择: {c['name']}")
                    print(f"{'─' * 40}")
                    for i, s in enumerate(c['sections']):
                        print(f"  {i+1}. {s['name']}  教学活动ID: {s['jxhdids']}")
                    total = sum(len(s['jxhdids']) for s in c['sections'])
                    iv = float(input(f"\n请求间隔秒 (默认1.0, 共{total}课件并行): ") or "1.0")
                    self.spam_course(c['id'], iv)
                    break
                else:
                    print(f"请输入 1-{len(self.courses)} 范围内的数字")
            except ValueError:
                print("请输入数字")

def main():
    print("""
╔══════════════════════════════════════════════════════╗
║        Reading请求伪造工具 v9.0                      ║
║        支持全课程自动并行刷课                           ║
╚══════════════════════════════════════════════════════╝

使用流程:
  1. 浏览器打开 https://eqx.shzhzj.cn/zhjxpt/#/
  2. 登录后，F12 → Console → 粘贴运行 export_auth.js
  3. 弹窗中按提示手动获取 JSESSIONID 并合并
  4. 点击"点击复制"，将 JSON 粘贴到下方

────────────────────────────────────────────────────
请粘贴 JSON (粘贴后按两次 Enter 结束):
""")
    lines = []; empty = 0
    while True:
        try:
            line = input()
            if line.strip() == '': empty += 1; 
            if empty >= 2: break
            if line.strip() != '': empty = 0
            lines.append(line)
        except EOFError: break
    js = '\n'.join(lines).strip()
    if not js: print("无输入"); return
    try:
        cfg = json.loads(js)
        print("[+] 解析成功")
        ReadingSpammer(cfg).run()
    except json.JSONDecodeError as e:
        print(f"[-] JSON错误: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as _e:
        print(f"\n[-] 错误: {_e}")
        traceback.print_exc()
    finally:
        input("\n按回车退出...")