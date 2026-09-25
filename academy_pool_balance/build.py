from __future__ import annotations
from pathlib import Path
import io, os, math
import requests
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "assets"
OUT = ROOT / "output"
ASSET.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W,H = A4
NAVY=HexColor("#10263F")
NAVY2=HexColor("#18364E")
CYAN=HexColor("#35A8C8")
CYAN_D=HexColor("#2388A7")
LIGHT=HexColor("#F3F6F8")
MID=HexColor("#D7E0E6")
TEXT=HexColor("#24384A")
MUTED=HexColor("#697D8B")
ORANGE=HexColor("#D4822D")
RED=HexColor("#C44A3B")
GREEN=HexColor("#3D806B")
WHITE=HexColor("#FFFFFF")
SAND=HexColor("#E6D7B0")

URLS={
"overflow_pool":"https://www.delfin-wellness.at/referenzen/pool/projekte/detail/assets/images/3/P513-pool-schwebeflaechen-01-9f63b8e2.jpg",
"balance_tridea":"https://www.trideaprojects.com/wp/wp-content/uploads/2020/12/IMG_3717-720x540.jpeg",
"balance_cloward":"https://blooloop.com/media-library/balance-tank-cloward.jpg?id=56477264&quality=90&width=800",
"balance_anchem":"https://anchem-baseny.pl/image/public/6e106af2-79df-11ec-bb4c-525400e16d32_hd_zw1-img-5273.jpeg?tag=416848",
"overflow_grating":"https://dam.fluidra.com/transform/Medium/3b5edd29-5a74-41db-b763-a78bf96c2f67/MainView_AP_FOT_00212_Transversal_Grating3987",
"overflow_nozzle":"https://dam.fluidra.com/m/694a37736171db8d/original/productimages_suctionnozzle-overflowchannel.jpg",
}
HEADERS={"User-Agent":"Mozilla/5.0 (Academy DB Plumbing Services; technical education)"}

def dl(key):
    path=ASSET/f"{key}.jpg"
    if path.exists() and path.stat().st_size>5000:
        return path
    errs=[]
    for _ in range(3):
        try:
            r=requests.get(URLS[key],headers=HEADERS,timeout=35,allow_redirects=True)
            ct=(r.headers.get("content-type") or "").lower()
            if r.ok and len(r.content)>5000 and ("image" in ct or key in ("overflow_grating",)):
                tmp=ASSET/f"{key}.tmp"
                tmp.write_bytes(r.content)
                try:
                    with Image.open(tmp) as im:
                        im.verify()
                    tmp.replace(path)
                    return path
                except Exception as e:
                    tmp.unlink(missing_ok=True)
                    errs.append(f"invalid image {e}")
            else:
                errs.append(f"HTTP {r.status_code} {ct} {len(r.content)}")
        except Exception as e:
            errs.append(str(e))
    raise RuntimeError(f"Unable to download {key}: {errs}")

ASSETS={k:dl(k) for k in URLS}

def crop_product(path,name):
    im=Image.open(path).convert("RGB")
    bg=Image.new("RGB",im.size,(255,255,255))
    diff=ImageOps.grayscale(ImageChops.difference(im,bg)) if False else None
    # Generic safe trim using bbox against white
    from PIL import ImageChops
    d=ImageChops.difference(im,bg).convert("L")
    bbox=d.point(lambda p:0 if p<12 else 255).getbbox()
    if bbox:
        l,t,r,b=bbox
        l=max(0,l-18); t=max(0,t-18); r=min(im.width,r+18); b=min(im.height,b+18)
        im=im.crop((l,t,r,b))
    out=ASSET/name
    im.save(out,quality=94)
    return out

ASSETS["overflow_grating_crop"]=crop_product(ASSETS["overflow_grating"],"overflow_grating_crop.jpg")
ASSETS["overflow_nozzle_crop"]=crop_product(ASSETS["overflow_nozzle"],"overflow_nozzle_crop.jpg")

