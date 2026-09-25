from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"; OUT.mkdir(parents=True,exist_ok=True)

W,H=A4
NAVY=HexColor("#10263F"); CYAN=HexColor("#35A8C8"); CYAN_D=HexColor("#2388A7")
LIGHT=HexColor("#F3F6F8"); MID=HexColor("#D7E0E6"); TEXT=HexColor("#24384A"); MUTED=HexColor("#697D8B")
ORANGE=HexColor("#D4822D"); RED=HexColor("#C44A3B"); GREEN=HexColor("#3D806B"); WHITE=HexColor("#FFFFFF")
PALE_GREEN=HexColor("#EEF7F3"); PALE_ORANGE=HexColor("#FFF5E8"); PALE_RED=HexColor("#FFF0EF"); BLUEW=HexColor("#EAF7FB")

PENETRATIONS=[
("A1 AIR",120,110,"Ø32","Ø50","Ø70"),
("A2 AIR",300,110,"Ø32","Ø50","Ø70"),
("B1 AIR",480,110,"Ø32","Ø50","Ø70"),
("B2 AIR",660,110,"Ø32","Ø50","Ø70"),
("AIR SCALE",840,110,"Ø32","Ø50","Ø70"),
("R1",1000,110,"Ø50","Ø75","Ø100"),
("R2",1160,110,"Ø50","Ø75","Ø100"),
("ASP HJ1",1360,110,"Ø90","Ø125","Ø150"),
("ASP HJ2",1580,110,"Ø90","Ø125","Ø150"),
("A1 WATER",120,300,"Ø63","Ø90","Ø110"),
("A2 WATER",300,300,"Ø63","Ø90","Ø110"),
("B1 WATER",480,300,"Ø63","Ø90","Ø110"),
("B2 WATER",660,300,"Ø63","Ø90","Ø110"),
("W SCALE",840,300,"Ø63","Ø90","Ø110"),
("R3",1000,300,"Ø50","Ø75","Ø100"),
("R4",1160,300,"Ø50","Ø75","Ø100"),
("SCOPA",1360,300,"Ø63","Ø90","Ø110"),
("FONDO",1580,300,"Ø63","Ø90","Ø110"),
]

LAYOUT=[
("MAXIM HJ1",900,1332,350,1195,"845 x 432","floor + antivibration"),
("MAXIM HJ2",1482,1914,350,1195,"845 x 432","150 mm clear between pumps"),
("C-HJ",900,1900,120,300,"Ø160 x L1000","axis Z +1600"),
("Victoria 100T",2300,2881,350,631,"581 x 281","filtration pump"),
("Vesubio Ø600",3300,3900,400,1000,"Ø600 / h ~865","6-way valve toward pump"),
("pH / ORP",4300,5200,250,700,"900 x 450 zone","controls Z ~1400-1800"),
("BT FUTURE RESERVE",5400,6900,250,1200,"1500 x 950","do not occupy permanently"),
]

