from __future__ import annotations
import os, io, textwrap, zipfile
from pathlib import Path
import requests
from PIL import Image, ImageChops
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"
OUT_DIR = ROOT / "output"
ASSET_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = A4
NAVY = HexColor("#10263F")
NAVY2 = HexColor("#18364E")
CYAN = HexColor("#35A8C8")
CYAN_D = HexColor("#2388A7")
LIGHT = HexColor("#F3F6F8")
MID = HexColor("#D7E0E6")
TEXT = HexColor("#23384B")
MUTED = HexColor("#6C7E8C")
ORANGE = HexColor("#D4822D")
RED = HexColor("#C44A3B")
GREEN = HexColor("#3D806B")
WHITE = HexColor("#FFFFFF")
BLACK = HexColor("#111111")

URLS = {
    "valve_photo": [
        "https://dam.fluidra.com/asset/26c1c1ea-98c4-4a8d-8573-ad78ff54f8a7/Medium/MainView_ap_20569_v01_n0149572.jpg",
        "https://www.quimipool.com/img/scenes/93-scene_default.jpg",
    ],
    "valve_exploded": [
        "https://www.quimipool.com/img/scenes/93-scene_default.jpg",
        "https://spareparts.astralpool.com/fotos/pb-00431%2300%230.jpg",
    ],
    "filter_exploded": [
        "https://www.quimipool.com/img/scenes/74-scene_default.jpg",
    ],
    "filter_photo": [
        "https://piscinasdelestrecho.com/img/p/8/9/7/5/8975.jpg",
        "https://www.quimipool.com/img/scenes/74-scene_default.jpg",
    ],
    "pump_exploded": [
        "https://www.quimipool.com/img/scenes/159-scene_default.jpg",
    ],
    "pump_photo": [
        "https://recambiosdepiscinas.com/8812-medium_default/bomba-piscina-astral-victoria-plus-silent-100t-100cv-tf-65563.jpg",
        "https://www.quimipool.com/img/scenes/159-scene_default.jpg",
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Academy DB Plumbing Services)"}

def download_asset(key):
    path = ASSET_DIR / f"{key}.jpg"
    if path.exists() and path.stat().st_size > 5000:
        return path
    errs = []
    for url in URLS[key]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            ctype = (r.headers.get("content-type") or "").lower()
            if r.ok and len(r.content) > 5000 and ctype.startswith("image/"):
                tmp = path.with_suffix(".tmp")
                tmp.write_bytes(r.content)
                try:
                    with Image.open(tmp) as test:
                        test.verify()
                    tmp.replace(path)
                    return path
                except Exception as e:
                    tmp.unlink(missing_ok=True)
                    errs.append(f"{url} -> invalid image: {e}")
                    continue
            errs.append(f"{url} -> HTTP {r.status_code}, type={ctype}, {len(r.content)} bytes")
        except Exception as e:
            errs.append(f"{url} -> {e}")
    raise RuntimeError("Cannot download required REAL source image " + key + ":\n" + "\n".join(errs))

def trim_white(path: Path, out_name: str, margin=14):
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, (255,255,255))
    diff = ImageChops.difference(img, bg).convert("L")
    bbox = diff.point(lambda p: 0 if p < 10 else 255).getbbox()
    if bbox:
        l,t,r,b = bbox
        l=max(0,l-margin); t=max(0,t-margin); r=min(img.width,r+margin); b=min(img.height,b+margin)
        img = img.crop((l,t,r,b))
    out = ASSET_DIR / out_name
    img.save(out, quality=94)
    return out

ASSETS = {k: download_asset(k) for k in URLS}
ASSETS["valve_photo_crop"] = trim_white(ASSETS["valve_photo"], "valve_photo_crop.jpg", 12)
ASSETS["valve_exploded_crop"] = trim_white(ASSETS["valve_exploded"], "valve_exploded_crop.jpg", 10)
ASSETS["filter_crop"] = trim_white(ASSETS["filter_exploded"], "filter_crop.jpg", 10)
ASSETS["pump_crop"] = trim_white(ASSETS["pump_exploded"], "pump_crop.jpg", 10)
ASSETS["pump_photo_crop"] = trim_white(ASSETS["pump_photo"], "pump_photo_crop.jpg", 12)

