from pathlib import Path

source = Path(__file__).with_name("build_pdf.py")
code = source.read_text(encoding="utf-8")
old_load = "parts=''.join((ROOT/'v6'/f'payload{i:02d}.txt').read_text() for i in range(1,16))\npage=gzip.decompress(base64.b64decode(parts)).decode('utf-8')"
new_load = "page=''.join((ROOT/'v4'/f'part{i:02d}.txt').read_text(encoding='utf-8') for i in range(1,11))"
old_image = "p=TMP/f'img{i}.jpg'; p.write_bytes(base64.b64decode(data)); imgs[htmllib.unescape(alt).lower()]=p"
new_image = "data += '=' * (-len(data) % 4); p=TMP/f'img{i}.jpg'; p.write_bytes(base64.b64decode(data)); imgs[htmllib.unescape(alt).lower()]=p"
if old_load not in code or old_image not in code:
    raise RuntimeError("No se encontró el bloque que debía corregirse")
code = code.replace(old_load, new_load).replace(old_image, new_image)
namespace = {"__name__": "__main__", "__file__": str(source)}
exec(compile(code, str(source), "exec"), namespace)
