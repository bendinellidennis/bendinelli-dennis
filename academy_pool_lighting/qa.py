from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
report=[]; ok=True
for lang in ["IT","EN"]:
    pdf=ROOT/"output"/f"ACADEMY_DB_POOL_SYSTEMS_LIGHTING_PNEUMATIC_CONTROL_REV08_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    r=PdfReader(str(pdf))
    text="\n".join((p.extract_text() or "") for p in r.pages)
    report.append(f"{lang}: pages={len(r.pages)} bytes={pdf.stat().st_size}")
    if len(r.pages)!=8 or pdf.stat().st_size<300000:
        ok=False; report.append(f"FAIL {lang}: page count or size")
    if lang=="IT":
        banned=["REAL COMPONENT","COMMISSIONING AND","POOL LIGHTING +","DESIGN BOUNDARY","ELECTRICAL BOUNDARY","SERVICE SEPARATION","REAL PRODUCT FAMILY"]
    else:
        banned=["PRODOTTO REALE","MESSA IN SERVIZIO","ILLUMINAZIONE PISCINA +","LIMITE DI PROGETTO","LIMITE ELETTRICO","SEPARAZIONE DEI SERVIZI"]
    for token in banned:
        if token in text:
            ok=False; report.append(f"FAIL {lang}: foreign editorial text -> {token}")
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