COPY = {
"IT": {
"edition":"EDIZIONE ITALIANA",
"cover_kicker":"ACADEMY DB PLUMBING SERVICES",
"cover_title":"SISTEMI PISCINA",
"cover_sub":"NUCLEO FILTRAZIONE",
"cover_desc":"Valvola 6 vie • Filtro Vesubio • Victoria Plus Silent • percorso dell’acqua",
"cover_tag":"Manuale tecnico-professionale • Standard visivo REV03",
"p2k":"01 • COMPONENTE REALE",
"p2t":"Valvola 6 vie: prima capire il circuito, poi la posizione",
"p2lead":"La leva non è il punto di partenza. Un tecnico legge prima le cinque funzioni idrauliche — POMPA, RITORNO, SCARICO, ALTO e BASSO — e solo dopo associa la posizione operativa.",
"rule":"REGOLA OPERATIVA",
"ruletext":"Arrestare la pompa prima di cambiare posizione. Il percorso dell’acqua viene verificato sul componente realmente installato e sul relativo manuale.",
"ports":[("POMPA","mandata dalla pompa"),("RITORNO","ritorno verso piscina"),("SCARICO","scarico / controlavaggio"),("ALTO","collegamento lato alto filtro"),("BASSO","ritorno dal fondo filtro")],
"real":"FOTOGRAFIA REALE",
"p3k":"02 • ESPLOSO UFFICIALE / RICAMBI",
"p3t":"Dentro la 20569: organi, tenute e raccordi",
"p3lead":"L’esploso non sostituisce il manuale di servizio: serve a riconoscere gli organi che lavorano insieme e i punti in cui usura, particelle o deformazioni possono creare passaggi interni anomali.",
"p3cards":[("MANIGLIA + COPERCHIO","Comando meccanico e chiusura superiore."),("DISTRIBUTORE + TENUTA","Seleziona quali bocche vengono messe in comunicazione."),("CORPO + RACCORDI","Definisce le connessioni esterne reali dell’installazione.")],
"critical":"PUNTO CRITICO",
"criticaltext":"Non diagnosticare una valvola “a memoria”: prima seguire il circuito, poi verificare tenute, distributore e configurazione del corpo.",
"p4k":"03 • SEI POSIZIONI",
"p4t":"Seguire l’acqua: sei funzioni, una sola logica",
"p4lead":"Le denominazioni della maniglia sono operative. La diagnosi diventa più semplice quando ogni posizione viene tradotta nel percorso reale dell’acqua.",
"modes":[("FILTRAZIONE","POMPA → ALTO → letto filtrante → BASSO → RITORNO"),
("CONTROLAVAGGIO","POMPA → BASSO → letto filtrante → ALTO → SCARICO"),
("RISCIACQUO","POMPA → ALTO → letto filtrante → BASSO → SCARICO"),
("RICIRCOLO","POMPA → RITORNO • esclusione del filtro"),
("SCARICO","POMPA → SCARICO • scarico diretto"),
("CHIUSA","Circuito chiuso • pompa ferma")],
"p5k":"04 • FILTRO REALE + ESPLOSO",
"p5t":"Vesubio Ø600: leggere il filtro dall’interno",
"p5lead":"Nel progetto DB il riferimento è AstralPool Vesubio 15786: Ø600, portata nominale 14 m³/h, valvola 1½”. La fotografia e l’esploso mostrano insieme involucro, diffusore, letto filtrante e collettore.",
"filter_specs":[("Ø600 mm","diametro nominale"),("14 m³/h","portata nominale"),("1½”","valvola laterale"),("2.5 bar","pressione massima componente")],
"filter_note":"La pressione massima dichiarata non è la pressione di lavoro da “cercare”: è un limite del componente. La selezione reale dipende da portata, perdite e curva pompa.",
"p6k":"05 • POMPA REALE + SISTEMA",
"p6t":"Victoria Plus Silent 100T: la pompa crea portata, non decide il percorso",
"p6lead":"Il codice 65563 identifica la Victoria Plus Silent 1 HP trifase. Nel sistema la pompa genera portata e prevalenza; la valvola indirizza il flusso; il filtro separa le particelle.",
"roles":[("POMPA","portata + prevalenza"),("VALVOLA 6 VIE","scelta del percorso"),("FILTRO","separazione particelle"),("TRATTAMENTO","correzione pH / ORP")],
"p7k":"06 • CASO REALE DB",
"p7t":"Dal componente al sistema reale",
"p7lead":"La catena seguente usa solo connessioni già confermate nel documento tecnico del progetto. La vasca di compenso entra nella filtrazione; il circuito idromassaggio HJ resta separato.",
"chain":["SCOPA","FONDO","VASCA COMPENSO","C-F-SUCT","VICTORIA 100T","6 VIE","VESUBIO Ø600","pH / ORP","C-F-RET","R1–R4"],
"installer":"CONTROLLO INSTALLATORE",
"checks":["Verificare POMPA / RITORNO / SCARICO sulla valvola realmente fornita.","Misurare gli attacchi reali prima dell’incollaggio definitivo.","Mantenere SCARICO / CONTROLAVAGGIO separato Ø63.","Confermare curva pompa e perdite reali prima del dimensionamento finale."],
"sources":"FONTI VISIVE E TECNICHE",
},
"EN": {
"edition":"ENGLISH EDITION",
"cover_kicker":"ACADEMY DB PLUMBING SERVICES",
"cover_title":"POOL SYSTEMS",
"cover_sub":"FILTRATION CORE",
"cover_desc":"6-way valve • Vesubio filter • Victoria Plus Silent • water-path logic",
"cover_tag":"Technical-professional manual • Visual Standard REV03",
"p2k":"01 • REAL COMPONENT",
"p2t":"6-way valve: understand the circuit before the handle position",
"p2lead":"The lever is not the starting point. A technician first reads the five hydraulic functions — PUMP, RETURN, WASTE, TOP and BOTTOM — and only then associates the operating position.",
"rule":"OPERATING RULE",
"ruletext":"Stop the pump before changing position. Verify the water path on the actual installed component and its corresponding manual.",
"ports":[("PUMP","flow from the pump"),("RETURN","return to the pool"),("WASTE","drain / backwash"),("TOP","connection to filter top"),("BOTTOM","return from filter bottom")],
"real":"REAL PHOTOGRAPH",
"p3k":"02 • OFFICIAL EXPLODED / SPARES",
"p3t":"Inside 20569: moving parts, seals and unions",
"p3lead":"The exploded view does not replace the service manual. It helps identify the parts that work together and the areas where wear, particles or deformation can create abnormal internal bypass.",
"p3cards":[("HANDLE + COVER","Mechanical control and upper closure."),("DIVERTER + SEAL","Selects which ports communicate."),("BODY + UNIONS","Defines the actual external installation connections.")],
"critical":"CRITICAL POINT",
"criticaltext":"Do not diagnose a valve from memory: trace the circuit first, then inspect seals, diverter and body configuration.",
"p4k":"03 • SIX POSITIONS",
"p4t":"Follow the water: six functions, one logic",
"p4lead":"Handle labels describe operating functions. Diagnosis becomes much clearer when each position is translated into the real water path.",
"modes":[("FILTER","PUMP → TOP → filter bed → BOTTOM → RETURN"),
("BACKWASH","PUMP → BOTTOM → filter bed → TOP → WASTE"),
("RINSE","PUMP → TOP → filter bed → BOTTOM → WASTE"),
("RECIRCULATE","PUMP → RETURN • filter bypass"),
("WASTE","PUMP → WASTE • direct drain"),
("CLOSED","Circuit closed • pump stopped")],
"p5k":"04 • REAL FILTER + EXPLODED",
"p5t":"Vesubio Ø600: read the filter from the inside",
"p5lead":"The DB project reference is AstralPool Vesubio 15786: Ø600, nominal 14 m³/h, 1½” valve. The photograph and exploded view show the shell, diffuser, filter bed and collector together.",
"filter_specs":[("Ø600 mm","nominal diameter"),("14 m³/h","nominal flow"),("1½”","side valve"),("2.5 bar","component maximum pressure")],
"filter_note":"Maximum declared pressure is not a target operating pressure: it is a component limit. Real selection depends on flow, losses and pump curve.",
"p6k":"05 • REAL PUMP + SYSTEM",
"p6t":"Victoria Plus Silent 100T: the pump creates flow, it does not choose the path",
"p6lead":"Code 65563 identifies the Victoria Plus Silent 1 HP three-phase pump. The pump creates flow and head; the valve directs the water; the filter separates particles.",
"roles":[("PUMP","flow + head"),("6-WAY VALVE","path selection"),("FILTER","particle separation"),("TREATMENT","pH / ORP correction")],
"p7k":"06 • DB CASE STUDY",
"p7t":"From the component to the real system",
"p7lead":"The chain below uses only connections already confirmed in the project handoff. The Balance Tank is part of filtration; the HJ hydromassage circuit remains separate.",
"chain":["VACUUM","MAIN DRAIN","BALANCE TANK","C-F-SUCT","VICTORIA 100T","6-WAY","VESUBIO Ø600","pH / ORP","C-F-RET","R1–R4"],
"installer":"INSTALLER CHECK",
"checks":["Verify PUMP / RETURN / WASTE on the actual supplied valve.","Measure real machine connections before final solvent welding.","Keep WASTE / BACKWASH on its own Ø63 line.","Confirm pump curve and real pressure losses before final sizing."],
"sources":"VISUAL & TECHNICAL SOURCES",
}}
SOURCES_IT = [
("S1","Pagina prodotto AstralPool 20569 / catalogo Fluidra"),
("S2","Quimipool: componente reale + esploso, famiglia valvole"),
("S3","Dati prodotto AstralPool Vesubio 15786"),
("S4","Quimipool: Vesubio reale + esploso"),
("S5","Catalogo ricambi Fluidra 65563"),
("S6","Documento tecnico DB Plumbing Services 22-09-2026"),
]
SOURCES_EN = [
("S1","AstralPool 20569 product page / Fluidra catalogue"),
("S2","Quimipool real component + exploded view, valve family"),
("S3","AstralPool Vesubio 15786 product data"),
("S4","Quimipool real Vesubio + exploded view"),
("S5","Fluidra spare-parts catalogue 65563"),
("S6","DB Plumbing Services project handoff 22-09-2026"),
]

