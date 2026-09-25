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
 "main_drain":"https://dam.fluidra.com/asset/4edd8826-0bf2-47f6-834d-9c223950bd7d/Medium/productimages_normmaindrain.jpg",
 "suction":"https://dam.fluidra.com/m/18dfa08f3f8bcc79/original/productimages_suctionnozzle-glue.jpg",
 "wall_conduit":"https://dam.fluidra.com/m/1a3b64afc4187101/original/productimages_wallconduitsinabs.jpg",
 "return_wall":"https://dam.fluidra.com/m/c211a0d74821f1b/original/productimages_normreturninletnozzleadjustable.jpg",
 "shell_manual":"https://fluidra.bynder.com/m/600948e161638c33/original/installationmanual_15863_ALL_2021_11.pdf",
}

def dl(key):
    url=URLS[key]; ext=".pdf" if url.lower().endswith(".pdf") else ".jpg"
    p=ASSET/f"{key}{ext}"
    if p.exists() and p.stat().st_size>4000: return p
    r=requests.get(url,headers=HEADERS,timeout=45)
    r.raise_for_status()
    p.write_bytes(r.content)
    if ext==".jpg":
        with Image.open(p) as im: im.verify()
    else:
        if p.read_bytes()[:4] != b"%PDF": raise RuntimeError(f"{key} not PDF")
    return p

RAW={k:dl(k) for k in URLS}

def trim_white(path,out_name,margin=12):
    im=Image.open(path).convert("RGB")
    bg=Image.new("RGB",im.size,(255,255,255))
    diff=ImageChops.difference(im,bg).convert("L")
    bbox=diff.point(lambda p:0 if p<12 else 255).getbbox()
    if bbox:
        l,t,r,b=bbox; l=max(0,l-margin); t=max(0,t-margin); r=min(im.width,r+margin); b=min(im.height,b+margin)
        im=im.crop((l,t,r,b))
    out=ASSET/out_name; im.save(out,quality=95); return out

def render_page_with_term(pdf_path,term,out_name,dpi=220):
    doc=fitz.open(str(pdf_path))
    idx=0
    for i,p in enumerate(doc):
        try:
            if term in p.get_text():
                idx=i; break
        except Exception:
            pass
    page=doc[idx]
    pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
    out=ASSET/out_name; pix.save(str(out)); doc.close()
    return out,idx

