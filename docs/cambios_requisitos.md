# Registro de cambios de requisitos

## Etapa 5 – Asignación de tareas (aprobado el 9/11/2026)

Antes: `Task.user` era a la vez dueño y creador, con `on_delete=CASCADE`.
Ahora: `created_by` (creador) y `user` (asignado), ambos FK nullables con `SET_NULL`.

| ID | Decisión | Impacto en pruebas existentes |
|---|---|---|
| C1 | `SET_NULL` en `created_by` y `user`. Al eliminar un usuario se borran solo las tareas vinculadas a él que quedan sin creador ni asignado. | `test_cascade_al_borrar_usuario` pasa sin cambios: la tarea de alice (creada y asignada por ella) queda huérfana y se elimina. |
| C2 | El modelo no deduce `created_by`. Se actualizó el fixture `tarea_a` en `tests/conftest.py` con `created_by=user_a`. | Solo cambia el fixture; ninguna aserción. El resto de pruebas crean tareas con `user=` sin `created_by`, que son tareas *asignadas* a alice; siguen siendo visibles para ella como asignada, por lo que no requieren ajuste. |
| C3 | El creador puede reasignar la tarea al editarla. El asignado solo cambia `complete`. | `test_no_puede_reasignar_tarea_a_otro_usuario` queda obsoleta por el nuevo requisito y se actualizará en la etapa 5.2 (cuando se cambien las vistas), con autorización explícita. |
| C4 | Administrador = `is_staff` o `is_superuser`; ve todas las tareas en la lista principal. | Se implementa en la etapa 5.2. |
