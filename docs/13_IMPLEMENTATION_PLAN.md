# Plan de implementación incremental

La fase terminada por esta entrega es **F0 · revisión y diseño**. Codex comienza por **F1**. Los nombres de fase siguientes son los de esta revisión. Respecto de V1.0 §12, persistencia y uso manual se adelantan a F2, el objetivo base pasa a F3 y la reparación a F4. El candidato al piloto se obtiene en F6. Cada incremento termina en una demostración o un resultado reproducible.

| Fase | Depende de | Incremento comprobable y demo de salida | Evidencia exigida |
|---|---|---|---|
| F1 · dominio y tiempo | F0 | Construir una semana ficticia en memoria; leer jornada partida/nocturna, minutos y presencia. Completar B01–B03. | Entorno recreado desde las instrucciones; tests unitarios de límites, bordes y vigencia. Ejecutar sin Qt ni solver. |
| F2 · circuito manual persistente | F1 | Crear personas y reglas sintéticas desde el caso de uso, guardar un borrador, validarlo, confirmar, reabrir y recuperar el vigente. Una vista semanal mínima da acceso al recorrido; se puede usar un adaptador simulado de reloj. Completar B04–B07. | Comparación de revisión antes/después de cancelación, fallo y reinicio. Ensayo breve de Qt + zona horaria en Windows para detectar problemas de empaquetado temprano; registrar entorno o dejarlo pendiente. |
| F3 · factibilidad | F1 y circuito de confirmación F2 | Integrar esquema, captura de insumos, validador independiente y un worker. Devolver una propuesta válida o diagnóstico concreto. B08–B10. | Contrato de ida/vuelta con un motor simulado y otro real. Comparar con enumeración en casos pequeños. Simular caída y entrada cambiada. |
| F4 · equidad, alternativas y reparación | F3 y revisiones F2 | Ver en qué difieren las propuestas. En una semana ya publicada, registrar un imprevisto y confirmar únicamente el cambio autorizado. B11–B13. | Tabla antes/después reproducible, cupos históricos sin duplicar, pruebas de perfil, diversidad y reparación; tiempos medidos en escenarios descritos. |
| F5 · flujos completos e intercambio | F2; F4 para generación completa | Configurar desde la interfaz, revisar semana/día/mes, importar parámetros y restaurar una copia en base temporal. Exportar una semana legible en PDF y PNG. B14–B16. | Ejemplos de salida sintéticos y prueba de restauración en entorno aislado. Recorrido con teclado, escala de texto y revisión temprana del encargado. |
| F6 · instalación y piloto | F5; insumos del local para uso real | Instalar en Windows limpio, trabajar desconectado, probar actualización/recuperación y ensayar con el encargado en paralelo al proceso habitual. B17–B18. | Acta de versión, equipo, instalación y pruebas efectivas; perfil laboral y condiciones particulares verificados para el piloto real; comprobación del último respaldo. |

### Primer incremento de F1

1. Inspeccionar Git y leer las decisiones. Preparar `pyproject.toml`, intérprete soportado y lock de dependencias con hashes para el entorno elegido. Documentar comandos efectivamente ejecutados en Windows o identificar el sistema usado.
2. Implementar identidad, fecha operativa, intervalo real semiabierto, bloque y jornada. Convertir hora civil usando zona IANA y precisión de minuto. Mantener el núcleo puro y usar fixtures temporales independientes de la fecha de hoy.
3. Ejecutar T01–T05, T07 y casos adicionales de T27 en el alcance disponible. Verificar 360 + 360 min, 17 h de descanso y que el hueco en un turno partido no aporte cobertura.
4. Agregar dominios de patrón, disponibilidad, versiones sin solape ambiguo y reglas de franco fijo/adicional. Probar el núcleo de T06, T08–T10. Reunir las pruebas de F1 en un cierre de fase. Los tests end-to-end de esos mismos requisitos se completan al existir los demás módulos.

**Corte de entrega.** En F1 se detiene el desarrollo tras probar el núcleo y actualizar instrucciones. Una futura ampliación debe citar el requisito o la decisión que cambia. Si la revisión del convenio exige una clase de regla adicional, escribir su ejemplo y su oráculo antes de habilitarla en un perfil real. Las tareas siguientes figuran listas para priorizar en [el backlog](18_BACKLOG.md).

### Registro que debe acompañar a cada corte

Identificar commit de partida y final, plataforma y versión de intérprete, datos sintéticos, comandos, número de pruebas aprobadas/fallidas/omitidas, vínculo a la evidencia y fallos pendientes. Una prueba omitida sigue pendiente. Registrar también qué puede hacer ya el encargado, qué solo se probó con dobles y el siguiente incremento. No incluir una copia real de la base en los informes.