COPY={
"IT":{
"edition":"EDIZIONE ITALIANA",
"cover_title":"OVERFLOW & BALANCE TANK",
"cover_sub":"Dal bordo sfioratore al controllo del livello",
"cover_desc":"Funzione idraulica • volumi operativi • connessioni • commissioning • case study DB",
"k2":"01 • PRINCIPIO DI FUNZIONAMENTO",
"t2":"Dallo sfioro alla Balance Tank: il percorso che stabilizza il livello",
"l2":"In una piscina a sfioro l'acqua che supera il bordo non viene persa: viene raccolta, trasferita alla vasca di compenso e rimessa nel circuito di filtrazione. La Balance Tank assorbe le variazioni di volume e rende possibile un livello d'acqua visivamente stabile.",
"k3":"02 • LIVELLI E VOLUMI",
"t3":"Dentro la Balance Tank: non esiste un solo livello",
"l3":"Per leggere correttamente una vasca di compenso bisogna distinguere livello statico, livello operativo minimo, volume disponibile per lo sfioro e margine di sicurezza. Le quote esatte dipendono dal progetto reale: il diagramma qui sotto e' didattico, non una quota universale.",
"k4":"03 • CONNESSIONI",
"t4":"Cinque funzioni da riconoscere prima di progettare i bocchelli",
"l4":"Le connessioni della vasca devono essere lette per funzione, non per posizione. Nel case study DB tre collegamenti sono gia' certi; troppo pieno, scarico e controllo livello restano da rilevare e definire.",
"conn":[("ARRIVO SFIORO","Ingresso per gravita' dall'overflow della piscina.","CONFIRMATO DB"),
("ASPIRAZIONE FILTRAZIONE","Uscita verso il collettore di aspirazione filtrazione.","CONFIRMATO DB"),
("RIEMPIMENTO / MAKE-UP","Linea di reintegro acqua.","CONFIRMATO DB: PPR VERDE"),
("TROPPO PIENO / SCARICO","Protezione contro sovrariempimento e svuotamento manutentivo.","DA RILEVARE DB"),
("CONTROLLO LIVELLO","Galleggiante, sonde o altra logica in base al sistema reale.","DA RILEVARE DB")],
"k5":"04 • COMPONENTI REALI DI SFIORO",
"t5":"Canale, griglia e presa: esempi reali, non componenti imposti al progetto",
"l5":"L'Academy separa il principio idraulico dal prodotto. Le immagini reali AstralPool mostrano due componenti tipici di sistemi a sfioro. Nel progetto DB il bordo e' una fessura continua stretta: questi prodotti sono riferimenti didattici e non una selezione automatica.",
"g1":"GRIGLIA TRASVERSALE ASTRALPOOL 00212",
"g1b":"PP stabilizzato UV. AstralPool indica di costruire il canale 5 mm piu' largo della griglia per consentire rimozione ed espansione.",
"g2":"PRESA SFIORO ASTRALPOOL 00302",
"g2b":"Corpo e griglia in ABS, incollaggio su tubo Ø63. Portata massima dichiarata 4.5 m3/h. Applicazione a parete / canale di sfioro.",
"k6":"05 • COMMISSIONING",
"t6":"Avviamento: osservare livelli, aria e ritorno dell'acqua prima di regolare",
"l6":"Una Balance Tank puo' essere geometricamente grande ma idraulicamente mal utilizzata. Il commissioning serve a verificare cosa accade realmente quando la pompa parte, il livello scende, l'acqua ritorna e lo sfioro riprende.",
"checks":[("1","Pompa ferma","Osservare il livello statico/equalizzato e registrarlo."),
("2","Pompa in marcia","Controllare il drawdown e la sommersione dell'aspirazione."),
("3","Sfioro attivo","Verificare ritorno continuo alla vasca senza strozzature o rigurgiti."),
("4","Reintegro","Provare il make-up e verificare che non mascheri perdite o troppo pieno."),
("5","Transitorio","Simulare variazioni di volume e osservare margine disponibile / freeboard."),
("6","Aria e vortici","Nessun trascinamento d'aria verso la pompa e nessun vortice persistente.")],
"k7":"06 • CASE STUDY DB PLUMBING SERVICES",
"t7":"Il progetto reale: cosa e' certo e cosa deve restare aperto",
"l7":"La pagina usa esclusivamente i dati confermati nell'handoff del 22/09/2026. Dove il rilievo non e' completo, il dato resta volutamente NON DEFINITO.",
"confirmed":"DATI CONFERMATI",
"confitems":["Piscina privata a Malta con sfioro continuo su un solo lato lungo.","Fessura sfioro circa 2-3 cm.","Livello acqua/sfioro circa +3.10 m dal pavimento del locale tecnico.","Balance Tank dietro la parete lunga.","Sviluppo usato nei calcoli: 4.80 m dalla parete destra = 4.50 m vasca + 0.30 m offset.","Linea PPR verde esistente = riempimento Balance Tank.","Connessioni certe: sfioro in ingresso, aspirazione filtrazione, riempimento PPR."],
"open":"DA RILEVARE / NON CONGELARE",
"openitems":["Profondita' interna completa della Balance Tank.","Quote e diametri reali dei bocchelli BT.","Troppo pieno / scarico.","Sistema di controllo livello.","Dettagli interni e forometria dedicata."],
"k8":"07 • SCHEDA DI RILIEVO",
"t8":"Balance Tank: cosa misurare prima del progetto definitivo",
"l8":"Questa scheda chiude il metodo Academy: non si inventa cio' che il cantiere non ha ancora confermato. Il rilievo trasforma la vasca esistente in dati progettuali verificabili.",
"fields":["Lunghezza interna utile","Larghezza interna utile","Altezza interna utile","Livello statico a pompa ferma","Livello minimo a pompa in marcia","Quota arrivo sfioro","Quota aspirazione filtrazione","Diametro aspirazione filtrazione","Quota e diametro PPR riempimento","Troppo pieno: quota + diametro","Scarico manutenzione: quota + diametro","Sistema controllo livello","Dimensione/accesso botola","Possibilita' pulizia interna","Foto di ogni parete + attacco"],
"footer_note":"Foto esterne usate come riferimenti didattici con attribuzione. Per vendita o distribuzione commerciale occorre verificare/ottenere i relativi diritti d'uso."
},
"EN":{
"edition":"ENGLISH EDITION",
"cover_title":"OVERFLOW & BALANCE TANK",
"cover_sub":"From the overflow edge to stable water-level control",
"cover_desc":"Hydraulic function • operating volumes • connections • commissioning • DB case study",
"k2":"01 • OPERATING PRINCIPLE",
"t2":"From overflow edge to Balance Tank: the path that stabilises the water level",
"l2":"In an overflow pool, water crossing the edge is not lost: it is collected, transferred to the balance tank and returned to the filtration circuit. The balance tank absorbs volume changes and makes a visually stable water level possible.",
"k3":"02 • LEVELS AND VOLUMES",
"t3":"Inside the Balance Tank: there is more than one meaningful level",
"l3":"A balance tank must be read in terms of static level, minimum operating level, available surge volume and safety margin. Exact elevations belong to the real project; the diagram below is educational and not a universal dimension.",
"k4":"03 • CONNECTIONS",
"t4":"Five functions to identify before designing any tank nozzle",
"l4":"Tank connections should be read by function, not by location. In the DB case study three connections are already certain; overflow protection, drain and level control still require survey and final definition.",
"conn":[("OVERFLOW INLET","Gravity inlet from the pool overflow system.","DB CONFIRMED"),
("FILTRATION SUCTION","Outlet toward the filtration suction manifold.","DB CONFIRMED"),
("MAKE-UP / FILL","Water make-up line.","DB CONFIRMED: GREEN PPR"),
("SAFETY OVERFLOW / DRAIN","Protection against overfill and maintenance drainage.","DB TO SURVEY"),
("LEVEL CONTROL","Float valve, probes or other logic according to the actual system.","DB TO SURVEY")],
"k5":"04 • REAL OVERFLOW COMPONENTS",
"t5":"Channel, grating and suction fitting: real examples, not imposed selections",
"l5":"The Academy separates hydraulic principle from product selection. The real AstralPool images show two common overflow-system components. The DB project uses a narrow continuous overflow slot: these products are teaching references, not an automatic selection.",
"g1":"ASTRALPOOL TRANSVERSAL GRATING 00212",
"g1b":"UV-stabilised PP. AstralPool states that the channel should be built 5 mm wider than the grating to allow removal and expansion.",
"g2":"ASTRALPOOL OVERFLOW SUCTION NOZZLE 00302",
"g2b":"ABS body and grille, glued to Ø63 pipe. Manufacturer maximum flow 4.5 m3/h. Wall / overflow-channel application.",
"k6":"05 • COMMISSIONING",
"t6":"Start-up: observe levels, air and water return before adjusting controls",
"l6":"A balance tank may be physically large yet poorly used hydraulically. Commissioning verifies what actually happens when the pump starts, the tank level drops, water returns and overflow resumes.",
"checks":[("1","Pump stopped","Observe and record the static/equalised level."),
("2","Pump running","Check drawdown and suction submergence."),
("3","Overflow active","Verify continuous return to the tank without restriction or backup."),
("4","Make-up","Test make-up and confirm it does not hide leakage or safety overflow issues."),
("5","Transient","Simulate volume changes and observe available surge margin / freeboard."),
("6","Air and vortices","No air entrainment into the pump and no persistent suction vortex.")],
"k7":"06 • DB PLUMBING SERVICES CASE STUDY",
"t7":"The real project: what is confirmed and what must remain open",
"l7":"This page uses only data confirmed in the 22/09/2026 project handoff. Where the survey is incomplete, the value intentionally remains NOT DEFINED.",
"confirmed":"CONFIRMED DATA",
"confitems":["Private pool in Malta with continuous overflow on one long side only.","Overflow slot approximately 2-3 cm.","Water / overflow level approximately +3.10 m above technical-room floor.","Balance Tank behind the long wall.","Development used in calculations: 4.80 m from right wall = 4.50 m tank + 0.30 m absorbed offset.","Existing green PPR line = Balance Tank filling line.","Certain connections: overflow inlet, filtration suction, PPR fill."],
"open":"TO SURVEY / DO NOT FREEZE",
"openitems":["Complete internal Balance Tank depth.","Actual BT nozzle elevations and diameters.","Safety overflow / drain.","Level-control system.","Internal details and dedicated penetrations."],
"k8":"07 • SURVEY SHEET",
"t8":"Balance Tank: what to measure before final design",
"l8":"This sheet closes the Academy method: do not invent what the site has not confirmed. Survey data turns an existing tank into verifiable design information.",
"fields":["Useful internal length","Useful internal width","Useful internal height","Static level with pump stopped","Minimum level with pump running","Overflow inlet elevation","Filtration suction elevation","Filtration suction diameter","PPR fill elevation + diameter","Safety overflow: elevation + diameter","Maintenance drain: elevation + diameter","Level-control system","Access hatch dimensions","Internal cleaning access","Photo of each wall + connection"],
"footer_note":"External photographs are used as attributed technical/educational references. Commercial sale or distribution requires checking/obtaining the relevant image rights."
}}

