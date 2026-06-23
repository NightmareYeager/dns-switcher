"""
DNS Switcher v4 — Auto-Update Edition
SQLite backend · Custom DNS · Smart Benchmark · Hosts Injector · Auto-Updater
"""
import sys, os, platform, subprocess, threading, socket, time, ctypes, math
import sqlite3, json, urllib.request, urllib.error, ssl, shutil, tempfile, webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# ──────────────────────────── VERSION / AUTHOR ───────────────────────────────
__version__  = "4.0.0"
AUTHOR       = "NightmareYeager"
GITHUB_REPO  = "NightmareYeager/dns-switcher"
GITHUB_URL   = "https://github.com/NightmareYeager"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RAW_SCRIPT   = "https://raw.githubusercontent.com/{repo}/{tag}/dns_switcher_pro.py"

# ─────────────────────────── PALETTE ──────────────────────────────────────────
C = {
    "bg":         "#080c10",
    "surface":    "#0d1117",
    "card":       "#0f1923",
    "card_hi":    "#131f2e",
    "active":     "#051a0c",
    "accent":     "#00ff88",
    "cyan":       "#00cfff",
    "purple":     "#a855f7",
    "warn":       "#facc15",
    "danger":     "#ff4757",
    "text":       "#cdd9e5",
    "muted":      "#4a5a6a",
    "border":     "#1a2535",
    "border_hi":  "#1a4d35",
    "tag_bg":     "#0a1628",
}
TAG_COL = {
    "BYPASS":  "#00ff88", "GAMING":  "#ff6b35",
    "SECURE":  "#00cfff", "STABLE":  "#a855f7",
    "FAST":    "#facc15", "GLOBAL":  "#94a3b8",
    "MOBILE":  "#f472b6", "CUSTOM":  "#fb923c",
    "PRIVACY": "#818cf8",
}
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ──────────────────────────── DEFAULT DATA ────────────────────────────────────
DEFAULT_DNS = [
    (1,"رادار",      "10.202.10.10",   "10.202.10.11",    "داخلی — عبور از تحریم و گیمینگ",    "bypass","BYPASS",0),
    (2,"الکترو",     "78.157.42.100",  "78.157.42.101",   "داخلی — سرعت خوب بازی آنلاین",      "gaming","GAMING",0),
    (3,"شکن",        "178.22.122.100", "185.51.200.2",    "داخلی — دور زدن تحریم‌ها",           "bypass","BYPASS",0),
    (4,"بگذر",       "185.55.226.26",  "185.55.225.25",   "داخلی — عبور از محدودیت‌ها",         "bypass","BYPASS",0),
    (5,"Quad9",      "9.9.9.9",        "149.112.112.112", "امنیت بالا — بلاک مالویر",           "secure","SECURE",0),
    (6,"UltraDNS",   "64.6.64.6",      "64.6.65.6",       "پایدار — مناسب دانلود بازی",         "download","STABLE",0),
    (7,"UltraDNS 2", "156.154.70.2",   "156.154.71.2",    "پایدار — دانلود حجیم",              "download","STABLE",0),
    (8,"NTT",        "129.250.35.250", "129.250.35.251",  "سرعت دانلود — کاربران ایرانی",       "download","FAST",0),
    (9,"OpenDNS",    "208.67.222.222", "208.67.220.220",  "بهبود پینگ و سرعت دانلود",           "general","GLOBAL",0),
    (10,"Xbox DNS",  "37.220.84.124",  "",                "مخصوص Xbox — تغییر منطقه",          "gaming","GAMING",0),
    (11,"همراه اول", "208.67.220.200", "208.67.222.222",  "مخصوص اینترنت موبایل",               "mobile","MOBILE",0),
    (12,"ایرانسل",   "74.82.42.42",    "0.0.0.0",         "مخصوص اینترنت موبایل",               "mobile","MOBILE",0),
    (13,"رایتل",     "91.239.100.100", "89.223.43.71",    "مخصوص اینترنت موبایل",               "mobile","MOBILE",0),
    (14,"Cloudflare","1.1.1.1",        "1.0.0.1",         "سریع‌ترین DNS جهان — وب‌گردی",        "general","FAST",0),
    (15,"Google",    "8.8.8.8",        "8.8.4.4",         "مناسب جستجو — پایدار",               "general","GLOBAL",0),
    (16,"AdGuard",   "94.140.14.14",   "94.140.15.15",    "بلاک تبلیغات+تراکر — حریم خصوصی",   "privacy","PRIVACY",0),
    (17,"Mullvad",   "194.242.2.2",    "194.242.2.3",     "حداکثر حریم خصوصی — no-log",        "privacy","PRIVACY",0),
    (18,"Shecan",    "178.22.122.100", "185.51.200.2",    "داخلی — دور زدن سانسور",             "bypass","BYPASS",0),
]

GAME_HOSTS = {
    "Steam":         ["208.64.202.87","208.64.202.81","104.64.130.111","185.25.182.1"],
    "Epic Games":    ["13.226.63.59","13.226.63.2","13.226.63.73","13.226.63.33"],
    "PlayStation":   ["103.0.26.140","103.0.26.144","208.67.222.222"],
    "Xbox Live":     ["13.68.180.60","52.183.116.234","104.40.75.53"],
    "Battle.net":    ["24.105.30.129","116.202.224.146","185.60.112.157"],
    "Origin/EA":     ["159.153.235.77","159.153.235.32","192.30.15.24"],
    "Riot/Valorant": ["185.40.64.69","162.249.5.229","185.40.64.69"],
}

