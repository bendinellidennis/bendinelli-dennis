from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
out=ROOT/"output"
report=[]
ok=True
for lang in ["IT","EN"]:
    pdf=out/f"ACADEMY_DB_POOL_SYSTEMS_OVERFLOW_BALANCE_TANK_REV04_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    r=PdfReader(str(pdf))
    report.append(f"{lang}: pages={len(r.pages)} bytes={pdf.stat().st_size}")
    if len(r.pages)!=8 or pdf.stat().st_size<500000:
        ok=False; report.append(f"FAIL {lang}: page count or size")
    render=ROOT/f"render_{lang.lower()}"
    imgs=sorted(render.glob("page-*.png"))
    report.append(f"{lang}: renders={len(imgs)}")
    if len(imgs)!=8:
        ok=False; report.append(f"FAIL {lang}: render count")
    for imf in imgs:
        im=Image.open(imf).convert("RGB")
        stat=ImageStat.Stat(im)
        mean=sum(stat.mean)/3
        if mean>254.6:
            ok=False; report.append(f"FAIL {lang}: near-empty page {imf.name}")
report.append("PASS" if ok else "FAIL")
(ROOT/"qa_report.txt").write_text("\n".join(report),encoding="utf-8")
print("\n".join(report))
if not ok: raise SystemExit(1)