SOURCES=[
("S1","Delfin Wellness P513 - one-sided infinity edge project"),
("S2","Tridea Projects - overflow pool compensation tanks"),
("S3","Cloward H2O balance tank design concepts via blooloop, 2024"),
("S4","ANCHEM - real polypropylene overflow/balance tank installation"),
("S5","AstralPool 00212 Transversal Grating product page"),
("S6","AstralPool 00302 Suction nozzle - overflow channel product page"),
("S7","AstralPool private overflow spa manual - automatic fill / safety outlet example"),
("S8","DB Plumbing Services - Handoff completo progetto piscina 22/09/2026"),
]

def wrap_lines(txt,font,size,maxw):
    words=txt.split()
    lines=[]; cur=""
    for w in words:
        trial=w if not cur else cur+" "+w
        if stringWidth(trial,font,size)<=maxw:
            cur=trial
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def draw_text(c,txt,x,y,maxw,font="Helvetica",size=10,leading=None,color=TEXT,max_lines=None):
    if leading is None: leading=size*1.26
    lines=wrap_lines(txt,font,size,maxw)
    if max_lines: lines=lines[:max_lines]
    c.setFont(font,size); c.setFillColor(color)
    yy=y
    for line in lines:
        c.drawString(x,yy,line); yy-=leading
    return yy

