from __future__ import annotations
from pathlib import Path
import requests, fitz
from PIL import Image, ImageChops
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
PALE_GREEN=HexColor("#EEF7F3"); PALE_ORANGE=HexColor("#FFF5E8"); PALE_RED=HexColor("#FFF0EF"); BLUEW=HexColor("#EAF7FB")

HEADERS={"User-Agent":"Mozilla/5.0 (Academy DB Plumbing Services technical education)"}
URLS={
 "product_photo":"https://fluidra.bynder.com/m/2f2d6fbcd2f3f091/Medium-66162-p.jpg",
 "manual":"https://fluidra.bynder.com/m/47f67167a81098a1/original/installationmanual_controlbasicnext_DE_EN_ES_FR_IT_2021_12.pdf",
 "brochure":"https://fluidra.bynder.com/m/6385faec4db3b3b7/original/leaflet_poolpatrolcontroller_ES_2021_12.pdf",
}

def dl(key):
    url=URLS[key]; ext=".pdf" if url.lower().endswith(".pdf") else ".jpg"
    p=ASSET/f"{key}{ext}"
    if p.exists() and p.stat().st_size>5000: return p
    r=requests.get(url,headers=HEADERS,timeout=45)
    r.raise_for_status()
    p.write_bytes(r.content)
    if ext==".jpg":
        with Image.open(p) as im: im.verify()
    else:
        if p.read_bytes()[:4] != b"%PDF": raise RuntimeError("Downloaded manual is not a PDF")
    return p

RAW={k:dl(k) for k in URLS}

def trim_white(path,out_name,margin=15):
    im=Image.open(path).convert("RGB")
    bg=Image.new("RGB",im.size,(255,255,255))
    diff=ImageChops.difference(im,bg).convert("L")
    bbox=diff.point(lambda p:0 if p<12 else 255).getbbox()
    if bbox:
        l,t,r,b=bbox; l=max(0,l-margin); t=max(0,t-margin); r=min(im.width,r+margin); b=min(im.height,b+margin)
        im=im.crop((l,t,r,b))
    out=ASSET/out_name; im.save(out,quality=95); return out

def render_pdf(pdf_path,page_index,out_name,dpi=220,crop=None):
    doc=fitz.open(str(pdf_path))
    if page_index >= len(doc): page_index=len(doc)-1
    page=doc[page_index]
    pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
    out=ASSET/out_name; pix.save(str(out)); doc.close()
    if crop:
        im=Image.open(out).convert("RGB")
        l=int(im.width*crop[0]); t=int(im.height*crop[1]); r=int(im.width*crop[2]); b=int(im.height*crop[3])
        im.crop((l,t,r,b)).save(out,quality=95)
    return out

