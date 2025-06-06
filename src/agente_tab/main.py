#!/usr/bin/env python
import sys
import warnings
import os

from agente_tab.crew import AgenteTop20MYSQLV2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

print("🔵 [MAIN] Current working directory:", os.getcwd())
print("🔵 [MAIN] Script file path:", os.path.abspath(__file__))

def run():
    print("🔵 [MAIN] Ejecutando run()...")
    customer_infoname = 'EQUIP. AUTOMOTRIZ Y OBRAS DE ING. CAMONT LIMITADA'
    
    # Define the SQL template with named placeholders (e.g., :param_name)
    sql_template = """
        SELECT 
            vd.producto, 
            vd.descripcion_producto AS descripcion,
            vd.familia, 
            SUM(vd.neto) AS total_ventas_netas,
            SUM(vd.cantidad) AS total_unidades_vendidas,
            COUNT(DISTINCT CONCAT(vd.anno, vd.mes)) AS meses_con_ventas,
            ROUND(SUM(vd.cantidad) / COUNT(DISTINCT CONCAT(vd.anno, vd.mes)), 2) AS promedio_mensual_unidades,
            p.stock,
            p.marca,
            p.imagen1,
            CASE c.tipo
              WHEN 'A4' THEN p.precio_A4 WHEN 'A5' THEN p.precio_A5
              WHEN 'A6' THEN p.precio_A6 WHEN 'C1' THEN p.precio_C1
              WHEN 'D1' THEN p.precio_D1 WHEN 'D2' THEN p.precio_D2
              WHEN 'F1' THEN p.precio_F1 WHEN 'G1' THEN p.precio_G1
              WHEN 'G2' THEN p.precio_G2 WHEN 'G3' THEN p.precio_G3
              WHEN 'G4' THEN p.precio_G4 WHEN 'H1' THEN p.precio_H1
              WHEN 'H2' THEN p.precio_H2 WHEN 'I1' THEN p.precio_I1
              WHEN 'I2' THEN p.precio_I2 WHEN 'J1' THEN p.precio_J1
              WHEN 'J2' THEN p.precio_J2 WHEN 'J3' THEN p.precio_J3
              WHEN 'P1' THEN p.precio_P1 WHEN 'Q2' THEN p.precio_Q2
              WHEN 'Z1' THEN p.precio_Z1 WHEN 'Z2' THEN p.precio_Z2
              WHEN 'Z3' THEN p.precio_Z3 WHEN 'Z4' THEN p.precio_Z4
              WHEN 'oferta_1' THEN p.oferta_1 WHEN 'oferta_2' THEN p.oferta_2
              ELSE NULL
            END AS precio_final
        FROM ventas_detalle vd
        JOIN productos p ON vd.producto = p.codigo_laudus
        JOIN (
            SELECT producto
            FROM ventas_detalle
            WHERE TRIM(cliente) LIKE :cliente_like_1  -- Named Placeholder 1
            GROUP BY producto, descripcion_producto, familia
            ORDER BY SUM(neto) DESC
            LIMIT 20
        ) top20 ON vd.producto = top20.producto
        JOIN clientes c ON TRIM(c.nombre) LIKE :cliente_like_2  -- Named Placeholder 2
        WHERE TRIM(vd.cliente) LIKE :cliente_like_3  -- Named Placeholder 3
        GROUP BY vd.producto, descripcion, vd.familia, p.stock, p.marca, p.imagen1, c.tipo
        ORDER BY total_ventas_netas DESC; 
    """
    
    # Define the parameter values as a dictionary mapping names to values (including wildcards)
    parameter_values = {
        'cliente_like_1': f'%{customer_infoname}%', # Value for Placeholder 1
        'cliente_like_2': f'%{customer_infoname}%', # Value for Placeholder 2
        'cliente_like_3': f'%{customer_infoname}%'  # Value for Placeholder 3
    }
    
    # Construct the inputs dictionary
    inputs = {
        'customer_infoname': customer_infoname,
        'sql_template': sql_template,
        'parameter_values': parameter_values
    }

    agente = AgenteTop20MYSQLV2()
    crew_instance = agente.crew()
    print("🔵 [MAIN] Ejecutando kickoff...")
    # Log the dictionary structure, showing keys and types/snippets of values
    print(f"🔍 Inputs enviados a kickoff: {{ \
        'customer_infoname': type {type(inputs['customer_infoname'])}, \
        'sql_template': type {type(inputs['sql_template'])}, snippet: '{inputs['sql_template'][:100]}...', \
        'parameter_values': type {type(inputs['parameter_values'])}, value: {inputs['parameter_values']} \
    }}")
    
    # Execute the crew
    result = crew_instance.kickoff(inputs=inputs)

    print("🟢 [MAIN] La Crew ha terminado su ejecución.")
    print(f"🏁 Resultado final: {result}") # Print the result returned by kickoff

def train():
    print("🔵 [MAIN] Ejecutando train()...")
    inputs = {"topic": "Advanced SQL queries"}
    try:
        AgenteTop20MYSQLV2().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"❌ [MAIN] Error al entrenar la Crew: {e}")

def replay():
    print("🔵 [MAIN] Ejecutando replay()...")
    try:
        AgenteTop20MYSQLV2().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"❌ [MAIN] Error al reproducir la Crew: {e}")

def test():
    print("🔵 [MAIN] Ejecutando test()...")
    inputs = {"topic": "Advanced SQL queries"}
    try:
        AgenteTop20MYSQLV2().crew().test(n_iterations=int(sys.argv[2]), openai_model_name=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"❌ [MAIN] Error durante la prueba de la Crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ [MAIN] Se requiere un comando (run, train, replay, test).")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"❌ [MAIN] Comando desconocido: {command}")