def fit(c,path,x,y,w,h,cover=False):
    im=Image.open(path).convert("RGB")
    iw,ih=im.size
    if cover:
        scale=max(w/iw,h/ih)
        nw,nh=int(iw*scale),int(ih*scale)
        im=im.resize((nw,nh),Image.Resampling.LANCZOS)
        l=max(0,(nw-int(w))/2); t=max(0,(nh-int(h))/2)
        im=im.crop((l,t,l+int(w),t+int(h)))
        c.drawImage(ImageReader(im),x,y,w,h,mask='auto')
    else:
        scale=min(w/iw,h/ih); dw,dh=iw*scale,ih*scale
        c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')

def image_panel(c,path,x,y,w,h,label=None,cover=False):
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.setLineWidth(.8); c.roundRect(x,y,w,h,9,fill=1,stroke=1)
    c.saveState()
    p=c.beginPath(); p.roundRect(x+1,y+1,w-2,h-2,8)
    c.clipPath(p,stroke=0,fill=0)
    fit(c,path,x+5,y+5,w-10,h-10,cover=cover)
    c.restoreState()
    if label:
        c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.roundRect(x+10,y+h-28,140,18,7,fill=1,stroke=0)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7); c.drawString(x+18,y+h-22,label)

def header(c,k,page,edition):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.3); c.drawString(42,H-30,"ACADEMY DB PLUMBING SERVICES")
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",7); c.drawRightString(W-42,H-30,"POOL SYSTEMS • OVERFLOW / BALANCE TANK • REV04")
    c.setStrokeColor(MID); c.line(42,H-38,W-42,H-38)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",9); c.drawString(42,H-62,k)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.7); c.drawRightString(W-42,24,f"{edition} • {page}")
    c.setStrokeColor(CYAN); c.setLineWidth(1.4); c.line(42,35,95,35)