ASSETS={}
ASSETS["product"]=trim_white(RAW["product_photo"],"product_crop.jpg",10)
ASSETS["brochure_p2"]=render_pdf(RAW["brochure"],2,"brochure_p2.png",210,(0.02,0.02,0.98,0.72))
# English calibration pages and Italian calibration pages from multilingual manual.
ASSETS["en_ph"]=render_pdf(RAW["manual"],5,"manual_en_ph.png",220,(0.03,0.02,0.97,0.72))
ASSETS["en_orp"]=render_pdf(RAW["manual"],6,"manual_en_orp.png",220,(0.03,0.02,0.97,0.72))
ASSETS["it_ph"]=render_pdf(RAW["manual"],29,"manual_it_ph.png",220,(0.03,0.02,0.97,0.72))
ASSETS["it_orp"]=render_pdf(RAW["manual"],30,"manual_it_orp.png",220,(0.03,0.02,0.97,0.72))

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"CHIMICA DELL'ACQUA + DOSAGGIO AUTOMATICO",
"cover_sub":"pH, ORP, sonde, dosaggio e interblocco di flusso",
"cover_desc":"Control Basic Next 66162 / 66163 - principi corretti per studenti e caso reale DB Plumbing Services",
"k2":"01 - DUE MISURE DIVERSE",
"t2":"pH e ORP non sono la stessa cosa e non vanno letti allo stesso modo",
"l2":"Il pH descrive l'acidita/alcalinita dell'acqua. L'ORP (redox) misura un potenziale elettrico in millivolt legato alla capacita ossidante del sistema. Un valore ORP non e' una concentrazione di cloro in ppm.",
"ph_box":"pH",
"ph_body":"Scala logaritmica. Nel controllo piscina influenza comfort, materiali e soprattutto l'efficacia del cloro. CDC indica 7.0-7.8 per piscine domestiche; WHO indica 7.2-7.8 per sistemi a cloro.",
"orp_box":"ORP / REDOX",
"orp_body":"Misura in mV usata per monitoraggio operativo della disinfezione. WHO sottolinea che il valore appropriato deve essere definito caso per caso e dipende anche dal tipo di elettrodo di riferimento.",
"rule2":"REGOLA DIDATTICA: prima verificare pH e disinfettante reale; non convertire automaticamente mV in ppm.",
"k3":"02 - COMPONENTI REALI",
"t3":"Control Basic Next: due apparecchi separati nel progetto DB",
"l3":"AstralPool Control Basic Next e' un sistema automatico di misura e dosaggio. Nel progetto DB sono previsti un controllo pH e un controllo ORP distinti, entrambi nella versione 1.5 L/h.",
"rows3":[("66162","Control Basic Next pH","1.5 L/h","1.5 bar","sonda pH + soluzioni tampone pH 4 / pH 7"),
("66163","Control Basic Next ORP","1.5 L/h","1.5 bar","sonda ORP + soluzione tampone 465 mV")],
"note3":"Il catalogo Fluidra 2025 associa il modello pH a dosaggio acido o basico e il modello ORP a cloro liquido. La selezione del prodotto chimico reale deve seguire manuale, SDS e condizioni dell'impianto.",
"k4":"03 - CALIBRAZIONE",
"t4":"Una sonda non si 'crede': si calibra e si verifica",
"l4":"Il manuale AstralPool prevede calibrazione pH a due punti (pH 7 e pH 4), oppure un solo punto pH 7 se configurato. Per Redox e' previsto il riferimento 465 mV. Le sonde vanno risciacquate tra le soluzioni.",
"phcal":"CALIBRAZIONE pH",
"orpcal":"CALIBRAZIONE ORP",
"calnote":"Lo schermo mostra anche una valutazione della qualita della sonda durante la calibrazione. In caso di errore il manuale indica di controllare o sostituire la sonda o la soluzione tampone e ripetere la procedura.",
"k5":"04 - INTERBLOCCO DI FLUSSO",
"t5":"Nessun dosaggio automatico senza circolazione verificata",
"l5":"Il Control Basic Next dispone di un ingresso di flusso collegabile alla circolazione. Nel progetto DB l'interblocco di flusso e' un requisito importante: il dosaggio non deve proseguire quando manca la condizione di ricircolo prevista.",
"flowsteps":[("1","RICIRCOLO ATTIVO","La pompa di filtrazione e' in servizio e la portata e' disponibile."),
("2","CONSENSO FLUSSO","Il regolatore riceve il segnale previsto dal sistema."),
("3","MISURA","La sonda legge pH oppure ORP."),
("4","CONFRONTO VALORE IMPOSTATO","Il regolatore confronta misura e valore impostato."),
("5","DOSAGGIO","La pompa peristaltica dosa solo quando la logica lo richiede.")],
"flowhold":"DA CONFERMARE: la posizione esatta di sonde, punti di prelievo e punti di iniezione del progetto DB deve essere definita solo dopo verifica del corredo realmente fornito e del manuale di installazione.",
"k6":"05 - VALORI IMPOSTATI E CHIMICA",
"t6":"Il valore di fabbrica non e' automaticamente il valore di progetto",
"l6":"Il manuale riporta come valori predefiniti 7.4 pH e 750 mV (Rx), ma sono parametri iniziali del regolatore, non una prescrizione universale. La chimica reale dipende da acqua, disinfettante, stabilizzante, temperatura, carico bagnanti e obiettivi operativi.",
"facts6":[("CDC - piscina domestica","pH 7.0-7.8; almeno 1 ppm cloro libero senza acido cianurico, almeno 2 ppm se si usa acido cianurico/stabilizzato."),
("WHO - piscine a cloro","pH 7.2-7.8 come guida generale."),
("WHO - ORP","Valori >720 mV con elettrodo Ag/AgCl o >680 mV con calomel possono indicare buona condizione microbiologica, ma il valore appropriato va definito caso per caso."),
("AstralPool - valori predefiniti del regolatore","7.4 pH e 750 mV; impostabili, quindi non confondere i valori predefiniti del software con obiettivi obbligatori.")],
"k7":"06 - CASO REALE DB",
"t7":"Dove entra il trattamento nella catena reale della piscina",
"l7":"Nel progetto DB la filtrazione e' separata dall'idromassaggio. Il trattamento pH/ORP e' previsto dopo Victoria + valvola 6 vie/Vesubio e prima del collettore ritorni C-F-RET.",
"confirmed":"CONFERMATO",
"conf7":["Control Basic Next pH 1.5 L/h - 66162.","Control Basic Next ORP 1.5 L/h - 66163.","Zona trattamento sulla parete destra, circa X 4300-5200 mm.","Catena: Victoria -> 6 vie/Vesubio -> pH/ORP -> C-F-RET -> R1-R4.","Flussostato/interblocco considerato importante.","Vaschetta di contenimento chimici considerata prudente."],
"hold":"DA VERIFICARE / NON CONFERMARE",
"hold7":["Cella di derivazione sonde: opzione da confermare, non componente definitivo.","Posizione esatta dei porta-sonda e dei punti di iniezione.","Prodotti chimici finali e concentrazioni fornite.","Valori operativi definitivi.","Sequenza e distanze fisiche dei punti di iniezione secondo corredo e manuali reali."],
"k8":"07 - MESSA IN SERVIZIO",
"t8":"Avviamento e manutenzione: misurare con un riferimento indipendente",
"l8":"L'automazione non elimina il controllo umano. Durante avviamento e manutenzione le letture delle sonde devono essere confrontate con un metodo indipendente appropriato, e gli allarmi non devono essere ignorati.",
"checks8":[("1","Identita apparecchi","Confermare 66162 e 66163 e il contenuto reale dei corredi."),
("2","Installazione sonde","Verificare immersione, tenuta, cablaggio e orientamento secondo manuale."),
("3","Calibrazione","pH con soluzioni tampone pH7/pH4 secondo configurazione; ORP con 465 mV."),
("4","Flusso","Provare l'interblocco: la perdita di ricircolo deve impedire il dosaggio previsto."),
("5","Dosaggio","Controllare tubi peristaltici, aspirazione, iniezione e assenza di perdite."),
("6","Confronto indipendente","Verificare pH e disinfettante con strumento o prova adeguata."),
("7","Allarmi e OFA","Provare gli allarmi previsti e registrare gli interventi."),
("8","Sicurezza chimica","Mai miscelare prodotti; seguire SDS, etichette e istruzioni del produttore.")],
"footer":"Fonti: AstralPool/Fluidra Control Basic Next, manuale 0000137847 Rev 2.0, opuscolo Fluidra, indicazioni CDC per la balneazione sicura, linee guida WHO sulle acque ricreative, documento tecnico DB 22-09-2026."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"WATER CHEMISTRY + AUTOMATIC DOSING",
"cover_sub":"pH, ORP, probes, dosing and flow interlock",
"cover_desc":"Control Basic Next 66162 / 66163 - technically verified principles and DB Plumbing Services case study",
"k2":"01 - TWO DIFFERENT MEASUREMENTS",
"t2":"pH and ORP are not the same measurement and must not be interpreted the same way",
"l2":"pH describes the acidity/alkalinity of water. ORP (redox) is an electrical potential in millivolts related to the oxidising condition of the system. An ORP value is not a chlorine concentration in ppm.",
"ph_box":"pH",
"ph_body":"A logarithmic scale. In pool control it affects comfort, materials and especially chlorine effectiveness. CDC gives 7.0-7.8 for home pools; WHO gives 7.2-7.8 for chlorinated pools.",
"orp_box":"ORP / REDOX",
"orp_body":"Measured in mV and used for operational monitoring of disinfection. WHO notes that appropriate values should be determined case by case and also depend on the reference-electrode system.",
"rule2":"TEACHING RULE: verify pH and actual disinfectant level; never automatically convert mV into ppm.",
"k3":"02 - REAL COMPONENTS",
"t3":"Control Basic Next: two separate controllers in the DB project",
"l3":"AstralPool Control Basic Next is an automatic measurement and dosing system. The DB project uses separate pH and ORP controllers, both in the 1.5 L/h version.",
"rows3":[("66162","Control Basic Next pH","1.5 L/h","1.5 bar","pH probe + pH 4 / pH 7 buffers"),
("66163","Control Basic Next ORP","1.5 L/h","1.5 bar","ORP probe + 465 mV buffer")],
"note3":"Fluidra's 2025 catalogue associates the pH model with acid or alkaline dosing and the ORP model with liquid chlorine. The actual chemical product must follow the equipment manual, SDS and site conditions.",
"k4":"03 - CALIBRATION",
"t4":"A probe is not 'trusted': it is calibrated and checked",
"l4":"The AstralPool manual provides two-point pH calibration at pH 7 and pH 4, or one-point pH 7 when configured. Redox uses the 465 mV reference. Probes are rinsed between buffer solutions.",
"phcal":"pH CALIBRATION",
"orpcal":"ORP CALIBRATION",
"calnote":"The controller also displays probe quality during calibration. On calibration error, the manual instructs the user to check/replace the probe or buffer solution and repeat the procedure.",
"k5":"04 - FLOW INTERLOCK",
"t5":"No automatic dosing without verified circulation",
"l5":"Control Basic Next provides a flow input that can be linked to circulation. In the DB project, a flow interlock is treated as important: dosing must not continue when the intended recirculation condition is absent.",
"flowsteps":[("1","CIRCULATION ON","The filtration pump is operating and flow is available."),
("2","FLOW PERMISSION","The controller receives the intended system signal."),
("3","MEASUREMENT","The probe reads either pH or ORP."),
("4","SETPOINT COMPARISON","The controller compares the measurement to the set value."),
("5","DOSING","The peristaltic pump doses only when the logic calls for it.")],
"flowhold":"HOLD: the exact probe positions, sample points and injection points in the DB project must be frozen only after checking the actual supplied kit and its installation instructions.",
"k6":"05 - SETPOINTS AND CHEMISTRY",
"t6":"A factory default is not automatically a project target",
"l6":"The manual lists factory defaults of 7.4 pH and 750 mV (Rx), but these are controller starting parameters, not universal prescriptions. Real chemistry depends on source water, disinfectant, stabiliser, temperature, bather load and operating objectives.",
"facts6":[("CDC - home pool","pH 7.0-7.8; at least 1 ppm free chlorine without cyanuric acid, at least 2 ppm when cyanuric acid/stabilised chlorine is used."),
("WHO - chlorinated pools","pH 7.2-7.8 as general guidance."),
("WHO - ORP","Values >720 mV with Ag/AgCl reference or >680 mV with calomel can suggest good microbial condition, but the appropriate value should be determined case by case."),
("AstralPool - controller default","7.4 pH and 750 mV; configurable values, so software defaults must not be confused with mandatory targets.")],
"k7":"06 - DB CASE STUDY",
"t7":"Where treatment sits in the real pool filtration chain",
"l7":"In the DB project, filtration is separate from hydromassage. pH/ORP treatment is planned after Victoria + six-way valve/Vesubio and before the C-F-RET return manifold.",
"confirmed":"CONFIRMED",
"conf7":["Control Basic Next pH 1.5 L/h - 66162.","Control Basic Next ORP 1.5 L/h - 66163.","Treatment zone on the right wall, approximately X 4300-5200 mm.","Chain: Victoria -> six-way/Vesubio -> pH/ORP -> C-F-RET -> R1-R4.","Flow switch/interlock is considered important.","Chemical containment tray is considered prudent."],
"hold":"TO VERIFY / DO NOT FREEZE",
"hold7":["Probe bypass cell is optional and not a frozen project component.","Exact probe-holder and injection-point positions.","Final chemical products and supplied concentrations.","Final operating setpoints.","Physical spacing/order of injection points per actual kit and manuals."],
"k8":"07 - COMMISSIONING",
"t8":"Start-up and maintenance: compare automation with an independent reference",
"l8":"Automation does not remove operator verification. During commissioning and maintenance, probe readings should be compared with an appropriate independent method, and alarms must not be ignored.",
"checks8":[("1","Equipment identity","Confirm 66162 and 66163 and the actual kit contents."),
("2","Probe installation","Verify immersion, sealing, wiring and orientation to the manual."),
("3","Calibration","pH with pH7/pH4 buffers as configured; ORP with 465 mV."),
("4","Flow","Test the interlock: loss of recirculation must inhibit intended dosing."),
("5","Dosing","Inspect peristaltic tubing, suction, injection and leakage."),
("6","Independent check","Verify pH and disinfectant with a suitable independent instrument/test."),
("7","Alarms and OFA","Test relevant alarms and record interventions."),
("8","Chemical safety","Never mix chemicals; follow SDS, labels and manufacturer instructions.")],
"footer":"Sources: AstralPool/Fluidra Control Basic Next, manual 0000137847 Rev 2.0, Fluidra brochure, CDC Healthy Swimming, WHO recreational-water guidance, DB handoff 22-09-2026."
}}

