from pathlib import Path
import base64,gzip,re,html as htmllib
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'Guia_Chillout_COMPLETA_FINAL.pdf'
TMP=ROOT/'_build_images'; TMP.mkdir(exist_ok=True)
parts=''.join((ROOT/'v6'/f'payload{i:02d}.txt').read_text() for i in range(1,16))
page=gzip.decompress(base64.b64decode(parts)).decode('utf-8')
found=re.findall(r'src="data:image/jpeg;base64,([^\"]+)" alt="([^\"]+)"',page)
imgs={}
for i,(data,alt) in enumerate(found):
    p=TMP/f'img{i}.jpg'; p.write_bytes(base64.b64decode(data)); imgs[htmllib.unescape(alt).lower()]=p

def pick(*terms):
    for alt,p in imgs.items():
        if all(t.lower() in alt for t in terms): return p
    raise KeyError(terms)

paths={
'fire':pick('fire tv'),'tdt':pick('tdt'),'barra':pick('barra'),'proyector':pick('proyector'),
'tele_int':pick('tele interior'),'tele_ext':pick('tele exterior'),'aire':pick('aire'),'splitter':pick('splitter')}

REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',REG)); pdfmetrics.registerFont(TTFont('DejaVu-Bold',BOLD))
NAVY=colors.HexColor('#173B74'); BLUE=colors.HexColor('#4A83EA'); LIGHT=colors.HexColor('#F2F6FD'); LINE=colors.HexColor('#C8D8F3'); TEXT=colors.HexColor('#1F2937'); MUTED=colors.HexColor('#667085'); GREEN=colors.HexColor('#27A85F'); RED=colors.HexColor('#D9483B'); PALE_RED=colors.HexColor('#FFF5F3'); PALE_GREEN=colors.HexColor('#F1FBF5'); WHITE=colors.white
PW,PH=A4; M=16*mm
styles=getSampleStyleSheet()
for name,font,size,leading,color,after in [
('TitleX','DejaVu-Bold',24,28,NAVY,3),('SubtitleX','DejaVu',10.5,14,TEXT,5),('H1X','DejaVu-Bold',17,21,NAVY,3),('H2X','DejaVu-Bold',12.5,16,NAVY,1.5),('BodyX','DejaVu',9.5,13,TEXT,0),('SmallX','DejaVu',8.4,11,TEXT,0),('CommandX','DejaVu-Bold',9.3,12,TEXT,0),('WhiteH','DejaVu-Bold',14.5,18,WHITE,0),('WhiteBody','DejaVu',9.4,13,WHITE,0),('CenterSmall','DejaVu',8,10,MUTED,0)]:
    styles.add(ParagraphStyle(name=name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after*mm,alignment=TA_CENTER if name=='CenterSmall' else 0))
P=lambda t,s='BodyX':Paragraph(t,styles[s])
def im(path,w,h=None):
    if h is None:
        x=PILImage.open(path); h=w*x.height/x.width
    return Image(str(path),width=w*mm,height=h*mm)
def card(content,bg=WHITE,border=LINE,pad=4*mm):
    t=Table([[content]],colWidths=[PW-2*M]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),.8,border),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('VALIGN',(0,0),(-1,-1),'TOP')])); return t
def grid(items,cols=2,color=BLUE):
    data=[]
    for i in range(0,len(items),cols):
        data.append([P(f'<font color="#{color.hexval()[2:]}">●</font>&nbsp;&nbsp;"{items[i+j]}"','CommandX') if i+j<len(items) else '' for j in range(cols)])
    t=Table(data,colWidths=[(PW-2*M-(cols-1)*3*mm)/cols]*cols); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#FAFCFF')),('BOX',(0,0),(-1,-1),.65,LINE),('INNERGRID',(0,0),(-1,-1),.55,LINE),('LEFTPADDING',(0,0),(-1,-1),3*mm),('RIGHTPADDING',(0,0),(-1,-1),3*mm),('TOPPADDING',(0,0),(-1,-1),2.4*mm),('BOTTOMPADDING',(0,0),(-1,-1),2.4*mm),('VALIGN',(0,0),(-1,-1),'MIDDLE')])); return t