LAYERS=[
("Y1","80-130 mm","Ø32","air / services",CYAN),
("Y2","150-220 mm","Ø50","returns",GREEN),
("Y3","230-320 mm","Ø63","HJ / filtration",ORANGE),
("Y4","330-450 mm","Ø90","main lines",RED),
]

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"POSA LOCALE TECNICO + FOROMETRIA",
"cover_sub":"Coordinate X/Y/Z, 18 attraversamenti, guaine, carotaggi e sequenza di montaggio",
"cover_desc":"Modulo Academy costruito solo sui dati tecnici confermati del progetto DB Plumbing Services.",
"k2":"01 - SISTEMA DI COORDINATE",
"t2":"Prima di montare, definire un riferimento unico per X, Y e Z",
"l2":"Il progetto DB usa pavimento finito Z=0 e faccia della parete destra Y=0. Tutto l'impianto principale resta sulla parete destra; la parete sinistra deve rimanere libera.",
"coords":[("X","sviluppo lungo la parete destra","0 -> 6900 mm"),("Y","distanza dalla faccia parete","0 -> verso il locale"),("Z","quota verticale dal pavimento","Z=0 sul pavimento finito")],
"rules2":["C-F-SUCT: asse Z +550 mm","C-F-RET: asse Z +1350 mm","C-HJ: asse Z +1600 mm","Macchine da circa Y 350 mm in avanti","Parete sinistra: nessun impianto principale"],
"k3":"02 - POSA PARETE DESTRA",
"t3":"Le apparecchiature occupano fasce precise, ma gli attacchi finali si misurano sul prodotto reale",
"l3":"Le posizioni X/Y sotto sono il layout confermato. Le quote degli attacchi macchina non vanno inventate: gli ultimi raccordi si chiudono solo dopo misura dell'apparecchiatura realmente acquistata.",
"k4":"03 - STRATI DI TUBAZIONE",
"t4":"Piccole dietro, grandi davanti: una logica che mantiene accesso e manutenzione",
"l4":"Il progetto ordina le tubazioni per fasce Y. Questa e' una regola di posa del caso DB: serve a ridurre incroci e a mantenere accessibili pompe, filtro, valvola 6 vie e collettori.",
"note4":"I collettori devono essere supportati in modo indipendente: le pompe non devono sostenere il peso delle tubazioni.",
"k5":"04 - FOROMETRIA: 18 ATTRAVERSAMENTI",
"t5":"Due file nella fascia alta 1680 x 400 mm, solo sulla parete destra",
"l5":"Gli attraversamenti idraulici confermati sono 18: 5 aria HJ, 5 acqua HJ, 2 aspirazioni HJ, 4 ritorni, 1 presa scopa e 1 presa fondo.",
"k6":"05 - GUAINE, CAROTAGGI E TENUTA",
"t6":"Il foro non e' solo un diametro: tubazione, guaina e carota hanno funzioni diverse",
"l6":"Ogni attraversamento ha un diametro di servizio, una guaina di protezione e un diametro di carotaggio. Tutte le guaine sono previste lunghe 550 mm.",
"totals":[("Ø50","5 guaine"),("Ø75","4 guaine"),("Ø90","7 guaine"),("Ø125","2 guaine"),("Lunghezza totale","9,90 m")],
"safety6":["Usare sistema waterstop / flangia puddle / sigillatura compatibile.","Prima di carotare: verifica dei servizi e coordinamento strutturale.","Se si incontra armatura, non spostare automaticamente il centro foro.","Taglio, ripristino o rinforzo dell'armatura devono essere coordinati con il responsabile strutturale."],
"k7":"06 - SEQUENZA DI INSTALLAZIONE",
"t7":"L'ordine di montaggio evita di chiudere raccordi prima di conoscere le quote reali",
"l7":"La sequenza seguente e' quella gia definita per il progetto DB. Non e' un ordine universale per ogni piscina: e' il metodo operativo di questo cantiere.",
"steps":[
("1","Tracciatura","Segnare X apparecchiature, quote Z +550/+1350/+1600 e i 18 centri foro."),
("2","Carotaggi","Eseguire carotaggi, guaine e waterstop dopo verifica servizi/struttura."),
("3","Posteriori","Montare per primi supporti posteriori e linee aria Ø32."),
("4","Posa a secco","Posizionare le macchine, controllare manutenzione e misurare gli attacchi reali."),
("5","Aspirazioni HJ","ASP HJ1 -> MAXIM1 e ASP HJ2 -> MAXIM2 con tratte Ø90 corte."),
("6","Mandate HJ","MAXIM Ø90 + intercettazione + valvola di non ritorno -> C-HJ Ø160 a Z +1600."),
("7","Dorsali HJ","Dal C-HJ partire con 5 x Ø63 A1/A2/B1/B2/SCALE."),
("8","Filtrazione aspirazione","C-F-SUCT a Z +550: SCOPA/FONDO/BT -> Victoria."),
("9","Filtrazione trattamento","Victoria -> Vesubio/6 vie -> trattamento -> C-F-RET; scarico separato."),
("10","Ritorni","C-F-RET a Z +1350 -> R1/R2/R3/R4 Ø50, ciascuno valvolato."),
("11","Raccordi finali","Chiudere gli ultimi raccordi macchina solo dopo misura reale degli attacchi."),
("12","Prove","Eseguire prove di pressione/tenuta circuito per circuito prima della chiusura.")],
"k8":"07 - CONTROLLO PRIMA DELLA CHIUSURA",
"t8":"Prima di nascondere un tubo, deve essere identificabile, accessibile e provato",
"l8":"Il controllo finale non aggiunge nuove quote: verifica che quanto installato corrisponda ai dati confermati e che non siano comparsi componenti o passaggi non previsti.",
"checks":[
("1","18 fori","Contare fisicamente tutti gli attraversamenti e confrontare X, D, guaina e carota."),
("2","Parete sinistra","Verificare che resti completamente libera."),
("3","Fasce Y","Controllare Ø32, Ø50, Ø63 e Ø90 nelle rispettive fasce senza incroci inutili."),
("4","Quote Z","Verificare C-F-SUCT +550, C-F-RET +1350, C-HJ +1600."),
("5","Accesso manutenzione","Prefiltri MAXIM/Victoria, coperchio Vesubio, valvola 6 vie e valvole collettori devono restare accessibili."),
("6","Supporti","Collettori e tubazioni devono essere sostenuti indipendentemente dalle pompe."),
("7","Tenuta","Registrare le prove circuito per circuito prima di chiusure o rivestimenti."),
("8","Attacchi reali","Nessuna quota di raccordo macchina deve essere fissata per supposizione.")],
"footer":"Fonte progetto: Documento tecnico DB Plumbing Services - Handoff completo piscina 22/09/2026, sezioni 11-13 e 18."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"TECHNICAL ROOM LAYOUT + PENETRATIONS",
"cover_sub":"X/Y/Z coordinates, 18 penetrations, sleeves, core holes and installation sequence",
"cover_desc":"Academy module built only from confirmed DB Plumbing Services project data.",
"k2":"01 - COORDINATE SYSTEM",
"t2":"Before installation, define one common X, Y and Z reference",
"l2":"The DB project uses finished floor as Z=0 and the face of the right wall as Y=0. The complete main installation stays on the right wall; the left wall remains clear.",
"coords":[("X","distance along right wall","0 -> 6900 mm"),("Y","distance from wall face","0 -> into technical room"),("Z","vertical level from floor","Z=0 at finished floor")],
"rules2":["C-F-SUCT: axis Z +550 mm","C-F-RET: axis Z +1350 mm","C-HJ: axis Z +1600 mm","Equipment from approximately Y 350 mm forward","Left wall: no main installation"],
"k3":"02 - RIGHT-WALL LAYOUT",
"t3":"Equipment occupies defined bands, but final connection heights are measured on the real product",
"l3":"The X/Y positions below are the confirmed layout. Equipment connection offsets must not be invented: final machine connections are closed only after measuring the actual purchased equipment.",
"k4":"03 - PIPE LAYERS",
"t4":"Small behind, large in front: a layout logic that preserves access",
"l4":"The project organises pipework into Y layers. This is a DB project rule intended to reduce crossings and preserve access to pumps, filter, six-way valve and manifolds.",
"note4":"Manifolds must be independently supported: pumps must not carry the weight of pipework.",
"k5":"04 - PENETRATIONS: 18 CROSSINGS",
"t5":"Two rows inside the upper 1680 x 400 mm strip, right wall only",
"l5":"The confirmed hydraulic penetrations are 18: 5 HJ air, 5 HJ water, 2 HJ suction, 4 returns, 1 vacuum point and 1 main drain line.",
"k6":"05 - SLEEVES, CORE HOLES AND SEALING",
"t6":"A penetration is more than one diameter: service pipe, sleeve and core hole perform different jobs",
"l6":"Each crossing has a service diameter, a protective sleeve and a core-hole diameter. All sleeves are specified at 550 mm length.",
"totals":[("Ø50","5 sleeves"),("Ø75","4 sleeves"),("Ø90","7 sleeves"),("Ø125","2 sleeves"),("Total sleeve length","9.90 m")],
"safety6":["Use a compatible waterstop / puddle-flange / sealing system.","Before core drilling: verify services and structural coordination.","If reinforcement is encountered, do not automatically move the penetration centre.","Cutting, repair or reinforcement must be coordinated with the structural responsible person."],
"k7":"06 - INSTALLATION SEQUENCE",
"t7":"The installation order prevents final connections from being fixed before real offsets are known",
"l7":"The following sequence is the one already defined for the DB project. It is not a universal sequence for every pool; it is this site's operating method.",
"steps":[
("1","Setting out","Mark equipment X positions, Z +550/+1350/+1600 and all 18 penetration centres."),
("2","Core drilling","Install core holes, sleeves and waterstop after services/structural checks."),
("3","Rear services","Install rear supports and Ø32 air lines first."),
("4","Dry positioning","Place equipment dry, check maintenance access and measure real connections."),
("5","HJ suction","ASP HJ1 -> MAXIM1 and ASP HJ2 -> MAXIM2 with short Ø90 runs."),
("6","HJ discharge","MAXIM Ø90 + isolation + check valve -> C-HJ Ø160 at Z +1600."),
("7","HJ branches","From C-HJ run 5 x Ø63 A1/A2/B1/B2/SCALE."),
("8","Filtration suction","C-F-SUCT at Z +550: VACUUM/MAIN DRAIN/BT -> Victoria."),
("9","Filtration treatment","Victoria -> Vesubio/six-way -> treatment -> C-F-RET; separate waste line."),
("10","Returns","C-F-RET at Z +1350 -> R1/R2/R3/R4 Ø50, each valved."),
("11","Final machine joints","Close final equipment joints only after measuring real connections."),
("12","Testing","Pressure/leak-test each circuit before closing works.")],
"k8":"07 - PRE-CLOSURE CHECK",
"t8":"Before a pipe is hidden, it must be identifiable, accessible and tested",
"l8":"Final inspection does not add new dimensions: it confirms that installed work matches the confirmed data and that no unapproved component or route has appeared.",
"checks":[
("1","18 penetrations","Physically count all crossings and compare X, D, sleeve and core size."),
("2","Left wall","Verify it remains completely clear."),
("3","Y layers","Check Ø32, Ø50, Ø63 and Ø90 in their intended layers with no unnecessary crossings."),
("4","Z levels","Check C-F-SUCT +550, C-F-RET +1350, C-HJ +1600."),
("5","Maintenance access","MAXIM/Victoria prefilters, Vesubio lid, six-way valve and manifold valves remain accessible."),
("6","Supports","Manifolds and pipework are independently supported from pumps."),
("7","Leak tests","Record circuit-by-circuit tests before closure/finishes."),
("8","Real connections","No equipment connection dimension is fixed by assumption.")],
"footer":"Project source: DB Plumbing Services - Complete pool project handoff 22/09/2026, sections 11-13 and 18."
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
    lines=wrap(txt,font,size,maxw)
    if max_lines: lines=lines[:max_lines]
    c.setFillColor(color); c.setFont(font,size)
    yy=y
    for s in lines:
        c.drawString(x,yy,s); yy-=leading
    return yy

