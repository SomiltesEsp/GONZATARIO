# Añadir soporte para CANTOS

## Descripción del objetivo

El usuario quiere que el bot registre el inventario de cantos (bordeado) en **metros lineales**, junto con color, nombre, cantidad y ancho (22 mm, 44 mm y opcionalmente 30 mm). Se utilizará una fórmula para calcular los metros lineales a partir de los datos ingresados. Esto requiere ampliar la integración con Google Sheets, agregar una nueva hoja llamada "CANTOS" y actualizar el flujo conversacional para que el operador elija el tipo de inventario (Melaminas vs CANTOS) y proporcione los campos correspondientes.

## Revisión requerida por el usuario

> [!IMPORTANTE]
> *Necesitamos confirmar la fórmula exacta para calcular los metros lineales.*
> *Definir el prefijo de ID para los registros de CANTOS (por ejemplo, `C-`).*
> *Confirmar si el bot debe permitir editar/eliminar filas de CANTOS.*

## Preguntas abiertas

- **Fórmula**: ¿Cómo se deben calcular los metros lineales? (p. ej., `metros_totales = cantidad * largo_de_cada_pieza` o `metros_totales = cantidad * ancho`). Proporcione la expresión exacta.
- **Esquema de ID**: ¿Los IDs de CANTOS deben tener un prefijo distinto (`C-XXX`) para diferenciarlos de los IDs de Melaminas (`M-XXX`)?
- **Opciones de ancho**: ¿Los anchos están limitados a 22 mm, 44 mm y 30 mm? ¿El bot debe presentar estas opciones como un teclado?
- **Columnas adicionales**: ¿La hoja "CANTOS" necesita una columna "Nombre" además de "Color"? En caso afirmativo, indique el orden de columnas.
- **Entrada de cantidad**: ¿El bot debe solicitar una cantidad (número de piezas) y luego calcular automáticamente los metros lineales, o el operador ingresará directamente los metros lineales totales?
- **Seguridad**: La whitelist basada en contraseña está pendiente; confirme si también debe proteger las operaciones de CANTOS.

## Cambios propuestos

---
### src/db_sheets.py

- **[MODIFICAR] src/db_sheets.py**
  - Añadir una función auxiliar `def get_worksheet(name: str):` que devuelva `client.open_by_key(SPREADSHEET_ID).worksheet(name)`.
  - Refactorizar `get_sheet()` para que llame a `get_worksheet("Melaminas")` (manteniendo compatibilidad retroactiva).
  - Implementar `def add_canto(nombre: str, color: str, ancho_mm: int, cantidad: int, largo_m: float, foto_url: str):` que:
    1. Genere un ID con prefijo `C-` (ej., `C-XYZ`).
    2. Calcule `total_metros = cantidad * largo_m` (o use la fórmula que el usuario indique).
    3. Construya una fila según el orden de columnas de la hoja "CANTOS": `ID, Nombre, Color, Ancho (mm), Cantidad, Largo (m), Total metros, Foto Ref, Estado, Date`.
    4. Añada la fila a la hoja "CANTOS".
  - Añadir una función de solo lectura `list_cantos()` (opcional) para futuros reportes.

---
### src/bot_core.py

- **[MODIFICAR] src/bot_core.py**
  - Al iniciar la conversación, presentar un teclado: `[Melamina] [Canto]`.
  - Branchar el manejador según la selección:
    - **Melamina** – conservar flujo existente.
    - **Canto** – nuevo flujo que solicite:
      1. Nombre (descripción opcional).
      2. Color.
      3. Ancho (mostrar teclado con "22 mm", "44 mm", "30 mm").
      4. Cantidad (número de tiras).
      5. Largo (m) – longitud de cada tira.
      6. Foto (opcional – reutilizar la lógica de carga de foto existente).
  - Calcular `total_metros` usando la fórmula acordada y pasarla a `add_canto`.
  - Devolver el ID generado (p. ej., `C-AB3`) al operador.

---
### Hoja de Google (paso manual)

- Asegurarse de que exista una hoja de cálculo llamada **CANTOS** con la fila de encabezado que coincida con el orden usado en `add_canto`.
- Ejemplo de encabezado: `ID | Nombre | Color | Ancho (mm) | Cantidad | Largo (m) | Total metros | Foto Ref | Estado | Date`.

---
### Pruebas

- **[NUEVO] tests/test_db_sheets.py** – agregar pruebas unitarias para `add_canto` y `get_worksheet`.
- Actualizar las pruebas existentes para que usen la hoja "Melaminas" por defecto.

---
### Documentación

- Actualizar **HANDOVER.md** con una nueva sección “Soporte CANTOS”.
- Añadir una breve descripción de la fórmula de cálculo y de las nuevas columnas.

## Plan de verificación

### Pruebas automatizadas
- Ejecutar la suite de pruebas existente (`pytest -q`).
- Las pruebas nuevas para `add_canto` deben verificar:
  - Prefijo correcto del ID.
  - Longitud y orden correctos de la fila.
  - Cálculo preciso de `total_metros`.

### Verificación manual
- Desplegar el contenedor actualizado en Cloud Run (usando `deploy.ps1`).
- Interactuar con el bot en Telegram:
  1. Elegir **Canto**.
  2. Proveer datos de ejemplo (p. ej., "Rojo", "22 mm", cantidad 10, largo 2.5 m).
  3. Confirmar que el bot devuelve un ID y que una nueva fila aparece en la hoja "CANTOS" con los metros calculados correctamente.
- Verificar que el flujo de Melamina sigue funcionando sin cambios.

---
**Próximo paso**: Esperar la confirmación del usuario sobre las preguntas abiertas (fórmula, prefijo de ID, orden de columnas, etc.) antes de proceder con la implementación.

