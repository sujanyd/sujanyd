"""Generate all hand-built arcade SVGs for Sujan's profile README."""
import os

BG = "#0d1117"
PANEL = "#161b22"
SCREEN = "#0a0c10"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PURPLE = "#a371f7"
GREEN = "#7ee787"
CYAN = "#79c0ff"
PINK = "#ff7b72"
AMBER = "#f2cc60"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

def frame(w, h, title, sub, accent):
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{SCREEN}" stroke="{BORDER}" stroke-width="2"/>'
            f'<path d="M1 13a12 12 0 0 1 12-12h{w - 26}a12 12 0 0 1 12 12v17H1Z" fill="{PANEL}"/>'
            f'<path d="M1 30H{w - 1}" stroke="{BORDER}" stroke-width="2"/>'
            f'<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/>'
            f'<circle cx="50" cy="16" r="5" fill="#27c93f"/>'
            f'<text x="68" y="20" font-size="11.5" font-weight="700" fill="{accent}">{title}</text>'
            f'<text x="{w - 16}" y="20" text-anchor="end" font-size="10.5" fill="{MUTED}">{sub}</text>')

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<g font-family="{MONO}">{body}</g></svg>\n')

# 1. Level banners
def make_lvl(num, title, color):
    w, h = 900, 48
    body = (
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="8" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<path d="M1 1h8v{h-2}H1Z" fill="{color}"/>'
        f'<text x="24" y="29" font-size="13" font-weight="800" letter-spacing="3" fill="{color}">LVL {num:02d}</text>'
        f'<text x="105" y="29" font-size="13" font-weight="700" letter-spacing="2" fill="{MUTED}">//</text>'
        f'<text x="135" y="29" font-size="13" font-weight="700" letter-spacing="2" fill="{TEXT}">{title.upper()}</text>'
        f'<line x1="420" y1="24" x2="840" y2="24" stroke="{BORDER}" stroke-dasharray="4 6"/>'
        f'<circle cx="865" cy="24" r="4" fill="{color}"><animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite"/></circle>'
    )
    return svg(w, h, body)

# 2. Hero banner
def make_hero():
    w, h = 900, 190
    fr = frame(w, h, "~/arcade/marquee.exe", "PLAYER 1: READY · INSERT COIN", PURPLE)
    content = (
        f'<defs>'
        f'<linearGradient id="grad-title" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{PURPLE}"/>'
        f'<stop offset="50%" stop-color="{CYAN}"/>'
        f'<stop offset="100%" stop-color="{GREEN}"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<text x="450" y="78" text-anchor="middle" font-size="34" font-weight="900" letter-spacing="6" fill="url(#grad-title)">SUJAN Y D</text>'
        f'<text x="450" y="112" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="3" fill="{AMBER}">AI AGENTS  ·  LLMs  ·  VOICE ASSISTANTS  ·  FULL-STACK</text>'
        f'<rect x="250" y="132" width="400" height="30" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<text x="450" y="152" text-anchor="middle" font-size="11.5" letter-spacing="2" fill="{TEXT}">'
        f'<tspan fill="{GREEN}">PRESS START</tspan> · TO BEGIN PLAY'
        f'<animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/>'
        f'</text>'
        f'<circle cx="270" cy="147" r="4" fill="{GREEN}"/>'
        f'<circle cx="630" cy="147" r="4" fill="{PINK}"/>'
    )
    return svg(w, h, fr + content)

