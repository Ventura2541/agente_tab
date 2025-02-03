from typing import Any, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class CustomNL2SQLToolInput(BaseModel):
    sql_query: str = Field(
        title="SQL Query",
        description="The SQL query to execute.",
    )
    customer_infoname: str = Field(
        title="Customer Info Name",
        description="The name of the customer to analyze.",
    )


class CustomNL2SQLTool(BaseTool):
    name: str = "CustomNL2SQLTool"
    description: str = """
    Ejecuta consultas SQL para analizar datos de clientes.
    
    Inputs requeridos:
    - sql_query: La consulta SQL a ejecutar (texto)
    - customer_infoname: El nombre del cliente a analizar (texto)
    
    Ejemplos de uso:

    1. Consulta básica de ventas:
    {
        "sql_query": "SELECT * FROM ventas_detalle WHERE cliente LIKE '%CUSTOMER%'",
        "customer_infoname": "NOMBRE DEL CLIENTE"
    }

    2. Consulta de productos top:
    {
        "sql_query": "SELECT producto, SUM(cantidad) as total FROM ventas_detalle WHERE cliente LIKE '%CUSTOMER%' GROUP BY producto ORDER BY total DESC LIMIT 10",
        "customer_infoname": "EQUIP. AUTOMOTRIZ Y OBRAS DE ING. CAMONT LIMITADA"
    }

    3. Consulta de stock y precios:
    {
        "sql_query": "SELECT p.codigo_laudus, p.stock, p.precio_A4 FROM productos p JOIN ventas_detalle v ON p.codigo_laudus = v.producto WHERE v.cliente LIKE '%CUSTOMER%'",
        "customer_infoname": "DISTRIBUIDORA COMERCIAL ALVAREZ LIMITADA"
    }
    """
    db_uri: str = Field(
        title="Database URI",
        description="The URI of the database to connect to.",
    )
    tables: list = []
    columns: dict = {}
    args_schema: Type[BaseModel] = CustomNL2SQLToolInput

    def model_post_init(self, __context: Any) -> None:
        data = {}
        tables = self._fetch_available_tables()

        for table in tables:
            table_columns = self._fetch_all_available_columns(table["table_name"])
            data[f'{table["table_name"]}_columns'] = table_columns

        self.tables = tables
        self.columns = data

    def _fetch_available_tables(self):
        try:
            return self.execute_sql(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'tabparts_ai';"
            )
        except Exception as e:
            print(f"Error fetching tables: {e}")
            return []

    def _fetch_all_available_columns(self, table_name: str):
        try:
            return self.execute_sql(
                f"SELECT column_name, data_type FROM information_schema.columns "
                f"WHERE table_schema = 'tabparts_ai' AND table_name = '{table_name}';"
            )
        except Exception as e:
            print(f"Error fetching columns for {table_name}: {e}")
            return []

    def _run(self, sql_query: str, customer_infoname: str):
        try:
            # Validación extra de inputs
            if not isinstance(sql_query, str):
                raise ValueError("sql_query debe ser una cadena de texto")
            if not isinstance(customer_infoname, str):
                raise ValueError("customer_infoname debe ser una cadena de texto")
            if not sql_query.strip():
                raise ValueError("sql_query no puede estar vacío")
            if not customer_infoname.strip():
                raise ValueError("customer_infoname no puede estar vacío")

            print(f"🔍 Ejecutando consulta para cliente: {customer_infoname}")
            data = self.execute_sql(sql_query)
            
            # Validación del resultado
            if not data:
                print(f"⚠️ La consulta no retornó datos para el cliente: {customer_infoname}")
                
            return data
        except Exception as exc:
            error_msg = (
                f"Error ejecutando la consulta para el cliente {customer_infoname}.\n"
                f"Consulta original: {sql_query}\n"
                f"Error: {exc}\n"
                "Asegúrate de proporcionar los inputs en el formato correcto:\n"
                '{"sql_query": "TU_CONSULTA_SQL", "customer_infoname": "NOMBRE_CLIENTE"}'
            )
            print(f"❌ {error_msg}")
            return error_msg

    def execute_sql(self, sql_query: str) -> Union[list, str]:
        engine = create_engine(self.db_uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            result = session.execute(text(sql_query))
            session.commit()

            if result.returns_rows:
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in result.fetchall()]
                return data
            else:
                return f"Query {sql_query} executed successfully"

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()
