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
PALE_GREEN=HexColor("#EEF7F3"); PALE_ORANGE=HexColor("#FFF5E8"); BLUEW=HexColor("#EAF7FB")

MANIFOLDS = {
"C-HJ":{"body":"Ø160","L":1000,"in":[("Ø90",250),("Ø90",750)],"out":[("A1 Ø63",100),("A2 Ø63",300),("B1 Ø63",500),("B2 Ø63",700),("SCALE Ø63",900)]},
"C-A-W":{"body":"Ø110","L":500,"in":[("Ø63",125),("Ø63",375)],"out":[("F4 Ø63",80),("F5 Ø63",250),("F6 Ø63",420)]},
"C-B-W":{"body":"Ø110","L":500,"in":[("Ø63",125),("Ø63",375)],"out":[("F7 Ø63",80),("F8 Ø63",250),("F9 Ø63",420)]},
"C-A-AIR":{"body":"Ø63","L":400,"in":[("Ø32",100),("Ø32",300)],"out":[("F4 Ø32",60),("F5 Ø32",200),("F6 Ø32",340)]},
"C-B-AIR":{"body":"Ø63","L":400,"in":[("Ø32",100),("Ø32",300)],"out":[("F7 Ø32",60),("F8 Ø32",200),("F9 Ø32",340)]},
"C-S-W":{"body":"Ø90","L":400,"in":[("Ø63",200)],"out":[("G1 Ø50",70),("G2 Ø50",200),("G3 Ø50",330)]},
"C-S-AIR":{"body":"Ø50","L":350,"in":[("Ø32",175)],"out":[("G1 Ø32",60),("G2 Ø32",175),("G3 Ø32",290)]},
"C-F-SUCT":{"body":"Ø90","L":600,"in":[("SCOPA Ø63",100),("FONDO Ø63",300),("BT Ø63",500)],"out":[("ASSIALE Ø63",600)]},
"C-F-RET":{"body":"Ø90","L":650,"in":[("ASSIALE Ø63",0)],"out":[("R1 Ø50",110),("R2 Ø50",250),("R3 Ø50",390),("R4 Ø50",530)]},
}

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"COLLETTORI E DISTRIBUTORI",
"cover_sub":"Geometria costruttiva, attacchi, valvole e identificazione dei rami",
"cover_desc":"Modulo Academy basato esclusivamente sulle dimensioni definite del progetto DB Plumbing Services.",
"k2":"01 - FAMIGLIA COLLETTORI",
"t2":"Ogni collettore ha un compito preciso e un codice che deve restare leggibile",
"l2":"Il progetto DB definisce nove collettori/distributori. La forma costruttiva cambia in funzione di diametro del corpo, numero di ingressi, numero di uscite e circuito servito.",
"family":[("C-HJ","collettore principale idromassaggio acqua","Ø160 x 1000"),("C-A-W / C-B-W","distributori acqua parete","Ø110 x 500"),("C-A-AIR / C-B-AIR","distributori aria Venturi parete","Ø63 x 400"),("C-S-W","distributore acqua scale","Ø90 x 400"),("C-S-AIR","distributore aria scale","Ø50 x 350"),("C-F-SUCT","collettore aspirazione filtrazione","Ø90 x 600"),("C-F-RET","collettore ritorni filtrazione","Ø90 x 650")],
"k3":"02 - C-HJ: COLLETTORE PRINCIPALE",
"t3":"Due ingressi Ø90 alimentano cinque uscite Ø63 indipendenti",
"l3":"C-HJ e' il collettore principale acqua dell'idromassaggio. Riceve le due mandate MAXIM e distribuisce verso A1, A2, B1, B2 e SCALE.",
"chj":["Corpo Ø160, lunghezza 1000 mm","Ingressi 2 x Ø90 a X250 e X750","Uscite 5 x Ø63 a X100/300/500/700/900","5 valvole Ø63, una per uscita","Manometro 0-4 bar","Scarico 1/2\"","2 valvole di non ritorno Ø90 a monte"],
"k4":"03 - DISTRIBUTORI A/B PARETE",
"t4":"Acqua e aria restano su collettori distinti ma geometricamente coordinati",
"l4":"I settori parete A e B usano la stessa geometria: due ingressi e tre uscite. I collettori acqua sono Ø110; quelli aria Venturi sono Ø63.",
"k5":"04 - DISTRIBUTORI SCALE",
"t5":"Un ramo acqua e un ramo aria alimentano tre gruppi dedicati alle scale",
"l5":"Per le scale il progetto usa due collettori separati: C-S-W per l'acqua e C-S-AIR per l'aria. Le uscite restano tre e devono essere identificate gruppo per gruppo.",
"k6":"05 - COLLETTORI FILTRAZIONE",
"t6":"C-F-SUCT raccoglie tre aspirazioni; C-F-RET separa quattro ritorni",
"l6":"La filtrazione mantiene aspirazioni e ritorni su due collettori distinti. SCOPA, FONDO e BT confluiscono nel collettore aspirazione; R1-R4 partono dal collettore ritorni.",
"k7":"06 - METODO DI FABBRICAZIONE",
"t7":"Prima si traccia il corpo, poi si verificano le quote X, infine si chiudono gli attacchi",
"l7":"Le quote X indicate sono dimensioni definite del progetto. Il metodo seguente serve a trasferirle sul pezzo senza inventare offset diversi.",
"steps":[("1","Identificare","Scrivere codice collettore, diametro corpo e lunghezza totale prima del taglio."),
("2","Tracciare asse","Definire un'origine X=0 su una estremita del corpo."),
("3","Marcare attacchi","Riportare esattamente le quote X degli ingressi e delle uscite previste."),
("4","Verificare","Controllare numero, diametro e destinazione di ogni bocca prima della lavorazione."),
("5","Allineare","Mantenere la disposizione coerente con il layout di installazione previsto."),
("6","Montare valvole","Installare le valvole previste sui rami indicati dal progetto."),
("7","Supportare","Prevedere supporti indipendenti: il peso del collettore non deve gravare sulle pompe."),
("8","Etichettare","Applicare identificazione permanente di corpo, rami e senso funzionale."),
("9","Provare","Eseguire prova di tenuta del collettore prima della posa definitiva.")],
"k8":"07 - CONTROLLO PRIMA DELLA POSA",
"t8":"Un collettore sbagliato puo' essere perfetto esteticamente ma inutilizzabile in impianto",
"l8":"Prima della posa ogni pezzo deve essere confrontato con la distinta dimensionale del progetto. Nessuna uscita va spostata per 'comodita' senza aggiornare il progetto.",
"checks":[("C-HJ","2 ingressi Ø90 + 5 uscite Ø63 + 5 valvole + manometro + scarico"),("C-A-W / C-B-W","2 ingressi Ø63 + 3 uscite Ø63"),("C-A-AIR / C-B-AIR","2 ingressi Ø32 + 3 uscite Ø32"),("C-S-W","1 ingresso Ø63 + 3 uscite Ø50"),("C-S-AIR","1 ingresso Ø32 + 3 uscite Ø32"),("C-F-SUCT","SCOPA/FONDO/BT Ø63 + uscita assiale Ø63"),("C-F-RET","ingresso assiale Ø63 + R1/R2/R3/R4 Ø50")],
"footer":"Fonte progetto: documento tecnico DB Plumbing Services - Handoff piscina 22/09/2026, sezione 14. Le quote sono specifiche di questo progetto e non costituiscono uno standard universale."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"MANIFOLDS AND DISTRIBUTORS",
"cover_sub":"Fabrication geometry, connections, valves and branch identification",
"cover_desc":"Academy module based exclusively on defined DB Plumbing Services project dimensions.",
"k2":"01 - MANIFOLD FAMILY",
"t2":"Every manifold has a precise job and a code that must remain readable",
"l2":"The DB project defines nine manifolds/distributors. Their geometry changes with body diameter, number of inlets, number of outlets and circuit served.",
"family":[("C-HJ","main hydromassage water manifold","Ø160 x 1000"),("C-A-W / C-B-W","wall-water distributors","Ø110 x 500"),("C-A-AIR / C-B-AIR","wall Venturi-air distributors","Ø63 x 400"),("C-S-W","steps-water distributor","Ø90 x 400"),("C-S-AIR","steps-air distributor","Ø50 x 350"),("C-F-SUCT","filtration suction manifold","Ø90 x 600"),("C-F-RET","filtration return manifold","Ø90 x 650")],
"k3":"02 - C-HJ: MAIN MANIFOLD",
"t3":"Two Ø90 inlets feed five independent Ø63 outlets",
"l3":"C-HJ is the main hydromassage-water manifold. It receives the two MAXIM discharges and distributes flow to A1, A2, B1, B2 and STEPS.",
"chj":["Ø160 body, 1000 mm long","2 x Ø90 inlets at X250 and X750","5 x Ø63 outlets at X100/300/500/700/900","5 x Ø63 valves, one per outlet","0-4 bar pressure gauge","1/2\" drain","2 x Ø90 check valves upstream"],
"k4":"03 - A/B WALL DISTRIBUTORS",
"t4":"Water and air remain on separate but geometrically coordinated manifolds",
"l4":"Wall sectors A and B use the same geometry: two inlets and three outlets. Water manifolds are Ø110; Venturi-air manifolds are Ø63.",
"k5":"04 - STEPS DISTRIBUTORS",
"t5":"One water branch and one air branch feed three dedicated step groups",
"l5":"The steps use two separate manifolds: C-S-W for water and C-S-AIR for air. There are three outlets on each, and each group must remain individually identified.",
"k6":"05 - FILTRATION MANIFOLDS",
"t6":"C-F-SUCT collects three suction branches; C-F-RET separates four returns",
"l6":"Filtration keeps suction and return on two different manifolds. VACUUM, MAIN DRAIN and BT enter the suction manifold; R1-R4 leave the return manifold.",
"k7":"06 - FABRICATION METHOD",
"t7":"Mark the body first, verify X dimensions next, and only then close the connections",
"l7":"The listed X positions are defined project dimensions. The method below transfers them to the component without inventing different offsets.",
"steps":[("1","Identify","Write manifold code, body diameter and total length before cutting."),
("2","Set datum","Define X=0 at one end of the body."),
("3","Mark ports","Transfer the specified X dimensions for every inlet and outlet."),
("4","Verify","Check quantity, diameter and destination of every port before fabrication."),
("5","Align","Keep orientation coherent with the intended installation layout."),
("6","Fit valves","Install the valves required on the branches defined by the project."),
("7","Support","Provide independent supports: manifold weight must not load the pumps."),
("8","Label","Permanently identify body, branches and functional direction."),
("9","Test","Leak-test the manifold before final installation.")],
"k8":"07 - PRE-INSTALLATION CHECK",
"t8":"A manifold can look perfect and still be unusable if its geometry is wrong",
"l8":"Before installation, each piece must be compared with the project dimensional schedule. No outlet is moved for 'convenience' without a project update.",
"checks":[("C-HJ","2 x Ø90 inlets + 5 x Ø63 outlets + 5 valves + gauge + drain"),("C-A-W / C-B-W","2 x Ø63 inlets + 3 x Ø63 outlets"),("C-A-AIR / C-B-AIR","2 x Ø32 inlets + 3 x Ø32 outlets"),("C-S-W","1 x Ø63 inlet + 3 x Ø50 outlets"),("C-S-AIR","1 x Ø32 inlet + 3 x Ø32 outlets"),("C-F-SUCT","VACUUM/MAIN DRAIN/BT Ø63 + axial Ø63 outlet"),("C-F-RET","axial Ø63 inlet + R1/R2/R3/R4 Ø50")],
"footer":"Project source: DB Plumbing Services pool handoff 22/09/2026, section 14. These dimensions are project-specific and are not a universal standard."
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
    c.setFillColor(color); c.setFont(font,size); yy=y
    for s in lines:
        c.drawString(x,yy,s); yy-=leading
    return yy