# 3. Player Character Sheet
def make_player():
    w, h = 900, 260
    fr = frame(w, h, "~/arcade/player_profile.chr", "CHARACTER CLASS: AI ARCHITECT", CYAN)
    content = (
        # Avatar Box
        f'<rect x="24" y="48" width="180" height="190" rx="10" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
        # Pixel sprite representation
        f'<circle cx="114" cy="100" r="32" fill="{PURPLE}" fill-opacity="0.2" stroke="{PURPLE}" stroke-width="2"/>'
        f'<text x="114" y="108" text-anchor="middle" font-size="28">⚡</text>'
        f'<text x="114" y="158" text-anchor="middle" font-size="13" font-weight="800" fill="{TEXT}">PLAYER 1</text>'
        f'<text x="114" y="176" text-anchor="middle" font-size="11" fill="{CYAN}">SUJAN Y D</text>'
        f'<rect x="44" y="196" width="140" height="22" rx="4" fill="{SCREEN}" stroke="{BORDER}"/>'
        f'<text x="114" y="211" text-anchor="middle" font-size="9.5" font-weight="700" fill="{GREEN}">LVL 99 ARCHITECT</text>'
        
        # Stats Table
        f'<rect x="224" y="48" width="652" height="190" rx="10" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
        
        # Rows
        f'<text x="248" y="80" font-size="11" letter-spacing="1" fill="{MUTED}">CLASS</text>'
        f'<text x="350" y="80" font-size="12" font-weight="700" fill="{TEXT}">Autonomous AI Agent & Systems Builder</text>'
        
        f'<text x="248" y="112" font-size="11" letter-spacing="1" fill="{MUTED}">ACADEMY</text>'
        f'<text x="350" y="112" font-size="12" font-weight="700" fill="{CYAN}">Newton School of Technology (B.Tech CSE & AI)</text>'
        
        f'<text x="248" y="144" font-size="11" letter-spacing="1" fill="{MUTED}">EXP / GUILD</text>'
        f'<text x="350" y="144" font-size="12" font-weight="700" fill="{AMBER}">Research Intern @ IIT Guwahati</text>'
        
        f'<line x1="248" y1="162" x2="852" y2="162" stroke="{BORDER}"/>'
        
        # Attributes Bars
        f'<text x="248" y="188" font-size="11" font-weight="700" fill="{PURPLE}">INTELLIGENCE [AI/ML]</text>'
        f'<rect x="440" y="177" width="220" height="12" rx="3" fill="{SCREEN}"/>'
        f'<rect x="440" y="177" width="205" height="12" rx="3" fill="{PURPLE}"/>'
        f'<text x="670" y="188" font-size="11" font-weight="800" fill="{TEXT}">95%</text>'
        
        f'<text x="248" y="218" font-size="11" font-weight="700" fill="{GREEN}">AGILITY [FULL-STACK]</text>'
        f'<rect x="440" y="207" width="220" height="12" rx="3" fill="{SCREEN}"/>'
        f'<rect x="440" y="207" width="195" height="12" rx="3" fill="{GREEN}"/>'
        f'<text x="670" y="218" font-size="11" font-weight="800" fill="{TEXT}">90%</text>'
    )
    return svg(w, h, fr + content)

# 4. Quest Cards
def make_quest(title, sub, stack, status, stat_col, icon):
    w, h = 440, 200
    fr = frame(w, h, f"~/quests/{title.lower().replace(' ', '_')}.exe", "QUEST LOG", stat_col)
    content = (
        f'<circle cx="48" cy="74" r="22" fill="{PANEL}" stroke="{stat_col}" stroke-width="2"/>'
        f'<text x="48" y="82" text-anchor="middle" font-size="20">{icon}</text>'
        f'<text x="82" y="70" font-size="14" font-weight="800" fill="{TEXT}">{title}</text>'
        f'<text x="82" y="88" font-size="11" fill="{MUTED}">{sub}</text>'
        f'<rect x="24" y="112" width="392" height="42" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<text x="36" y="136" font-size="11" fill="{TEXT}"><tspan fill="{MUTED}">STACK:</tspan> {stack}</text>'
        f'<rect x="24" y="164" width="110" height="22" rx="4" fill="{SCREEN}" stroke="{stat_col}"/>'
        f'<text x="79" y="179" text-anchor="middle" font-size="9.5" font-weight="800" fill="{stat_col}">● {status}</text>'
    )
    return svg(w, h, fr + content)