def draw_text(c, text, x, y, maxw, font="Helvetica", size=10, leading=None, color=TEXT, max_lines=None):
    if leading is None: leading = size*1.25
    c.setFont(font, size); c.setFillColor(color)
    words = text.split()
    lines=[]; cur=""
    for w in words:
        trial = w if not cur else cur+" "+w
        if stringWidth(trial, font, size) <= maxw:
            cur=trial
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    if max_lines: lines=lines[:max_lines]
    yy=y
    for line in lines:
        c.drawString(x, yy, line)
        yy -= leading
    return yy

def fit_img(c, path, x, y, w, h, pad=0):
    im = Image.open(path)
    iw,ih=im.size
    scale=min((w-2*pad)/iw,(h-2*pad)/ih)
    dw,dh=iw*scale,ih*scale
    xx=x+(w-dw)/2; yy=y+(h-dh)/2
    c.drawImage(ImageReader(im),xx,yy,dw,dh,mask='auto')
    return (xx,yy,dw,dh)

def header(c, kicker, page, edition):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.3); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.1); c.drawRightString(W-42,H-30,("POOL SYSTEMS • FILTRATION CORE • REV03" if edition.startswith("EN") else "SISTEMI PISCINA • NUCLEO FILTRAZIONE • REV03"))
    c.setStrokeColor(MID); c.setLineWidth(.6); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",9); c.drawString(42,H-62,kicker)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.7); c.drawRightString(W-42,24,f"{edition} • {page}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.5); c.line(42,35,95,35)

