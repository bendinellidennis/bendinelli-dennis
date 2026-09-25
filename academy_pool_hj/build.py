from __future__ import annotations
from pathlib import Path
import io, os, math, re
import requests
from PIL import Image, ImageOps, ImageChops
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path(__file__).resolve().parent
ASSET=ROOT/"assets"; OUT=ROOT/"output"
ASSET.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
W,H=A4

NAVY=HexColor("#10263F"); NAVY2=HexColor("#18364E"); CYAN=HexColor("#35A8C8"); CYAN_D=HexColor("#2388A7")
LIGHT=HexColor("#F3F6F8"); MID=HexColor("#D7E0E6"); TEXT=HexColor("#24384A"); MUTED=HexColor("#697D8B")
ORANGE=HexColor("#D4822D"); RED=HexColor("#C44A3B"); GREEN=HexColor("#3D806B"); WHITE=HexColor("#FFFFFF")
BLUEW=HexColor("#DFF2F8"); PALE_GREEN=HexColor("#EEF7F3"); PALE_ORANGE=HexColor("#FFF5E8"); PALE_RED=HexColor("#FFF0EF")

HEADERS={"User-Agent":"Mozilla/5.0 (Academy DB Plumbing Services technical education)"}
URLS={
 "maxim_photo":[
   "https://fluidra.bynder.com/m/1d66d01ee83aa879/Medium-maximpump.jpg",
 ],
 "maxim_datasheet":[
   "https://fluidra.bynder.com/m/7a868efc4b0eb6ee/original/productdatasheet_08005_08004_08003_EN_ES_2021_11.pdf",
 ],
 "maxim_exploded":[
   "https://spareparts.astralpool.com/fotos/pb-00394%2306%230.jpg",
   "https://spareparts.fluidra.com/fotos/pb-00394%2306%230.jpg",
 ],
 "grating":[
   "https://fluidra.bynder.com/m/7eede3d1d26836d2/Medium-00285bp144_00281.jpg",
 ],
 "balboa_manual":[
   "https://www.balboawater.com/wp-content/uploads/2024/08/Freedom-Jets_French.pdf",
 ]
}

def download(key):
    urls=URLS[key]
    ext=".pdf" if "pdf" in urls[0].lower() or "manual" in key or "datasheet" in key else ".jpg"
    p=ASSET/f"{key}{ext}"
    if p.exists() and p.stat().st_size>5000: return p
    errs=[]
    for url in urls:
        try:
            r=requests.get(url,headers=HEADERS,timeout=40,allow_redirects=True)
            ct=(r.headers.get("content-type") or "").lower()
            if r.ok and len(r.content)>5000:
                if ext==".pdf" and ("pdf" in ct or r.content[:4]==b"%PDF"):
                    p.write_bytes(r.content); return p
                if ext!=".pdf" and ("image" in ct or r.content[:2]==b"\xff\xd8"):
                    p.write_bytes(r.content)
                    try:
                        with Image.open(p) as im: im.verify()
                        return p
                    except Exception as e:
                        p.unlink(missing_ok=True); errs.append(f"invalid image {e}"); continue
            errs.append(f"{url} HTTP {r.status_code} {ct} {len(r.content)}")
        except Exception as e: errs.append(f"{url} {e}")
    raise RuntimeError(f"DOWNLOAD FAIL {key}: {errs}")

RAW={k:download(k) for k in URLS}

def render_pdf_page(pdf_path,page_index,out_name,dpi=180,clip=None):
    doc=fitz.open(str(pdf_path)); page=doc[page_index]
    mat=fitz.Matrix(dpi/72,dpi/72)
    pix=page.get_pixmap(matrix=mat,alpha=False,clip=clip)
    out=ASSET/out_name
    pix.save(str(out))
    doc.close()
    return out

# Manufacturer document page visuals
ASSETS={}
ASSETS["maxim_photo"]=RAW["maxim_photo"]
ASSETS["maxim_exploded"]=RAW["maxim_exploded"]
ASSETS["grating"]=RAW["grating"]
ASSETS["maxim_curve_page"]=render_pdf_page(RAW["maxim_datasheet"],1,"maxim_curve_page.png",180)
ASSETS["maxim_data_page"]=render_pdf_page(RAW["maxim_datasheet"],2,"maxim_data_page.png",180)
ASSETS["balboa_page"]=render_pdf_page(RAW["balboa_manual"],0,"balboa_page.png",220)
def crop_box(path,out_name,frac_box):
    im=Image.open(path).convert("RGB")
    l=int(im.width*frac_box[0]); t=int(im.height*frac_box[1]); r=int(im.width*frac_box[2]); b=int(im.height*frac_box[3])
    out=ASSET/out_name
    im.crop((l,t,r,b)).save(out,quality=96)
    return out
