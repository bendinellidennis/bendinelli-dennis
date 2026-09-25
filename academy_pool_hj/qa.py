from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
report=[]; ok=True
for lang in ["IT","EN"]:
    pdf=ROOT/"output"/f"ACADEMY_DB_POOL_SYSTEMS_HYDROMASSAGE_VENTURI_REV05R_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    r=PdfReader(str(pdf))
    report.append(f"{lang}: pages={len(r.pages)} bytes={pdf.stat().st_size}")
    if len(r.pages)!=8 or pdf.stat().st_size<500000:
        ok=False; report.append(f"FAIL {lang}: page count or file size")
    rd=ROOT/f"render_{lang.lower()}"
    imgs=sorted(rd.glob("page-*.png"))
    report.append(f"{lang}: renders={len(imgs)}")
    if len(imgs)!=8:
        ok=False; report.append(f"FAIL {lang}: render count")
    for fp in imgs:
        im=Image.open(fp).convert("RGB")
        stat=ImageStat.Stat(im)
        mean=sum(stat.mean)/3
        extrema=im.getextrema()
        if mean>254.7:
            ok=False; report.append(f"FAIL {lang}: near-empty {fp.name}")
        # edge safety: detect very dark ink in 5-pixel outer border
        px=im.load(); w,h=im.size; dark=0
        for x in range(w):
            for y in list(range(0,5))+list(range(h-5,h)):
                if sum(px[x,y])<180: dark+=1
        for y in range(h):
            for x in list(range(0,5))+list(range(w-5,w)):
                if sum(px[x,y])<180: dark+=1
        if dark>100:
            report.append(f"WARN {lang}: dark content touches outer edge on {fp.name}")
report.append("PASS" if ok else "FAIL")
(ROOT/"qa_report.txt").write_text("\n".join(report),encoding="utf-8")
print("\n".join(report))
if not ok: raise SystemExit(1)