def title(c,t,lead,y=H-101):
    yy=draw_text(c,t,42,y,W-84,"Helvetica-Bold",24,27,NAVY,3)
    c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(42,yy-3,128,yy-3)
    yy=draw_text(c,lead,42,yy-28,W-84,"Helvetica",10.1,13.5,MUTED,5)
    return yy

def footer_sources(c,txt):
    c.setFillColor(MUTED); c.setFont("Helvetica",6.1); c.drawString(42,58,txt)

def cover(c,L):
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
    fit(c,ASSETS["overflow_pool"],0,H*0.40,W,H*0.60,cover=True)
    c.setFillColor(HexColor("#10263F")); c.setFillAlpha(.82); c.rect(0,H*0.40,W,H*0.60,fill=1,stroke=0); c.setFillAlpha(1)
    c.setFillColor(CYAN); c.rect(0,0,10,H,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8); c.drawString(48,H-62,"ACADEMY DB PLUMBING SERVICES")
    c.setFont("Helvetica-Bold",31); draw_text(c,L["cover_title"],48,H-118,500,"Helvetica-Bold",31,34,WHITE,2)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold",15); c.drawString(48,H-188,L["cover_sub"])
    draw_text(c,L["cover_desc"],48,H-220,380,"Helvetica",10.6,14,WHITE,4)
    # bottom real tanks montage
    image_panel(c,ASSETS["balance_tridea"],48,88,230,210,"REAL BALANCE TANK INSTALLATION",cover=True)
    image_panel(c,ASSETS["balance_cloward"],300,88,247,210,"PROFESSIONAL AQUATIC MECHANICAL ROOM",cover=True)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8); c.drawString(48,55,"VISUAL STANDARD REV04 • REAL PHOTOGRAPHY + ORIGINAL TECHNICAL SCHEMES")
    c.showPage()

