from pathlib import Path

source = Path(__file__).with_name("build_pdf.py")
code = source.read_text(encoding="utf-8")
old = "parts=''.join((ROOT/'v6'/f'payload{i:02d}.txt').read_text() for i in range(1,16))\npage=gzip.decompress(base64.b64decode(parts)).decode('utf-8')"
new = "page=''.join((ROOT/'v4'/f'part{i:02d}.txt').read_text(encoding='utf-8') for i in range(1,11))"
if old not in code:
    raise RuntimeError("No se encontró el bloque de carga que debía sustituirse")
namespace = {"__name__": "__main__", "__file__": str(source)}
exec(compile(code.replace(old, new), str(source), "exec"), namespace)
