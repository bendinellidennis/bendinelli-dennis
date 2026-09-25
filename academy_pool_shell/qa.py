from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
report=[]; ok=True
for lang in ["IT","EN"]:
    pdf=ROOT/"output"/f"ACADEMY_DB_POOL_SYSTEMS_SHELL_HYDRAULICS_REV07_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    r=PdfReader(str(pdf))
    report.append(f"{lang}: pages={len(r.pages)} bytes={pdf.stat().st_size}")
    if len(r.pages)!=8 or pdf.stat().st_size<350000:
        ok=False; report.append(f"FAIL {lang}: page count or size")
    rd=ROOT/f"render_{lang.lower()}"
    imgs=sorted(rd.glob("page-*.png"))
    report.append(f"{lang}: renders={len(imgs)}")
    if len(imgs)!=8:
        ok=False; report.append(f"FAIL {lang}: render count")
    for fp in imgs:
        im=Image.open(fp).convert("RGB")
        mean=sum(ImageStat.Stat(im).mean)/3
        if mean>254.7:
            ok=False; report.append(f"FAIL {lang}: near-empty {fp.name}")
report.append("PASS" if ok else "FAIL")
(ROOT/"qa_report.txt").write_text("\n".join(report),encoding="utf-8")
print("\n".join(report))
if not ok: raise SystemExit(1)
