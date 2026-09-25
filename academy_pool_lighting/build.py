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
NAVY=HexColor("#10263F"); CYAN=HexColor("#35A8C8"); CYAN_D=HexColor("#2388A7")
LIGHT=HexColor("#F3F6F8"); MID=HexColor("#D7E0E6"); TEXT=HexColor("#24384A"); MUTED=HexColor("#697D8B")
ORANGE=HexColor("#D4822D"); RED=HexColor("#C44A3B"); GREEN=HexColor("#3D806B"); WHITE=HexColor("#FFFFFF")
PALE_GREEN=HexColor("#EEF7F3"); PALE_ORANGE=HexColor("#FFF5E8"); PALE_RED=HexColor("#FFF0EF"); BLUEW=HexColor("#EAF7FB")

HEADERS={"User-Agent":"Mozilla/5.0 (Academy DB Plumbing Services technical education)"}
URLS={
 "product":"https://dam.fluidra.com/m/5437470d5ef62892/original/flatprojectors.png",
 "datasheet":"https://fluidra.bynder.com/m/1dae8c939d8dc57e/original/productdatasheet_flatprojectors_EN_2024_11.pdf",
 "manual":"https://fluidra.bynder.com/m/470eb3fba09f23e9/original/Manual_LumiplusEssential__EN_ES_FR_AR_DE_EN_ES_FR_IT_PT.pdf",
}

def dl(key):
    url=URLS[key]; ext=".pdf" if url.lower().endswith(".pdf") else ".png"
    p=ASSET/f"{key}{ext}"
    if p.exists() and p.stat().st_size>5000: return p
    r=requests.get(url,headers=HEADERS,timeout=45); r.raise_for_status()
    p.write_bytes(r.content)
    if ext==".pdf":
        if p.read_bytes()[:4] != b"%PDF": raise RuntimeError(f"{key} is not PDF")
    else:
        with Image.open(p) as im: im.verify()
    return p

RAW={k:dl(k) for k in URLS}

def trim_white(path,out_name,margin=10):
    im=Image.open(path).convert("RGB")
    bg=Image.new("RGB",im.size,(255,255,255))
    diff=ImageChops.difference(im,bg).convert("L")
    bbox=diff.point(lambda p:0 if p<12 else 255).getbbox()
    if bbox:
        l,t,r,b=bbox; l=max(0,l-margin); t=max(0,t-margin); r=min(im.width,r+margin); b=min(im.height,b+margin)
        im=im.crop((l,t,r,b))
    out=ASSET/out_name; im.save(out,quality=95); return out

def render_page(pdf_path,page_index,out_name,dpi=220,crop=None):
    doc=fitz.open(str(pdf_path)); page=doc[page_index]
    pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
    out=ASSET/out_name; pix.save(str(out)); doc.close()
    if crop:
        im=Image.open(out).convert("RGB")
        l=int(im.width*crop[0]); t=int(im.height*crop[1]); r=int(im.width*crop[2]); b=int(im.height*crop[3])
        im.crop((l,t,r,b)).save(out,quality=95)
    return out