def wrap(txt,font,size,maxw):
    words=txt.split(); out=[]; cur=""
    for w in words:
        t=w if not cur else cur+" "+w
        if stringWidth(t,font,size)<=maxw: cur=t
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

def draw_text(c,txt,x,y,maxw,font="Helvetica",size=11,leading=None,color=TEXT,max_lines=None):
    if leading is None: leading=size*1.28
    ls=wrap(txt,font,size,maxw)
    if max_lines: ls=ls[:max_lines]
    c.setFillColor(color); c.setFont(font,size)
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
        im=im.crop((l,t,l+int(w),t+int(h))); c.drawImage(ImageReader(im),x,y,w,h,mask='auto')
    else:
        scale=min(w/iw,h/ih); dw,dh=iw*scale,ih*scale
        c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')

def img_panel(c,path,x,y,w,h,label=None,cover=False):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.saveState(); p=c.beginPath(); p.roundRect(x+1,y+1,w-2,h-2,8); c.clipPath(p,stroke=0,fill=0)
    fit(c,path,x+6,y+6,w-12,h-12,cover=cover); c.restoreState()
    if label:
        c.setFillColor(WHITE); c.roundRect(x+10,y+h-28,min(190,w-20),18,7,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.6); c.drawString(x+17,y+h-22,label)

