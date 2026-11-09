"""Inspección de solo lectura de una base SQLite (uso: python verificar_db.py <archivo>)."""
import json
import pathlib
import sqlite3
import sys

ruta = pathlib.Path(sys.argv[1]).resolve()
con = sqlite3.connect(ruta.as_uri() + "?mode=ro", uri=True)
q = lambda s: con.execute(s).fetchall()
tablas = [t for (t,) in q("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
columnas_task = [c[1] for c in q("PRAGMA table_info(base_task)")]
info = {
    "archivo": str(ruta),
    "integrity_check": q("PRAGMA integrity_check")[0][0],
    "foreign_key_check": q("PRAGMA foreign_key_check"),
    "migraciones_base": [n for (n,) in q("SELECT name FROM django_migrations WHERE app='base' ORDER BY id")],
    "columnas_base_task": columnas_task,
    "filas": {t: q(f'SELECT COUNT(*) FROM "{t}"')[0][0] for t in tablas},
}
if "created_by_id" in columnas_task:
    info["tareas_created_by_distinto_de_user"] = q(
        "SELECT COUNT(*) FROM base_task WHERE user_id IS NOT NULL AND created_by_id IS NOT user_id")[0][0]
print(json.dumps(info, indent=1, ensure_ascii=False))