def header(c,k,p,edition):
    en=edition.startswith("EN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.5); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7.7)
    c.drawRightString(W-42,H-30,("POOL SYSTEMS - MANIFOLDS / DISTRIBUTORS - REV10" if en else "SISTEMI PISCINA - COLLETTORI / DISTRIBUTORI - REV10"))
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

def draw_manifold(c,x,y,w,h,code,data,en=False,accent=CYAN_D):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10.5); c.drawString(x+14,y+h-24,code)
    c.setFillColor(MUTED); c.setFont("Helvetica",7.5); c.drawRightString(x+w-14,y+h-24,f'{data["body"]} x L{data["L"]}')
    body_y=y+h/2
    bx=x+35; bw=w-70
    c.setFillColor(BLUEW); c.setStrokeColor(accent); c.roundRect(bx,body_y-18,bw,36,18,fill=1,stroke=1)
    # dimension line
    c.setStrokeColor(MUTED); c.setLineWidth(.6); c.line(bx,body_y-42,bx+bw,body_y-42)
    c.line(bx,body_y-46,bx,body_y-38); c.line(bx+bw,body_y-46,bx+bw,body_y-38)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.8); c.drawCentredString(bx+bw/2,body_y-54,f'L = {data["L"]} mm')
    # top inlets
    for lab,pos in data["in"]:
        px=bx+(pos/data["L"])*bw
        c.setStrokeColor(RED); c.setLineWidth(2.2); c.line(px,body_y+18,px,body_y+52)
        c.setFillColor(RED); c.circle(px,body_y+52,3.5,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",6.5); c.drawCentredString(px,body_y+64,lab)
        c.setFillColor(MUTED); c.setFont("Helvetica",5.8); c.drawCentredString(px,body_y+75,f'X{pos}')
    # bottom outlets
    for lab,pos in data["out"]:
        px=bx+(pos/data["L"])*bw
        c.setStrokeColor(GREEN); c.setLineWidth(2.2); c.line(px,body_y-18,px,body_y-52)
        c.setFillColor(GREEN); c.circle(px,body_y-52,3.5,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",6.2); c.drawCentredString(px,body_y-66,lab)
        if pos not in (0,data["L"]):
            c.setFillColor(MUTED); c.setFont("Helvetica",5.8); c.drawCentredString(px,body_y-76,f'X{pos}')

def cover(c,L):
    en=L["edition"].startswith("EN")
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8.5); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    draw_text(c,L["cover_title"],48,H-125,250,"Helvetica-Bold",30,33,WHITE,4)
    draw_text(c,L["cover_sub"],48,H-255,245,"Helvetica-Bold",13.2,17,CYAN,4)
    draw_text(c,L["cover_desc"],48,H-332,240,"Helvetica",11.3,15,WHITE,5)
    # technical art
    c.setFillColor(WHITE); c.roundRect(315,145,225,500,16,fill=1,stroke=0)
    draw_manifold(c,330,410,195,170,"C-HJ",MANIFOLDS["C-HJ"],en,CYAN_D)
    draw_manifold(c,330,205,195,150,"C-F-RET",MANIFOLDS["C-F-RET"],en,GREEN)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",9.2); c.drawString(48,80,("VISUAL STANDARD REV10" if en else "STANDARD VISIVO REV10"))
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.1); c.drawString(48,60,("PROJECT GEOMETRY - FABRICATION CHECKS - NO INVENTED OFFSETS" if en else "GEOMETRIA DI PROGETTO - CONTROLLI COSTRUTTIVI - NESSUN OFFSET INVENTATO"))
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    y=575
    for code,desc,size in L["family"]:
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,y-60,511,50,8,fill=1,stroke=1)
        c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",10); c.drawString(58,y-35,code)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(185,y-35,desc)
        c.setFillColor(MUTED); c.setFont("Helvetica-Bold",8.5); c.drawRightString(535,y-35,size)
        y-=64
    c.setFillColor(PALE_GREEN); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,105,511,75,9,fill=1,stroke=1)
    msg=("Codes are project identifiers, not commercial product names. They must remain consistent from drawing to fabrication and installation."
         if L["edition"].startswith("EN") else
         "I codici sono identificatori di progetto, non nomi commerciali. Devono restare coerenti dal disegno alla fabbricazione e alla posa.")
    draw_text(c,msg,60,150,470,"Helvetica-Bold",9.3,12,NAVY,4)
    source(c,("Source: DB project section 14 - defined manifold dimensions." if L["edition"].startswith("EN") else "Fonte: progetto DB, sezione 14 - dimensioni definite dei collettori."))
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    draw_manifold(c,42,310,511,300,"C-HJ",MANIFOLDS["C-HJ"],L["edition"].startswith("EN"),CYAN_D)
    c.setFillColor(PALE_ORANGE); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,115,511,150,9,fill=1,stroke=1)
    y=235
    for item in L["chj"]:
        c.setFillColor(ORANGE); c.circle(60,y+2,2.5,fill=1,stroke=0)
        y=draw_text(c,item,74,y+5,455,"Helvetica",9.0,11.6,TEXT,2)-10
    source(c,("C-HJ project data: Ø160 body, L1000, 2xØ90 inlets, 5xØ63 outlets, 5 valves, 0-4 bar gauge, 1/2 in drain, 2xØ90 check valves upstream."
              if L["edition"].startswith("EN") else
              "Dati progetto C-HJ: corpo Ø160 L1000, 2 ingressi Ø90, 5 uscite Ø63, 5 valvole, manometro 0-4 bar, scarico 1/2\", 2 valvole di non ritorno Ø90 a monte."))
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    draw_manifold(c,42,365,245,220,"C-A-W",MANIFOLDS["C-A-W"],L["edition"].startswith("EN"),CYAN_D)
    draw_manifold(c,308,365,245,220,"C-B-W",MANIFOLDS["C-B-W"],L["edition"].startswith("EN"),CYAN_D)
    draw_manifold(c,42,125,245,200,"C-A-AIR",MANIFOLDS["C-A-AIR"],L["edition"].startswith("EN"),GREEN)
    draw_manifold(c,308,125,245,200,"C-B-AIR",MANIFOLDS["C-B-AIR"],L["edition"].startswith("EN"),GREEN)
    source(c,("A/B project geometry: water Ø110 L500, in X125/375, out X80/250/420; air Ø63 L400, in X100/300, out X60/200/340."
              if L["edition"].startswith("EN") else
              "Geometria progetto A/B: acqua Ø110 L500, ingressi X125/375, uscite X80/250/420; aria Ø63 L400, ingressi X100/300, uscite X60/200/340."))
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    draw_manifold(c,42,350,511,250,"C-S-W",MANIFOLDS["C-S-W"],L["edition"].startswith("EN"),ORANGE)
    draw_manifold(c,42,120,511,190,"C-S-AIR",MANIFOLDS["C-S-AIR"],L["edition"].startswith("EN"),GREEN)
    source(c,("Steps project geometry: C-S-W Ø90 L400, one Ø63 inlet at X200, three Ø50 outlets X70/200/330; C-S-AIR Ø50 L350, one Ø32 inlet X175, three Ø32 outlets X60/175/290."
              if L["edition"].startswith("EN") else
              "Geometria progetto scale: C-S-W Ø90 L400, un ingresso Ø63 a X200, tre uscite Ø50 X70/200/330; C-S-AIR Ø50 L350, un ingresso Ø32 X175, tre uscite Ø32 X60/175/290."))
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    draw_manifold(c,42,350,511,250,"C-F-SUCT",MANIFOLDS["C-F-SUCT"],L["edition"].startswith("EN"),RED)
    draw_manifold(c,42,120,511,190,"C-F-RET",MANIFOLDS["C-F-RET"],L["edition"].startswith("EN"),CYAN_D)
    source(c,("Filtration project geometry: C-F-SUCT Ø90 L600, three Ø63 inlets at X100/300/500 and axial Ø63 outlet; C-F-RET Ø90 L650, axial Ø63 inlet and four Ø50 outlets at X110/250/390/530."
              if L["edition"].startswith("EN") else
              "Geometria progetto filtrazione: C-F-SUCT Ø90 L600, tre ingressi Ø63 a X100/300/500 e uscita assiale Ø63; C-F-RET Ø90 L650, ingresso assiale Ø63 e quattro uscite Ø50 a X110/250/390/530."))
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,110,511,500,10,fill=1,stroke=1)
    y=570
    for n,h,b in L["steps"]:
        c.setFillColor(CYAN); c.circle(62,y-3,8.5,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7); c.drawCentredString(62,y-6,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.2); c.drawString(82,y,h)
        draw_text(c,b,175,y,345,"Helvetica",8.3,10.4,MUTED,2)
        y-=49
    source(c,("Project method: use the defined X schedule; do not introduce 20-30 mm 'precision' not supported by the real installation."
              if L["edition"].startswith("EN") else
              "Metodo di progetto: usare la distinta X definita; non introdurre precisioni di 20-30 mm non supportate dall'installazione reale."))
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    y=570
    for code,desc in L["checks"]:
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(42,y-61,511,52,8,fill=1,stroke=1)
        c.setFillColor(GREEN); c.rect(42,y-61,6,52,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(60,y-35,code)
        draw_text(c,desc,180,y-27,350,"Helvetica",8.6,10.5,TEXT,2)
        y-=65
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,82,511,52,8,fill=1,stroke=1)
    draw_text(c,L["footer"],57,116,480,"Helvetica",7.3,9,MUTED,4)
    source(c,("Academy rule: project-specific collector geometry is taught as project-specific, not universal." if L["edition"].startswith("EN") else "Regola Academy: la geometria dei collettori di questo progetto viene insegnata come specifica di progetto, non come standard universale."))
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_MANIFOLDS_REV10_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Manifolds and Distributors")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save(); return out

if __name__=="__main__":
    print(build("IT")); print(build("EN"))