ASSETS={
 "main":trim_white(RAW["main_drain"],"main_crop.jpg",10),
 "suction":trim_white(RAW["suction"],"suction_crop.jpg",10),
 "wall":trim_white(RAW["wall_conduit"],"wall_crop.jpg",10),
 "return":trim_white(RAW["return_wall"],"return_crop.jpg",10),
}
ASSETS["floor_page"], FLOOR_PAGE = render_page_with_term(RAW["shell_manual"],"20140","floor_20140_page.png",220)

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"IDRAULICA DELLA VASCA",
"cover_sub":"Aspirazioni, passanti, bocchette e ritorni",
"cover_desc":"NORM 56379 • 00300 • 15661 • 15863 • 20140 • architettura reale DB Plumbing Services",
"k2":"01 - FUNZIONI DA NON CONFONDERE",
"t2":"Aspirazione e ritorno: stessa parete, lavoro opposto",
"l2":"Le bocche nel vaso non si classificano per forma, ma per funzione idraulica. Aspirazioni e ritorni possono sembrare simili, ma appartengono a lati opposti del circuito e richiedono verifiche diverse.",
"func":[("ASPIRAZIONE","L'acqua lascia la piscina verso la pompa/filtrazione. Rischi principali: restrizioni, aria, vortici e sicurezza anti-intrappolamento."),
("RITORNO","L'acqua filtrata/trattata rientra nel vaso. Obiettivo: distribuzione uniforme senza cortocircuiti idraulici o getti squilibrati."),
("PASSANTE","Attraversa la struttura e riceve la bocchetta. Non e' una valvola e non sostituisce il componente terminale."),
("SCARICO DI FONDO","E' una presa sul fondo collegata al circuito di aspirazione. Il componente e la posa devono rispettare prescrizioni specifiche.")],
"rule2":"REGOLA ACADEMY: prima identificare la funzione, poi il componente, poi il diametro e infine la posizione.",
"k3":"02 - SCARICO DI FONDO REALE",
"t3":"NORM 56379: leggere dati del prodotto senza trasformarli in una 'patente di sicurezza'",
"l3":"AstralPool 56379 e' uno scarico NORM antivortex per piscine in cemento. Il produttore dichiara corpo ABS UV, uscita laterale 2 in, uscita inferiore 1 1/2 in e portata massima 15 m3/h. La griglia antivortex e' dichiarata conforme EN 13451-1 e EN 13451-3.",
"main_specs":[("56379","codice prodotto"),("15 m3/h","portata massima dichiarata"),("2 in","uscita laterale"),("1 1/2 in","uscita inferiore"),("ABS UV","materiale corpo"),("EN 13451-1/-3","griglia antivortex")],
"main_warn":"Il rating del componente NON dimostra che una configurazione reale sia anti-intrappolamento o conforme. Servono verifica di progetto, posa, numero di aspirazioni, coperture, collegamenti e regole applicabili.",
"k4":"03 - PRESA SCOPA + PASSANTE",
"t4":"00300 + 15661: la bocchetta e il passante hanno due lavori diversi",
"l4":"La 00300 e' una bocchetta di aspirazione per piscine in cemento. AstralPool la indica per incollaggio su Ø63 PN6 e Ø50, con tappo filettato 1 1/2 in e pressione massima 6 bar. Il passante 15661 e' invece il corpo che attraversa la parete.",
"vac_specs":[("00300","bocchetta aspirazione"),("Ø63 PN6 / Ø50","connessioni incollaggio"),("6 bar","pressione massima componente"),("1 1/2 in","tappo filettato"),("15661","passante ABS 300 mm"),("EN 16582-1 / EN 16713-2","norme dichiarate 00300")],
"vac_note":"Nel progetto DB la 00300 + 15661 e' una CANDIDATA per la presa scopa. La scelta resta da congelare solo dopo verifica della fornitura reale e del dettaglio costruttivo della parete.",
"k5":"04 - RITORNI PARETE E PAVIMENTO",
"t5":"15863 e 20140: due modi diversi di reimmettere acqua nel vaso",
"l5":"La 15863 e' una bocchetta di ritorno regolabile per parete; la 20140 e' una bocchetta di fondo regolabile per impulsione/aspirazione. I dati di portata sono limiti/raccomandazioni del componente, non la portata che l'impianto 'deve' avere.",
"ret_wall":[("15863","ritorno parete NORM regolabile"),("13.5 m3/h","portata massima raccomandata"),("100% / 65% / 35%","tre posizioni di regolazione"),("Ø63","connessione a parete"),("EN 16582-1 / EN 16713-2","norme dichiarate")],
"ret_floor":[("20140","bocchetta fondo Ø63 PN6 / Ø50"),("12 m3/h","portata massima raccomandata"),("Impulsione / aspirazione","funzione dichiarata dal catalogo"),("ABS + viteria inox","materiali dichiarati"),("EN 16582-1 / EN 16713-2","norme dichiarate")],
"k6":"05 - ARCHITETTURA DB",
"t6":"Tre aspirazioni, quattro ritorni: ogni ramo resta identificabile e valvolabile",
"l6":"Nel progetto DB la filtrazione usa tre rami di aspirazione distinti verso C-F-SUCT e quattro rami di ritorno distinti da C-F-RET. Questa architettura permette isolamento e bilanciamento senza confondere filtrazione e idromassaggio.",
"k7":"06 - BILANCIAMENTO E MESSA IN SERVIZIO",
"t7":"La portata non si 'indovina' dalla bocchetta: si verifica nel sistema",
"l7":"Il componente terminale pone limiti e vincoli, ma la distribuzione reale dipende da perdite di carico, regolazioni, posizione dei rami e punto di lavoro della pompa. Il commissioning deve verificare il comportamento del circuito completo.",
"checks":[("1","Identita dei rami","Etichettare SCOPA, FONDO, BT e R1-R4 prima dell'avviamento."),
("2","Valvole","Aprire/regolare un ramo alla volta e registrare la posizione finale."),
("3","Aria","Nessuna aspirazione d'aria o cavitazione percepibile nel circuito filtrazione."),
("4","Distribuzione","Controllare che R1-R4 restituiscano acqua in modo coerente con il progetto."),
("5","Componenti","Nessun terminale deve superare i limiti dichiarati dal produttore."),
("6","Sicurezza","Le aspirazioni richiedono verifica specifica anti-intrappolamento; una sola portata nominale non basta."),
("7","Manutenzione","Tappi, griglie, bocchette e passanti devono restare accessibili e ispezionabili.")],
"k8":"07 - CASO REALE DB / PUNTI DA CONFERMARE",
"t8":"Candidato non significa approvato: congelare solo cio' che e' stato verificato",
"l8":"L'Academy usa il progetto DB come esempio reale ma conserva lo stato tecnico corretto di ogni elemento. I codici sotto sono candidati del progetto, non tutti gia' acquistati o approvati definitivamente.",
"confirmed":"ARCHITETTURA CONFERMATA",
"conf":["Aspirazioni filtrazione: SCOPA + FONDO + VASCA DI COMPENSO -> C-F-SUCT -> Victoria.","Ritorni: C-F-RET -> R1/R2/R3/R4, ciascuno con propria valvola.","R1/R2 sono ritorni parete; R3/R4 sono ritorni pavimento.","Linea SCARICO/CONTROLAVAGGIO separata Ø63.","Filtrazione e idromassaggio restano circuiti distinti."],
"hold":"COMPONENTI CANDIDATI / DA CONFERMARE",
"holds":["Scarico di fondo AstralPool NORM 56379.","Presa scopa AstralPool 00300 + passante 15661.","Ritorni parete AstralPool 15863 + passante 15661.","Ritorni pavimento AstralPool 20140.","Quote esatte, orientamento, numero e posa finale dei terminali nel vaso."],
"rights":"Le immagini prodotto AstralPool/Fluidra sono usate come riferimenti tecnici di studio. Prima di distribuzione commerciale/pubblica dell'Academy, verificare i diritti di riproduzione."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"IDRAULICA DELLA VASCA",
"cover_sub":"Suction points, wall conduits, inlets and returns",
"cover_desc":"NORM 56379 • 00300 • 15661 • 15863 • 20140 • real DB Plumbing Services architecture",
"k2":"01 - FUNCTIONS NOT TO CONFUSE",
"t2":"Suction and return: same shell, opposite hydraulic job",
"l2":"Pool-shell fittings should be classified by hydraulic function, not by appearance. Suction and return fittings can look similar but sit on opposite sides of the circuit and require different checks.",
"func":[("SUCTION","Water leaves the pool toward pump/filtration. Main concerns include restriction, air, vortexing and entrapment safety."),
("RETURN","Filtered/treated water re-enters the pool. The goal is even distribution without hydraulic short-circuiting or badly unbalanced jets."),
("WALL CONDUIT","Passes through the structure and receives the fitting. It is not a valve and does not replace the terminal component."),
("MAIN DRAIN","A floor suction fitting connected to the suction circuit. Product and installation require specific verification.")],
"rule2":"ACADEMY RULE: identify the function first, then the component, then the diameter, and only then the position.",
"k3":"02 - REAL MAIN DRAIN",
"t3":"NORM 56379: read product data without turning it into a 'safety certificate'",
"l3":"AstralPool 56379 is a NORM antivortex main drain for concrete pools. The manufacturer lists UV-treated ABS, a 2 in side outlet, a 1 1/2 in bottom outlet and maximum flow of 15 m3/h. The antivortex grating is declared compliant with EN 13451-1 and EN 13451-3.",
"main_specs":[("56379","product code"),("15 m3/h","declared maximum flow"),("2 in","side outlet"),("1 1/2 in","bottom outlet"),("UV ABS","body material"),("EN 13451-1/-3","antivortex grating")],
"main_warn":"The component rating does NOT prove that an actual arrangement is entrapment-safe or compliant. Design, installation, number of suctions, covers, pipework and applicable rules must be verified.",
"k4":"03 - VACUUM POINT + WALL CONDUIT",
"t4":"00300 + 15661: the nozzle and the wall conduit perform two different jobs",
"l4":"00300 is a suction nozzle for concrete pools. AstralPool lists glue connections for Ø63 PN6 and Ø50, a 1 1/2 in threaded plug and 6 bar maximum pressure. Wall conduit 15661 is the body passing through the wall.",
"vac_specs":[("00300","suction nozzle"),("Ø63 PN6 / Ø50","glue connections"),("6 bar","component maximum pressure"),("1 1/2 in","threaded plug"),("15661","300 mm ABS wall conduit"),("EN 16582-1 / EN 16713-2","declared standards for 00300")],
"vac_note":"In the DB project, 00300 + 15661 is a CANDIDATE for the vacuum point. Final selection remains open until the actual supply and wall construction detail are verified.",
"k5":"04 - WALL AND FLOOR RETURNS",
"t5":"15863 and 20140: two different ways to return water to the pool",
"l5":"15863 is an adjustable wall return nozzle; 20140 is an adjustable floor nozzle for return/suction. Their flow data are component limits/recommendations, not the flow the system 'must' have.",
"ret_wall":[("15863","adjustable NORM wall return"),("13.5 m3/h","maximum recommended flow"),("100% / 65% / 35%","three adjustment positions"),("Ø63","wall connection"),("EN 16582-1 / EN 16713-2","declared standards")],
"ret_floor":[("20140","Ø63 PN6 / Ø50 floor nozzle"),("12 m3/h","maximum recommended flow"),("Return / suction","catalogue-declared function"),("ABS + stainless hardware","declared materials"),("EN 16582-1 / EN 16713-2","declared standards")],
"k6":"05 - DB ARCHITECTURE",
"t6":"Three suction branches, four return branches: each line remains identifiable and valved",
"l6":"The DB filtration system uses three separate suction branches into C-F-SUCT and four separate return branches from C-F-RET. This keeps isolation and balancing possible without mixing filtration and hydromassage functions.",
"k7":"06 - BALANCING AND COMMISSIONING",
"t7":"Flow is not 'guessed' from the nozzle: it is verified in the complete system",
"l7":"The terminal fitting sets limits and constraints, but real distribution depends on pressure loss, valve settings, branch geometry and the pump operating point. Commissioning must verify the complete circuit.",
"checks":[("1","Branch identity","Label VACUUM, MAIN DRAIN, BT and R1-R4 before start-up."),
("2","Valves","Open/adjust one branch at a time and record the final setting."),
("3","Air","No unwanted air intake or evident cavitation in the filtration circuit."),
("4","Distribution","Check that R1-R4 return water consistently with the design intent."),
("5","Components","No terminal fitting should exceed manufacturer-declared limits."),
("6","Safety","Suction requires a specific entrapment-safety review; one nominal flow number is not enough."),
("7","Maintenance","Caps, grilles, nozzles and wall conduits must remain accessible and inspectable.")],
"k8":"07 - DB CASE STUDY / HOLD POINTS",
"t8":"Candidate does not mean approved: freeze only what has been verified",
"l8":"The Academy uses the DB project as a real example while preserving the correct technical status of every item. The codes below are project candidates, not all already purchased or finally approved.",
"confirmed":"CONFIRMED ARCHITECTURE",
"conf":["Filtration suction: VACUUM + MAIN DRAIN + Balance Tank -> C-F-SUCT -> Victoria.","Returns: C-F-RET -> R1/R2/R3/R4, each with its own valve.","R1/R2 are wall returns; R3/R4 are floor returns.","Separate Ø63 WASTE/BACKWASH line.","Filtration and hydromassage remain separate circuits."],
"hold":"CANDIDATE COMPONENTS / TO FREEZE",
"holds":["AstralPool NORM main drain 56379.","AstralPool 00300 vacuum point + wall conduit 15661.","AstralPool 15863 wall returns + wall conduit 15661.","AstralPool 20140 floor returns.","Exact elevations, orientation, quantity and final shell installation details."],
"rights":"AstralPool/Fluidra product images are used as technical study references. Before commercial/public distribution of the Academy, reproduction rights should be checked."
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
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.7); c.drawRightString(W-42,H-30,("POOL SYSTEMS - SHELL HYDRAULICS - REV07" if edition.startswith("EN") else "SISTEMI PISCINA - IDRAULICA DELLA VASCA - REV07"))
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

