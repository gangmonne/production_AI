#!/usr/bin/env python3
"""프로덕션 폴더에서 파이프라인 보드 HTML을 생성한다.

사용법: python build_pipeline_board.py <production_dir> [--ep EP01]
입력: <dir>/00_analysis.md 제목용, 01_asset_manifest.json, 02_*.scene.json, 03_prompts/*.txt
출력: <dir>/<ep>_pipeline_board.html
"""
import argparse, glob, html, json, os, sys

CSS = """
body{font-family:'Segoe UI',Pretendard,sans-serif;background:#141118;color:#e8e2ee;margin:0;padding:24px}
h1{font-size:22px;color:#e9c46a} h2{font-size:16px;color:#c9a0dc;border-bottom:1px solid #3a2f47;padding-bottom:6px;margin-top:36px}
.meta{color:#9a8fb0;font-size:13px;line-height:1.7}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.card{background:#1e1826;border:1px solid #3a2f47;border-radius:10px;padding:12px}
.hd{display:flex;justify-content:space-between;margin-bottom:6px}
.tag{color:#e9c46a;font-weight:700;font-family:monospace} .typ{color:#7a6f90;font-size:11px}
.role{font-size:13px;margin-bottom:8px}
details summary{cursor:pointer;color:#8ecae6;font-size:12px}
pre{white-space:pre-wrap;background:#0f0c14;border-radius:8px;padding:10px;font-size:11px;color:#cfc7dd;line-height:1.5}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;color:#c9a0dc;border-bottom:1px solid #3a2f47;padding:8px 6px}
td{padding:8px 6px;border-bottom:1px solid #251d30;vertical-align:top}
.cut{color:#e9c46a;font-weight:700;font-family:monospace} .au{color:#9a8fb0;font-style:italic}
tr.pr td{border-bottom:1px solid #3a2f47;background:#181221}
.lock{background:#231a2e;border-left:3px solid #e76f51;padding:10px 14px;border-radius:6px;font-size:13px;line-height:1.7}
"""

def esc(s):
    return html.escape(str(s), quote=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("production_dir")
    ap.add_argument("--ep", default=None, help="에피소드 ID (기본: scene 파일명에서 추출)")
    args = ap.parse_args()
    d = args.production_dir

    scenes = sorted(glob.glob(os.path.join(d, "02_*.scene.json")))
    if not scenes:
        sys.exit("02_*.scene.json 없음")
    scene = json.load(open(scenes[0], encoding="utf-8"))
    manifest = json.load(open(os.path.join(d, "01_asset_manifest.json"), encoding="utf-8"))
    ep = args.ep or os.path.basename(scenes[0]).split("_")[1].split(".")[0]

    meta, look = scene["meta"], scene["look"]
    sdl = scene.get("screen_direction_lock", {})
    total = sum(s["dur_sec"] for s in scene["shotlist"])
    sdl_txt = " · ".join(f"{k} = {v}" for k, v in sdl.items() if k != "rule")

    out = [f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{esc(manifest["project"].upper())} {esc(ep)} — Pipeline Board</title>'
           f'<style>{CSS}</style></head><body>']
    out.append(f'<h1>{esc(manifest["project"].upper())} — {esc(ep)} 「{esc(meta["title"])}」 · AI 영상 자동화 파이프라인 보드</h1>')
    out.append(f'<p class="meta">{esc(meta["aspect_ratio"])} 세로 · 타깃 {meta["runtime_target_sec"]}초 · '
               f'이미지 {esc(manifest["image_model"])} / 영상 {esc(meta["video_model"])}<br>'
               f'스크린 방향 락: {esc(sdl_txt)} · {esc(sdl.get("rule",""))} · 화면 내 텍스트 생성 금지</p>')
    out.append(f'<div class="lock"><b>실행 전제:</b> 힉스필드 MCP 커넥터를 이 대화에서 켠 뒤 — '
               f'Phase A(에셋 {len(manifest["assets"])}종 × count 2) 발주 → 핸들당 1장 픽 → '
               f'Phase B({len(scene["shotlist"])}클립 순차 발주). 상세는 RUN_MANIFEST.json.</div>')

    out.append(f'<h2>2단계 — 에셋 매니페스트 ({len(manifest["assets"])}종)</h2><div class="grid">')
    for a in manifest["assets"]:
        out.append(f'<div class="card"><div class="hd"><span class="tag">{esc(a["handle"])}</span>'
                   f'<span class="typ">{esc(a["type"])}</span></div><div class="role">{esc(a["role"])}</div>'
                   f'<details><summary>generation prompt</summary><pre>{esc(a["prompt"])}</pre></details></div>')
    out.append('</div>')

    out.append(f'<h2>4·5단계 — 컷리스트 + 클립 프롬프트 ({len(scene["shotlist"])}클립 · 합계 {total}초)</h2>')
    out.append('<table><tr><th>컷</th><th>비트</th><th>길이</th><th>사이즈</th><th>카메라</th><th>레퍼런스</th><th>오디오</th></tr>')
    for s in scene["shotlist"]:
        out.append(f'<tr><td class="cut">{esc(s["cut"])}</td><td>{esc(s["beat"])}</td><td>{s["dur_sec"]}s</td>'
                   f'<td>{esc(s["size"])}</td><td>{esc(s["cam"])}</td><td>{esc(" ".join(s["refs"]))}</td>'
                   f'<td class="au">{esc(s["audio"])}</td></tr>')
        pf = os.path.join(d, s["prompt_file"])
        body = open(pf, encoding="utf-8").read() if os.path.exists(pf) else "(prompt file missing)"
        out.append(f'<tr class="pr"><td colspan="7"><details><summary>clip prompt — '
                   f'{esc(os.path.basename(s["prompt_file"]))}</summary><pre>{esc(body)}</pre></details></td></tr>')
    out.append('</table></body></html>')

    dest = os.path.join(d, f"{ep.lower()}_pipeline_board.html")
    open(dest, "w", encoding="utf-8").write("".join(out))
    print(dest)

if __name__ == "__main__":
    main()