ASSETS["balboa_specs_crop"]=crop_box(ASSETS["balboa_page"],"balboa_specs_crop.jpg",(0.03,0.02,0.97,0.43))

def crop_nonwhite(path,out_name,margin=15):
    im=Image.open(path).convert("RGB")
    bg=Image.new("RGB",im.size,(255,255,255))
    diff=ImageChops.difference(im,bg).convert("L")
    bbox=diff.point(lambda p:0 if p<12 else 255).getbbox()
    if bbox:
        l,t,r,b=bbox
        l=max(0,l-margin); t=max(0,t-margin); r=min(im.width,r+margin); b=min(im.height,b+margin)
        im=im.crop((l,t,r,b))
    out=ASSET/out_name; im.save(out,quality=95)
    return out

ASSETS["maxim_photo_crop"]=crop_nonwhite(ASSETS["maxim_photo"],"maxim_photo_crop.jpg",10)
ASSETS["maxim_exploded_crop"]=crop_nonwhite(ASSETS["maxim_exploded"],"maxim_exploded_crop.jpg",10)
ASSETS["grating_crop"]=crop_nonwhite(ASSETS["grating"],"grating_crop.jpg",12)

COPY={
"IT":{
 "edition":"EDIZIONE ITALIANA",
 "cover_title":"IDROMASSAGGIO ACQUA + ARIA VENTURI",
 "cover_sub":"Jet, pompa, aspirazioni, bilanciamento e sicurezza",
 "cover_desc":"Componenti reali verificati • curve pompa • principio Venturi • caso reale DB Plumbing Services",
 "k2":"01 • IDENTITA' DEL JET",
 "t2":"Prima regola: non trasferire i dati da un jet all'altro",
 "l2":"Un jet aria/acqua puo' avere attacchi simili ma prestazioni e requisiti diversi. Nell'Academy i dati di un modello verificato restano legati a quel modello; un componente di progetto non riceve valori 'per analogia'.",
 "bench":"RIFERIMENTO TECNICO VERIFICATO",
 "balboa_specs":[("Balboa/HydroAir Freedom 10-FS715","modello verificato dal manuale ufficiale"),("Acqua Ø50 mm","attacco interno acqua"),("Aria Ø32 mm","attacco interno aria"),("3 m³/h @ 9 m H2O","portata raccomandata 10-FS711/10-FS715"),("Foro consigliato 2 5/8 in","circa 66.7 mm"),("Non drenante","10-FS715 / 10-FS715T")],
 "dbhold":"PUNTO DA CONFERMARE NEL PROGETTO DB",
 "dbholdtxt":"Il materiale di progetto identifica BOOSPA aria/acqua 50/32, rif. A-000000-00182. Gli attacchi 50/32 sono confermati nel dossier DB, ma portata, curva, foro, tenute e geometria interna NON sono confermati senza documentazione del produttore/fornitore. Il Balboa 10-FS715 e' un riferimento verificato, non un sostituto approvato automaticamente.",
 "k3":"02 • PRINCIPIO VENTURI",
 "t3":"L'aria non viene 'spinta': il getto d'acqua la aspira",
 "l3":"Nel Freedom 10-FS715 il flusso d'acqua attraverso il corpo del jet genera la depressione che richiama aria dalla linea dedicata. Balboa specifica di collegare acqua e aria alle bocche marcate correttamente e di evitare cedimenti della linea aria che possono compromettere l'aspirazione.",
 "venturi_note":"Il manuale Balboa indica che l'uso di una pompa aria per aumentare artificialmente l'effetto dei Freedom non e' raccomandato: la serie e' progettata per funzionare senza pompa aria aggiuntiva.",
 "k4":"03 • POMPA REALE",
 "t4":"MAXIM 08005: il punto di lavoro si legge sulla curva, non dai cavalli",
 "l4":"AstralPool identifica la 08005 come MAXIM 5.5 HP trifase. La scheda ufficiale riporta 230/400 V, 50 Hz, connessioni da 3 in, prefiltro da 8 L e P1 4.83 kW. La portata cambia fortemente con la prevalenza.",
 "curve_rows":[("8 m","88 m³/h"),("10 m","78 m³/h"),("12 m","67 m³/h"),("14 m","53 m³/h"),("16 m","34 m³/h"),("18 m","17 m³/h")],
 "curve_rule":"Esempio: 67 m³/h e' il dato ufficiale a 12 m di prevalenza per la 08005. Non significa che la pompa 'dara' 67 m³/h in ogni impianto: il punto reale e' l'intersezione tra curva pompa e curva del sistema.",
 "k5":"04 • ASPIRAZIONI E SICUREZZA",
 "t5":"La portata della griglia non basta a dimostrare la sicurezza anti-intrappolamento",
 "l5":"AstralPool dichiara per la griglia inox AISI-316L 30766, 400x400 mm, una portata massima raccomandata di 83 m³/h a 0.5 m/s. Questo dato serve al dimensionamento idraulico, ma da solo non certifica che una configurazione sia sicura contro l'intrappolamento.",
 "suction_check":"VERIFICA IDRAULICA ILLUSTRATIVA - NON VERDETTO DI CONFORMITA'",
 "suction_txt":"Nel caso reale DB sono previste 4 griglie fisiche, 2 per ciascuna pompa. Se una pompa lavorasse a circa 67 m³/h, due griglie identiche e perfettamente bilanciate vedrebbero circa 33.5 m³/h ciascuna; anche una singola 30766 avrebbe nominalmente 67 < 83 m³/h. Questo NON sostituisce verifica di certificazione, spaziatura, collegamento, coperture, norme applicabili e comportamento in caso di blocco.",
 "k6":"05 • ARCHITETTURA DB",
 "t6":"Due pompe, un collettore comune e cinque dorsali acqua",
 "l6":"Questa e' l'architettura funzionale confermata nel progetto DB. E' un caso reale specifico, non una regola universale per tutte le piscine idromassaggio.",
 "k7":"06 • 45 JET + 5 CIRCUITI ARIA",
 "t7":"Bilanciare l'acqua e mantenere indipendenti le cinque linee Venturi",
 "l7":"Il progetto divide 36 jet parete in due settori da 18 e mantiene i 9 jet scale su una dorsale dedicata. Le cinque dorsali aria Ø32 restano indipendenti fino al punto asciutto; non e' previsto un collettore aria comune nel locale tecnico.",
 "k8":"07 • MESSA IN SERVIZIO E PUNTI DA CONFERMARE",
 "t8":"Prima dell'avviamento: misurare, provare, confrontare con le curve",
 "l8":"Un impianto idromassaggio non si approva perche' 'fa tante bolle'. L'accettazione richiede portata e pressione coerenti, aspirazioni sicure, nessuna aria indesiderata lato aspirazione, resa uniforme e dati elettrici entro targa.",
 "checks":[
  ("1","Identita' componenti","Confermare jet BOOSPA realmente fornito e relativa documentazione."),
  ("2","Aspirazioni","Confermare modello, certificazioni, disposizione e prescrizioni anti-intrappolamento."),
  ("3","Curve","Calcolare perdite reali di ogni circuito e confrontarle con la curva MAXIM 08005."),
  ("4","Tenuta","Provare circuiti acqua e aria separatamente prima della chiusura."),
  ("5","Venturi","Verificare aspirazione aria uniforme; nessuna sacca o cedimento che trattenga acqua."),
  ("6","Bilanciamento","Confrontare fasce 4-9 e scale; correggere solo con misure, non 'a occhio'."),
  ("7","Elettrico","Verificare corrente, protezioni e comando con elettricista qualificato."),
 ],
 "holdbox":"DATI NON ANCORA DA INSEGNARE COME DEFINITIVI NEL CASO REALE",
 "holditems":["Portata ufficiale del jet BOOSPA A-000000-00182.","Foro di posa / tenute / geometria interna BOOSPA.","Curva di sistema HJ completa e punto di lavoro finale.","Conformita' definitiva delle aspirazioni 30766 nella posa reale.","Quote esatte degli attacchi sulle macchine acquistate."],
 "footer":"Fonti tecniche: AstralPool/Fluidra, Balboa Water Group, dossier DB Plumbing Services. I dati di progetto non verificati restano DA CONFERMARE."
},
"EN":{
 "edition":"ENGLISH EDITION",
 "cover_title":"HYDROMASSAGE WATER + VENTURI AIR",
 "cover_sub":"Jets, pump, suction, balancing and safety",
 "cover_desc":"Verified real components • pump curves • Venturi principle • DB Plumbing Services case study",
 "k2":"01 • JET IDENTITY",
 "t2":"First rule: never transfer performance data from one jet to another",
 "l2":"Air/water jets may use similar connection sizes while having different performance and installation requirements. In the Academy, verified model data stays attached to that model; project components do not inherit values 'by analogy'.",
 "bench":"VERIFIED TECHNICAL BENCHMARK",
 "balboa_specs":[("Balboa/HydroAir Freedom 10-FS715","model verified from official manual"),("Water Ø50 mm","internal water connection"),("Air Ø32 mm","internal air connection"),("3 m³/h @ 9 m H2O","recommended flow 10-FS711/10-FS715"),("Recommended hole 2 5/8 in","approximately 66.7 mm"),("Non-drainable","10-FS715 / 10-FS715T")],
 "dbhold":"DB PROJECT HOLD",
 "dbholdtxt":"The project material identifies BOOSPA Air/Water 50/32, ref. A-000000-00182. The 50/32 connections are confirmed in the DB dossier, but flow, curve, hole size, seals and internal geometry are NOT frozen without manufacturer/supplier documentation. Balboa 10-FS715 is a verified benchmark, not an automatically approved substitute.",
 "k3":"02 • VENTURI PRINCIPLE",
 "t3":"Air is not 'pushed': the water jet draws it in",
 "l3":"In the Freedom 10-FS715, water flow through the jet body creates the pressure reduction that draws air through the dedicated line. Balboa requires water and air to be connected to the correct marked sockets and warns against sagging air hoses because aspiration can be impaired.",
 "venturi_note":"The Balboa manual states that using an air pump to boost Freedom jets is not recommended: the series is designed to operate efficiently without an air pump.",
 "k4":"03 • REAL PUMP",
 "t4":"MAXIM 08005: read the operating point from the curve, not from horsepower",
 "l4":"AstralPool identifies 08005 as the 5.5 HP three-phase MAXIM. The official datasheet states 230/400 V, 50 Hz, 3 in connections, 8 L prefilter and P1 4.83 kW. Flow changes strongly with system head.",
 "curve_rows":[("8 m","88 m³/h"),("10 m","78 m³/h"),("12 m","67 m³/h"),("14 m","53 m³/h"),("16 m","34 m³/h"),("18 m","17 m³/h")],
 "curve_rule":"Example: 67 m³/h is the official 08005 value at 12 m head. It does not mean the pump will always deliver 67 m³/h: the real operating point is where the pump curve intersects the system curve.",
 "k5":"04 • SUCTION AND SAFETY",
 "t5":"A grille flow rating alone does not prove anti-entrapment safety",
 "l5":"AstralPool lists the AISI-316L 30766, 400x400 mm drain grating at a maximum recommended flow of 83 m³/h at 0.5 m/s. This is useful hydraulic data, but by itself it does not certify a suction arrangement against entrapment.",
 "suction_check":"ILLUSTRATIVE HYDRAULIC CHECK - NOT A COMPLIANCE VERDICT",
 "suction_txt":"The DB case study uses 4 physical grilles, 2 per HJ pump. If one pump operated at about 67 m³/h, two identical perfectly balanced grilles would each carry about 33.5 m³/h; even one 30766 would be nominally at 67 < 83 m³/h. This does NOT replace verification of certification, spacing, plumbing, covers, applicable rules and blocked-outlet behaviour.",
 "k6":"05 • DB ARCHITECTURE",
 "t6":"Two pumps, one common pressure header and five water mains",
 "l6":"This is the confirmed functional architecture for the DB project. It is a project-specific case study, not a universal hydromassage-pool rule.",
 "k7":"06 • 45 JETS + 5 AIR CIRCUITS",
 "t7":"Balance the water and keep the five Venturi air lines independent",
 "l7":"The project splits 36 wall jets into two 18-jet sectors and keeps the 9 step jets on a dedicated main. The five Ø32 air mains remain independent to their dry termination; there is no common air manifold in the technical room.",
 "k8":"07 • COMMISSIONING AND HOLD POINTS",
 "t8":"Before start-up: measure, test and compare against the curves",
 "l8":"A hydromassage system is not accepted because it 'makes lots of bubbles'. Acceptance requires consistent flow and pressure, safe suction, no unwanted suction-side air, uniform jet effect and electrical values within nameplate limits.",
 "checks":[
  ("1","Component identity","Confirm the actual BOOSPA jet supplied and its documentation."),
  ("2","Suction","Confirm model, certifications, arrangement and anti-entrapment requirements."),
  ("3","Curves","Calculate real circuit losses and compare them with the MAXIM 08005 curve."),
  ("4","Leak testing","Test water and air circuits separately before closing construction."),
  ("5","Venturi","Verify even air induction; no sagging/low points that retain water."),
  ("6","Balancing","Compare wall groups 4-9 and steps; correct using measurements, not by eye."),
  ("7","Electrical","Verify current, protection and control with a qualified electrician."),
 ],
 "holdbox":"DATA NOT YET TO BE TAUGHT AS FINAL IN THE CASE STUDY",
 "holditems":["Official flow data for BOOSPA A-000000-00182.","BOOSPA hole size / seals / internal geometry.","Complete HJ system curve and final operating point.","Final compliance of 30766 suction fittings in the actual installation.","Exact connection elevations on the purchased machines."],
 "footer":"Technical sources: AstralPool/Fluidra, Balboa Water Group, DB Plumbing Services dossier. Unverified project data remains HOLD."
}}