# 5. Boss Fight SVG (Space Invaders)
def make_boss():
    w, h = 900, 260
    fr = frame(w, h, "~/arcade/boss_fight.exe", "STAGE 06 · DIFFICULTY: NIGHTMARE", PINK)
    
    # Invaders
    bugs = [("404_NOT_FOUND", PURPLE), ("MEMORY_LEAK", PINK), ("NULL_POINTER", CYAN), ("DEADLOCK", AMBER), ("HALLUCINATION", GREEN)]
    invaders = []
    for i, (b_name, col) in enumerate(bugs):
        x = 60 + i * 164
        invaders.append(
            f'<rect x="{x}" y="56" width="130" height="38" rx="6" fill="{PANEL}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{x + 65}" y="79" text-anchor="middle" font-size="10.5" font-weight="800" fill="{col}">👾 {b_name}</text>'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 8,0; -8,0; 0,0" dur="3s" repeatCount="indefinite"/>'
        )
    
    # Player laser ship
    ship_x = 425
    lasers = (
        f'<line x1="{ship_x + 25}" y1="180" x2="{ship_x + 25}" y2="98" stroke="{GREEN}" stroke-width="3" stroke-dasharray="12 8">'
        f'<animate attributeName="stroke-dashoffset" from="0" to="-40" dur="0.4s" repeatCount="indefinite"/>'
        f'</line>'
        f'<polygon points="{ship_x + 25},185 {ship_x + 10},215 {ship_x + 40},215" fill="{CYAN}"/>'
        f'<rect x="{ship_x + 21}" y="195" width="8" height="24" fill="{TEXT}"/>'
        f'<circle cx="{ship_x + 25}" cy="222" r="5" fill="{PINK}"><animate attributeName="r" values="3;7;3" dur="0.3s" repeatCount="indefinite"/></circle>'
    )
    
    hud = (
        f'<text x="36" y="244" font-size="11" letter-spacing="2" fill="{MUTED}">PLAYER 1 SHIELD: <tspan fill="{GREEN}">100%</tspan></text>'
        f'<text x="900 - 36" y="244" text-anchor="end" font-size="11" letter-spacing="2" fill="{MUTED}">BOSS HP: <tspan fill="{PINK}">0% (DEFEATED)</tspan></text>'
    )
    
    return svg(w, h, fr + "".join(invaders) + lasers + hud)

# 6. Continue banner
def make_continue():
    w, h = 900, 110
    fr = frame(w, h, "~/arcade/game_over_prompt.sys", "INSERT COIN TO COLLAB", AMBER)
    content = (
        f'<text x="450" y="64" text-anchor="middle" font-size="16" font-weight="900" letter-spacing="4" fill="{TEXT}">'
        f'CONTINUE?  <tspan fill="{PINK}">9</tspan>'
        f'<animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite"/>'
        f'</text>'
        f'<text x="450" y="88" text-anchor="middle" font-size="11" letter-spacing="2" fill="{AMBER}">INSERT COIN / CONNECT TO COLLABORATE</text>'
    )
    return svg(w, h, fr + content)

def main():
    out_dir = "/Users/sujanyd/sujanyd/assets"
    os.makedirs(out_dir, exist_ok=True)
    
    # Levels
    lvls = [
        ("lvl1.svg", make_lvl(1, "Fidgets & Telemetry", PURPLE)),
        ("lvl2.svg", make_lvl(2, "Player Character Sheet", CYAN)),
        ("lvl3.svg", make_lvl(3, "Active Quests & Builds", GREEN)),
        ("lvl4.svg", make_lvl(4, "Weapons & Tech Inventory", PINK)),
        ("lvl5.svg", make_lvl(5, "System Metrics & Commits", CYAN)),
        ("lvl6.svg", make_lvl(6, "Boss Stage", PINK)),
        ("lvl7.svg", make_lvl(7, "Neon Snake Arena", GREEN)),
    ]
    for fn, content in lvls:
        with open(os.path.join(out_dir, fn), "w") as f:
            f.write(content)
            
    # Hero & Player
    with open(os.path.join(out_dir, "hero.svg"), "w") as f:
        f.write(make_hero())
    with open(os.path.join(out_dir, "player.svg"), "w") as f:
        f.write(make_player())
        
    # Quests
    quests = [
        ("quest-jarvis.svg", make_quest("J.A.R.V.I.S", "Voice Assistant & System Automation", "Python · SpeechRecognition · PyTorch", "LEGENDARY", PURPLE, "🎙️")),
        ("quest-chatgpt.svg", make_quest("Offline ChatGPT", "Local LLM Inference Engine & Web UI", "React · Ollama · FastAPI · Docker", "DEPLOYED", GREEN, "🤖")),
        ("quest-hub.svg", make_quest("My Project Hub", "Showcase of Engineering Projects & Apps", "Next.js · TailwindCSS · Vercel", "LIVE", CYAN, "🚀")),
        ("quest-iit.svg", make_quest("Research Intern @ IIT", "IIT Guwahati Deep Learning Research", "Python · Graph Neural Nets · PyTorch", "RESEARCH", AMBER, "🏛️")),
    ]
    for fn, content in quests:
        with open(os.path.join(out_dir, fn), "w") as f:
            f.write(content)
            
    # Boss & Continue
    with open(os.path.join(out_dir, "boss.svg"), "w") as f:
        f.write(make_boss())
    with open(os.path.join(out_dir, "continue.svg"), "w") as f:
        f.write(make_continue())

    print("All arcade SVGs generated successfully in", out_dir)

if __name__ == "__main__":
    main()