# ──────────────────────────── DATABASE ───────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dns_switcher.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dns_entries (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            primary_ip   TEXT NOT NULL,
            secondary_ip TEXT DEFAULT '',
            note     TEXT DEFAULT '',
            category TEXT DEFAULT 'general',
            tag      TEXT DEFAULT 'GLOBAL',
            is_custom INTEGER DEFAULT 0
        )
    """)
    c.execute("SELECT COUNT(*) FROM dns_entries")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO dns_entries(id,name,primary_ip,secondary_ip,note,category,tag,is_custom) VALUES(?,?,?,?,?,?,?,?)",
            DEFAULT_DNS
        )
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_dns_list():
    conn = get_db()
    rows = conn.execute("SELECT * FROM dns_entries ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_dns_entry(name, primary, secondary, note, category, tag):
    conn = get_db()
    conn.execute(
        "INSERT INTO dns_entries(name,primary_ip,secondary_ip,note,category,tag,is_custom) VALUES(?,?,?,?,?,?,1)",
        (name, primary, secondary, note, category, tag)
    )
    conn.commit()
    conn.close()

def delete_dns_entry(entry_id):
    conn = get_db()
    conn.execute("DELETE FROM dns_entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()

def save_setting(key, val):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key,str(val)))
    conn.commit(); conn.close()

def load_setting(key, default=None):
    conn = get_db()
    r = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return r[0] if r else default

# ──────────────────────────── OS / ADMIN ─────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() if platform.system()=="Windows" else os.geteuid()==0
    except: return False

def get_win_ifaces():
    try:
        r = subprocess.run(["netsh","interface","show","interface"],capture_output=True,text=True)
        return [" ".join(l.split()[3:]) for l in r.stdout.splitlines() if "Connected" in l] or ["Wi-Fi","Ethernet"]
    except: return ["Wi-Fi","Ethernet"]

def apply_dns_os(dns):
    p = dns["primary_ip"]; s = dns["secondary_ip"]
    sys_ = platform.system()
    if sys_ == "Windows":
        iface = get_win_ifaces()[0]
        subprocess.run(["netsh","interface","ip","set","dns",iface,"static",p],capture_output=True)
        if s and s not in("","0.0.0.0","-"):
            subprocess.run(["netsh","interface","ip","add","dns",iface,s,"index=2"],capture_output=True)
    elif sys_ == "Linux":
        lines = [f"# DNS Switcher — {dns['name']}\n", f"nameserver {p}\n"]
        if s and s not in("","0.0.0.0","-"): lines.append(f"nameserver {s}\n")
        open("/etc/resolv.conf","w").writelines(lines)
    else:
        raise OSError(f"Unsupported OS: {sys_}")

def reset_dns_os():
    sys_ = platform.system()
    if sys_ == "Windows":
        for i in get_win_ifaces():
            subprocess.run(["netsh","interface","ip","set","dns",i,"dhcp"],capture_output=True)
    elif sys_ == "Linux":
        open("/etc/resolv.conf","w").write("nameserver 8.8.8.8\n")

def inject_hosts(hosts_map):
    """Add/update static host entries. hosts_map = {hostname: ip}"""
    if platform.system() == "Windows":
        path = r"C:\Windows\System32\drivers\etc\hosts"
    else:
        path = "/etc/hosts"
    with open(path,"r") as f:
        lines = f.readlines()
    # remove old switcher lines
    lines = [l for l in lines if "# DNS-Switcher" not in l]
    for host, ip in hosts_map.items():
        lines.append(f"{ip}\t{host}\t# DNS-Switcher\n")
    with open(path,"w") as f:
        f.writelines(lines)

def clear_hosts_injections():
    if platform.system() == "Windows":
        path = r"C:\Windows\System32\drivers\etc\hosts"
    else:
        path = "/etc/hosts"
    with open(path,"r") as f:
        lines = f.readlines()
    with open(path,"w") as f:
        f.writelines(l for l in lines if "# DNS-Switcher" not in l)

def flush_dns():
    sys_ = platform.system()
    if sys_ == "Windows":
        subprocess.run(["ipconfig","/flushdns"],capture_output=True)
    elif sys_ == "Linux":
        for cmd in [["systemctl","restart","systemd-resolved"],
                    ["service","nscd","restart"]]:
            try: subprocess.run(cmd,capture_output=True)
            except: pass

# ──────────────────────────── PING / TEST ────────────────────────────────────
def tcp_ping(ip, port=53, timeout=2.0):
    if not ip or ip in("","0.0.0.0","-"): return None
    try:
        t = time.time()
        s = socket.socket(); s.settimeout(timeout); s.connect((ip,port)); s.close()
        return round((time.time()-t)*1000,1)
    except: return None

def dns_resolve_test(ip, domain="google.com", timeout=2.0):
    """Return ms for a real DNS lookup, or None."""
    if not ip or ip in("","0.0.0.0","-"): return None
    try:
        t = time.time()
        resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        resolver.settimeout(timeout)
        # Build a minimal DNS query for 'google.com'
        tid = b'\xab\xcd'
        flags = b'\x01\x00'
        counts = b'\x00\x01\x00\x00\x00\x00\x00\x00'
        qname = b''.join(len(p).to_bytes(1,'big')+p.encode() for p in domain.split('.'))+b'\x00'
        qtype = b'\x00\x01'; qclass = b'\x00\x01'
        query = tid+flags+counts+qname+qtype+qclass
        resolver.sendto(query,(ip,53))
        resolver.recv(512)
        resolver.close()
        return round((time.time()-t)*1000,1)
    except: return None

def ping_color(ms):
    if ms is None: return C["muted"]
    if ms < 80:   return C["accent"]
    if ms < 200:  return C["warn"]
    return C["danger"]

# ──────────────────────────── ANIMATED BAR ───────────────────────────────────
class PingBar(tk.Canvas):
    W,H = 88,5
    def __init__(self,parent,**kw):
        kw.setdefault("bg", C["card"])
        super().__init__(parent,width=self.W,height=self.H,
                         highlightthickness=0,**kw)
        self._ms=None; self._ph=0.0; self._running=True; self._tick()
    def set_ms(self,ms): self._ms=ms
    def destroy(self): self._running=False; super().destroy()
    def _tick(self):
        if not self._running: return
        self.delete("all")
        ms=self._ms
        if ms is None:
            self._ph=(self._ph+0.07)%(2*math.pi)
            x=int((math.sin(self._ph)*0.5+0.5)*self.W)
            self.create_rectangle(max(0,x-10),0,min(self.W,x+10),self.H,
                                  fill=C["muted"],outline="")
        else:
            fill=max(0.0,min(1.0,1.0-ms/500.0))
            w=int(fill*self.W)
            self.create_rectangle(0,0,self.W,self.H,fill="#0d1117",outline="")
            if w>0:
                col=ping_color(ms)
                # gradient-ish: draw 3 rects
                for i,alpha in enumerate([0.3,0.6,1.0]):
                    sw=int(w*(i+1)/3)
                    self.create_rectangle(0,0,sw,self.H,fill=col,outline="")
        self.after(35,self._tick)

# ──────────────────────────── DNS CARD ───────────────────────────────────────
class DNSCard(ctk.CTkFrame):
    H = 82
    def __init__(self,parent,dns,app,**kw):
        super().__init__(parent,fg_color=C["card"],corner_radius=8,
                         border_width=1,border_color=C["border"],height=self.H,**kw)
        self.dns=dns; self.app=app; self._active=False
        self.pack_propagate(False)
        self._build()

    def _build(self):
        d=self.dns
        sec=d["secondary_ip"]
        sec_txt = sec if sec and sec not in("","0.0.0.0","-") else "—"
        tag_col = TAG_COL.get(d["tag"],C["muted"])

        # ── tag pill ──
        pill=tk.Label(self,text=d["tag"],bg=C["tag_bg"],fg=tag_col,
                      font=("Courier New",7,"bold"),padx=4,pady=1)
        pill.place(x=8,y=7)

        # ── custom badge ──
        if d.get("is_custom"):
            tk.Label(self,text="CUSTOM",bg=C["tag_bg"],fg=C["warn"],
                     font=("Courier New",7,"bold"),padx=3,pady=1).place(x=70,y=7)

        # ── name ──
        self.name_lbl=tk.Label(self,text=d["name"],bg=C["card"],fg=C["text"],
                               font=("Segoe UI",13,"bold"),anchor="w")
        self.name_lbl.place(x=10,y=26)

        # ── note ──
        self.note_lbl=tk.Label(self,text=d["note"],bg=C["card"],fg=C["muted"],
                               font=("Segoe UI",9),anchor="w")
        self.note_lbl.place(x=10,y=55)

        # ── IPs ──
        self.ip1=tk.Label(self,text=d["primary_ip"],bg=C["card"],
                          fg=C["cyan"],font=("Courier New",10),anchor="w")
        self.ip1.place(x=200,y=24)

        self.ip2=tk.Label(self,text=sec_txt,bg=C["card"],
                          fg=C["muted"],font=("Courier New",9),anchor="w")
        self.ip2.place(x=200,y=48)

        # ── ping bar ──
        self.bar=PingBar(self,bg=C["card"])
        self.bar.place(x=390,y=30)

        self.ping_lbl=tk.Label(self,text="···",bg=C["card"],
                               fg=C["muted"],font=("Courier New",10,"bold"),
                               anchor="e",width=9)
        self.ping_lbl.place(x=484,y=26)

        # ── apply btn ──
        self.apply_btn=ctk.CTkButton(
            self,text="APPLY",width=76,height=28,
            fg_color=C["border"],hover_color="#1a3028",
            text_color=C["accent"],corner_radius=4,
            font=ctk.CTkFont(family="Courier New",size=11,weight="bold"),
            command=lambda: self.app.apply_dns(self.dns)
        )
        self.apply_btn.place(x=580,y=26)

        # ── delete btn (custom only) ──
        if d.get("is_custom"):
            ctk.CTkButton(
                self,text="✕",width=26,height=26,
                fg_color="transparent",hover_color="#3a0f0f",
                text_color=C["danger"],corner_radius=4,
                font=ctk.CTkFont(size=12),
                command=lambda: self.app.delete_entry(self.dns)
            ).place(x=660,y=27)

        # click anywhere
        for w in (self,self.name_lbl,self.note_lbl):
            w.bind("<Button-1>",lambda e: self.app.apply_dns(self.dns))
            w.bind("<Enter>",   self._hover_on)
            w.bind("<Leave>",   self._hover_off)
        self.configure(cursor="hand2")

    def update_ping(self,ms):
        self.bar.set_ms(ms)
        if ms is None:
            self.ping_lbl.configure(text="···",fg=C["muted"])
        else:
            self.ping_lbl.configure(text=f"{ms}ms",fg=ping_color(ms))

    def _sync_bg(self,col):
        self.configure(fg_color=col)
        for w in self.winfo_children():
            if isinstance(w,tk.Label): w.configure(bg=col)
            if isinstance(w,PingBar):  w.configure(bg=col)

    def set_active(self,active):
        self._active=active
        if active:
            self._sync_bg(C["active"])
            self.configure(border_color=C["accent"])
            self.name_lbl.configure(fg=C["accent"])
            self.apply_btn.configure(text="ACTIVE",fg_color=C["accent"],text_color=C["bg"])
        else:
            self._sync_bg(C["card"])
            self.configure(border_color=C["border"])
            self.name_lbl.configure(fg=C["text"])
            self.apply_btn.configure(text="APPLY",fg_color=C["border"],text_color=C["accent"])

    def _hover_on(self,e):
        if not self._active: self.configure(fg_color=C["card_hi"],border_color=C["border_hi"])
    def _hover_off(self,e):
        if not self._active: self.configure(fg_color=C["card"],border_color=C["border"])

# ──────────────────────────── ADD DNS DIALOG ─────────────────────────────────
class AddDNSDialog(ctk.CTkToplevel):
    def __init__(self,parent,on_save):
        super().__init__(parent)
        self.title("افزودن DNS جدید")
        self.geometry("460x380")
        self.configure(fg_color=C["surface"])
        self.resizable(False,False)
        self.on_save=on_save
        self._build()
        self.grab_set()

    def _build(self):
        def row(label,row_num,default=""):
            tk.Label(self,text=label,bg=C["surface"],fg=C["text"],
                     font=("Segoe UI",11)).grid(row=row_num,column=0,sticky="w",padx=20,pady=6)
            e=ctk.CTkEntry(self,width=260,fg_color=C["card"],border_color=C["border"],
                           text_color=C["text"])
            e.grid(row=row_num,column=1,padx=10,pady=6)
            if default: e.insert(0,default)
            return e

        self.grid_columnconfigure(1,weight=1)
        self.e_name  = row("نام DNS",       0)
        self.e_p     = row("IP اصلی",       1)
        self.e_s     = row("IP ثانویه",     2)
        self.e_note  = row("توضیح",         3)

        tk.Label(self,text="دسته‌بندی",bg=C["surface"],fg=C["text"],
                 font=("Segoe UI",11)).grid(row=4,column=0,sticky="w",padx=20,pady=6)
        self.cat_var=tk.StringVar(value="general")
        cats=["general","gaming","bypass","download","mobile","privacy","secure"]
        ctk.CTkOptionMenu(self,values=cats,variable=self.cat_var,
                          fg_color=C["card"],button_color=C["border"],
                          text_color=C["text"],width=260).grid(row=4,column=1,padx=10,pady=6)

        tk.Label(self,text="Tag",bg=C["surface"],fg=C["text"],
                 font=("Segoe UI",11)).grid(row=5,column=0,sticky="w",padx=20,pady=6)
        self.tag_var=tk.StringVar(value="CUSTOM")
        tags=list(TAG_COL.keys())
        ctk.CTkOptionMenu(self,values=tags,variable=self.tag_var,
                          fg_color=C["card"],button_color=C["border"],
                          text_color=C["text"],width=260).grid(row=5,column=1,padx=10,pady=6)

        ctk.CTkButton(self,text="ذخیره",width=120,height=34,
                      fg_color=C["accent"],text_color=C["bg"],
                      hover_color="#00cc70",corner_radius=6,
                      font=ctk.CTkFont(size=13,weight="bold"),
                      command=self._save).grid(row=6,column=0,columnspan=2,pady=16)

    def _save(self):
        name=self.e_name.get().strip()
        p=self.e_p.get().strip()
        if not name or not p:
            messagebox.showwarning("خطا","نام و IP اصلی اجباری است",parent=self)
            return
        self.on_save(name,p,self.e_s.get().strip(),
                     self.e_note.get().strip(),
                     self.cat_var.get(),self.tag_var.get())
        self.destroy()

# ──────────────────────────── BENCHMARK WINDOW ───────────────────────────────
class BenchmarkWindow(ctk.CTkToplevel):
    def __init__(self,parent,dns_list):
        super().__init__(parent)
        self.title("DNS Benchmark — رقابت سرعت")
        self.geometry("600x520")
        self.configure(fg_color=C["surface"])
        self.dns_list=dns_list
        self._results={}
        self._build()
        threading.Thread(target=self._run,daemon=True).start()

    def _build(self):
        tk.Label(self,text="⚡ DNS BENCHMARK RACE",bg=C["surface"],
                 fg=C["accent"],font=("Courier New",14,"bold")).pack(pady=(16,4))
        tk.Label(self,text="تست واقعی DNS resolve — google.com",bg=C["surface"],
                 fg=C["muted"],font=("Courier New",9)).pack()

        self.progress=ctk.CTkProgressBar(self,width=540,fg_color=C["card"],
                                         progress_color=C["accent"])
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.scroll=ctk.CTkScrollableFrame(self,fg_color=C["bg"],width=560,height=340)
        self.scroll.pack(fill="both",expand=True,padx=16,pady=8)

        self.status=tk.Label(self,text="در حال تست...",bg=C["surface"],
                             fg=C["muted"],font=("Courier New",9))
        self.status.pack(pady=4)

    def _run(self):
        total=len(self.dns_list); done=0
        for dns in self.dns_list:
            ip=dns["primary_ip"]
            ms=dns_resolve_test(ip)
            self._results[dns["name"]]=ms
            done+=1
            self.after(0,lambda d=done,t=total: self.progress.set(d/t))
            self.after(0,lambda n=dns["name"],m=ms: self._add_row(n,m))
        self.after(0,lambda: self.status.configure(
            text=f"✓ تست کامل — {total} سرور بررسی شد",fg=C["accent"]))
        self.after(0,self._sort_rows)

    def _add_row(self,name,ms):
        col=ping_color(ms)
        ms_txt=f"{ms}ms" if ms else "TIMEOUT"
        bar_w=int(ms/500*200) if ms else 0
        f=tk.Frame(self.scroll,bg=C["card"])
        f.pack(fill="x",pady=2,padx=2)
        tk.Label(f,text=name,bg=C["card"],fg=C["text"],
                 font=("Segoe UI",11),width=14,anchor="w").pack(side="left",padx=8,pady=5)
        tk.Frame(f,bg=col,width=max(2,bar_w),height=8).pack(side="left",pady=5)
        tk.Label(f,text=ms_txt,bg=C["card"],fg=col,
                 font=("Courier New",11,"bold"),width=10).pack(side="right",padx=10)
        self._rows=getattr(self,"_rows",[]); self._rows.append((ms or 9999,f))

    def _sort_rows(self):
        for w in self.scroll.winfo_children(): w.pack_forget()
        sorted_rows=sorted(getattr(self,"_rows",[]),key=lambda x:x[0])
        for i,(ms,f) in enumerate(sorted_rows):
            f.pack(fill="x",pady=2,padx=2)
            if i==0:
                for w in f.winfo_children():
                    if isinstance(w,tk.Label): w.configure(fg=C["accent"])

# ──────────────────────────── HOSTS INJECTOR WINDOW ─────────────────────────
class HostsWindow(ctk.CTkToplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.title("Game Hosts Injector")
        self.geometry("520x460")
        self.configure(fg_color=C["surface"])
        self._build()

    def _build(self):
        tk.Label(self,text="🎮 GAME HOSTS INJECTOR",bg=C["surface"],
                 fg=C["accent"],font=("Courier New",13,"bold")).pack(pady=(14,4))
        tk.Label(self,text="بایپس DNS Hijacking — مستقیم به سرور بازی وصل شو",
                 bg=C["surface"],fg=C["muted"],font=("Courier New",9)).pack()

        if not is_admin():
            tk.Label(self,text="⚠  نیاز به ادمین / root دارید",bg=C["surface"],
                     fg=C["warn"],font=("Courier New",10,"bold")).pack(pady=6)

        scroll=ctk.CTkScrollableFrame(self,fg_color=C["bg"],height=300)
        scroll.pack(fill="both",expand=True,padx=16,pady=10)

        self._checks={}
        for game,ips in GAME_HOSTS.items():
            f=tk.Frame(scroll,bg=C["card"])
            f.pack(fill="x",pady=3,padx=2)
            var=tk.BooleanVar(value=False)
            ctk.CTkCheckBox(f,text=game,variable=var,
                            fg_color=C["accent"],text_color=C["text"],
                            font=ctk.CTkFont(size=12)).pack(side="left",padx=10,pady=8)
            tk.Label(f,text=f"{len(ips)} servers",bg=C["card"],
                     fg=C["muted"],font=("Courier New",9)).pack(side="right",padx=10)
            self._checks[game]=var

        btn_row=tk.Frame(self,bg=C["surface"])
        btn_row.pack(pady=10)
        ctk.CTkButton(btn_row,text="Inject Selected",width=160,height=34,
                      fg_color=C["accent"],text_color=C["bg"],
                      hover_color="#00cc70",corner_radius=6,
                      command=self._inject).pack(side="left",padx=6)
        ctk.CTkButton(btn_row,text="Clear All",width=120,height=34,
                      fg_color=C["danger"],text_color="#fff",
                      hover_color="#cc2233",corner_radius=6,
                      command=self._clear).pack(side="left",padx=6)

        self.status=tk.Label(self,text="",bg=C["surface"],fg=C["muted"],
                             font=("Courier New",9))
        self.status.pack(pady=4)

    def _inject(self):
        if not is_admin():
            self.status.configure(text="ERROR: نیاز به ادمین",fg=C["danger"]); return
        hosts_map={}
        for game,var in self._checks.items():
            if var.get():
                for ip in GAME_HOSTS[game]:
                    hosts_map[f"{game.lower().replace(' ','.')}.game"]=ip
        if not hosts_map:
            self.status.configure(text="هیچ موردی انتخاب نشده",fg=C["warn"]); return
        try:
            inject_hosts(hosts_map)
            flush_dns()
            self.status.configure(text=f"✓ {len(hosts_map)} entry اضافه شد",fg=C["accent"])
        except Exception as e:
            self.status.configure(text=f"ERROR: {e}",fg=C["danger"])

    def _clear(self):
        if not is_admin():
            self.status.configure(text="ERROR: نیاز به ادمین",fg=C["danger"]); return
        try:
            clear_hosts_injections()
            flush_dns()
            self.status.configure(text="✓ همه entries پاک شدند",fg=C["muted"])
        except Exception as e:
            self.status.configure(text=f"ERROR: {e}",fg=C["danger"])

# ──────────────────────────── AUTO-UPDATER ───────────────────────────────────

def _parse_version(v):
    """'4.0.0' -> (4,0,0) for comparison."""
    try:
        return tuple(int(x) for x in v.lstrip("v").split(".")[:3])
    except Exception:
        return (0, 0, 0)

def check_for_update():
    """
    Hit GitHub releases API.
    Returns dict: {available, latest, current, download_url, html_url} or raises.
    """
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        RELEASES_API,
        headers={"User-Agent": f"dns-switcher/{__version__}",
                 "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
        data = json.loads(r.read().decode())

    latest_tag  = data.get("tag_name", "")
    latest_ver  = latest_tag.lstrip("v")
    html_url    = data.get("html_url", GITHUB_URL)

    # Try to find a .py asset in the release
    download_url = None
    for asset in data.get("assets", []):
        if asset["name"].endswith(".py"):
            download_url = asset["browser_download_url"]
            break
    # Fallback: raw script from tag
    if not download_url:
        download_url = RAW_SCRIPT.format(repo=GITHUB_REPO, tag=latest_tag)

    available = _parse_version(latest_ver) > _parse_version(__version__)
    return {
        "available":    available,
        "latest":       latest_ver,
        "current":      __version__,
        "download_url": download_url,
        "html_url":     html_url,
    }

def download_and_apply_update(download_url, on_progress=None, on_done=None, on_error=None):
    """
    Download the new script, replace current file, then restart.
    Runs in a background thread — callbacks fire on the calling thread via `after`.
    """
    def worker():
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(
                download_url,
                headers={"User-Agent": f"dns-switcher/{__version__}"}
            )
            if on_progress: on_progress("DOWNLOADING ...")
            with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
                content = r.read()

            # Write to a temp file first (atomic-ish)
            current_script = os.path.abspath(sys.argv[0])
            tmp = current_script + ".new"
            with open(tmp, "wb") as f:
                f.write(content)

            # Replace
            backup = current_script + ".bak"
            shutil.copy2(current_script, backup)
            shutil.move(tmp, current_script)

            if on_done: on_done()

            # Restart
            time.sleep(0.8)
            subprocess.Popen([sys.executable, current_script] + sys.argv[1:])
            os._exit(0)

        except Exception as ex:
            if on_error: on_error(str(ex))

    threading.Thread(target=worker, daemon=True).start()


# ──────────────────────────── UPDATE DIALOG ──────────────────────────────────

class UpdateDialog(ctk.CTkToplevel):
    """Shown when an update is available or after a manual check."""

    def __init__(self, parent, info: dict):
        super().__init__(parent)
        self.info = info
        self.title("DNS Switcher — آپدیت")
        self.geometry("480x300")
        self.resizable(False, False)
        self.configure(fg_color=C["surface"])
        self.grab_set()
        self._build()

    def _build(self):
        info = self.info

        if info["available"]:
            title_text  = "⬆  نسخه جدید موجود است"
            title_color = C["accent"]
            sub_text    = f"v{info['current']}  →  v{info['latest']}"
        else:
            title_text  = "✓  نسخه شما به‌روز است"
            title_color = C["muted"]
            sub_text    = f"نسخه فعلی:  v{info['current']}"

        tk.Label(self, text=title_text, bg=C["surface"], fg=title_color,
                 font=("Courier New", 14, "bold")).pack(pady=(24, 4))
        tk.Label(self, text=sub_text, bg=C["surface"], fg=C["text"],
                 font=("Courier New", 11)).pack(pady=4)

        # Progress / status label
        self.prog_lbl = tk.Label(self, text="", bg=C["surface"], fg=C["muted"],
                                 font=("Courier New", 10))
        self.prog_lbl.pack(pady=6)

        # Progress bar (hidden until download starts)
        self.pbar = ctk.CTkProgressBar(self, width=400,
                                        fg_color=C["card"],
                                        progress_color=C["accent"])
        self.pbar.set(0)

        btn_row = tk.Frame(self, bg=C["surface"])
        btn_row.pack(pady=16)

        if info["available"]:
            ctk.CTkButton(
                btn_row, text="دانلود و نصب خودکار", width=180, height=36,
                fg_color=C["accent"], text_color=C["bg"],
                hover_color="#00cc70", corner_radius=6,
                font=ctk.CTkFont(family="Courier New", size=12, weight="bold"),
                command=self._do_update
            ).pack(side="left", padx=6)

            ctk.CTkButton(
                btn_row, text="باز کردن در GitHub", width=160, height=36,
                fg_color=C["card"], text_color=C["cyan"],
                hover_color=C["card_hi"], corner_radius=6,
                font=ctk.CTkFont(family="Courier New", size=12),
                command=lambda: webbrowser.open(info["html_url"])
            ).pack(side="left", padx=6)
        else:
            ctk.CTkButton(
                btn_row, text="بستن", width=120, height=36,
                fg_color=C["card"], text_color=C["muted"],
                corner_radius=6,
                command=self.destroy
            ).pack()

    def _do_update(self):
        self.pbar.pack(pady=4)
        self.pbar.configure(mode="indeterminate")
        self.pbar.start()
        self.prog_lbl.configure(text="در حال دانلود...", fg=C["warn"])

        def on_progress(msg):
            self.after(0, lambda: self.prog_lbl.configure(text=msg, fg=C["warn"]))

        def on_done():
            self.after(0, lambda: self.prog_lbl.configure(
                text="✓ دانلود کامل شد — در حال راه‌اندازی مجدد...", fg=C["accent"]))
            self.after(0, lambda: self.pbar.stop())

        def on_error(msg):
            self.after(0, lambda: self.prog_lbl.configure(
                text=f"خطا: {msg}", fg=C["danger"]))
            self.after(0, lambda: self.pbar.stop())

        download_and_apply_update(
            self.info["download_url"],
            on_progress=on_progress,
            on_done=on_done,
            on_error=on_error,
        )


# ──────────────────────────── HEADER CANVAS ───────────────────────────────────
class HeaderCanvas(tk.Canvas):
    def __init__(self,parent,**kw):
        super().__init__(parent,height=74,bg=C["surface"],
                         highlightthickness=0,**kw)
        self._off=0; self._draw()
    def _draw(self):
        self.delete("g")
        w=self.winfo_width() or 900
        for x in range(0,w,44):
            shade="#0d1117" if (x//44)%2==0 else "#0f1520"
            self.create_rectangle(x,0,x+44,74,fill=shade,outline="",tags="g")
        y=self._off%74
        self.create_line(0,y,w,y,fill="#0d2a1a",tags="g")
        self.create_line(0,(y+37)%74,w,(y+37)%74,fill="#0a1f28",tags="g")
        self._off+=1
        self.after(28,self._draw)

# ──────────────────────────── MAIN APP ───────────────────────────────────────
CATS = {"all":"ALL","bypass":"BYPASS","gaming":"GAMING","download":"DL",
        "mobile":"MOBILE","general":"GLOBAL","privacy":"PRIVACY","secure":"SECURE"}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"DNS Switcher Pro  v{__version__}")
        self.geometry("860x780")
        self.minsize(780,600)
        self.configure(fg_color=C["bg"])

        init_db()
        self._dns_list      = []
        self._all_cards     = []
        self._active_name   = load_setting("active_dns")
        self._cat           = "all"
        self._search        = ""
        self._pings         = {}

        self._build_ui()
        self._reload_dns()
        threading.Thread(target=self._ping_all, daemon=True).start()
        # Auto-check for updates 2 s after launch (non-blocking)
        self.after(2000, lambda: threading.Thread(
            target=self._startup_update_check, daemon=True).start())

    # ── UI BUILD ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        self.hdr = HeaderCanvas(self)
        self.hdr.pack(fill="x")
        tk.Label(self.hdr, text="⚡ DNS SWITCHER PRO", bg=C["surface"],
                 fg=C["accent"], font=("Courier New",17,"bold")).place(x=18, y=14)
        tk.Label(self.hdr, text=f"v{__version__}  by {AUTHOR}",
                 bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9)).place(x=20, y=42)
        self.status_var=tk.StringVar(value="READY")
        self.status_lbl=tk.Label(self.hdr,textvariable=self.status_var,
                                 bg=C["surface"],fg=C["muted"],font=("Courier New",9))
        self.status_lbl.place(x=20,y=50)
        adm_t = "● ADMIN" if is_admin() else "● NO ADMIN (read-only)"
        adm_c = C["accent"] if is_admin() else C["warn"]
        tk.Label(self.hdr, text=adm_t, bg=C["surface"], fg=adm_c,
                 font=("Courier New",9,"bold")).place(relx=1.0, x=-16, y=18, anchor="ne")

        # Update notification badge (hidden until update found)
        self._upd_badge = tk.Label(
            self.hdr, text="", bg=C["surface"], fg=C["warn"],
            font=("Courier New",9,"bold"), cursor="hand2"
        )
        self._upd_badge.place(relx=1.0, x=-16, y=38, anchor="ne")
        self._upd_badge.bind("<Button-1>", lambda e: self._open_update_dialog())

        # Toolbar row 1: search + cats
        tb1=tk.Frame(self,bg=C["surface"],height=46)
        tb1.pack(fill="x")
        sf=tk.Frame(tb1,bg=C["border"],padx=1,pady=1)
        sf.pack(side="left",padx=10,pady=8)
        self._sv=tk.StringVar(); self._sv.trace_add("write",lambda *_: self._on_search())
        tk.Entry(sf,textvariable=self._sv,bg=C["card"],fg=C["accent"],
                 insertbackground=C["accent"],font=("Courier New",10),
                 relief="flat",width=16,bd=4).pack()

        self._cat_btns={}
        for k,lbl in CATS.items():
            b=tk.Label(tb1,text=lbl,bg=C["card_hi"],fg=C["muted"],
                       font=("Courier New",8,"bold"),padx=6,pady=3,cursor="hand2")
            b.pack(side="left",padx=2,pady=10)
            b.bind("<Button-1>",lambda e,kk=k: self._set_cat(kk))
            self._cat_btns[k]=b
        self._set_cat("all",silent=True)

        # Toolbar row 2: action buttons
        tb2=tk.Frame(self,bg=C["surface"],height=40)
        tb2.pack(fill="x")
        tk.Frame(self,bg=C["border"],height=1).pack(fill="x")

        def tbtn(parent,text,col,cmd,side="left"):
            b=tk.Label(parent,text=text,bg=C["card_hi"],fg=col,
                       font=("Courier New",9,"bold"),padx=10,pady=5,
                       cursor="hand2",relief="flat")
            b.pack(side=side,padx=4,pady=8)
            b.bind("<Button-1>",lambda e: cmd())
            b.bind("<Enter>",lambda e,w=b: w.configure(bg=C["card"]))
            b.bind("<Leave>",lambda e,w=b: w.configure(bg=C["card_hi"]))
            return b

        tbtn(tb2,"[ + ADD DNS ]",    C["accent"],  self._open_add)
        tbtn(tb2,"[ ⚡ BENCHMARK ]", C["cyan"],    self._open_bench)
        tbtn(tb2,"[ 🎮 GAME HOSTS ]",C["purple"],  self._open_hosts)
        tbtn(tb2,"[ 🔄 RE-PING ]",   C["muted"],   self._reping)
        self._upd_btn = tbtn(tb2,"[ ⬆ UPDATE ]",  C["warn"],   self._check_update_manual, side="right")
        tbtn(tb2,"[ 🚿 FLUSH DNS ]", C["warn"],    self._flush, side="right")
        tbtn(tb2,"[ ↺ RESET DHCP ]", C["danger"], self._reset, side="right")

        # Scroll area
        self.scroll=ctk.CTkScrollableFrame(self,fg_color=C["bg"],
                                           scrollbar_button_color=C["border"],
                                           scrollbar_button_hover_color=C["accent"])
        self.scroll.pack(fill="both",expand=True,padx=10,pady=(6,0))

        # ── About / Footer ──────────────────────────────────────────────────
        footer = tk.Frame(self, bg=C["card"], height=54)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Frame(footer, bg=C["border"], height=1).pack(fill="x", side="top")

        # Left: author info
        left_f = tk.Frame(footer, bg=C["card"])
        left_f.pack(side="left", padx=14, pady=0, fill="y")

        tk.Label(left_f, text=f"⚡ DNS Switcher Pro  v{__version__}",
                 bg=C["card"], fg=C["accent"],
                 font=("Courier New", 10, "bold")).pack(anchor="w", pady=(10, 0))

        gh_row = tk.Frame(left_f, bg=C["card"])
        gh_row.pack(anchor="w")
        tk.Label(gh_row, text="by ", bg=C["card"], fg=C["muted"],
                 font=("Courier New", 9)).pack(side="left")
        gh_lnk = tk.Label(gh_row, text=AUTHOR, bg=C["card"], fg=C["cyan"],
                          font=("Courier New", 9, "bold"), cursor="hand2")
        gh_lnk.pack(side="left")
        gh_lnk.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))
        gh_lnk.bind("<Enter>",    lambda e: gh_lnk.configure(fg=C["accent"]))
        gh_lnk.bind("<Leave>",    lambda e: gh_lnk.configure(fg=C["cyan"]))
        tk.Label(gh_row, text=f"  ·  {GITHUB_URL}", bg=C["card"], fg=C["muted"],
                 font=("Courier New", 9)).pack(side="left")

        # Middle: active DNS status
        mid_f = tk.Frame(footer, bg=C["card"])
        mid_f.pack(side="left", expand=True, fill="both", padx=10)
        self.active_lbl = tk.Label(mid_f, text="NO DNS SELECTED",
                                   bg=C["card"], fg=C["muted"],
                                   font=("Courier New", 10))
        self.active_lbl.pack(anchor="center", pady=16)

        # Right: clock
        right_f = tk.Frame(footer, bg=C["card"])
        right_f.pack(side="right", padx=14, fill="y")
        self._clock_lbl = tk.Label(right_f, text="", bg=C["card"],
                                   fg=C["muted"], font=("Courier New", 9))
        self._clock_lbl.pack(anchor="e", pady=(10, 0))
        # open-source label
        tk.Label(right_f, text="open source", bg=C["card"], fg=C["muted"],
                 font=("Courier New", 8)).pack(anchor="e")

        self._tick_clock()

    def _tick_clock(self):
        self._clock_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000,self._tick_clock)

    # ── DNS List ──────────────────────────────────────────────────────────────
    def _reload_dns(self):
        self._dns_list=load_dns_list()
        # destroy old cards
        for c in self._all_cards:
            c.destroy()
        self._all_cards.clear()
        for dns in self._dns_list:
            card=DNSCard(self.scroll,dns,self)
            self._all_cards.append(card)
        self._apply_filter()

    def _apply_filter(self):
        q=self._search.lower(); cat=self._cat
        for c in self._all_cards: c.pack_forget()
        for card in self._all_cards:
            d=card.dns
            if cat!="all" and d["category"]!=cat: continue
            if q and q not in d["name"].lower() and q not in d["primary_ip"] \
               and q not in d["note"].lower(): continue
            card.pack(fill="x",pady=3,padx=2)
            card.update_ping(self._pings.get(d["primary_ip"]))
            card.set_active(d["name"]==self._active_name)

    def _set_cat(self,key,silent=False):
        self._cat=key
        for k,b in self._cat_btns.items():
            b.configure(bg=C["accent"] if k==key else C["card_hi"],
                        fg=C["bg"] if k==key else C["muted"])
        if not silent: self._apply_filter()

    def _on_search(self):
        self._search=self._sv.get().strip()
        self._apply_filter()

    # ── Apply / Reset ─────────────────────────────────────────────────────────
    def apply_dns(self,dns):
        if not is_admin():
            self._set_status("ERROR: نیاز به ADMIN / root",C["danger"]); return
        self._set_status(f"APPLYING {dns['name'].upper()} ...",C["warn"])
        def worker():
            try:
                apply_dns_os(dns)
                self._active_name=dns["name"]
                save_setting("active_dns",dns["name"])
                self.after(0,lambda: self._set_status(
                    f"OK  {dns['name']}  PRIMARY={dns['primary_ip']}",C["accent"]))
                self.after(0,lambda: self.active_lbl.configure(
                    text=f"ACTIVE ▶  {dns['name']}  {dns['primary_ip']}",fg=C["accent"]))
            except Exception as ex:
                self.after(0,lambda: self._set_status(f"ERROR: {ex}",C["danger"]))
            for c in self._all_cards:
                self.after(0,lambda cc=c: cc.set_active(cc.dns["name"]==self._active_name))
        threading.Thread(target=worker,daemon=True).start()

    def _reset(self):
        if not is_admin():
            self._set_status("ERROR: نیاز به ADMIN / root",C["danger"]); return
        def w():
            try:
                reset_dns_os()
                self._active_name=None
                save_setting("active_dns","")
                self.after(0,lambda: self._set_status("RESET — DHCP RESTORED",C["muted"]))
                self.after(0,lambda: self.active_lbl.configure(
                    text="NO DNS SELECTED",fg=C["muted"]))
                for c in self._all_cards:
                    self.after(0,lambda cc=c: cc.set_active(False))
            except Exception as ex:
                self.after(0,lambda: self._set_status(f"ERROR: {ex}",C["danger"]))
        threading.Thread(target=w,daemon=True).start()

    def _flush(self):
        def w():
            try:
                flush_dns()
                self.after(0,lambda: self._set_status("DNS CACHE FLUSHED",C["cyan"]))
            except Exception as ex:
                self.after(0,lambda: self._set_status(f"ERROR: {ex}",C["danger"]))
        threading.Thread(target=w,daemon=True).start()

    # ── Custom DNS ────────────────────────────────────────────────────────────
    def _open_add(self):
        AddDNSDialog(self,self._on_save_custom)

    def _on_save_custom(self,name,p,s,note,cat,tag):
        add_dns_entry(name,p,s,note,cat,tag)
        self._reload_dns()
        self._set_status(f"✓ DNS '{name}' اضافه شد",C["accent"])

    def delete_entry(self,dns):
        if messagebox.askyesno("حذف",f"حذف '{dns['name']}'?",parent=self):
            delete_dns_entry(dns["id"])
            self._reload_dns()
            self._set_status(f"✓ DNS '{dns['name']}' حذف شد",C["muted"])

    # ── Ping ──────────────────────────────────────────────────────────────────
    def _ping_all(self):
        for dns in self._dns_list:
            ip=dns["primary_ip"]
            ms=dns_resolve_test(ip)
            self._pings[ip]=ms
            for c in self._all_cards:
                if c.dns["primary_ip"]==ip:
                    self.after(0,lambda cc=c,m=ms: cc.update_ping(m))

    def _reping(self):
        self._pings.clear()
        for c in self._all_cards: c.update_ping(None)
        threading.Thread(target=self._ping_all,daemon=True).start()

    # ── Tools ─────────────────────────────────────────────────────────────────
    def _open_bench(self):
        BenchmarkWindow(self,self._dns_list)

    def _open_hosts(self):
        HostsWindow(self)

    # ── Auto-Updater ──────────────────────────────────────────────────────────
    def _startup_update_check(self):
        """Silent background check on startup — only shows badge if update found."""
        try:
            info = check_for_update()
            if info["available"]:
                self._update_info = info
                self.after(0, self._show_update_badge)
        except Exception:
            pass  # silently ignore on startup (no network, etc.)

    def _show_update_badge(self):
        self._upd_badge.configure(text=f"⬆ v{self._update_info['latest']} available")
        # Make the toolbar button glow
        self._upd_btn.configure(fg=C["accent"])

    def _check_update_manual(self):
        """Called by toolbar button — always shows result dialog."""
        self._set_status("Checking for updates...", C["warn"])

        def worker():
            try:
                info = check_for_update()
                self._update_info = info
                self.after(0, lambda: self._set_status(
                    f"Latest: v{info['latest']}  Current: v{info['current']}",
                    C["accent"] if info["available"] else C["muted"]
                ))
                self.after(0, lambda: UpdateDialog(self, info))
            except Exception as ex:
                self.after(0, lambda: self._set_status(
                    f"Update check failed: {ex}", C["danger"]))

        threading.Thread(target=worker, daemon=True).start()

    def _open_update_dialog(self):
        """Called when user clicks the badge."""
        info = getattr(self, "_update_info", None)
        if info:
            UpdateDialog(self, info)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _set_status(self,msg,col=None):
        self.status_var.set(msg)
        self.status_lbl.configure(fg=col or C["muted"])


if __name__=="__main__":
    app=App()
    app.mainloop()