ASSETS={}
ASSETS["product"]=trim_white(RAW["product"],"product_crop.jpg",8)
ASSETS["datasheet"]=render_page(RAW["datasheet"],0,"datasheet.png",220,(0.02,0.00,0.98,0.78))
ASSETS["manual_en"]=render_page(RAW["manual"],1,"manual_en.png",220,(0.02,0.04,0.98,0.82))
ASSETS["manual_it"]=render_page(RAW["manual"],2,"manual_it.png",220,(0.02,0.34,0.98,0.98))

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"ILLUMINAZIONE PISCINA + COMANDO PNEUMATICO HJ",
"cover_sub":"LumiPlus 75821, trasformatore di sicurezza, guaine e comando idromassaggio",
"cover_desc":"Modulo didattico con dati verificati del produttore e caso reale DB Plumbing Services",
"k2":"01 - COMPONENTE REALE",
"t2":"LumiPlus Essential Flat 75821: leggere prima i dati del produttore",
"l2":"Nel progetto DB il candidato e' AstralPool LumiPlus Essential Flat bianco 75821. La pagina ufficiale e la scheda tecnica indicano montaggio in superficie, alimentazione 12 Vca e cavo fornito da 2,5 m.",
"specs":[("75821","modello bianco"),("12 Vca","tensione di alimentazione"),("14,5 W / 20 VA","potenza / carico apparente"),("1.485 lm","flusso luminoso"),("5.700 K","temperatura colore"),("IP68","grado di protezione"),("2 m","profondita massima di installazione"),("2,5 m","cavo H07RN-F 2 x 1 mm2")],
"cand":"STATO NEL PROGETTO DB",
"candtxt":"Sono confermate 3 luci piscina; il codice 75821 resta candidato finche' la fornitura reale non viene verificata. Non trasferire automaticamente quote di posa o accessori da altri modelli LumiPlus.",
"k3":"02 - CARICO E TRASFORMATORE",
"t3":"Tre fari da 20 VA = 60 VA collegati: questo non sceglie da solo il trasformatore",
"l3":"La scheda tecnica assegna 20 VA al 75821. Tre unita' producono quindi 60 VA di carico nominale collegato. Il manuale richiede che il trasformatore di sicurezza sia dimensionato per i VA dei proiettori connessi.",
"calc":[("1 faro","20 VA"),("3 fari","60 VA collegati"),("Tensione fari","12 Vca"),("Trasformatore finale","DA DIMENSIONARE")],
"rule3":"NON inventare un margine percentuale. La taglia finale dipende dalla fornitura reale, dalla lunghezza dei cavi, dalla caduta di tensione e dalle regole elettriche applicabili.",
"k4":"03 - TRE GUAINE SOSTITUIBILI",
"t4":"Una guaina dedicata per ogni luce: manutenzione futura senza demolire",
"l4":"Il progetto DB conferma tre guaine dedicate e sostituibili, una per ciascuna luce. Il servizio elettrico della luce deve restare separato dalle tubazioni idrauliche; eventuali attraversamenti comuni devono mantenere separazione e guainatura corretta.",
"steps4":[("L1","Guaina luce 1","percorso dedicato e sostituibile"),("L2","Guaina luce 2","percorso dedicato e sostituibile"),("L3","Guaina luce 3","percorso dedicato e sostituibile"),("LT","Locale tecnico","trasformatore e protezioni fuori dal circuito idraulico")],
"note4":"Il cavo fornito con il 75821 e' 2,5 m: prolunghe, giunzioni, cassette e percorso definitivo devono seguire il manuale del prodotto e il progetto elettrico reale.",
"k5":"04 - SICUREZZA E LIMITI",
"t5":"12 Vca non significa 'elettrico risolto': la sicurezza dipende dall'intero impianto",
"l5":"Il manuale LumiPlus richiede un trasformatore di sicurezza e l'uso della lampada immersa. L'installazione e la manutenzione devono essere eseguite da persone qualificate. La norma IEC 60364-7-702 riguarda le installazioni elettriche di piscine e zone circostanti.",
"safe":[("TRASFORMATORE DI SICUREZZA","La tensione ricevuta dal proiettore non deve superare 12 V secondo il manuale."),
("USO IMMERSO","Il manuale indica che il proiettore e' progettato per funzionare immerso in acqua."),
("PERSONALE QUALIFICATO","Montaggio e interventi elettrici richiedono qualificazione adeguata."),
("PROGETTO ELETTRICO SEPARATO","Zone piscina, RCD, SELV, equipotenziale e dimensionamento finale restano competenza dell'elettricista qualificato.")],
"k6":"05 - COMANDO PNEUMATICO HJ",
"t6":"Il pulsante vicino alle scale trasmette un impulso d'aria, non la potenza delle pompe",
"l6":"Nel progetto DB il pulsante HJ e' pneumatico e a filo pavimento vicino alle scale. Un tubo pneumatico in guaina dedicata e sostituibile raggiunge il locale tecnico, dove l'impulso viene ricevuto dall'interruttore pneumatico/logica di comando.",
"chain6":["PULSANTE PNEUMATICO","TUBO IN GUAINA DEDICATA","INTERRUTTORE PNEUMATICO / LOGICA","CIRCUITO DI COMANDO","POMPA HJ 1 + POMPA HJ 2"],
"warn6":"Lo schema mostra la LOGICA FUNZIONALE confermata. Modello dell'interruttore pneumatico, contattori, protezioni, interblocchi e cablaggio finale NON sono ancora componenti confermati.",
"k7":"06 - SEPARAZIONE DEI SERVIZI",
"t7":"Acqua, elettrico e pneumatico possono attraversare la stessa zona, ma non la stessa tubazione",
"l7":"Il progetto consente una zona comune di penetrazione per piccoli servizi solo se restano separati e correttamente inguainati. Le guaine luci e la guaina pneumatica restano indipendenti; nessun servizio elettrico o pneumatico viene fatto passare dentro una tubazione idraulica.",
"paths":[("IDRAULICA","Tubazioni acqua dedicate","PVC/linee impianto"),
("LUCI","3 guaine dedicate","una per ciascun faro"),
("PNEUMATICO HJ","1 guaina dedicata","pulsante -> locale tecnico"),
("POTENZA POMPE","Percorso elettrico separato","definito dal progetto elettrico")],
"k8":"07 - MESSA IN SERVIZIO E PUNTI DA CONFERMARE",
"t8":"Prima di consegnare: verificare prodotto, tensione, comando e manutenzione",
"l8":"La messa in servizio del sottosistema luci/comando deve dimostrare che i componenti reali corrispondono al progetto e che il sistema funziona in sicurezza senza trasformare dati candidati in fatti.",
"checks":[("1","Identita fari","Confermare che i tre fari realmente forniti siano 75821 o documentare il modello equivalente."),
("2","Guaine","Verificare continuita, sostituibilita e separazione delle 3 guaine luci e della guaina pneumatica."),
("3","Trasformatore","Calcolare la taglia sul carico reale, sul percorso cavi e sulla caduta di tensione; nessuna taglia inventata."),
("4","Tensione ai fari","Verificare la tensione reale in esercizio secondo manuale e progetto elettrico."),
("5","Pulsante HJ","Provare avvio/arresto dal pulsante pneumatico e verificare la risposta delle due pompe."),
("6","Logica di comando","Confermare interruttore pneumatico, contattori/interfacce e protezioni realmente installati."),
("7","Sicurezza piscina","RCD, SELV, equipotenziale, zone e protezioni finali da verificare dall'elettricista qualificato."),
("8","Documentazione","Registrare modelli, trasformatori, protezioni, prove e schema finale come realizzato.")],
"footer":"Fonti: AstralPool/Fluidra LumiPlus Essential Flat 75821, scheda tecnica 2024-11, manuale LumiPlus Essential; IEC 60364-7-702:2010; documento tecnico DB 22-09-2026."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"POOL LIGHTING + PNEUMATIC HJ CONTROL",
"cover_sub":"LumiPlus 75821, safety transformer, conduits and hydromassage control",
"cover_desc":"Teaching module using verified manufacturer data and the real DB Plumbing Services case study",
"k2":"01 - REAL COMPONENT",
"t2":"LumiPlus Essential Flat 75821: read manufacturer data first",
"l2":"The DB project candidate is the white AstralPool LumiPlus Essential Flat 75821. The official page and datasheet state surface mounting, 12 Vac supply and a supplied 2.5 m cable.",
"specs":[("75821","white model"),("12 Vac","supply voltage"),("14.5 W / 20 VA","power / apparent load"),("1,485 lm","luminous flux"),("5,700 K","colour temperature"),("IP68","protection rating"),("2 m","maximum installation depth"),("2.5 m","H07RN-F 2 x 1 mm2 cable")],
"cand":"DB PROJECT STATUS",
"candtxt":"Three pool lights are confirmed; code 75821 remains a candidate until the actual supply is verified. Do not automatically transfer installation dimensions or accessories from other LumiPlus models.",
"k3":"02 - LOAD AND TRANSFORMER",
"t3":"Three 20 VA lights = 60 VA connected: this alone does not select the transformer",
"l3":"The datasheet assigns 20 VA to model 75821. Three units therefore give a 60 VA nominal connected load. The manual requires the safety transformer to be sized for the VA of the connected LumiPlus projectors.",
"calc":[("1 light","20 VA"),("3 lights","60 VA connected"),("Light voltage","12 Vac"),("Final transformer","TO BE SIZED")],
"rule3":"Do NOT invent a percentage margin. Final transformer selection depends on the actual supply, cable length, voltage drop and applicable electrical rules.",
"k4":"03 - THREE REPLACEABLE CONDUITS",
"t4":"One dedicated conduit per light: future maintenance without demolition",
"l4":"The DB project confirms three dedicated replaceable conduits, one for each light. The lighting electrical service remains separate from hydraulic pipes; any common penetration zone must preserve proper separation and conduit protection.",
"steps4":[("L1","Light conduit 1","dedicated and replaceable path"),("L2","Light conduit 2","dedicated and replaceable path"),("L3","Light conduit 3","dedicated and replaceable path"),("TR","Technical room","transformer and protections outside hydraulic circuit")],
"note4":"The 75821 is supplied with 2.5 m of cable. Extensions, joints, boxes and the final route must follow the product manual and the actual electrical design.",
"k5":"04 - SAFETY AND BOUNDARIES",
"t5":"12 Vac does not mean 'electrical design complete': safety depends on the whole installation",
"l5":"The LumiPlus manual requires a safety transformer and submerged operation. Installation and maintenance must be carried out by qualified persons. IEC 60364-7-702 covers electrical installations in swimming pools and surrounding zones.",
"safe":[("SAFETY TRANSFORMER","The manual states that voltage received by the projector must not exceed 12 V."),
("SUBMERGED OPERATION","The manual states that the projector is designed to operate submerged in water."),
("QUALIFIED PERSONNEL","Assembly and electrical work require suitable qualification."),
("SEPARATE ELECTRICAL DESIGN","Pool zones, RCD, SELV, equipotential bonding and final sizing remain the qualified electrician's responsibility.")],
"k6":"05 - PNEUMATIC HJ CONTROL",
"t6":"The button near the steps transmits an air pulse, not pump power",
"l6":"In the DB project the HJ button is pneumatic and flush with the floor near the steps. A pneumatic tube in its own replaceable conduit reaches the technical room, where the pulse is received by the air switch/control logic.",
"chain6":["PNEUMATIC BUTTON","TUBE IN DEDICATED CONDUIT","AIR SWITCH / LOGIC","CONTROL CIRCUIT","HJ PUMP 1 + HJ PUMP 2"],
"warn6":"The diagram shows the confirmed FUNCTIONAL LOGIC. The air-switch model, contactors, protections, interlocks and final wiring are NOT yet frozen components.",
"k7":"06 - SERVICE SEPARATION",
"t7":"Water, electrical and pneumatic services may share a penetration zone, but never the same pipe",
"l7":"The project allows a common penetration zone for small services only when they remain separated and correctly sleeved. Light conduits and the pneumatic conduit remain independent; no electrical or pneumatic service runs inside a hydraulic pipe.",
"paths":[("HYDRAULIC","Dedicated water pipes","PVC/system lines"),
("LIGHTS","3 dedicated conduits","one per projector"),
("PNEUMATIC HJ","1 dedicated conduit","button -> technical room"),
("PUMP POWER","Separate electrical route","defined by electrical design")],
"k8":"07 - COMMISSIONING AND HOLD POINTS",
"t8":"Before handover: verify product, voltage, control and maintainability",
"l8":"Commissioning of the lighting/control subsystem must demonstrate that actual components match the design and that the system operates safely without turning candidate data into facts.",
"checks":[("1","Light identity","Confirm that the three supplied lights are 75821 or document the actual equivalent model."),
("2","Conduits","Verify continuity, replaceability and separation of the 3 light conduits and pneumatic conduit."),
("3","Transformer","Size from actual load, cable route and voltage drop; do not invent a transformer rating."),
("4","Voltage at lights","Verify real operating voltage according to the manual and electrical design."),
("5","HJ button","Test ON/OFF pneumatic command and verify response of both HJ pumps."),
("6","Control logic","Confirm the actually installed air switch, contactors/interfaces and protections."),
("7","Pool electrical safety","RCD, SELV, equipotential bonding, zones and final protections to be verified by the qualified electrician."),
("8","Documentation","Record models, transformer, protections, tests and final as-built schematic.")],
"footer":"Sources: AstralPool/Fluidra LumiPlus Essential Flat 75821, 2024-11 datasheet, LumiPlus Essential manual; IEC 60364-7-702:2010; DB technical document 22-09-2026."
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