def zone(title,body,example):
    t=Table([[[P(title,'H2X'),P(body),Spacer(1,1.5*mm),P(f'<i>{example}</i>','SmallX')]]],colWidths=[(PW-2*M-5*mm)/2]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),1.2,LINE),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),4*mm),('BOTTOMPADDING',(0,0),(-1,-1),4*mm)])); return t
def remote(title,desc,path):
    t=Table([[im(path,30,40),[P(title,'H2X'),P(desc,'SmallX')]]],colWidths=[34*mm,51*mm]); t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.8,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),3*mm),('RIGHTPADDING',(0,0),(-1,-1),3*mm),('TOPPADDING',(0,0),(-1,-1),3*mm),('BOTTOMPADDING',(0,0),(-1,-1),3*mm)])); return t
def remgrid(cards):
    rows=[]
    for i in range(0,len(cards),2): rows.append([cards[i],cards[i+1] if i+1<len(cards) else ''])
    t=Table(rows,colWidths=[(PW-2*M-5*mm)/2]*2); t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2.5*mm),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),3*mm)])); return t
def header(c,d):
    c.saveState(); c.setFillColor(colors.HexColor('#EDF3FB')); c.rect(0,PH-18*mm,PW,18*mm,fill=1,stroke=0); c.setStrokeColor(colors.HexColor('#D7E3F7')); c.setLineWidth(.7); c.roundRect(9*mm,9*mm,PW-18*mm,PH-18*mm,6*mm,fill=0,stroke=1); c.setFillColor(MUTED); c.setFont('DejaVu',7.5); c.drawRightString(PW-13*mm,12*mm,f'Guia del Chillout - pagina {d.page}'); c.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=M,leftMargin=M,topMargin=23*mm,bottomMargin=17*mm,title='Guia completa del Chillout',author='Marcos')