def cover(c,L):
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.5); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-125,255,"Helvetica-Bold",30,33,WHITE,4)
    draw_text(c,L["cover_sub"],48,H-260,245,"Helvetica-Bold",13.5,17,CYAN,3)
    draw_text(c,L["cover_desc"],48,H-326,240,"Helvetica",11.3,15,WHITE,6)
    # product montage
    c.setFillColor(WHITE); c.roundRect(315,145,225,500,16,fill=1,stroke=0)
    fit(c,ASSETS["main"],330,480,195,140,False)
    fit(c,ASSETS["suction"],330,330,90,120,False)
    fit(c,ASSETS["return"],435,330,90,120,False)
    fit(c,ASSETS["wall"],330,175,195,115,False)
    en=L["edition"].startswith("EN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.8); c.drawCentredString(427,158,("REAL ASTRALPOOL / FLUIDRA COMPONENTS" if en else "COMPONENTI REALI ASTRALPOOL / FLUIDRA"))
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.2); c.drawString(48,80,("VISUAL STANDARD REV07" if en else "STANDARD VISIVO REV07"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.2); c.drawString(48,60,("REAL PRODUCTS - VERIFIED DATA - PROJECT HOLD POINTS" if en else "PRODOTTI REALI - DATI VERIFICATI - PUNTI DA CONFERMARE"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    positions=[(42,355),(305,355),(42,145),(305,145)]
    colors=[RED,CYAN_D,GREEN,ORANGE]
    for i,(h,b) in enumerate(L["func"]):
        x,y=positions[i]
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,248,180,9,fill=1,stroke=1)
        c.setFillColor(colors[i]); c.rect(x,y,248,5,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",11.5); c.drawString(x+16,y+145,h)
        draw_text(c,b,x+16,y+118,216,"Helvetica",10.0,13,TEXT,8)
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,78,511,46,8,fill=1,stroke=1)
    draw_text(c,L["rule2"],57,108,480,"Helvetica-Bold",9.2,11.5,NAVY,3)
    source(c,("Academy principle - functional classification before component selection." if L["edition"].startswith("EN") else "Principio Academy - classificazione funzionale prima della selezione del componente."))
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    img_panel(c,ASSETS["main"],42,270,260,290,"ASTRALPOOL NORM 56379 - REAL PRODUCT")
    x=322; y=560
    for a,b in L["main_specs"]:
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(x,y-43,231,38,7,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.7); c.drawString(x+12,y-24,a)
        c.setFillColor(MUTED); c.setFont("Helvetica",7.8); c.drawRightString(x+219,y-24,b)
        y-=47
    c.setFillColor(PALE_RED); c.setStrokeColor(HexColor("#F0CAC5")); c.roundRect(42,115,511,145,10,fill=1,stroke=1)
    c.setFillColor(RED); c.setFont("Helvetica-Bold",10); c.drawString(60,235,("SAFETY BOUNDARY" if L["edition"].startswith("EN") else "LIMITE DI SICUREZZA"))
    draw_text(c,L["main_warn"],60,212,470,"Helvetica",9.7,12.8,TEXT,7)
    source(c,("[S1] AstralPool NORM main drain official product page - code 56379; manufacturer product description and declared standards." if L["edition"].startswith("EN") else "[S1] Pagina prodotto ufficiale AstralPool NORM - codice 56379; descrizione del produttore e norme dichiarate."))
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    en=L["edition"].startswith("EN")
    img_panel(c,ASSETS["suction"],42,320,245,290,("ASTRALPOOL 00300 - REAL PRODUCT" if en else "ASTRALPOOL 00300 - PRODOTTO REALE"))
    img_panel(c,ASSETS["wall"],308,320,245,290,("ASTRALPOOL 15661 FAMILY - REAL PRODUCT" if en else "ASTRALPOOL 15661 - FAMIGLIA PRODOTTO REALE"))
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,125,511,155,10,fill=1,stroke=1)
    y=252; x1=58
    for i,(a,b) in enumerate(L["vac_specs"]):
        col=i%3; row=i//3; x=x1+col*160; yy=y-row*62
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(x,yy,a)
        draw_text(c,b,x,yy-18,145,"Helvetica",8.2,10,MUTED,2)
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,75,511,38,7,fill=1,stroke=1)
    draw_text(c,L["vac_note"],57,99,480,"Helvetica",8.4,10.5,TEXT,3)
    source(c,("[S2] AstralPool 00300 suction nozzle official product page   [S3] AstralPool ABS wall conduit official product page." if L["edition"].startswith("EN") else "[S2] Pagina prodotto ufficiale AstralPool 00300, bocchetta di aspirazione   [S3] Pagina prodotto ufficiale AstralPool, passante parete in ABS."))
    c.showPage()

