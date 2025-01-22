**Plan Atómico para el Crew de Agentes de TAB**

Este documento describe paso a paso cómo diseñar, implementar y probar un crew de agentes que asista al equipo de vendedores de TAB en la generación de propuestas comerciales.

**Fase 1: Definir Roles y Objetivos de Cada Agente**  
**Customer Analyst 1**

	•	**Objetivo**: Consultar la base de datos para obtener los 20 productos más vendidos para un cliente, incluyendo detalles como producto, descripción\_producto, familia, neto, cantidad, año, mes, stock, marca, imagen1 y código\_laudus.

	•	**Herramienta principal**: NL2SQLTool.

	•	**Salida esperada**: Un bloque de consulta SQL formateado en Markdown y sus resultados en formato tabular.  
**Product Manager**

	•	**Objetivo**: Para los productos sin stock identificados por Customer Analyst 1, buscar productos similares basándose en descripción, familia y marca.

	•	**Herramienta principal**: MySQLSearchTool (o similar).

	•	**Salida esperada**: Lista de productos similares para aquellos sin stock.  
**Revenue Manager**

	•	**Objetivo**: Determinar la lista de precios asignada al cliente desde la tabla clientes y luego consultar en productos los precios correspondientes para la lista de productos.

	•	**Herramienta principal**: NL2SQLTool.

	•	**Salida esperada**: Información de precios para los productos recomendados.  
**Offer Composer**

	•	**Objetivo**: Generar un documento de cotización final en formato PDF utilizando la información proporcionada por los agentes anteriores.

	•	**Herramienta potencial**: Biblioteca de generación de PDF (e.g., python-docx, ReportLab).

	•	**Salida esperada**: Documento PDF estructurado con encabezado, tabla de productos (Imagen, Código, Descripción, Marca, Cantidad, Precio, Total), subtotales y total con IVA.

**Fase 2: Diseñar Tareas en tasks.yaml**  
**Pasos para cada tarea:**

	1\.	**Crear una entrada en** tasks.yaml **para cada tarea**:

	•	Definir el nombre de la tarea (por ejemplo, sql\_query\_task).

	•	Especificar description clara sobre lo que debe hacer la tarea.

	•	Definir expected\_output con el formato esperado (por ejemplo, un bloque de consulta SQL en Markdown).

	•	Configurar tool\_input para la herramienta asociada, usando la clave "sql\_query" y una referencia a la variable de input correspondiente.

	2\.	**Asegurarse de evitar ambigüedades** en las descripciones para que los agentes no alteren las consultas esperadas.

**Fase 3: Configuración en crew.py**  
**Pasos para configurar agentes y tareas:**

	1\.	**Inicializar herramientas**:

	•	Crear instancias de NL2SQLTool y otras herramientas necesarias.

	•	Configurar conexiones a la base de datos y especificar tablas y columnas relevantes.

	2\.	**Cargar configuraciones**:

	•	Cargar configuraciones de agents.yaml y tasks.yaml.

	3\.	**Crear instancias de Agentes**:

	•	Para cada agente (e.g., customer\_analyst\_1), crea una instancia usando su configuración y asigna las herramientas correspondientes.

	4\.	**Crear instancias de Tareas**:

	•	Para cada tarea definida en tasks.yaml, crear una instancia de Task, asignándola al agente correspondiente.

	5\.	**Construir la Crew**:

	•	Definir un método decorado con @crew que retorne una instancia de Crew con los agentes, tareas y proceso secuencial definidos.

**Fase 4: Implementación del Flujo de Trabajo**  
**Para cada agente/tarea:**  
**Customer Analyst 1 \-** sql\_query\_task

	•	Utiliza NL2SQLTool para ejecutar la consulta SQL que obtiene los 20 productos más vendidos.

	•	Almacena el resultado en una variable como {lista\_productos} para uso posterior.  
**Product Manager \-** recommend\_similar\_products\_task

	•	Recibe {lista\_productos} y filtra productos sin stock.

	•	Para cada producto sin stock, utiliza MySQLSearchTool para buscar productos similares basados en familia, descripción y marca.

	•	Almacena los resultados similares en {productos\_similares}.  
**Revenue Manager \-** select\_pricing\_task

	•	Consulta la lista de precios asignada al cliente desde la tabla clientes.

	•	Utiliza esa lista para buscar precios de los productos en la tabla productos.

	•	Guarda la información de precios en {precios\_productos}.  
**Offer Composer \-** build\_offer\_document\_task

	•	Recibe como contexto la información de {lista\_productos}, {productos\_similares} y {precios\_productos}.

	•	Utiliza una herramienta de generación de PDF para crear un documento de cotización:

	•	Incluye encabezado con logo, número de cotización, nombre del cliente, fecha, vigencia, vendedor.

	•	Crea una tabla con columnas: Imagen, Código, Descripción, Marca, Cantidad, Precio, Total.

	•	Calcula subtotales y total con IVA.

	•	Guarda o envía el documento final.

**Fase 5: Pruebas y Ajustes**  
**Pasos para probar y ajustar el crew:**

	1\.	**Probar cada tarea individualmente**:

	•	Ejecutar solo sql\_query\_task y verificar que la consulta se ejecute y retorne datos correctos.

	•	Agregar progresivamente recommend\_similar\_products\_task, select\_pricing\_task y build\_offer\_document\_task, verificando la salida en cada paso.

	2\.	**Verificar el encadenamiento**:

	•	Asegurarse de que la salida de una tarea se pase correctamente a la siguiente mediante contextos y variables compartidas.

	3\.	**Implementar y probar la generación del PDF**:

	•	Configurar la librería elegida para generación de PDF.

	•	Probar que build\_offer\_document\_task genere correctamente un documento de cotización con encabezado, tabla de productos y totales.

	4\.	**Manejo de errores y casos especiales**:

	•	Simular situaciones como falta de stock o ausencia de datos.

	•	Verificar que el flujo maneje condiciones no ideales (por ejemplo, generando consultas alternativas o mensajes adecuados).

	5\.	**Documentar el código y el flujo**:

	•	Comentar y documentar cada paso para facilitar el mantenimiento y la escalabilidad.

	•	Registrar las dependencias y configuración para futuras referencias.  