s=[]
s += [P('GUIA COMPLETA DEL CHILLOUT','TitleX'),P('Uso del Fire Stick, comandos de voz, zonas de imagen, mandos de apoyo y soluciones rapidas.','SubtitleX')]
hero=Table([[[im(paths['fire'],33,44),Spacer(1,1*mm),P('<b>Mando principal</b>','CenterSmall')],[P('Empieza siempre por el mando Fire TV','WhiteH'),Spacer(1,1.5*mm),P('Para YouTube, Twitch, Netflix, Prime Video y casi todo lo demas, usa siempre el Fire Stick.','WhiteBody'),Spacer(1,2.5*mm),P('<b>Como hablar con Alexa</b><br/>1. Manten pulsado el boton azul.<br/>2. Di el comando.<br/>3. Suelta el boton.','WhiteBody')]]],colWidths=[43*mm,PW-2*M-43*mm]); hero.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5*mm),('RIGHTPADDING',(0,0),(-1,-1),5*mm),('TOPPADDING',(0,0),(-1,-1),5*mm),('BOTTOMPADDING',(0,0),(-1,-1),5*mm)])); s += [hero,Spacer(1,5*mm),P('Abrir aplicaciones','H1X'),grid(['Abre YouTube','Abre Twitch','Abre Netflix','Abre Prime Video','Abre Disney Plus','Abre [nombre de la app]']),Spacer(1,5*mm),P('Comandos principales','H1X'),grid(['Enciendelo todo','Apagalo todo','Pon el Fire Stick en el proyector','Pon el Fire Stick en la tele','Verano','Invierno','Apaga el aire','Pon mas brillo al fuego','Pon menos brillo al fuego']),Spacer(1,4*mm),card(P('<b>Importante:</b> "Apagalo todo" puede encender algun aparato que ya estaba apagado, porque los mandos infrarrojos no conocen el estado real. Espera a que termine la rutina y apaga ese aparato individualmente.','SmallX'),PALE_RED,RED,3*mm),PageBreak()]
s += [P('LAS DOS ZONAS DE IMAGEN','TitleX'),P('La ultima parte del comando indica que salida quieres cambiar. Las dos zonas funcionan de forma independiente.','SubtitleX')]
z=Table([[zone('PROYECTOR','Todo comando que termine en <b>"en el proyector"</b> cambia solamente lo que se muestra en el proyector.','Ejemplo: "Pon el Fire Stick en el proyector".'),zone('TELE','Todo comando que termine en <b>"en la tele"</b> cambia solamente lo que se muestra en las televisiones.','Ejemplo: "Pon los canales en la tele".')]],colWidths=[(PW-2*M-5*mm)/2]*2); z.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2.5*mm)])); s += [z,Spacer(1,4*mm),card(P('<b>Una zona no cambia la otra:</b> puedes dejar una fuente en el proyector y otra distinta en la tele.'),PALE_GREEN,GREEN,3.5*mm),Spacer(1,5*mm),P('Canales en directo','H1X'),grid(['Pon los canales en el proyector','Pon los canales en la tele']),Spacer(1,4*mm),P('Ordenador y Wii','H1X'),grid(['Pon el PC en el proyector','Pon el PC en la tele','Pon la Wii en el proyector','Pon la Wii en la tele']),Spacer(1,5*mm)]
notes=Table([[P('<b>Proyector:</b> la señal pasa por la barra de sonido LG. Si el proyector esta encendido pero no hay imagen o sonido, comprueba que la barra este encendida y que muestre <b>HDMI</b>.')],[P('<b>Tele:</b> la tele interior LG y la tele exterior Sony reciben la misma señal. Si alguna no muestra imagen, selecciona la entrada <b>HDMI</b> con su mando.')]],colWidths=[PW-2*M]); notes.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.8,LINE),('INNERGRID',(0,0),(-1,-1),.5,LINE),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),3.5*mm),('BOTTOMPADDING',(0,0),(-1,-1),3.5*mm)])); s += [notes,PageBreak()]
s += [P('MANDOS DE APOYO - PARTE 1','TitleX'),P('Usalos solamente cuando la voz no resuelva la tarea o necesites controlar una funcion concreta.','SubtitleX'),remgrid([remote('Fire TV - mando principal','Manten pulsado el boton azul para hablar con Alexa. Tambien sirve para moverte por el Fire Stick y abrir aplicaciones.',paths['fire']),remote('TDT STRONG','Utilizalo solo para cambiar de canal cuando ya hayas puesto "los canales" en la zona deseada.',paths['tdt']),remote('Barra de sonido LG','Controla el volumen. Si el proyector no se ve o no se oye, comprueba que la barra este encendida y que aparezca HDMI.',paths['barra']),remote('Proyector ViewSonic','Mando de respaldo para encender y apagar. Para encender, pulsa una vez. Para apagar, pulsa dos veces.',paths['proyector'])]),Spacer(1,3*mm),card(P('<b>Regla practica:</b> primero intenta el comando de voz con el mando Fire TV. Usa estos mandos solo como respaldo.'),LIGHT,BLUE),PageBreak()]
s += [P('MANDOS DE APOYO - PARTE 2','TitleX'),P('Estas fotografias corresponden a los mandos reales del sistema.','SubtitleX'),remgrid([remote('Tele interior LG','Encender, apagar y controlar volumen. Si no se ve la imagen, selecciona la entrada HDMI.',paths['tele_int']),remote('Tele exterior Sony','Encender, apagar y controlar volumen. La fuente correcta debe ser HDMI.',paths['tele_ext']),remote('Aire acondicionado Eiluxe','Para cambiar manualmente la temperatura, ajusta TEMP y pulsa ON/OFF para enviar o confirmar el cambio.',paths['aire']),remote('HDMI splitter 6x2','Sirve para cambiar manualmente la fuente si falla la voz. La parte superior corresponde al proyector y la inferior a la tele.',paths['splitter'])]),Spacer(1,3*mm)]
extra=Table([[P('<b>Fuego decorativo</b><br/>El mando propio permite encender, apagar y ajustar el brillo manualmente. Por voz puedes usar "Pon mas brillo al fuego" y "Pon menos brillo al fuego".','SmallX'),P('<b>Transmisor inalambrico del PC</b><br/>Conecta el HDMI al ordenador y tambien el USB de alimentacion. Sin el USB, el transmisor no funcionara.','SmallX')]],colWidths=[(PW-2*M-5*mm)/2]*2); extra.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.8,LINE),('INNERGRID',(0,0),(-1,-1),.5,LINE),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),4*mm),('BOTTOMPADDING',(0,0),(-1,-1),4*mm),('VALIGN',(0,0),(-1,-1),'TOP')])); s += [extra,PageBreak()]
s += [P('SOLUCIONES RAPIDAS','TitleX'),P('Comprueba estos puntos antes de cambiar cables o tocar varios mandos a la vez.','SubtitleX')]
tr=Table([[P('<b>No se ve el proyector</b><br/>Enciende el proyector y la barra de sonido LG. En la barra debe aparecer HDMI.'),P('<b>No se ve la tele</b><br/>Selecciona la entrada HDMI con el mando de la tele correspondiente.')],[P('<b>No aparece el PC</b><br/>Conecta el transmisor HDMI al ordenador y su cable USB de alimentacion.'),P('<b>La voz no cambia la fuente</b><br/>Prueba de nuevo manteniendo pulsado el boton azul. Si sigue fallando, usa el mando HDMI splitter.')]],colWidths=[(PW-2*M-5*mm)/2]*2); tr.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.8,LINE),('INNERGRID',(0,0),(-1,-1),.6,LINE),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),4*mm),('BOTTOMPADDING',(0,0),(-1,-1),4*mm),('VALIGN',(0,0),(-1,-1),'TOP')])); s += [tr,Spacer(1,5*mm),P('Audio por zonas','H1X')]
audio=Table([[P('<b>Zona 1:</b> cristalera exterior'),P('<b>Zona 2:</b> interior')],[P('<b>Zona 3:</b> barbacoa'),P('<b>Zona 4:</b> no se usa')]],colWidths=[(PW-2*M-5*mm)/2]*2); audio.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.8,LINE),('INNERGRID',(0,0),(-1,-1),.5,LINE),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),3*mm),('BOTTOMPADDING',(0,0),(-1,-1),3*mm)])); s += [audio,Spacer(1,4*mm),card(P('<b>Si todo esta apagado pero sigue sonando musica:</b><br/>1. Mira el amplificador situado junto a los interruptores de las luces.<br/>2. Si hay un LED azul, el sistema de altavoces sigue encendido.<br/>3. Apaga las zonas activas del selector.<br/>4. Baja el volumen del amplificador hasta el minimo, hasta notar el clic.'),PALE_GREEN,GREEN),Spacer(1,5*mm),P('Cambio manual con el HDMI splitter','H1X'),card(P('<b>Parte superior del mando:</b> controla la salida del proyector.<br/><b>Parte inferior del mando:</b> controla la salida de la tele.<br/>Cada boton selecciona manualmente una fuente. Si no sabes que boton tocar, vuelve primero al mando Fire TV e intenta el comando de voz.'),LIGHT,BLUE),Spacer(1,6*mm)]
summary=Table([[P('RESUMEN: usa el mando Fire TV, manten pulsado el boton azul, di el comando y suelta. Para streaming usa el Fire Stick. "Proyector" cambia solo el proyector y "tele" cambia solo las televisiones.','WhiteBody')]],colWidths=[PW-2*M]); summary.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('LEFTPADDING',(0,0),(-1,-1),5*mm),('RIGHTPADDING',(0,0),(-1,-1),5*mm),('TOPPADDING',(0,0),(-1,-1),5*mm),('BOTTOMPADDING',(0,0),(-1,-1),5*mm)])); s += [summary]
doc.build(s,onFirstPage=header,onLaterPages=header)
print(OUT)