def lines(txt,font,size,maxw):
    out=[]; cur=""
    for w in txt.split():
        t=w if not cur else cur+" "+w
        if stringWidth(t,font,size)<=maxw: cur=t
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

def draw_text(c,txt,x,y,maxw,font="Helvetica",size=10,leading=None,color=TEXT,max_lines=None):
    if leading is None: leading=size*1.27
    ls=lines(txt,font,size,maxw)
    if max_lines: ls=ls[:max_lines]
    c.setFont(font,size); c.setFillColor(color)
    yy=y
    for s in ls:
        c.drawString(x,yy,s); yy-=leading
    return yy

def fit(c,path,x,y,w,h,cover=False):
    im=Image.open(path).convert("RGB"); iw,ih=im.size
    if cover:
        scale=max(w/iw,h/ih); nw,nh=int(iw*scale),int(ih*scale)
        im=im.resize((nw,nh),Image.Resampling.LANCZOS)
        l=max(0,(nw-int(w))/2); t=max(0,(nh-int(h))/2)
        im=im.crop((l,t,l+int(w),t+int(h)))
        c.drawImage(ImageReader(im),x,y,w,h,mask='auto')
    else:
        scale=min(w/iw,h/ih); dw,dh=iw*scale,ih*scale
        c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')

def img_panel(c,path,x,y,w,h,label=None,cover=False):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.saveState(); p=c.beginPath(); p.roundRect(x+1,y+1,w-2,h-2,8); c.clipPath(p,stroke=0,fill=0)
    fit(c,path,x+6,y+6,w-12,h-12,cover=cover); c.restoreState()
    if label:
        c.setFillColor(WHITE); c.roundRect(x+10,y+h-28,170,18,7,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.0); c.drawString(x+17,y+h-22,label)