def title(c, t, lead=None, y=H-100):
    yy=draw_text(c,t,42,y,W-84,"Helvetica-Bold",25,28,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-2,128,yy-2)
    if lead:
        yy=draw_text(c,lead,42,yy-28,W-84,"Helvetica",10.3,14,MUTED,4)
    return yy

def card(c,x,y,w,h,title_txt,body,accent=CYAN):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.setLineWidth(.8)
    c.roundRect(x,y,w,h,8,fill=1,stroke=1)
    c.setFillColor(accent); c.rect(x,y,w,4,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.2); c.drawString(x+12,y+h-22,title_txt)
    draw_text(c,body,x+12,y+h-40,w-24,"Helvetica",8.1,11,MUTED,4)

def image_panel(c,path,x,y,w,h,label=None):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,10,fill=1,stroke=1)
    fit_img(c,path,x+10,y+10,w-20,h-20)
    if label:
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7); c.drawString(x+12,y+8,label)

def cover(c,L):
    c.setFillColor(LIGHT); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(NAVY); c.rect(0,0,W,70,fill=1,stroke=0)
    c.setFillColor(CYAN); c.rect(0,70,9,H-70,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawString(54,H-58,L["cover_kicker"])
    c.setFont("Helvetica-Bold",34); c.drawString(54,H-122,L["cover_title"])
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",17); c.drawString(54,H-154,L["cover_sub"])
    draw_text(c,L["cover_desc"],54,H-190,245,"Helvetica",11,15,TEXT,4)
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.3); c.drawString(54,H-250,L["cover_tag"])
    # visual hero
    image_panel(c,ASSETS["filter_crop"],315,150,230,430)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(54,115,"DB PLUMBING SERVICES • MALTA")
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9); c.drawString(54,37,("REAL COMPONENTS • VERIFIED SOURCES • INSTALLER-FIRST METHOD" if L["edition"].startswith("EN") else "COMPONENTI REALI • FONTI VERIFICATE • METODO PENSATO PER L'INSTALLATORE"))
    c.showPage()

