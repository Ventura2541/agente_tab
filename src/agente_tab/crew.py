from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import NL2SQLTool
import yaml
from pathlib import Path

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

@CrewBase
class AgenteTop20MYSQLV2:
    def __init__(self):
        print("🔵 [CREW] Inicializando AgenteTop20MYSQLV2...")

        # Inicializar herramientas
        self.initialize_tools()

        # Cargar configuración de agentes y tareas
        self.load_configurations()

        # Crear agentes y tareas
        self.create_agents_and_tasks()

    def initialize_tools(self):
        try:
            print("🔵 [CREW] Inicializando herramientas...")        
            self.nl2sql_tool = NL2SQLTool(
                db_uri="mysql+mysqldb://tabparts_ia:Tab123456Parts@201.148.105.157:3306/tabparts_ai",
                tables=["ventas_detalle", "productos", "clientes"],
                columns={
                    "ventas_detalle": ["producto", "descripcion_producto", "familia", "cantidad", "neto", "cliente", "anno", "mes"],
                    "productos": ["codigo_laudus", "descripcion", "familia_descripcion", "marca", "imagen1", "stock"],
                    "clientes": ["nombre", "rut"],
                },
            verbose=True            
            )
            print("✅ [CREW] NL2SQLTool inicializado correctamente.")
        except Exception as e:
            print(f"❌ [CREW]Error al inicializar herramientas: {e}")

    def load_configurations(self):
        try:
            print("🔵 [CREW] Cargando configuraciones...")
            self.agents_config = load_yaml(Path(__file__).parent / 'config' / 'agents.yaml')
            print(f"✅ [CREW] Agentes cargados: {list(self.agents_config.keys())}")

            self.tasks_config = load_yaml(Path(__file__).parent / 'config' / 'tasks.yaml')
            print(f"✅ [CREW] Tareas cargadas: {list(self.tasks_config.keys())}")

        except Exception as e:
            print(f"❌ [CREW]Error al cargar configuraciones: {e}")

    def create_agents_and_tasks(self):
        try:
            print("🔵 [CREW] Creando agentes y tareas...")
            self.customer_analyst_1 = Agent(config=self.agents_config['customer_analyst_1'], tools=[self.nl2sql_tool])
            print(f"✅ Agente creado: {self.customer_analyst_1.role}")

            self.sql_query_task = Task(config=self.tasks_config['sql_query_task'], agent=self.customer_analyst_1)
            print(f"✅ Tarea creada: {self.sql_query_task.description}")

            # Crear el agente revenue_manager
            self.offer_builder = Agent(config=self.agents_config['offer_builder'], tools=[])
            print(f"✅ Agente creado: {self.offer_builder.role}")

            # Crear la tarea para revenue_manager
            self.compose_offer_document_task = Task(config=self.tasks_config['compose_offer_document_task'], agent=self.offer_builder, output_file="offer_document.pdf")
            print(f"✅ Tarea creada: {self.compose_offer_document_task.description}")

        except Exception as e:
            print(f"❌ [CREW]Error al crear agentes y tareas: {e}")

    @crew
    def crew(self) -> Crew:
        print("🔵 [CREW] Construyendo la Crew...")

        print("🟠 Agentes en la Crew:")
        for agent in [self.customer_analyst_1]:
            print(f"   - {agent.role}")
            
        for agent in [self.offer_builder]:
            print(f"   - {agent.role}")

        print("🟠 Tareas en la Crew:")
        for task in [self.sql_query_task]:
            print(f"   - {task.description}")
        
        for task in [self.compose_offer_document_task]:
            print(f"   - {task.description}")
            
        print("🟠 Proceso en la Crew:")
        print(f"   - {Process.sequential}")
        
        print("🟢 [CREW] Finalizando construcción de la Crew...")

        return Crew(
            agents=[self.customer_analyst_1, self.offer_builder],
            tasks=[self.sql_query_task, self.compose_offer_document_task],
            process=Process.sequential,
            verbose=True,
            )

if __name__ == "__main__":
    agente = AgenteTop20MYSQLV2()
    crew_instance = agente.crew()
    print(crew_instance)
    
    # Ejecutar kickoff si se ejecuta directamente
    print("🔵 Ejecutando kickoff...")
    crew_instance.kickoff(inputs={'customer_infoname': 'EQUIP AUTOMOTRIZ Y OBRAS DE ING CAMONT LIMITADA'})
    print("🟢 La Crew ha terminado su ejecución.")