# Guion general del video

**Duración máxima: 30:00 (estricta).** Objetivo: ~28:00 para tener margen.

## Estructura y tiempos

| # | Bloque | Archivo | Objetivo | Acumulado |
|---|---|---|---|---|
| 0 | Identificación + caso | `01_intro.md` | 1:00 | 1:00 |
| 1 | HDFS | `02_hdfs.md` | 3:00 | 4:00 |
| 2 | Pig | `03_pig.md` | 6:00 | 10:00 |
| 3 | Hive | `04_hive.md` | 7:00 | 17:00 |
| 4 | HBase | `05_hbase.md` | 5:00 | 22:00 |
| 5 | Mahout | `06_mahout.md` | 5:00 | 27:00 |
| 6 | Cierre | `07_cierre.md` | 2:30 | 29:30 |

El enunciado sugiere 6 min para Mahout y 3 para el cierre; se recortó 1 min de Mahout y 30 s del cierre para la intro, que es obligatoria (nombre, sección, título).

## Formato de cada archivo de etapa

Cada `.md` de etapa tiene las mismas secciones:

1. **Tarjeta de transición** — texto que aparece en pantalla 3–5 s al iniciar la etapa.
2. **Narración** — texto para leer con tu propia voz (en bloques `>`). Está separado por pasos para que leas mientras ejecutas.
3. **Comandos / scripts** — lo que se ejecuta en terminal. Los scripts indican el archivo donde guardarlos.
4. **Qué debe verse** — cifras esperadas para comprobar tu salida real **antes** de narrarla.
5. **Checklist de rúbrica** — qué criterio se cubre.

> Las cifras esperadas se calcularon a partir de los CSV entregados. En el video **siempre muestra la salida real de tu terminal**; si una cifra no coincide, revisa `08_problemas_y_verificacion.md` antes de grabar.

## Checklist de grabación

- [ ] Grabar con **OBS Studio** o **SimpleScreenRecorder** (en Zorin: `sudo apt install obs-studio`). **No usar Microsoft Teams.**
- [ ] Resolución ≥ 1280×720, MP4.
- [ ] Terminal con fuente grande: en GNOME Terminal `Ctrl` + `+` hasta ~16 pt. Fondo oscuro, alto contraste.
- [ ] Prompt corto para que se lean los comandos: `export PS1='\u@retail:\W\$ '`.
- [ ] Ocultar contraseñas, tokens y cualquier dato personal (no mostrar `~/.ssh`, `.bashrc` con claves, etc.).
- [ ] Probar el micrófono: voz clara, sin música de fondo encima de la narración.
- [ ] Servicios ya arrancados antes de grabar (puedes mostrar `jps` en el video, no hace falta grabar el arranque).
- [ ] Ensayar cada etapa una vez completa (Pig y Hive tardan; puedes cortar las esperas en edición, **no** las salidas).
- [ ] Limpiar ejecuciones previas para que se vea el flujo desde cero: ver "Reinicio limpio" en `00_preparacion_ambiente.md`.
- [ ] Tener abiertas 2 pestañas de terminal: una para comandos, otra con el editor (`nano`/`gedit`/VS Code) mostrando los scripts.

## Edición permitida

- Se pueden cortar pausas y esperas de jobs MapReduce.
- **No** se puede reemplazar evidencia de ejecución con capturas o diapositivas.
- Las tarjetas de transición son solo títulos; el contenido debe ser la terminal real.