def header(c,k,page,edition):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.6); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.0); c.drawRightString(W-42,H-30,("POOL SYSTEMS • HYDROMASSAGE / VENTURI • REV05R" if edition.startswith("EN") else "SISTEMI PISCINA • IDROMASSAGGIO / VENTURI • REV05R"))
    c.setStrokeColor(MID); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",10.5); c.drawString(42,H-62,k)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.8); c.drawRightString(W-42,24,f"{edition} • {page}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(42,35,95,35)

def title(c,t,lead):
    yy=draw_text(c,t,42,H-101,W-84,"Helvetica-Bold",27,30,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-3,128,yy-3)
    draw_text(c,lead,42,yy-29,W-84,"Helvetica",11.8,15.2,MUTED,5)

def source(c,txt):
    c.setFillColor(MUTED); draw_text(c,txt,42,60,W-84,"Helvetica",7.0,8.5,MUTED,2)

def cover(c,L):
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    # Hero real pump
    c.setFillColor(WHITE); c.roundRect(305,185,240,430,16,fill=1,stroke=0)
    fit(c,ASSETS["maxim_photo_crop"],320,235,210,325,cover=False)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawString(323,210,("ASTRALPOOL MAXIM 08005 • REAL PRODUCT" if L["edition"].startswith("EN") else "ASTRALPOOL MAXIM 08005 • PRODOTTO REALE"))
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-122,235,"Helvetica-Bold",30,33,WHITE,4)
    c.setFillColor(CYAN); draw_text(c,L["cover_sub"],48,H-230,225,"Helvetica-Bold",13.2,16,CYAN,3)
    draw_text(c,L["cover_desc"],48,H-290,225,"Helvetica",12.0,16,WHITE,5)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.5); c.drawString(48,80,("VISUAL STANDARD REV05R" if L["edition"].startswith("EN") else "STANDARD VISIVO REV05R"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",9.6); c.drawString(48,60,("VERIFIED DATA • PROJECT HOLD POINTS • INSTALLER-FIRST METHOD" if L["edition"].startswith("EN") else "DATI VERIFICATI • PUNTI DA CONFERMARE • METODO PENSATO PER L'INSTALLATORE"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    img_panel(c,ASSETS["balboa_specs_crop"],42,300,260,320,("BALBOA - VERIFIED SPECIFICATION EXTRACT" if L["edition"].startswith("EN") else "BALBOA - ESTRATTO SPECIFICHE VERIFICATE"),cover=False)
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(322,320,231,300,10,fill=1,stroke=1)
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",10.5); c.drawString(339,592,L["bench"])
    yy=562
    for a,b in L["balboa_specs"]:
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.6); c.drawString(339,yy,a)
        c.setFillColor(MUTED); c.setFont("Helvetica",8.4); c.drawString(339,yy-15,b); yy-=42
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(322,105,231,195,10,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10.4); c.drawString(339,276,L["dbhold"])
    draw_text(c,L["dbholdtxt"],339,255,197,"Helvetica",9.0,11.8,TEXT,12)
    source(c,"[S1] Balboa Water Group - Freedom Jets 10-FS711/10-FS715 official manual   [S5] DB project working dossier")
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    # Large technical venturi scheme
    x0,y0=42,245
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x0,y0,511,365,10,fill=1,stroke=1)
    # water line
    c.setStrokeColor(CYAN_D); c.setLineWidth(14); c.line(78,420,300,420)
    c.setFillColor(CYAN_D); c.circle(303,420,9,fill=1,stroke=0)
    # nozzle contraction and outlet
    c.setStrokeColor(CYAN_D); c.setLineWidth(8); c.line(310,420,390,420)
    c.setLineWidth(14); c.line(390,420,500,420)
    # air line
    c.setStrokeColor(GREEN); c.setLineWidth(8); c.line(335,550,335,442)
    c.setLineWidth(4); c.line(335,442,356,420)
    # bubbles
    c.setFillColor(GREEN)
    for bx,by,r in [(405,450,5),(430,462,4),(456,446,6),(478,466,3.5)]:
        c.circle(bx,by,r,fill=0,stroke=1)
    # labels
    en=L["edition"].startswith("EN")
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",10.5); c.drawString(80,447,"WATER Ø50" if en else "ACQUA Ø50")
    c.setFillColor(GREEN); c.drawString(350,542,"AIR Ø32" if en else "ARIA Ø32")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(390,392,"AIR/WATER JET" if en else "JET ARIA/ACQUA")
    vent_desc=("Higher local velocity through the jet body creates suction at the air port." if en else "La maggiore velocita' locale nel corpo del jet crea aspirazione sulla bocca aria.")
    c.setFillColor(MUTED); c.setFont("Helvetica",9.2); c.drawString(80,373,vent_desc)
    c.setStrokeColor(RED); c.setLineWidth(2)
    c.line(120,300,260,300); c.line(120,300,120,340); c.line(260,300,260,340)
    c.setFillColor(RED); c.setFont("Helvetica-Bold",9.3); c.drawString(128,314,"NO LOW SAG / WATER TRAP IN AIR LINE" if en else "NO SACCHE / RISTAGNI NELLA LINEA ARIA")
    # note
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,125,511,95,9,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",10.2); c.drawString(60,195,"MANUFACTURER NOTE" if L["edition"].startswith("EN") else "NOTA PRODUTTORE")
    draw_text(c,L["venturi_note"],60,173,470,"Helvetica",10.0,13.2,TEXT,6)
    source(c,("[S1] Balboa Water Group - Freedom Jets official manual: AIR/WATER socket identification, no sagging air hoses, no air-pump boost recommended." if L["edition"].startswith("EN") else "[S1] Manuale ufficiale Balboa Water Group Freedom Jets: identificazione attacchi aria/acqua, evitare cedimenti delle linee aria, pompa aria di rinforzo non raccomandata."))
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    img_panel(c,ASSETS["maxim_photo_crop"],42,340,210,275,"ASTRALPOOL MAXIM 08005")
    img_panel(c,ASSETS["maxim_curve_page"],270,340,283,275,"OFFICIAL PERFORMANCE CURVES" if L["edition"].startswith("EN") else "CURVE PRESTAZIONALI UFFICIALI")
    # verified data strip
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,125,511,180,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(58,280,"VERIFIED 08005 DATA" if L["edition"].startswith("EN") else "DATI 08005 VERIFICATI")
    x=58; y=244
    for i,(h,q) in enumerate(L["curve_rows"]):
        col=i%3; row=i//3; xx=x+col*150; yy=y-row*58
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(xx,yy-35,132,42,6,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.3); c.drawString(xx+10,yy-11,h)
        c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",9.7); c.drawRightString(xx+122,yy-11,q)
    draw_text(c,L["curve_rule"],58,155,475,"Helvetica",9.2,12.2,TEXT,5)
    source(c,("[S2] AstralPool MAXIM product page + official datasheet 105.01.01   [S3] Fluidra spare-parts catalogue 08005" if L["edition"].startswith("EN") else "[S2] Pagina prodotto AstralPool MAXIM + scheda tecnica ufficiale 105.01.01   [S3] Catalogo ricambi Fluidra 08005"))
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    en=L["edition"].startswith("EN")
    img_panel(c,ASSETS["grating_crop"],42,320,225,300,"ASTRALPOOL 30766 • REAL PRODUCT" if en else "ASTRALPOOL 30766 • PRODOTTO REALE")
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(287,320,266,300,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",11.2); c.drawString(305,590,"30766 - VERIFIED" if en else "30766 - VERIFICATA")
    specs=([("Material","AISI-316L"),("Face","400 x 400 mm"),("Max. rec. flow","83 m³/h"),("Reference velocity","0.5 m/s"),("Application","concrete pools")]
           if en else
           [("Materiale","AISI-316L"),("Dimensioni","400 x 400 mm"),("Portata max. racc.","83 m³/h"),("Velocita' rif.","0.5 m/s"),("Applicazione","piscine in calcestruzzo")])
    yy=555
    for a,b in specs:
        c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.6); c.drawString(305,yy,a.upper())
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.8); c.drawRightString(535,yy,b); yy-=46
    c.setFillColor(PALE_RED); c.setStrokeColor(HexColor("#F0CAC5")); c.roundRect(42,125,511,155,10,fill=1,stroke=1)
    c.setFillColor(RED); c.setFont("Helvetica-Bold",9.6); c.drawString(60,255,L["suction_check"])
    draw_text(c,L["suction_txt"],60,232,470,"Helvetica",9.3,12.4,TEXT,9)
    source(c,("[S4] AstralPool - Drain grating in stainless steel, code 30766. Safety note: rating alone is not an anti-entrapment compliance proof." if L["edition"].startswith("EN") else "[S4] AstralPool - Griglia di scarico in acciaio inox, codice 30766. Nota sicurezza: la sola portata dichiarata non dimostra la conformita anti-intrappolamento."))
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    # architectural schematic
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,160,511,455,10,fill=1,stroke=1)
    # Suction grilles and pumps
    en=L["edition"].startswith("EN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.6); c.drawString(60,585,"POOL SUCTIONS" if en else "ASPIRAZIONI PISCINA")
    gy=[540,495,400,355]
    for i,y in enumerate(gy):
        c.setFillColor(WHITE); c.setStrokeColor(GREEN); c.roundRect(60,y,62,30,5,fill=1,stroke=1)
        c.setFillColor(GREEN); c.setFont("Helvetica-Bold",8.0); c.drawCentredString(91,y+11,(f"GRILLE {i+1}" if en else f"GRIGLIA {i+1}"))
    # Pair lines
    c.setStrokeColor(NAVY); c.setLineWidth(3)
    c.line(122,555,170,555); c.line(122,510,170,510); c.line(170,510,170,555); c.line(170,533,220,533)
    c.line(122,415,170,415); c.line(122,370,170,370); c.line(170,370,170,415); c.line(170,393,220,393)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.0); c.drawString(155,563,"ASP HJ1 Ø90"); c.drawString(155,423,"ASP HJ2 Ø90")
    # pumps represented with real image thumbnails
    img_panel(c,ASSETS["maxim_photo_crop"],220,470,135,125,"MAXIM HJ1")
    img_panel(c,ASSETS["maxim_photo_crop"],220,330,135,125,"MAXIM HJ2")
    # discharge
    c.setStrokeColor(CYAN_D); c.setLineWidth(4)
    c.line(355,533,390,533); c.line(355,393,390,393)
    c.setFillColor(WHITE); c.setStrokeColor(ORANGE); c.roundRect(390,518,55,30,5,fill=1,stroke=1); c.roundRect(390,378,55,30,5,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",8.0); c.drawCentredString(417,529,"NRV"); c.drawCentredString(417,389,"NRV")
    c.setStrokeColor(CYAN_D); c.line(445,533,470,533); c.line(445,393,470,393); c.line(470,393,470,533)
    # common header
    c.setFillColor(BLUEW); c.setStrokeColor(CYAN_D); c.setLineWidth(2); c.roundRect(452,260,70,320,14,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawCentredString(487,566,"C-HJ Ø160")
    # five branches
    branch_y=[480,435,390,345,300]; labs=["A1 Ø63","A2 Ø63","B1 Ø63","B2 Ø63","SCALE Ø63"]
    for yy,lab in zip(branch_y,labs):
        c.setStrokeColor(CYAN_D); c.setLineWidth(3); c.line(522,yy,545,yy)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.5); c.drawRightString(545,yy+7,lab)
    # air independent at bottom
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",8); c.drawString(60,235,("VENTURI AIR - 5 INDEPENDENT Ø32 LINES" if en else "ARIA VENTURI - 5 LINEE Ø32 INDIPENDENTI"))
    names=(["A1 AIR","A2 AIR","B1 AIR","B2 AIR","SCALE AIR"] if en else ["A1 ARIA","A2 ARIA","B1 ARIA","B2 ARIA","SCALE ARIA"])
    x=60
    for n in names:
        c.setStrokeColor(GREEN); c.setLineWidth(2.5); c.line(x,205,x+70,205)
        c.setFillColor(GREEN); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(x+35,215,n)
        x+=92
    source(c,("[S5] DB Handoff 22-09-2026: 4 grilles -> 2 MAXIM -> NRV -> C-HJ Ø160 -> A1/A2/B1/B2/SCALE; five independent Ø32 air mains." if L["edition"].startswith("EN") else "[S5] Documento tecnico DB 22-09-2026: 4 griglie -> 2 MAXIM -> VNR -> C-HJ Ø160 -> A1/A2/B1/B2/SCALE; cinque dorsali aria Ø32 indipendenti."))
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,175,511,430,10,fill=1,stroke=1)
    # Two wall sectors with six fascia
    en=L["edition"].startswith("EN")
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",9.6); c.drawString(60,585,("WALL JETS - 36 TOTAL" if en else "JET PARETE - 36 TOTALI"))
    x0=64; top=505; bw=70; gap=9
    labels=["4","5","6","7","8","9"]
    for i,lab in enumerate(labels):
        x=x0+i*(bw+gap)
        c.setFillColor(BLUEW); c.setStrokeColor(CYAN_D); c.roundRect(x,top,bw,60,7,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawCentredString(x+bw/2,top+42,f"FASCIA {lab}")
        c.setFont("Helvetica-Bold",8.0); c.drawCentredString(x+bw/2,top+24,"4 UPPER + 2 LOWER" if en else "4 ALTI + 2 BASSI")
        c.setFillColor(CYAN_D)
        for r in range(2):
            for j in range(3):
                if r==1 and j==2: continue
                c.circle(x+18+j*17,top+10+r*12,2.7,fill=1,stroke=0)
    # sector labels
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.6); c.drawCentredString(180,477,"SECTOR A: A1 + A2 -> 4 / 5 / 6" if en else "SETTORE A: A1 + A2 -> 4 / 5 / 6")
    c.drawCentredString(415,477,"SECTOR B: B1 + B2 -> 7 / 8 / 9" if en else "SETTORE B: B1 + B2 -> 7 / 8 / 9")
    c.setStrokeColor(CYAN_D); c.setLineWidth(2); c.line(75,463,285,463); c.line(310,463,522,463)
    # Steps
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",9.6); c.drawString(60,425,"STEPS - 9 TOTAL" if en else "SCALE - 9 TOTALI")
    for i in range(3):
        y=375-i*52; w=360-i*38
        c.setFillColor(PALE_ORANGE); c.setStrokeColor(ORANGE); c.roundRect(95,y,w,38,6,fill=1,stroke=1)
        c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",8.6); c.drawString(108,y+14,(f"GROUP {i+1}" if en else f"GRUPPO {i+1}"))
        for j in range(3): c.circle(250+j*30-i*8,y+19,3,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.6); c.drawString(95,207,("SCALE Ø63 -> balanced local distributor -> 3 groups x 3 jets" if en else "SCALE Ø63 -> distributore locale bilanciato -> 3 gruppi x 3 jet"))
    # note on air
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(60,190,465,58,7,fill=1,stroke=1)
    air_note=("The five air lines mirror the water grouping and terminate at dry points above maximum water level. Keep them independent; avoid sags/low points."
              if L["edition"].startswith("EN") else
              "Le cinque linee aria rispecchiano i gruppi acqua e terminano in punti asciutti sopra il massimo livello acqua. Restano indipendenti; evitare sacche e punti bassi.")
    draw_text(c,air_note,76,225,430,"Helvetica",9.2,12.2,TEXT,4)
    source(c,("[S5] DB Handoff 22-09-2026: 36 wall jets + 9 step jets = 45; five independent Venturi-air circuits." if L["edition"].startswith("EN") else "[S5] Documento tecnico DB 22-09-2026: 36 jet parete + 9 jet scale = 45; cinque circuiti aria Venturi indipendenti."))
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,310,511,305,10,fill=1,stroke=1)
    yy=580
    for n,h,b in L["checks"]:
        c.setFillColor(CYAN); c.circle(62,yy-5,9,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7.3); c.drawCentredString(62,yy-8,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.6); c.drawString(82,yy,h)
        draw_text(c,b,82,yy-14,445,"Helvetica",8.5,10.8,MUTED,2)
        yy-=40
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,115,511,160,10,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10.2); c.drawString(60,248,L["holdbox"])
    yy=222
    for item in L["holditems"]:
        c.setFillColor(ORANGE); c.circle(63,yy+2,2.5,fill=1,stroke=0)
        draw_text(c,item,75,yy+5,450,"Helvetica",8.8,11.2,TEXT,2); yy-=27
    source(c,("Sources: [S1] Balboa Freedom Jets official manual; [S2] AstralPool MAXIM datasheet; [S3] Fluidra 08005 spare parts; [S4] AstralPool 30766; [S5] DB project dossiers." if L["edition"].startswith("EN") else "Fonti: [S1] manuale ufficiale Balboa Freedom Jets; [S2] scheda tecnica AstralPool MAXIM; [S3] ricambi Fluidra 08005; [S4] AstralPool 30766; [S5] documenti progetto DB."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_HYDROMASSAGE_VENTURI_REV05R_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Hydromassage & Venturi")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    print("ASSETS")
    for k,p in ASSETS.items(): print(k,p,p.stat().st_size)
    print(build("IT")); print(build("EN"))
