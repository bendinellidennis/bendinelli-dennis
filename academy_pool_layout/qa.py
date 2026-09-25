from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parent
report=[]; ok=True

EXPECTED_IDS=["A1 AIR","A2 AIR","B1 AIR","B2 AIR","AIR SCALE","R1","R2","ASP HJ1","ASP HJ2","A1 WATER","A2 WATER","B1 WATER","B2 WATER","W SCALE","R3","R4","SCOPA","FONDO"]

for lang in ["IT","EN"]:
    pdf=ROOT/"output"/f"ACADEMY_DB_POOL_SYSTEMS_LAYOUT_PENETRATIONS_REV09_{lang}.pdf"
    if not pdf.exists():
        ok=False; report.append(f"FAIL {lang}: missing PDF"); continue
    reader=PdfReader(str(pdf))
    text="\n".join((p.extract_text() or "") for p in reader.pages)
    report.append(f"{lang}: pages={len(reader.pages)} bytes={pdf.stat().st_size}")
    if len(reader.pages)!=8 or pdf.stat().st_size<15000:
        ok=False; report.append(f"FAIL {lang}: page count or file size")
    for ident in EXPECTED_IDS:
        if ident not in text:
            ok=False; report.append(f"FAIL {lang}: missing penetration ID {ident}")
    for token in ["+550","+1350","+1600","9,90" if lang=="IT" else "9.90","18"]:
        if token not in text:
            ok=False; report.append(f"FAIL {lang}: missing key datum {token}")
    if lang=="IT":
        banned=["TECHNICAL ROOM LAYOUT + PENETRATIONS","PRE-CLOSURE CHECK","RIGHT-WALL LAYOUT","PIPE LAYERS","INSTALLATION SEQUENCE","SLEEVE SCHEDULE","THREE DIAMETERS"]
    else:
        banned=["POSA LOCALE TECNICO + FOROMETRIA","CONTROLLO PRIMA DELLA CHIUSURA","POSA PARETE DESTRA","STRATI DI TUBAZIONE","SEQUENZA DI INSTALLAZIONE","DISTINTA GUAINE","TRE DIAMETRI"]
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