def header(c,k,page,edition):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.5); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.8); c.drawRightString(W-42,H-30,("POOL SYSTEMS - WATER CHEMISTRY / DOSING - REV06" if edition.startswith("EN") else "SISTEMI PISCINA - CHIMICA ACQUA / DOSAGGIO - REV06"))
    c.setStrokeColor(MID); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",10.2); c.drawString(42,H-62,k)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.6); c.drawRightString(W-42,24,f"{edition} - {page}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(42,35,95,35)

def title(c,t,lead):
    yy=draw_text(c,t,42,H-101,W-84,"Helvetica-Bold",26,29,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-3,128,yy-3)
    draw_text(c,lead,42,yy-30,W-84,"Helvetica",11.5,15,MUTED,5)

def source(c,txt):
    draw_text(c,txt,42,61,W-84,"Helvetica",6.8,8,MUTED,2)

def card(c,x,y,w,h,head,body,accent=CYAN):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.setFillColor(accent); c.rect(x,y,w,5,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",11); c.drawString(x+14,y+h-28,head)
    draw_text(c,body,x+14,y+h-52,w-28,"Helvetica",10.6,13.8,TEXT,8)

def cover(c,L):
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.roundRect(315,165,225,455,16,fill=1,stroke=0); fit(c,ASSETS["product"],330,230,195,320,False)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.5); c.drawCentredString(427,200,"ASTRALPOOL CONTROL BASIC NEXT")
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.5); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-125,245,"Helvetica-Bold",29,32,WHITE,4)
    draw_text(c,L["cover_sub"],48,H-260,245,"Helvetica-Bold",13.5,17,CYAN,3)
    draw_text(c,L["cover_desc"],48,H-324,240,"Helvetica",11.5,15,WHITE,6)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.2); c.drawString(48,80,("VISUAL STANDARD REV06" if L["edition"].startswith("EN") else "STANDARD VISIVO REV06"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.2); c.drawString(48,60,("VERIFIED DATA - SOURCE CONTEXT - PROJECT HOLD POINTS" if L["edition"].startswith("EN") else "DATI VERIFICATI - CONTESTO DELLE FONTI - PUNTI DA CONFERMARE"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    card(c,42,315,240,250,L["ph_box"],L["ph_body"],CYAN_D)
    card(c,313,315,240,250,L["orp_box"],L["orp_body"],GREEN)
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,160,511,115,10,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10.2); c.drawString(60,245,("KEY TEACHING POINT" if L["edition"].startswith("EN") else "PUNTO DIDATTICO CHIAVE"))
    draw_text(c,L["rule2"],60,220,470,"Helvetica-Bold",10.5,14,NAVY,5)
    source(c,("[S4] CDC Healthy Swimming 2024-2025   [S5] WHO Guidelines for Safe Recreational Water Environments, Vol. 2" if L["edition"].startswith("EN") else "[S4] CDC - indicazioni 2024-2025 per la balneazione sicura   [S5] WHO - linee guida per ambienti acquatici ricreativi, Vol. 2"))
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    img_panel(c,ASSETS["product"],42,300,230,315,("REAL PRODUCT - CONTROL BASIC NEXT" if L["edition"].startswith("EN") else "PRODOTTO REALE - CONTROL BASIC NEXT"))
    x=292; y=565
    for row in L["rows3"]:
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(x,y-105,261,95,8,fill=1,stroke=1)
        c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",13); c.drawString(x+14,y-32,row[0])
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(x+75,y-31,row[1])
        c.setFillColor(TEXT); c.setFont("Helvetica-Bold",9.5); c.drawString(x+14,y-55,row[2]+"  |  "+row[3])
        draw_text(c,row[4],x+14,y-76,230,"Helvetica",8.4,10.5,MUTED,2); y-=115
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,140,511,115,9,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",9.7); c.drawString(60,230,("MODEL-SPECIFIC DATA" if L["edition"].startswith("EN") else "DATI SPECIFICI DEL MODELLO"))
    draw_text(c,L["note3"],60,208,470,"Helvetica",9.4,12.5,TEXT,6)
    source(c,("[S1] AstralPool Control Basic Next product page   [S2] AstralPool/Fluidra dosing brochure   [S3] Fluidra 2025 catalogue" if L["edition"].startswith("EN") else "[S1] Pagina prodotto AstralPool Control Basic Next   [S2] Opuscolo dosaggio AstralPool/Fluidra   [S3] Catalogo Fluidra 2025"))
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    en=L["edition"].startswith("EN")
    ph=ASSETS["en_ph"] if en else ASSETS["it_ph"]
    orp=ASSETS["en_orp"] if en else ASSETS["it_orp"]

    # Large student-readable procedure panels.
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,300,245,320,10,fill=1,stroke=1)
    c.setFillColor(CYAN_D); c.rect(42,300,245,5,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",12); c.drawString(58,590,L["phcal"])
    phsteps=(["1. Rinse the probe.","2. Place in pH 7 buffer.","3. Hold CAL for 3 seconds.","4. Wait 60 seconds and check probe quality.","5. Rinse the probe.","6. Place in pH 4 buffer (two-point mode).","7. Calibrate again for 60 seconds.","8. Rinse, save and return to normal status."]
             if en else
             ["1. Risciacquare la sonda.","2. Immergere nella soluzione pH 7.","3. Tenere premuto per 3 secondi il tasto CAL (calibrazione).","4. Attendere 60 secondi e controllare la qualita sonda.","5. Risciacquare la sonda.","6. Immergere nella soluzione pH 4 (modalita due punti).","7. Ripetere la calibrazione per 60 secondi.","8. Risciacquare, salvare e tornare allo stato normale."])
    yy=558
    for s in phsteps:
        c.setFillColor(CYAN); c.circle(61,yy+3,2.5,fill=1,stroke=0)
        yy=draw_text(c,s,72,yy+6,195,"Helvetica",10.0,12.5,TEXT,2)-8

    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(308,300,245,320,10,fill=1,stroke=1)
    c.setFillColor(GREEN); c.rect(308,300,245,5,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",12); c.drawString(324,590,L["orpcal"])
    orpsteps=(["1. Rinse the probe.","2. Place in 465 mV buffer.","3. Hold CAL for 3 seconds.","4. Wait 60 seconds.","5. Check the displayed probe quality.","6. Rinse the probe.","7. Return to normal measurement/control status."]
              if en else
              ["1. Risciacquare la sonda.","2. Immergere nella soluzione 465 mV.","3. Tenere premuto per 3 secondi il tasto CAL (calibrazione).","4. Attendere 60 secondi.","5. Controllare la qualita sonda visualizzata.","6. Risciacquare la sonda.","7. Tornare allo stato normale di misura/controllo."])
    yy=558
    for s in orpsteps:
        c.setFillColor(GREEN); c.circle(327,yy+3,2.5,fill=1,stroke=0)
        yy=draw_text(c,s,338,yy+6,195,"Helvetica",10.0,12.5,TEXT,2)-10

    # Small official-source extracts: evidence, not primary reading material.
    img_panel(c,ph,42,160,245,105,"OFFICIAL MANUAL EXTRACT" if en else "ESTRATTO MANUALE UFFICIALE")
    img_panel(c,orp,308,160,245,105,"OFFICIAL MANUAL EXTRACT" if en else "ESTRATTO MANUALE UFFICIALE")

    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,92,511,48,8,fill=1,stroke=1)
    draw_text(c,L["calnote"],57,122,480,"Helvetica",8.8,10.6,TEXT,3)
    source(c,("[S2] AstralPool Control Basic Next installation manual, Code 0000137847 Rev 2.0 - calibration sections." if L["edition"].startswith("EN") else "[S2] Manuale di installazione AstralPool Control Basic Next, codice 0000137847 Rev 2.0 - sezioni calibrazione."))
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,250,511,355,10,fill=1,stroke=1)
    yy=555
    for n,h,b in L["flowsteps"]:
        c.setFillColor(CYAN); c.circle(67,yy-5,11,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.2); c.drawCentredString(67,yy-8,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(92,yy,h)
        draw_text(c,b,92,yy-18,425,"Helvetica",9.2,11.8,MUTED,3)
        if n!="5":
            c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(67,yy-25,67,yy-55)
        yy-=62
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,125,511,90,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",9.5); c.drawString(60,190,("PROJECT HOLD" if L["edition"].startswith("EN") else "PUNTO DI PROGETTO DA CONFERMARE"))
    draw_text(c,L["flowhold"],60,170,470,"Helvetica",9.0,11.8,TEXT,5)
    source(c,("[S2] Manual: pH/Redox probe input, flow input, 230 Vac supply; flow alarm restores when circulation flow is restored.   [S6] DB handoff." if L["edition"].startswith("EN") else "[S2] Manuale: ingresso sonda pH/Redox, ingresso flusso, alimentazione 230 Vca; l'allarme di flusso si ripristina quando torna la circolazione.   [S6] Documento tecnico DB."))
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    y=575
    colors=[CYAN_D,GREEN,ORANGE,NAVY]
    for i,(head,body) in enumerate(L["facts6"]):
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,y-98,511,86,9,fill=1,stroke=1)
        c.setFillColor(colors[i]); c.rect(42,y-98,6,86,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.2); c.drawString(62,y-36,head)
        draw_text(c,body,62,y-57,470,"Helvetica",9.1,11.6,TEXT,4)
        y-=104
    source(c,("[S2] AstralPool manual factory defaults   [S4] CDC home pool guidance   [S5] WHO pool pH and ORP guidance. Contexts differ; do not merge them into one universal target." if L["edition"].startswith("EN") else "[S2] Valori predefiniti del manuale AstralPool   [S4] Indicazioni CDC per piscine domestiche   [S5] Indicazioni WHO su pH e ORP. I contesti sono diversi: non unirli in un unico obiettivo universale."))
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    # flow chain
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8.8); c.drawString(42,570,("CONFIRMED DB FILTRATION CHAIN" if L["edition"].startswith("EN") else "CATENA FILTRAZIONE DB CONFERMATA"))
    labels=["VICTORIA","6-WAY","VESUBIO","pH 66162","ORP 66163","C-F-RET","R1-R4"]
    widths=[70,65,72,78,78,72,60]
    x=42; yy=530
    for i,(lab,ww) in enumerate(zip(labels,widths)):
        col=GREEN if "pH" in lab or "ORP" in lab else (ORANGE if lab=="VESUBIO" else NAVY)
        c.setFillColor(WHITE); c.setStrokeColor(col); c.roundRect(x,yy,ww,44,7,fill=1,stroke=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(x+ww/2,yy+16,lab)
        if i<len(labels)-1:
            c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(x+ww+2,yy+22,x+ww+13,yy+22)
        x+=ww+14
    # columns
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,175,245,300,9,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",10.5); c.drawString(58,445,L["confirmed"])
    y=415
    for item in L["conf7"]:
        c.setFillColor(GREEN); c.circle(61,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,74,y+5,194,"Helvetica",8.9,11.4,TEXT,3)-12
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(308,175,245,300,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10.5); c.drawString(324,445,L["hold"])
    y=415
    for item in L["hold7"]:
        c.setFillColor(ORANGE); c.circle(327,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,340,y+5,194,"Helvetica",8.9,11.4,TEXT,3)-14
    source(c,("[S6] DB Plumbing Services - Handoff completo progetto piscina 22-09-2026." if L["edition"].startswith("EN") else "[S6] DB Plumbing Services - documento tecnico completo progetto piscina 22-09-2026."))
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,175,511,430,10,fill=1,stroke=1)
    y=570
    for n,h,b in L["checks8"]:
        c.setFillColor(CYAN); c.circle(62,y-4,9,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(62,y-7,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(82,y,h)
        draw_text(c,b,82,y-15,445,"Helvetica",9.4,11.8,MUTED,2)
        y-=47
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,102,511,50,8,fill=1,stroke=1)
    draw_text(c,L["footer"],57,132,480,"Helvetica",7.3,9,MUTED,3)
    source(c,("Academy rule: distinguish manufacturer data, public-health guidance and DB project-specific decisions." if L["edition"].startswith("EN") else "Regola Academy: distinguere dati del produttore, indicazioni sanitarie pubbliche e decisioni specifiche del progetto DB."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_WATER_CHEMISTRY_DOSING_REV06_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Water Chemistry & Automatic Dosing")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    print("ASSETS")
    for k,p in ASSETS.items(): print(k,p,p.stat().st_size)
    print(build("IT")); print(build("EN"))