def draw_specs(c,x,y,w,rows,accent):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,235,9,fill=1,stroke=1)
    c.setFillColor(accent); c.rect(x,y,w,5,fill=1,stroke=0)
    yy=y+202
    for a,b in rows:
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(x+14,yy,a)
        draw_text(c,b,x+14,yy-18,w-28,"Helvetica",8.2,10.5,MUTED,2)
        yy-=42

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    en=L["edition"].startswith("EN")
    img_panel(c,ASSETS["return"],42,390,245,200,("15863 - REAL WALL RETURN" if en else "15863 - RITORNO PARETE REALE"))
    img_panel(c,ASSETS["floor_page"],308,390,245,200,("20140 - OFFICIAL MANUAL PAGE" if en else "20140 - PAGINA MANUALE UFFICIALE"),cover=False)
    draw_specs(c,42,125,245,L["ret_wall"],CYAN_D)
    draw_specs(c,308,125,245,L["ret_floor"],GREEN)
    source(c,("[S4] AstralPool 15863 official product page/manual   [S5] Fluidra installation manual 15863/20140 family; 2026 AstralPool catalogue data for 20140." if L["edition"].startswith("EN") else "[S4] Pagina prodotto/manuale ufficiale AstralPool 15863   [S5] Manuale installazione Fluidra famiglia 15863/20140; dati catalogo AstralPool 2026 per 20140."))
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,145,511,455,10,fill=1,stroke=1)
    # Suction side
    en=L["edition"].startswith("EN")
    c.setFillColor(RED); c.setFont("Helvetica-Bold",10); c.drawString(60,565,("SUCTION" if en else "ASPIRAZIONE"))
    sucs=(["VACUUM","MAIN DRAIN","BALANCE TANK"] if en else ["SCOPA","SCARICO DI FONDO","VASCA DI COMPENSO"])
    sy=[520,460,400]
    for lab,yy in zip(sucs,sy):
        c.setFillColor(PALE_RED); c.setStrokeColor(RED); c.roundRect(62,yy,130,38,6,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.7); c.drawCentredString(127,yy+14,lab)
        c.setStrokeColor(RED); c.setLineWidth(2); c.line(192,yy+19,235,yy+19)
        c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.roundRect(235,yy+4,68,30,5,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7); c.drawCentredString(269,yy+15,("VALVE" if en else "VALVOLA"))
    c.setStrokeColor(NAVY); c.setLineWidth(3)
    c.line(303,539,330,539); c.line(303,479,330,479); c.line(303,419,330,419); c.line(330,419,330,539)
    c.setFillColor(BLUEW); c.setStrokeColor(NAVY); c.roundRect(346,450,90,58,8,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawCentredString(391,483,"C-F-SUCT")
    c.setFont("Helvetica-Bold",7); c.drawCentredString(391,465,"Ø90 / 3xØ63 IN")
    c.setStrokeColor(NAVY); c.line(436,479,500,479)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawString(455,490,"VICTORIA")
    # return side
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",10); c.drawString(60,335,("RETURN" if en else "RITORNO"))
    c.setFillColor(BLUEW); c.setStrokeColor(CYAN_D); c.roundRect(62,255,100,60,8,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawCentredString(112,289,"C-F-RET")
    c.setFont("Helvetica-Bold",7); c.drawCentredString(112,271,"Ø90 / 4xØ50")
    rlabels=(["R1 WALL","R2 WALL","R3 FLOOR","R4 FLOOR"] if en else ["R1 PARETE","R2 PARETE","R3 PAVIMENTO","R4 PAVIMENTO"])
    x=190
    for lab in rlabels:
        c.setStrokeColor(CYAN_D); c.setLineWidth(2); c.line(162,285,x,285)
        c.setFillColor(WHITE); c.setStrokeColor(CYAN_D); c.roundRect(x,265,72,40,6,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7); c.drawCentredString(x+36,280,lab)
        x+=88
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(62,170,455,55,8,fill=1,stroke=1)
    note=("Each branch has its own shut-off/balancing valve. WASTE/BACKWASH remains a separate Ø63 line."
          if L["edition"].startswith("EN") else
          "Ogni ramo mantiene la propria valvola di intercettazione/bilanciamento. SCARICO/CONTROLAVAGGIO resta una linea Ø63 separata.")
    draw_text(c,note,78,205,425,"Helvetica-Bold",9.2,11.5,TEXT,4)
    source(c,("[S6] DB Plumbing Services handoff 22-09-2026 - filtration suction/return manifold architecture." if L["edition"].startswith("EN") else "[S6] Handoff DB Plumbing Services 22-09-2026 - architettura collettori di aspirazione e ritorno filtrazione."))
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,150,511,455,10,fill=1,stroke=1)
    y=565
    for n,h,b in L["checks"]:
        c.setFillColor(CYAN); c.circle(62,y-4,9,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(62,y-7,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.8); c.drawString(82,y,h)
        draw_text(c,b,82,y-17,445,"Helvetica",9.1,11.5,MUTED,2)
        y-=55
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,92,511,38,7,fill=1,stroke=1)
    msg=("Commissioning confirms system behaviour; it does not replace product certification or regulatory compliance."
         if L["edition"].startswith("EN") else
         "Il commissioning conferma il comportamento dell'impianto; non sostituisce certificazione del prodotto o conformita normativa.")
    draw_text(c,msg,57,116,480,"Helvetica-Bold",8.5,10.5,NAVY,3)
    source(c,("Manufacturer component limits + DB project architecture. Entrapment-safety review remains a separate design verification." if L["edition"].startswith("EN") else "Limiti dichiarati dei componenti + architettura del progetto DB. La verifica anti-intrappolamento resta un controllo progettuale separato."))
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,325,245,285,9,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",10.5); c.drawString(58,580,L["confirmed"])
    y=548
    for item in L["conf"]:
        c.setFillColor(GREEN); c.circle(61,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,74,y+5,194,"Helvetica",9.0,11.5,TEXT,3)-16
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(308,325,245,285,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",10.5); c.drawString(324,580,L["hold"])
    y=548
    for item in L["holds"]:
        c.setFillColor(ORANGE); c.circle(327,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,340,y+5,194,"Helvetica",9.0,11.5,TEXT,3)-17
    # product strip
    img_panel(c,ASSETS["main"],42,160,115,130,"56379")
    img_panel(c,ASSETS["suction"],174,160,115,130,"00300")
    img_panel(c,ASSETS["return"],306,160,115,130,"15863")
    img_panel(c,ASSETS["wall"],438,160,115,130,"15661")
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,94,511,45,8,fill=1,stroke=1)
    draw_text(c,L["rights"],57,122,480,"Helvetica",7.8,9.5,MUTED,3)
    source(c,("Sources: AstralPool/Fluidra official product pages & manuals; AstralPool 2026 catalogue for 20140; DB handoff 22-09-2026." if L["edition"].startswith("EN") else "Fonti: pagine prodotto e manuali ufficiali AstralPool/Fluidra; catalogo AstralPool 2026 per 20140; handoff DB 22-09-2026."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_SHELL_HYDRAULICS_REV07_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Shell Hydraulics")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    print("FLOOR MANUAL PAGE INDEX",FLOOR_PAGE)
    for k,p in ASSETS.items(): print(k,p,p.stat().st_size)
    print(build("IT")); print(build("EN"))
