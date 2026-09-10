# Añadir soporte para CANTOS

## Descripción del objetivo

El usuario quiere que el bot gestione un inventario doble: **Melaminas** y **Cantos**. 
Para los Cantos, se registrarán en la hoja "CANTOS" con su propio identificador, nombre, metros lineales (ML), grosor (GRS), ancho, foto de referencia, estado y fecha. La particularidad de los cantos es que los metros lineales (ML) no se ingresan directamente, sino que se calculan matemáticamente pidiendo al operario el diámetro exterior y el diámetro interior del rollo, usando la fórmula de área transversal.

## Flujo Conversacional Definido

1. **Menú Principal**:
   - `[ 🪵 Melamina ]`
   - `[ 🎞️ Canto ]`
2. **Submenú de Acción** (para cualquiera de las dos opciones):
   - `[ ➕ Agregar ]`
   - `[ ➖ Dar de baja ]`
3. **Flujo Canto -> Agregar**:
   - Pide **Nombre / Color** (ej. Blanco, Café).
   - Pide **Grosor** (ej. 0.8mm). Teclado: `[0.4mm, 0.8mm, 1mm, Otro...]`
   - Pide **Ancho** (ej. 22mm). Teclado: `[22mm, 44mm, Otro...]`
   - Pide **Diámetro Exterior** en milímetros.
   - Pide **Diámetro Interior** en milímetros.
   - *Cálculo interno*: `ML = (π * ((De/2)² - (Di/2)²)) / grosor / 1000`.
   - Pide **Foto** del rollo.
   - Guarda en Google Sheets con prefijo `C-` (ej. `C-5TG`).

4. **Flujo Canto -> Dar de baja**:
   - Pide el ID del rollo usado (ej. `C-5TG`).
   - Busca en la hoja "CANTOS" y cambia su estado a "USADO" (o 0 ML dependiendo de cómo se defina dar de baja, por ahora cambiaremos el estado a "USADO" o restaremos, asumiremos estado "USADO").

## Cambios a nivel código

### src/db_sheets.py
- Refactorizar `get_sheet()` para aceptar un parámetro de nombre de hoja (ej. `def get_sheet(sheet_name="Melaminas"):`).
- Adaptar `use_piece(piece_id, sheet_name)` para que busque en la hoja correspondiente.
- Nueva función `add_canto(nombre, grosor, ancho, diametro_ext, diametro_int, foto_url)`:
  - Genera ID con prefijo `C-` (ej. `C-5TG`).
  - Calcula los `ML` (Metros Lineales) con la fórmula extraída del HTML.
  - Inserta la fila en la hoja "CANTOS": `[ID, NOMBRE, ML, GRS, ANCHO, FOTO REF, ESTADO, DATE]`.

### src/bot_core.py
- Reestructurar los teclados iniciales y estados (`CHOOSING_MATERIAL`, `CHOOSING_ACTION_MELAMINA`, `CHOOSING_ACTION_CANTO`, etc.).
- Agregar manejadores para los nuevos pasos de Cantos: `NOMBRE_CANTO`, `GROSOR_CANTO`, `ANCHO_CANTO`, `DIAMETRO_EXT`, `DIAMETRO_INT`, `FOTO_CANTO`.
- Modificar el flujo de dar de baja para preguntar de qué material se está dando de baja (o detectarlo inteligentemente por el prefijo `M-` o `C-`).

## Reglas Operativas
- **No desplegar a la nube todavía**: Todo el desarrollo y pruebas se harán localmente, ya que la versión actual en la nube de Melaminas está funcionando en producción.