def header(c,k,p,edition):
    en=edition.startswith("EN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.5); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.7)
    c.drawRightString(W-42,H-30,("POOL SYSTEMS - LAYOUT / PENETRATIONS - REV09" if en else "SISTEMI PISCINA - POSA / FOROMETRIA - REV09"))
    c.setStrokeColor(MID); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",10.2); c.drawString(42,H-62,k)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.6); c.drawRightString(W-42,24,f"{edition} - {p}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(42,35,95,35)

def title(c,t,lead):
    yy=draw_text(c,t,42,H-101,W-84,"Helvetica-Bold",26,29,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-3,128,yy-3)
    draw_text(c,lead,42,yy-30,W-84,"Helvetica",11.4,15,MUTED,5)

def source(c,txt):
    draw_text(c,txt,42,60,W-84,"Helvetica",6.8,8,MUTED,2)

def cover(c,L):
    en=L["edition"].startswith("EN")
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.5); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-125,260,"Helvetica-Bold",29,32,WHITE,4)
    draw_text(c,L["cover_sub"],48,H-255,245,"Helvetica-Bold",13.0,17,CYAN,5)
    draw_text(c,L["cover_desc"],48,H-345,240,"Helvetica",11.2,15,WHITE,5)
    # right-side engineering sketch
    c.setFillColor(WHITE); c.roundRect(315,145,225,500,16,fill=1,stroke=0)
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(335,205,185,380,8,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawCentredString(427,555,("RIGHT WALL - 18 PENETRATIONS" if en else "PARETE DESTRA - 18 ATTRAVERSAMENTI"))
    # scaled two penetration rows
    for name,x,d,svc,sleeve,core in PENETRATIONS:
        px=348+(x/1680)*160
        py=475 if d==110 else 375
        c.setFillColor(CYAN if d==110 else ORANGE)
        c.circle(px,py,5.5,fill=1,stroke=0)
    c.setStrokeColor(MID); c.line(348,425,508,425)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.2); c.drawCentredString(427,337,("upper strip 1680 x 400 mm" if en else "fascia alta 1680 x 400 mm"))
    # layer sketch
    y0=245
    for i,(code,rng,diam,desc,col) in enumerate(LAYERS):
        c.setFillColor(col); c.rect(355,y0+i*20,145,12,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.6); c.drawCentredString(427,220,("PIPE LAYERS Y1-Y4" if en else "STRATI TUBAZIONE Y1-Y4"))
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.2); c.drawString(48,80,("VISUAL STANDARD REV09" if en else "STANDARD VISIVO REV09"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.1); c.drawString(48,60,("CONFIRMED COORDINATES - NO INVENTED OFFSETS - INSTALLER-FIRST METHOD" if en else "QUOTE CONFERMATE - NESSUN OFFSET INVENTATO - METODO PENSATO PER L'INSTALLATORE"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    # coordinate diagram
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,315,270,300,10,fill=1,stroke=1)
    ox,oy=90,365
    c.setStrokeColor(NAVY); c.setLineWidth(2.2)
    c.line(ox,oy,270,oy); c.line(ox,oy,ox,560); c.line(ox,oy,180,440)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",11); c.drawString(273,oy-3,"X"); c.drawString(83,568,"Z"); c.drawString(184,446,"Y")
    c.setFillColor(CYAN); c.circle(ox,oy,5,fill=1,stroke=0)
    c.setFillColor(MUTED); c.setFont("Helvetica",8.5); c.drawString(104,345,("ORIGIN: right wall / finished floor" if L["edition"].startswith("EN") else "ORIGINE: parete destra / pavimento finito"))
    # cards
    y=575
    for code,desc,val in L["coords"]:
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(335,y-70,218,60,8,fill=1,stroke=1)
        c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",14); c.drawString(350,y-38,code)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(382,y-28,desc)
        c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawString(382,y-44,val)
        y-=72
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,115,511,155,9,fill=1,stroke=1)
    yy=240
    for item in L["rules2"]:
        c.setFillColor(GREEN); c.circle(60,yy+2,2.4,fill=1,stroke=0)
        yy=draw_text(c,item,74,yy+5,460,"Helvetica-Bold",9.4,12,TEXT,2)-12
    source(c,"DB technical source: technical-room layout and X/Y/Z pipe layers.")
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    # plan area
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,250,511,350,10,fill=1,stroke=1)
    x0=60; y0=310; sx=470/6900
    c.setStrokeColor(NAVY); c.line(x0,y0,x0+470,y0)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.2)
    for mark in [0,1000,2000,3000,4000,5000,6000,6900]:
        px=x0+mark*sx
        c.line(px,y0-4,px,y0+4)
        c.drawCentredString(px,y0-17,str(mark))
    # equipment bars by X extents, stacking lanes
    lanes=[520,470,420,370,320,270,]
    colors=[RED,RED,ORANGE,CYAN_D,GREEN,CYAN]
    for i,(name,x1,x2,y1,y2,foot,note) in enumerate(LAYOUT[:6]):
        py=lanes[i]
        px=x0+x1*sx; pw=max(15,(x2-x1)*sx)
        c.setFillColor(colors[i]); c.roundRect(px,py,pw,28,5,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.2); c.drawString(60,py+8,name)
        c.setFillColor(MUTED); c.setFont("Helvetica",6.8); c.drawRightString(530,py+8,f"X {x1}-{x2} | Y {y1}-{y2} | {foot}")
    # BT reserve
    name,x1,x2,y1,y2,foot,note=LAYOUT[6]
    px=x0+x1*sx; pw=(x2-x1)*sx
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(ORANGE); c.roundRect(px,315,pw,55,5,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(px+pw/2,340,("BT FUTURE RESERVE" if L["edition"].startswith("EN") else "RISERVA FUTURA BT"))
    # maintenance rule
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,125,511,85,9,fill=1,stroke=1)
    note=("Keep MAXIM/Victoria prefilters, Vesubio lid, six-way valve and manifold valves accessible. Approx. clear corridor in front of MAXIM: 1345 mm."
          if L["edition"].startswith("EN") else
          "Mantenere accessibili prefiltri MAXIM/Victoria, coperchio Vesubio, valvola 6 vie e valvole collettori. Corridoio libero davanti alle MAXIM: circa 1345 mm.")
    draw_text(c,note,60,180,470,"Helvetica-Bold",9.3,12.2,NAVY,5)
    source(c,"DB technical source: confirmed right-wall X/Y equipment zones; left wall remains clear.")
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    # cross-section by Y
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,270,511,330,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.rect(70,310,16,245,fill=1,stroke=0)
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8); c.drawString(55,570,("RIGHT WALL Y=0" if L["edition"].startswith("EN") else "PARETE DESTRA Y=0"))
    base=105
    maxy=450
    for i,(code,rng,diam,desc,col) in enumerate(LAYERS):
        lo=int(rng.split("-")[0]); hi=int(rng.split("-")[1].split()[0])
        x1=86+lo/maxy*400; x2=86+hi/maxy*400
        py=520-i*58
        c.setFillColor(col); c.roundRect(x1,py,x2-x1,24,5,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.2); c.drawString(100,py+7,f"{code}  {rng}")
        c.setFillColor(MUTED); c.setFont("Helvetica",8.4); c.drawRightString(525,py+7,f"{diam} - {desc}")
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,145,511,80,8,fill=1,stroke=1)
    draw_text(c,L["note4"],60,195,470,"Helvetica-Bold",9.5,12,NAVY,4)
    source(c,"DB technical source: Y1 80-130, Y2 150-220, Y3 230-320, Y4 330-450 mm; equipment from about Y 350 mm forward.")
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    # scaled wall strip
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,290,511,315,10,fill=1,stroke=1)
    left=70; bottom=340; width=455; height=190
    c.setStrokeColor(NAVY); c.rect(left,bottom,width,height,fill=0,stroke=1)
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.5)
    c.drawString(left,bottom+height+14,("UPPER PENETRATION STRIP 1680 x 400 mm" if L["edition"].startswith("EN") else "FASCIA ALTA FOROMETRIA 1680 x 400 mm"))
    for name,x,d,svc,sleeve,core in PENETRATIONS:
        px=left+x/1680*width
        py=bottom+height-(d/400*height)
        col=CYAN if d==110 else ORANGE
        c.setFillColor(col); c.circle(px,py,5.2,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",5.8)
        c.saveState(); c.translate(px+2,py+8); c.rotate(50); c.drawString(0,0,name); c.restoreState()
    c.setFillColor(MUTED); c.setFont("Helvetica",6.6)
    c.drawString(left,bottom-18,("X from background wall ->" if L["edition"].startswith("EN") else "X dalla parete di fondo ->"))
    c.drawRightString(left+width,bottom-18,"1580 mm")
    # summary
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,130,511,120,9,fill=1,stroke=1)
    summary=(["5 x HJ air Ø32","5 x HJ water Ø63","2 x HJ suction Ø90","4 x returns Ø50","1 x vacuum Ø63","1 x main drain Ø63"]
             if L["edition"].startswith("EN") else
             ["5 x aria HJ Ø32","5 x acqua HJ Ø63","2 x aspirazioni HJ Ø90","4 x ritorni Ø50","1 x scopa Ø63","1 x fondo Ø63"])
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9)
    for i,s in enumerate(summary):
        c.drawString(62+(i%2)*245,220-(i//2)*30,s)
    source(c,"DB technical source: exact penetration IDs, X positions, D below ceiling, service diameters, sleeves and core sizes.")
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    # totals
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,345,240,255,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(58,570,("SLEEVE SCHEDULE" if L["edition"].startswith("EN") else "DISTINTA GUAINE"))
    y=535
    for a,b in L["totals"]:
        c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(58,y-42,208,34,6,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(70,y-28,a)
        c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.8); c.drawRightString(254,y-28,b)
        y-=43
    # diameter relation diagram
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(305,345,248,255,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(321,570,("THREE DIAMETERS" if L["edition"].startswith("EN") else "TRE DIAMETRI"))
    cx=430
    c.setFillColor(PALE_RED); c.setStrokeColor(RED); c.circle(cx,475,62,fill=1,stroke=1)
    c.setFillColor(WHITE); c.setStrokeColor(ORANGE); c.circle(cx,475,43,fill=1,stroke=1)
    c.setFillColor(BLUEW); c.setStrokeColor(CYAN_D); c.circle(cx,475,27,fill=1,stroke=1)
    labels=(["CORE HOLE","SLEEVE","SERVICE PIPE"] if L["edition"].startswith("EN") else ["CAROTA","GUAINA","TUBO SERVIZIO"])
    c.setFillColor(RED); c.setFont("Helvetica-Bold",8); c.drawString(332,410,labels[0])
    c.setFillColor(ORANGE); c.drawString(402,410,labels[1])
    c.setFillColor(CYAN_D); c.drawString(470,410,labels[2])
    # safety
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,120,511,180,9,fill=1,stroke=1)
    y=265
    for item in L["safety6"]:
        c.setFillColor(ORANGE); c.circle(61,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,74,y+5,460,"Helvetica",9.2,11.8,TEXT,3)-12
    source(c,"DB technical source: total sleeves 2 x Ø125, 7 x Ø90, 4 x Ø75, 5 x Ø50; each L550; total 9.90 m.")
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,100,511,515,10,fill=1,stroke=1)
    y=575
    for n,h,b in L["steps"]:
        c.setFillColor(CYAN); c.circle(61,y-2,8,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",6.7); c.drawCentredString(61,y-5,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.8); c.drawString(80,y,h)
        draw_text(c,b,190,y,330,"Helvetica",7.8,9.6,MUTED,2)
        y-=39
    source(c,"DB technical source: confirmed 12-step installation sequence.")
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,150,511,455,10,fill=1,stroke=1)
    y=570
    for n,h,b in L["checks"]:
        c.setFillColor(GREEN); c.circle(62,y-4,9,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(62,y-7,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.4); c.drawString(82,y,h)
        draw_text(c,b,82,y-16,445,"Helvetica",8.6,10.8,MUTED,2)
        y-=50
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,87,511,45,8,fill=1,stroke=1)
    draw_text(c,L["footer"],57,116,480,"Helvetica",7.2,8.8,MUTED,3)
    source(c,("Academy rule: project-specific dimensions are taught as project-specific, not universal standards." if L["edition"].startswith("EN") else "Regola Academy: le quote specifiche del progetto vengono insegnate come tali, non come standard universali."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_LAYOUT_PENETRATIONS_REV09_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Technical Room Layout & Penetrations")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    print(build("IT"))
    print(build("EN"))