def panel(c,path,x,y,w,h,label=None):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.saveState(); p=c.beginPath(); p.roundRect(x+1,y+1,w-2,h-2,8); c.clipPath(p,stroke=0,fill=0)
    fit(c,path,x+6,y+6,w-12,h-12,False); c.restoreState()
    if label:
        c.setFillColor(WHITE); c.roundRect(x+10,y+h-28,min(w-20,220),18,7,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.5); c.drawString(x+17,y+h-22,label)

def header(c,k,p,edition):
    en=edition.startswith("EN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.5); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.7)
    c.drawRightString(W-42,H-30,("POOL SYSTEMS - LIGHTING / PNEUMATIC CONTROL - REV08" if en else "SISTEMI PISCINA - LUCI / COMANDO PNEUMATICO - REV08"))
    c.setStrokeColor(MID); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",10.2); c.drawString(42,H-62,k)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.6); c.drawRightString(W-42,24,f"{edition} - {p}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(42,35,95,35)

def title(c,t,lead):
    yy=draw_text(c,t,42,H-101,W-84,"Helvetica-Bold",26,29,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-3,128,yy-3)
    draw_text(c,lead,42,yy-30,W-84,"Helvetica",11.5,15,MUTED,5)

def source(c,txt):
    draw_text(c,txt,42,60,W-84,"Helvetica",6.8,8,MUTED,2)

def card(c,x,y,w,h,head,body,accent=CYAN):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.setFillColor(accent); c.rect(x,y,w,5,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(x+14,y+h-28,head)
    draw_text(c,body,x+14,y+h-52,w-28,"Helvetica",9.6,12.5,TEXT,8)

def cover(c,L):
    en=L["edition"].startswith("EN")
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.5); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-125,245,"Helvetica-Bold",29,32,WHITE,5)
    draw_text(c,L["cover_sub"],48,H-292,245,"Helvetica-Bold",13.3,17,CYAN,4)
    draw_text(c,L["cover_desc"],48,H-365,235,"Helvetica",11.2,15,WHITE,5)
    c.setFillColor(WHITE); c.roundRect(315,145,225,500,16,fill=1,stroke=0)
    fit(c,ASSETS["product"],330,280,195,300,False)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawCentredString(427,225,"ASTRALPOOL LUMIPLUS ESSENTIAL FLAT 75821")
    c.setFillColor(NAVY); c.setFont("Helvetica",7.4); c.drawCentredString(427,207,("OFFICIAL PRODUCT FAMILY IMAGE" if en else "IMMAGINE UFFICIALE FAMIGLIA PRODOTTO"))
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.2); c.drawString(48,80,("VISUAL STANDARD REV08" if en else "STANDARD VISIVO REV08"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.1); c.drawString(48,60,("VERIFIED PRODUCT DATA - PROJECT BOUNDARIES - INSTALLER-FIRST METHOD" if en else "DATI PRODOTTO VERIFICATI - LIMITI DI PROGETTO - METODO PENSATO PER L'INSTALLATORE"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    panel(c,ASSETS["product"],42,320,245,290,("REAL PRODUCT FAMILY" if L["edition"].startswith("EN") else "FAMIGLIA PRODOTTO REALE"))
    x=310; y=590
    for a,b in L["specs"]:
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(x,y-51,243,44,7,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.6); c.drawString(x+12,y-27,a)
        c.setFillColor(MUTED); c.setFont("Helvetica",8.0); c.drawRightString(x+231,y-27,b)
        y-=50
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,130,511,145,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10); c.drawString(60,245,L["cand"])
    draw_text(c,L["candtxt"],60,220,470,"Helvetica",9.5,12.5,TEXT,7)
    source(c,("[S1] AstralPool LumiPlus Essential Flat official product page   [S2] Product datasheet Flat Projectors EN 2024-11   [S5] DB technical document." if L["edition"].startswith("EN") else "[S1] Pagina prodotto ufficiale AstralPool LumiPlus Essential Flat   [S2] Scheda tecnica proiettori Flat 2024-11   [S5] Documento tecnico DB."))
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    panel(c,ASSETS["datasheet"],42,325,250,285,("OFFICIAL DATASHEET" if L["edition"].startswith("EN") else "SCHEDA TECNICA UFFICIALE"))
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(315,325,238,285,10,fill=1,stroke=1)
    y=565
    for h,b in L["calc"]:
        c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",10.5); c.drawString(333,y,h)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",13); c.drawRightString(535,y,b)
        c.setStrokeColor(MID); c.line(333,y-12,535,y-12); y-=55
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,145,511,130,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10); c.drawString(60,245,("DESIGN BOUNDARY" if L["edition"].startswith("EN") else "LIMITE DI PROGETTO"))
    draw_text(c,L["rule3"],60,220,470,"Helvetica-Bold",9.7,12.7,NAVY,7)
    source(c,("[S2] 75821: 14.5 W / 20 VA.   [S3] LumiPlus Essential manual: safety transformer sized for connected projector VA." if L["edition"].startswith("EN") else "[S2] 75821: 14,5 W / 20 VA.   [S3] Manuale LumiPlus Essential: trasformatore di sicurezza dimensionato sui VA dei proiettori collegati."))
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,260,511,350,10,fill=1,stroke=1)
    y=550
    for code,h,b in L["steps4"]:
        c.setFillColor(CYAN); c.circle(68,y,15,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.2); c.drawCentredString(68,y-3,code)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.2); c.drawString(100,y+5,h)
        draw_text(c,b,100,y-14,420,"Helvetica",9.2,11.5,MUTED,2)
        if code!="LT" and code!="TR":
            c.setStrokeColor(CYAN); c.setLineWidth(1.3); c.line(68,y-20,68,y-70)
        y-=78
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,135,511,85,9,fill=1,stroke=1)
    draw_text(c,L["note4"],60,190,470,"Helvetica",9.3,12.0,TEXT,5)
    source(c,("[S2] Datasheet cable: 2.5 m H07RN-F 2 x 1 mm2.   [S5] DB project: 3 dedicated replaceable light conduits." if L["edition"].startswith("EN") else "[S2] Scheda tecnica: cavo 2,5 m H07RN-F 2 x 1 mm2.   [S5] Progetto DB: 3 guaine luci dedicate e sostituibili."))
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    man=ASSETS["manual_en"] if L["edition"].startswith("EN") else ASSETS["manual_it"]
    panel(c,man,42,335,245,275,("OFFICIAL MANUAL EXTRACT" if L["edition"].startswith("EN") else "ESTRATTO MANUALE UFFICIALE"))
    x=308; y=610
    accents=[CYAN_D,GREEN,ORANGE,RED]
    for i,(h,b) in enumerate(L["safe"]):
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y-88,245,78,8,fill=1,stroke=1)
        c.setFillColor(accents[i]); c.rect(x,y-88,5,78,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.3); c.drawString(x+15,y-34,h)
        draw_text(c,b,x+15,y-53,214,"Helvetica",8.3,10.4,MUTED,3)
        y-=88
    c.setFillColor(PALE_RED); c.setStrokeColor(HexColor("#F0CAC5")); c.roundRect(42,125,511,165,9,fill=1,stroke=1)
    msg=("This Academy module does not size final RCDs, bonding, pool zones or mains protections. Those values belong to the qualified electrician's design under applicable Malta/European rules."
         if L["edition"].startswith("EN") else
         "Questo modulo Academy non dimensiona RCD, equipotenziale, zone piscina o protezioni di rete finali. Questi valori appartengono al progetto dell'elettricista qualificato secondo le regole applicabili a Malta/Europa.")
    c.setFillColor(RED); c.setFont("Helvetica-Bold",10); c.drawString(60,260,("ELECTRICAL BOUNDARY" if L["edition"].startswith("EN") else "LIMITE ELETTRICO"))
    draw_text(c,msg,60,235,470,"Helvetica-Bold",9.2,12,NAVY,7)
    source(c,("[S3] LumiPlus Essential electrical manual.   [S4] IEC 60364-7-702:2010 - swimming pools and fountains." if L["edition"].startswith("EN") else "[S3] Manuale elettrico LumiPlus Essential.   [S4] IEC 60364-7-702:2010 - piscine e fontane."))
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,260,511,330,10,fill=1,stroke=1)
    labels=L["chain6"]; x=58; yy=450
    widths=[92,108,94,90,100]
    for i,(lab,w) in enumerate(zip(labels,widths)):
        col=[CYAN_D,GREEN,ORANGE,NAVY,RED][i]
        c.setFillColor(WHITE); c.setStrokeColor(col); c.roundRect(x,yy,w,70,8,fill=1,stroke=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold",7.5)
        lines=wrap(lab,"Helvetica-Bold",7.5,w-12)
        ly=yy+43
        for s in lines[:3]:
            c.drawCentredString(x+w/2,ly,s); ly-=11
        if i<len(labels)-1:
            c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(x+w,yy+35,x+w+12,yy+35)
            c.setFillColor(CYAN); c.circle(x+w+12,yy+35,2.2,fill=1,stroke=0)
        x+=w+14
    c.setFillColor(BLUEW); c.setStrokeColor(CYAN_D); c.roundRect(70,310,455,75,8,fill=1,stroke=1)
    mid=("WET SIDE: only pneumatic actuation at the button. Electrical power switching remains in the technical/control system."
         if L["edition"].startswith("EN") else
         "LATO BAGNATO: al pulsante arriva soltanto il comando pneumatico. La commutazione della potenza elettrica resta nel sistema tecnico/di comando.")
    draw_text(c,mid,90,350,415,"Helvetica-Bold",9.6,12.4,NAVY,4)
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,135,511,90,9,fill=1,stroke=1)
    draw_text(c,L["warn6"],60,190,470,"Helvetica",9.3,12,TEXT,5)
    source(c,("[S5] DB project: flush pneumatic HJ button near steps; dedicated replaceable tube to technical room; both HJ pumps controlled through air-switch/control logic." if L["edition"].startswith("EN") else "[S5] Progetto DB: pulsante HJ pneumatico a filo pavimento vicino alle scale; tubo dedicato e sostituibile fino al locale tecnico; entrambe le pompe HJ comandate tramite interruttore pneumatico/logica."))
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    y=560
    colors=[CYAN_D,CYAN,GREEN,ORANGE]
    for i,(h,a,b) in enumerate(L["paths"]):
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,y-93,511,82,9,fill=1,stroke=1)
        c.setFillColor(colors[i]); c.rect(42,y-93,6,82,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(62,y-34,h)
        c.setFillColor(TEXT); c.setFont("Helvetica-Bold",9.0); c.drawString(210,y-34,a)
        draw_text(c,b,210,y-54,320,"Helvetica",8.6,10.5,MUTED,2)
        y-=100
    c.setFillColor(PALE_RED); c.setStrokeColor(HexColor("#F0CAC5")); c.roundRect(42,105,511,55,8,fill=1,stroke=1)
    no=("Never route an electrical cable or pneumatic tube inside a hydraulic water pipe."
        if L["edition"].startswith("EN") else
        "Mai far passare un cavo elettrico o un tubo pneumatico dentro una tubazione idraulica dell'acqua.")
    draw_text(c,no,60,140,470,"Helvetica-Bold",9.6,12,NAVY,3)
    source(c,("[S5] DB technical document - service separation and replaceable conduit requirements." if L["edition"].startswith("EN") else "[S5] Documento tecnico DB - separazione dei servizi e requisiti delle guaine sostituibili."))
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,150,511,455,10,fill=1,stroke=1)
    y=570
    for n,h,b in L["checks"]:
        c.setFillColor(CYAN); c.circle(62,y-4,9,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(62,y-7,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(82,y,h)
        draw_text(c,b,82,y-16,445,"Helvetica",8.7,10.8,MUTED,2)
        y-=50
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,87,511,45,8,fill=1,stroke=1)
    draw_text(c,L["footer"],57,116,480,"Helvetica",7.1,8.8,MUTED,3)
    source(c,("Academy rule: manufacturer data, project-confirmed data and final electrical design are three different evidence layers." if L["edition"].startswith("EN") else "Regola Academy: dati del produttore, dati confermati del progetto e progetto elettrico finale sono tre livelli di evidenza distinti."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_LIGHTING_PNEUMATIC_CONTROL_REV08_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Lighting & Pneumatic HJ Control")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    for k,p in ASSETS.items(): print(k,p,p.stat().st_size)
    print(build("IT")); print(build("EN"))