def page2(c,L,pno):
    header(c,L["p2k"],pno,L["edition"]); y=title(c,L["p2t"],L["p2lead"])
    image_panel(c,ASSETS["valve_photo_crop"],42,278,280,300,L["real"])
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(342,278,211,300,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(360,550,L["rule"])
    draw_text(c,L["ruletext"],360,530,175,"Helvetica",8.6,12,TEXT,7)
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8); c.drawString(360,456,("FIVE FUNCTIONAL CONNECTIONS" if L["edition"].startswith("EN") else "CINQUE CONNESSIONI FUNZIONALI"))
    yy=432
    for lab,desc in L["ports"]:
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(360,yy,lab)
        c.setFillColor(MUTED); c.setFont("Helvetica",7.8); c.drawString(420,yy,desc)
        c.setStrokeColor(MID); c.line(360,yy-8,535,yy-8); yy-=36
    c.setFillColor(CYAN); c.rect(42,210,511,4,fill=1,stroke=0)
    draw_text(c,"20569 • Configuration 3 • 1½”",42,190,240,"Helvetica-Bold",11,14,NAVY,2)
    draw_text(c,"Use the model marking and the actual installation manual before gluing or cutting any connection." if L["edition"].startswith("EN") else "Usare la marcatura del modello e il manuale reale prima di incollare o tagliare qualsiasi collegamento.",42,160,511,"Helvetica",9.2,13,MUTED,4)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(42,58,"[S1] AstralPool / Fluidra 20569   [S2] Quimipool real component + exploded view")
    c.showPage()

