# AgenteTab Crew

Bienvenido al proyecto AgenteTab Crew, impulsado por [crewAI](https://crewai.com). Este proyecto demuestra un sistema de IA multiagente diseñado para interactuar con una base de datos utilizando consultas SQL parametrizadas y seguras.

## Funcionalidad Principal

El objetivo principal de este Crew es analizar los datos de ventas de clientes y, potencialmente, generar ofertas personalizadas. Logra esto a través de un proceso con dos agentes:

1.  **Analista de Ventas SQL Parametrizado (`customer_analyst_1`):** Este agente recibe una *plantilla* de consulta SQL con marcadores de posición nombrados (ej., `:param_name`) y un diccionario que contiene los valores para estos marcadores. Su tarea es utilizar la herramienta especializada `CustomNL2SQLTool` para ejecutar esta consulta de forma segura contra la base de datos.
2.  **Compositor de Ofertas (`offer_builder`):** Este agente toma los datos estructurados devueltos por la tarea del primer agente y los utiliza para componer un documento (ej., una cotización en PDF) basado en la información recuperada, centrándose en los productos disponibles.

## Ejecución de SQL Parametrizado

Una característica clave de este proyecto es el manejo seguro de las interacciones con la base de datos. En lugar de incrustar datos del usuario directamente en cadenas SQL, utiliza:

*   **Plantillas SQL:** Consultas SQL predefinidas almacenadas o pasadas con marcadores de posición nombrados (ej., `SELECT * FROM orders WHERE customer_id = :cust_id`).
*   **Diccionarios de Parámetros:** Los valores de los datos se pasan por separado en un diccionario (ej., `{"cust_id": 123}`).
*   **`CustomNL2SQLTool`:** Una herramienta personalizada construida usando `crewai.tools.BaseTool` y SQLAlchemy. Esta herramienta acepta la plantilla y el diccionario de parámetros, asegurando que los valores sean sustituidos de forma segura por el controlador de la base de datos, previniendo vulnerabilidades de inyección SQL.

## Instalación

Asegúrate de tener Python >=3.10 <=3.13 instalado en tu sistema. Este proyecto utiliza [UV](https://docs.astral.sh/uv/) para la gestión de dependencias.

1.  Instala uv: `pip install uv`
2.  Navega al directorio del proyecto e instala las dependencias: `crewai install` (o `uv pip install -r requirements.txt`)

## Configuración y Personalización

1.  **Variables de Entorno:** Añade la URI de tu base de datos y cualquier clave de API necesaria (como `OPENAI_API_KEY`) al archivo `.env`.
    *   Modifica la `db_uri` dentro de `src/agente_tab/tools/custom_nl2sql.py` si no utilizas variables de entorno.
2.  **Agentes (`src/agente_tab/config/agents.yaml`):** Define los roles, objetivos e historias de fondo de los agentes. Observa cómo el objetivo de `customer_analyst_1` se centra en *usar* la herramienta SQL con los inputs proporcionados.
3.  **Tareas (`src/agente_tab/config/tasks.yaml`):** Define la secuencia de tareas. Observa cómo `sql_query_task` espera `{sql_template}` y `{parameter_values}` (como diccionario) y especifica estos como inputs para la herramienta.
4.  **Lógica del Crew (`src/agente_tab/crew.py`):** Instancia los agentes, las tareas y la herramienta personalizada. Define la estructura general del crew y el proceso (ej., secuencial).
5.  **Punto de Entrada (`src/agente_tab/main.py`):** Define la `sql_template` específica y el diccionario `parameter_values` utilizados para una ejecución (`run`). Aquí es donde integrarías la lógica para recibir estos inputs dinámicamente (ej., desde una solicitud de API).

## Ejecutando el Proyecto

Para ejecutar el proceso definido del crew (actualmente recuperando los 20 productos principales para un cliente específico e intentando construir una oferta), ejecuta desde la raíz del proyecto:

```bash
crewai run
```

Este comando inicializa el AgenteTab Crew, utilizando las configuraciones en `main.py` y los archivos YAML para ejecutar las tareas definidas.

## Comprendiendo tu Crew

El AgenteTab Crew demuestra cómo los agentes especializados pueden colaborar:

*   Un agente se enfoca en la recuperación segura de datos utilizando herramientas específicas e inputs estructurados (plantilla + parámetros).
*   Otro agente procesa los datos recuperados con un propósito diferente (generación de documentos).

Esta separación de responsabilidades, combinada con prácticas seguras como consultas parametrizadas manejadas por herramientas personalizadas, forma la base de este proyecto.

## Soporte

Para soporte, preguntas o comentarios sobre AgenteTab Crew o crewAI.
- Visita nuestra [documentación](https://docs.crewai.com)
- Contáctanos a través de nuestro [repositorio de GitHub](https://github.com/joaomdmoura/crewai)
- [Únete a nuestro Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chatea con nuestra documentación](https://chatg.pt/DWjSBZn)

Creemos maravillas juntos con el poder y la simplicidad de crewAI.
