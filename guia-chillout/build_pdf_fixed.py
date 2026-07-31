from pathlib import Path

source = Path(__file__).with_name("build_pdf.py")
code = source.read_text(encoding="utf-8")
old = "page=gzip.decompress(base64.b64decode(parts)).decode('utf-8')"
new = "parts += '=' * (-len(parts) % 4)\npage=gzip.decompress(base64.b64decode(parts)).decode('utf-8')"
if old not in code:
    raise RuntimeError("No se encontró la línea que debía corregirse")
namespace = {"__name__": "__main__", "__file__": str(source)}
exec(compile(code.replace(old, new), str(source), "exec"), namespace)
