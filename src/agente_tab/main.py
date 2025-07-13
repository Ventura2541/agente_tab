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
    customer_infoname = 'IMPERIAL S.A.'
    
    # Define the SQL template with named placeholders (e.g., :param_name)
    sql_template = "SELECT p.codigo, p.descripcion, p.marca, (p.entradas - p.salidas - p.reserva) AS stock, pi.imagen1, CASE c.tipo WHEN 'A4' THEN pcp.precio_A4 WHEN 'A5' THEN pcp.precio_A5 WHEN 'A6' THEN pcp.precio_A6 WHEN 'C1' THEN pcp.precio_C1 WHEN 'D1' THEN pcp.precio_D1 WHEN 'D2' THEN pcp.precio_D2 WHEN 'F1' THEN pcp.precio_F1 WHEN 'G1' THEN pcp.precio_G1 WHEN 'G2' THEN pcp.precio_G2 WHEN 'G3' THEN pcp.precio_G3 WHEN 'G4' THEN pcp.precio_G4 WHEN 'H1' THEN pcp.precio_H1 WHEN 'H2' THEN pcp.precio_H2 WHEN 'I1' THEN pcp.precio_I1 WHEN 'I2' THEN pcp.precio_I2 WHEN 'J1' THEN pcp.precio_J1 WHEN 'J2' THEN pcp.precio_J2 WHEN 'J3' THEN pcp.precio_J3 WHEN 'P1' THEN pcp.precio_P1 WHEN 'P2' THEN pcp.precio_P2 WHEN 'Q2' THEN pcp.precio_Q2 WHEN 'Z1' THEN pcp.precio_Z1 WHEN 'Z2' THEN pcp.precio_Z2 WHEN 'Z3' THEN pcp.precio_Z3 WHEN 'Z4' THEN pcp.precio_Z4 ELSE NULL END AS precio_cliente FROM productos p JOIN productos_cpp pcp ON p.codigo_laudus = pcp.codigo_laudus JOIN familias f ON p.familia = f.id CROSS JOIN (SELECT tipo FROM clientes WHERE razon_social LIKE CONCAT('%', :cliente, '%') LIMIT 1) c LEFT JOIN productos_imagenes pi ON p.codigo = pi.codigo WHERE f.descripcion = :familia AND (p.entradas - p.salidas - p.reserva) > 0 AND p.estado = 'ACTIVO' ORDER BY p.ranking ASC LIMIT 10;"
    
    # Define the parameter values as a dictionary
    parameter_values = {
        'cliente': 'IMPERIAL S.A.',
        'familia': 'Ampolletas'
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