def page3(c,L,pno):
    header(c,L["p3k"],pno,L["edition"]); y=title(c,L["p3t"],L["p3lead"])
    image_panel(c,ASSETS["valve_exploded_crop"],42,190,335,420,("REAL COMPONENT + EXPLODED SUPPORT" if L["edition"].startswith("EN") else "COMPONENTE REALE + SUPPORTO ESPLOSO"))
    cy=545
    for i,(h,b) in enumerate(L["p3cards"]):
        card(c,397,cy-72,156,72,h,b,[CYAN,ORANGE,GREEN][i]); cy-=87
    c.setFillColor(HexColor("#FFF5E8")); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(397,190,156,92,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",9); c.drawString(411,258,L["critical"])
    draw_text(c,L["criticaltext"],411,238,128,"Helvetica",7.8,10.5,TEXT,7)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(42,58,"[S2] Quimipool / AstralPool valve family exploded view   [S1] AstralPool 20569")
    c.showPage()

def page4(c,L,pno):
    header(c,L["p4k"],pno,L["edition"]); y=title(c,L["p4t"],L["p4lead"])
    image_panel(c,ASSETS["valve_photo_crop"],42,385,170,165,L["real"])
    x0=235; y0=520; cw=150; ch=76
    for i,(m,path) in enumerate(L["modes"]):
        row=i//2; col=i%2
        x=x0+col*(cw+18); y=y0-row*(ch+18)-ch
        accent=[CYAN,ORANGE,CYAN_D,GREEN,RED,NAVY2][i]
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,cw,ch,8,fill=1,stroke=1)
        c.setFillColor(accent); c.rect(x,y,cw,4,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(x+11,y+ch-22,m)
        draw_text(c,path,x+11,y+ch-42,cw-22,"Helvetica-Bold",7.5,10,accent,3)
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,145,511,115,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(60,232,("ACADEMY METHOD" if L["edition"].startswith("EN") else "METODO ACADEMY"))
    meth=("Read the hydraulic function → trace the water path → verify the actual port markings → only then use the handle label."
          if L["edition"].startswith("EN") else
          "Leggere la funzione idraulica → seguire il percorso dell’acqua → verificare le marcature reali → solo dopo usare la posizione della leva.")
    draw_text(c,meth,60,208,475,"Helvetica",9.8,14,TEXT,5)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(42,58,"[S1] AstralPool six-way valve operating functions")
    c.showPage()

def page5(c,L,pno):
    header(c,L["p5k"],pno,L["edition"]); y=title(c,L["p5t"],L["p5lead"])
    image_panel(c,ASSETS["filter_crop"],42,245,330,400,("REAL FILTER + EXPLODED SUPPORT" if L["edition"].startswith("EN") else "FILTRO REALE + SUPPORTO ESPLOSO"))
    sx=394; sy=573
    for i,(v,d) in enumerate(L["filter_specs"]):
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(sx,sy,159,50,8,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",13.2); c.drawString(sx+13,sy+24,v)
        c.setFillColor(MUTED); c.setFont("Helvetica",6.8); c.drawString(sx+13,sy+10,d)
        sy-=58
    c.setFillColor(HexColor("#FFF0EF")); c.setStrokeColor(HexColor("#F0CAC5")); c.roundRect(394,245,159,92,8,fill=1,stroke=1)
    c.setFillColor(RED); c.setFont("Helvetica-Bold",8.3); c.drawString(408,313,"ENGINEERING NOTE")
    draw_text(c,L["filter_note"],408,294,130,"Helvetica",7.25,9.6,TEXT,8)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(42,58,"[S3] AstralPool Vesubio 15786   [S4] Quimipool real filter + exploded view")
    c.showPage()

def page6(c,L,pno):
    header(c,L["p6k"],pno,L["edition"]); y=title(c,L["p6t"],L["p6lead"])
    image_panel(c,ASSETS["pump_crop"],42,285,300,330,("REAL PUMP + EXPLODED SUPPORT" if L["edition"].startswith("EN") else "POMPA REALE + SUPPORTO ESPLOSO"))
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(362,285,191,330,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(380,584,("ROLE SEPARATION" if L["edition"].startswith("EN") else "SEPARAZIONE DELLE FUNZIONI"))
    yy=548
    for h,b in L["roles"]:
        c.setFillColor(CYAN); c.circle(383,yy+2,3.2,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.7); c.drawString(395,yy,h)
        c.setFillColor(MUTED); c.setFont("Helvetica",7.4); c.drawString(395,yy-14,b)
        yy-=62
    # elegant chain
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8); c.drawString(42,232,("FUNCTIONAL CHAIN" if L["edition"].startswith("EN") else "CATENA FUNZIONALE"))
    chain=(["VACUUM","MAIN DRAIN","BT","VICTORIA","6-WAY","VESUBIO","pH / ORP","R1-R4"] if L["edition"].startswith("EN") else ["SCOPA","FONDO","V. COMP.","VICTORIA","6 VIE","VESUBIO","pH / ORP","R1-R4"])
    start=42; yline=187; stepw=55; gap=8
    x=start
    for i,lab in enumerate(chain):
        col = NAVY if i not in (2,5,6) else (GREEN if i in (2,6) else ORANGE)
        c.setFillColor(col); c.setFont("Helvetica-Bold",6.1)
        c.drawCentredString(x+stepw/2,yline+13,lab)
        c.setStrokeColor(col); c.setLineWidth(1.8); c.line(x,yline,x+stepw,yline)
        if i < len(chain)-1:
            c.setStrokeColor(CYAN); c.setLineWidth(1.2); c.line(x+stepw,yline,x+stepw+gap-2,yline)
            c.setFillColor(CYAN); c.circle(x+stepw+gap-2,yline,2.0,fill=1,stroke=0)
        x += stepw+gap
    c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(42,58,("[S5] Fluidra spare-parts catalogue 65563   [S6] DB project handoff" if L["edition"].startswith("EN") else "[S5] Catalogo ricambi Fluidra 65563   [S6] Documento tecnico DB"))
    c.showPage()

def page7(c,L,pno):
    header(c,L["p7k"],pno,L["edition"]); y=title(c,L["p7t"],L["p7lead"])
    # montage using actual component imagery
    image_panel(c,ASSETS["pump_photo_crop"],42,390,145,160,"65563")
    image_panel(c,ASSETS["valve_photo_crop"],207,390,145,160,"20569")
    image_panel(c,ASSETS["filter_crop"],372,390,181,160,"15786")
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8); c.drawString(42,355,("CONFIRMED FILTRATION CHAIN" if L["edition"].startswith("EN") else "CATENA FILTRAZIONE CONFERMATA"))
    x=42; yline=320
    stepw=(511-9*6)/10
    for i,lab in enumerate(L["chain"]):
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",6.2)
        c.drawCentredString(x+stepw/2,yline+15,lab)
        c.setStrokeColor(CYAN if i in (0,1,4,5,6,9) else GREEN); c.setLineWidth(2.2)
        c.line(x,yline,x+stepw,yline)
        if i<9:
            c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8); c.drawString(x+stepw+1,yline-3,"›")
        x+=stepw+6
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,125,511,150,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(60,248,L["installer"])
    yy=220
    for chk in L["checks"]:
        c.setStrokeColor(GREEN); c.setLineWidth(1.5); c.rect(60,yy-3,9,9,fill=0,stroke=1)
        draw_text(c,chk,82,yy+1,445,"Helvetica",8.4,11,TEXT,2)
        yy-=28
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6.7); c.drawString(42,91,L["sources"])
    sx=42; sy=76
    for ref,desc in (SOURCES_EN if L["edition"].startswith("EN") else SOURCES_IT):
        c.setFont("Helvetica",5.8); c.setFillColor(MUTED)
        c.drawString(sx,sy,f"[{ref}] {desc}")
        sy-=9
    c.showPage()

def build_pdf(lang):
    L=COPY[lang]
    out=OUT_DIR / f"ACADEMY_DB_POOL_SYSTEMS_CONFERENCE_VISUAL_STANDARD_REV03_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L)
    page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7)
    c.save()
    return out

if __name__=="__main__":
    print("Downloading and embedding REAL source imagery...")
    for k,p in ASSETS.items():
        print(k,p,p.stat().st_size)
    it=build_pdf("IT")
    en=build_pdf("EN")
    print("Built:", it, en)