def page2(c,L,p):
    header(c,L["k2"],p,L["edition"]); title(c,L["t2"],L["l2"])
    image_panel(c,ASSETS["overflow_pool"],42,400,260,220,"ONE-SIDED INFINITY EDGE - REAL PROJECT",cover=True)
    image_panel(c,ASSETS["balance_tridea"],320,400,233,220,"COMPENSATION TANKS - REAL INSTALLATION",cover=True)
    # flow ribbon
    y=327
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8); c.drawString(42,y+33,"FUNCTIONAL WATER PATH")
    labels=["POOL","OVERFLOW EDGE","GRAVITY RETURN","BALANCE TANK","FILTRATION SUCTION"]
    widths=[70,100,105,96,112]
    x=42
    for i,(lab,ww) in enumerate(zip(labels,widths)):
        col=[NAVY,CYAN_D,CYAN_D,GREEN,NAVY][i]
        c.setFillColor(WHITE); c.setStrokeColor(col); c.setLineWidth(1.5); c.roundRect(x,y-18,ww,44,7,fill=1,stroke=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold",7.3); c.drawCentredString(x+ww/2,y+0,lab)
        if i<len(labels)-1:
            c.setStrokeColor(CYAN); c.setLineWidth(2); c.line(x+ww+3,y+4,x+ww+14,y+4)
            c.setFillColor(CYAN); c.circle(x+ww+14,y+4,2.5,fill=1,stroke=0)
        x+=ww+18
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,125,511,135,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(60,234,"WHY THE TANK EXISTS")
    expl=("When users enter the pool, water is displaced and the overflow system transfers that extra volume to the tank. The tank then provides water back to the circulation system as operating conditions change."
          if L["edition"].startswith("EN") else
          "Quando gli utenti entrano in vasca, il volume spostato fa aumentare lo sfioro. La vasca di compenso riceve questo volume e lo restituisce al sistema di circolazione quando le condizioni operative cambiano.")
    draw_text(c,expl,60,212,470,"Helvetica",9.3,13,TEXT,6)
    footer_sources(c,"[S1] Delfin Wellness P513   [S2] Tridea Projects   [S3] Cloward H2O / blooloop")
    c.showPage()

def page3(c,L,p):
    header(c,L["k3"],p,L["edition"]); title(c,L["t3"],L["l3"])
    image_panel(c,ASSETS["balance_cloward"],42,390,255,225,"REAL BALANCE TANK / MECHANICAL ROOM",cover=True)
    # tank conceptual section
    x,y,w,h=320,270,233,345
    c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y,w,h,10,fill=1,stroke=1)
    tx=x+38; ty=y+45; tw=w-76; th=h-100
    c.setStrokeColor(NAVY); c.setLineWidth(2); c.rect(tx,ty,tw,th,fill=0,stroke=1)
    bands=[("SAFETY / FREEBOARD",0.80,RED),("SURGE STORAGE",0.62,ORANGE),("NORMAL OPERATING",0.38,CYAN_D),("MINIMUM OPERATING",0.18,GREEN)]
    # water base
    c.setFillColor(HexColor("#DFF2F8")); c.rect(tx,ty,tw,th*0.62,fill=1,stroke=0)
    for label,frac,col in bands:
        yy=ty+th*frac
        c.setStrokeColor(col); c.setDash(4,3); c.line(tx,yy,tx+tw,yy); c.setDash()
        c.setFillColor(col); c.setFont("Helvetica-Bold",6.3); c.drawRightString(x+w-12,yy+2,label)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.1); c.drawString(x+14,y+18,"CONCEPT ONLY - NOT TO SCALE / NOT DB FINAL LEVELS")
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,150,255,205,9,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(58,330,"FOUR QUESTIONS BEFORE SIZING")
    qs=[
      ("1","What is the static/equalised level?" if L["edition"].startswith("EN") else "Qual e' il livello statico/equalizzato?"),
      ("2","How far does the level draw down with pumps running?" if L["edition"].startswith("EN") else "Quanto scende il livello con pompe in marcia?"),
      ("3","What surge/displacement volume must be absorbed?" if L["edition"].startswith("EN") else "Quale volume di sfioro/spostamento deve essere assorbito?"),
      ("4","What safety margin remains before overflow?" if L["edition"].startswith("EN") else "Quale margine resta prima del troppo pieno?")
    ]
    yy=295
    for n,q in qs:
        c.setFillColor(CYAN); c.circle(62,yy+2,8,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont("Helvetica-Bold",7); c.drawCentredString(62,yy,n)
        draw_text(c,q,80,yy+4,195,"Helvetica",8.1,11,TEXT,3); yy-=43
    footer_sources(c,"[S3] Cloward H2O / blooloop - static level, drawdown, minimum operating level, surge/storage volume")
    c.showPage()

def page4(c,L,p):
    header(c,L["k4"],p,L["edition"]); title(c,L["t4"],L["l4"])
    image_panel(c,ASSETS["balance_anchem"],42,365,215,255,"REAL PP TANK INSTALLATION",cover=True)
    # connection table
    x=278; y=604; rowh=63
    for i,(a,b,status) in enumerate(L["conn"]):
        yy=y-i*rowh
        status_col=GREEN if "CONFIRM" in status else ORANGE
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,yy-rowh+5,275,rowh-8,8,fill=1,stroke=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.4); c.drawString(x+12,yy-19,a)
        draw_text(c,b,x+12,yy-34,168,"Helvetica",7.4,9.5,MUTED,3)
        c.setFillColor(status_col); c.setFont("Helvetica-Bold",6.6); c.drawRightString(x+263,yy-19,status)
    # bottom rule block
    c.setFillColor(HexColor("#EEF7F3")); c.setStrokeColor(HexColor("#C8DFD5")); c.roundRect(42,120,511,135,10,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",9.5); c.drawString(60,230,"ACADEMY RULE" if L["edition"].startswith("EN") else "REGOLA ACADEMY")
    body=("A tank nozzle is not 'correct' because it looks convenient. Its elevation and diameter must be justified by the hydraulic function, operating level, accessible maintenance and the actual pipe network."
          if L["edition"].startswith("EN") else
          "Un bocchello non e' 'giusto' perche' sembra comodo. Quota e diametro devono essere giustificati dalla funzione idraulica, dai livelli operativi, dalla manutenzione accessibile e dalla rete reale.")
    draw_text(c,body,60,208,470,"Helvetica",9.1,13,TEXT,6)
    footer_sources(c,"[S4] ANCHEM tank reference   [S7] AstralPool overflow spa manual   [S8] DB handoff")
    c.showPage()

def page5(c,L,p):
    header(c,L["k5"],p,L["edition"]); title(c,L["t5"],L["l5"])
    image_panel(c,ASSETS["overflow_grating_crop"],42,355,235,250,"ASTRALPOOL 00212")
    image_panel(c,ASSETS["overflow_nozzle_crop"],318,355,235,250,"ASTRALPOOL 00302")
    # cards
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,150,235,165,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(58,288,L["g1"])
    draw_text(c,L["g1b"],58,267,202,"Helvetica",8.3,11.5,TEXT,8)
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(318,150,235,165,10,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(334,288,L["g2"])
    draw_text(c,L["g2b"],334,267,202,"Helvetica",8.3,11.5,TEXT,8)
    footer_sources(c,"[S5] AstralPool 00212   [S6] AstralPool 00302 - manufacturer data")
    c.showPage()

def page6(c,L,p):
    header(c,L["k6"],p,L["edition"]); title(c,L["t6"],L["l6"])
    image_panel(c,ASSETS["balance_cloward"],42,380,210,250,"REFERENCE MECHANICAL ROOM",cover=True)
    x=276; y=606; cw=277
    for i,(n,h,b) in enumerate(L["checks"]):
        yy=y-i*72
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,yy-63,cw,56,8,fill=1,stroke=1)
        c.setFillColor(CYAN); c.circle(x+18,yy-34,10,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8); c.drawCentredString(x+18,yy-37,n)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8.3); c.drawString(x+37,yy-28,h)
        draw_text(c,b,x+37,yy-42,cw-50,"Helvetica",7.2,9.4,MUTED,2)
    c.setFillColor(HexColor("#FFF5E8")); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(42,122,210,205,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",9); c.drawString(58,300,"DO NOT TUNE BY EYE" if L["edition"].startswith("EN") else "NON REGOLARE A OCCHIO")
    body=("Record water levels and pump state together. A level that looks acceptable may still expose the suction, entrain air or consume the safety margin during a surge."
          if L["edition"].startswith("EN") else
          "Registrare insieme livello acqua e stato pompe. Un livello che sembra accettabile puo' comunque scoprire l'aspirazione, trascinare aria o consumare il margine di sicurezza durante uno sfioro.")
    draw_text(c,body,58,278,178,"Helvetica",8.1,11,TEXT,9)
    footer_sources(c,"[S3] Cloward H2O / blooloop balance tank operating levels and design considerations")
    c.showPage()

def page7(c,L,p):
    header(c,L["k7"],p,L["edition"]); title(c,L["t7"],L["l7"])
    # clean project concept - confirmed only
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,345,511,260,10,fill=1,stroke=1)
    # pool
    c.setFillColor(HexColor("#DFF2F8")); c.setStrokeColor(NAVY); c.setLineWidth(1.5); c.roundRect(72,510,350,65,6,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(85,548,"POOL / PISCINA")
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",7); c.drawRightString(410,548,"ONE LONG-SIDE OVERFLOW")
    # overflow arrows to tank
    c.setStrokeColor(CYAN); c.setLineWidth(2)
    for ax in [120,220,320,390]:
        c.line(ax,510,ax,475); c.setFillColor(CYAN); c.circle(ax,472,2.5,fill=1,stroke=0)
    # BT
    c.setFillColor(HexColor("#E7F4F8")); c.setStrokeColor(GREEN); c.roundRect(95,410,320,58,6,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",9); c.drawString(110,442,"BALANCE TANK - EXISTING / TO SURVEY INTERNALLY")
    # tech room
    c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.roundRect(80,365,350,28,5,fill=1,stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",8); c.drawString(95,375,"TECHNICAL ROOM BELOW / IN FRONT OF WALL")
    # suction and fill
    c.setStrokeColor(NAVY); c.setLineWidth(2); c.line(415,439,500,439); c.setFillColor(NAVY); c.circle(500,439,3,fill=1,stroke=0)
    c.setFont("Helvetica-Bold",6.8); c.drawString(435,449,"TO FILTRATION SUCTION")
    c.setStrokeColor(GREEN); c.line(95,420,58,420); c.setFillColor(GREEN); c.circle(58,420,3,fill=1,stroke=0)
    c.setFont("Helvetica-Bold",6.8); c.drawString(46,430,"GREEN PPR FILL")
    # dimensions annotations
    c.setFillColor(MUTED); c.setFont("Helvetica",6.7)
    c.drawString(72,494,"Overflow slot approx. 2-3 cm • Water/overflow level approx. +3.10 m above technical-room floor")
    c.drawString(95,399,"Development used in calculations: 4.80 m from right wall = 4.50 m tank + 0.30 m absorbed offset")
    # two columns
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,115,245,205,9,fill=1,stroke=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",9.5); c.drawString(58,296,L["confirmed"])
    yy=273
    for item in L["confitems"]:
        c.setFillColor(GREEN); c.circle(60,yy+2,2.3,fill=1,stroke=0)
        yy=draw_text(c,item,70,yy+5,198,"Helvetica",7.5,9.7,TEXT,3)-7
    c.setFillColor(HexColor("#FFF5E8")); c.setStrokeColor(HexColor("#F1D5AE")); c.roundRect(308,115,245,205,9,fill=1,stroke=1)
    c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",9.5); c.drawString(324,296,L["open"])
    yy=273
    for item in L["openitems"]:
        c.setFillColor(ORANGE); c.circle(326,yy+2,2.3,fill=1,stroke=0)
        yy=draw_text(c,item,336,yy+5,198,"Helvetica",7.7,10,TEXT,3)-9
    footer_sources(c,"[S8] DB Plumbing Services - Handoff completo progetto piscina 22/09/2026")
    c.showPage()

def page8(c,L,p):
    header(c,L["k8"],p,L["edition"]); title(c,L["t8"],L["l8"])
    # 2-column survey form
    left=L["fields"][:8]; right=L["fields"][8:]
    for col,items in enumerate([left,right]):
        x=42+col*260; y=590
        for item in items:
            c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(x,y-48,238,42,6,fill=1,stroke=1)
            c.setFillColor(NAVY); c.setFont("Helvetica-Bold",7.5); c.drawString(x+10,y-21,item)
            c.setStrokeColor(CYAN); c.setLineWidth(.8); c.line(x+10,y-37,x+225,y-37)
            y-=56
    c.setFillColor(LIGHT); c.setStrokeColor(MID); c.roundRect(42,104,498,78,8,fill=1,stroke=1)
    note=("FIELD RULE: photograph each connection with a scale/reference, record elevation from one common datum, and tag every pipe before any redesign."
          if L["edition"].startswith("EN") else
          "REGOLA DI RILIEVO: fotografare ogni attacco con una scala/riferimento, quotare tutto da un unico datum e identificare ogni linea prima di riprogettare.")
    c.setFillColor(CYAN_D); c.setFont("Helvetica-Bold",8.5); c.drawString(58,158,"ACADEMY FIELD METHOD")
    draw_text(c,note,58,140,466,"Helvetica",8.3,11,TEXT,4)
    c.setFillColor(MUTED); c.setFont("Helvetica",5.8); draw_text(c,L["footer_note"],42,78,511,"Helvetica",5.8,7.5,MUTED,3)
    c.setFont("Helvetica",5.6); c.drawString(42,58,"[S1-S7] External references as listed in module source register   [S8] DB project handoff")
    c.showPage()

def build(lang):
    L=COPY[lang]
    out=OUT/f"ACADEMY_DB_POOL_SYSTEMS_OVERFLOW_BALANCE_TANK_REV04_{lang}.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("Academy DB Plumbing Services - Pool Systems - Overflow & Balance Tank")
    c.setAuthor("DB Plumbing Services - Dennis Bendinelli")
    cover(c,L); page2(c,L,2); page3(c,L,3); page4(c,L,4); page5(c,L,5); page6(c,L,6); page7(c,L,7); page8(c,L,8)
    c.save()
    return out

if __name__=="__main__":
    for k,p in ASSETS.items(): print(k,p,p.stat().st_size)
    print(build("IT"))
    print(build("EN"))
