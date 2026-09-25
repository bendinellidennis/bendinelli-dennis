from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
report=[]; ok=True
expected=["C-HJ","C-A-W","C-B-W","C-A-AIR","C-B-AIR","C-S-W","C-S-AIR","C-F-SUCT","C-F-RET","X250","X750","X100","X300","X500","X700","X900"]

for lang in ["IT","EN"]:
    pdf=ROOT/"output"/f"ACADEMY_DB_POOL_SYSTEMS_MANIFOLDS_REV10_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    r=PdfReader(str(pdf)); text="\n".join((p.extract_text() or "") for p in r.pages)
    report.append(f"{lang}: pages={len(r.pages)} bytes={pdf.stat().st_size}")
    if len(r.pages)!=8 or pdf.stat().st_size<15000:
        ok=False; report.append(f"FAIL {lang}: page count or size")
    for token in expected:
        if token not in text:
            ok=False; report.append(f"FAIL {lang}: missing {token}")
    if lang=="IT":
        banned=["MANIFOLDS AND DISTRIBUTORS","FABRICATION METHOD","PRE-INSTALLATION CHECK","MAIN MANIFOLD","WALL DISTRIBUTORS","STEPS DISTRIBUTORS","FILTRATION MANIFOLDS"]
    else:
        banned=["COLLETTORI E DISTRIBUTORI","METODO DI FABBRICAZIONE","CONTROLLO PRIMA DELLA POSA","COLLETTORE PRINCIPALE","DISTRIBUTORI A/B PARETE","DISTRIBUTORI SCALE","COLLETTORI FILTRAZIONE"]
    for t in banned:
        if t in text:
            ok=False; report.append(f"FAIL {lang}: foreign editorial text -> {t}")
    rd=ROOT/f"render_{lang.lower()}"; imgs=sorted(rd.glob("page-*.png"))
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
