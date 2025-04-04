from typing import Any, Type, Union, List, Dict

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class CustomNL2SQLToolInput(BaseModel):
    sql_template: str = Field(
        title="SQL Template",
        description="The SQL query template with named placeholders (e.g., :param_name) to execute.",
    )
    parameter_values: Dict[str, Any] = Field(
        title="Parameter Values",
        description="A dictionary mapping named placeholders in the template to their values.",
        default_factory=dict
    )
    customer_infoname: str = Field(
        title="Customer Info Name",
        description="The name of the customer for context/logging.",
    )


class CustomNL2SQLTool(BaseTool):
    name: str = "CustomNL2SQLTool"
    description: str = """
    Executes parameterized SQL queries using named placeholders to analyze customer data safely.
    It requires an SQL template with named placeholders (e.g., :param_name) and a dictionary mapping these names to their values.

    Required Inputs:
    - sql_template: The SQL query template with ':param_name' placeholders (string).
    - parameter_values: A dictionary mapping placeholder names to their values (dict).
    - customer_infoname: The name of the customer for context/logging (string).

    Example Usage:

    1. Basic sales query:
    {{
        "sql_template": "SELECT * FROM ventas_detalle WHERE cliente LIKE :cust_name",
        "parameter_values": {{"cust_name": "%CUSTOMER_NAME%"}},
        "customer_infoname": "CUSTOMER_NAME"
    }}

    2. Top products query:
    {{
        "sql_template": "SELECT producto, SUM(cantidad) as total FROM ventas_detalle WHERE cliente LIKE :cust_name GROUP BY producto ORDER BY total DESC LIMIT :limit_val",
        "parameter_values": {{"cust_name": "%EQUIP. AUTO%", "limit_val": 10}},
        "customer_infoname": "EQUIP. AUTOMOTRIZ Y OBRAS DE ING. CAMONT LIMITADA"
    }}
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
        # Fetch table and column info only if needed, or perhaps less frequently
        # For now, keeping the original logic but execute_sql needs modification
        # tables = self._fetch_available_tables()
        # for table in tables:
        #     table_columns = self._fetch_all_available_columns(table["table_name"])
        #     data[f'{table["table_name"]}_columns'] = table_columns
        # self.tables = tables
        # self.columns = data
        pass # No changes needed here for now, focus on execution path

    def _fetch_available_tables(self):
        try:
            # Pass empty dict for params as this query is static
            return self.execute_sql(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'tabparts_ai';", {}
            )
        except Exception as e:
            print(f"Error fetching tables: {e}")
            return []

    def _fetch_all_available_columns(self, table_name: str):
        try:
             # Pass empty dict for params as this query is static
             # Use named param for table_name for safety
            query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'tabparts_ai' AND table_name = :table_name;"
            return self.execute_sql(query, {"table_name": table_name})
        except Exception as e:
            print(f"Error fetching columns for {table_name}: {e}")
            return []

    def _run(self, sql_template: str, parameter_values: Dict[str, Any], customer_infoname: str):
        try:
            # Input validation
            if not isinstance(sql_template, str) or not sql_template.strip():
                raise ValueError("sql_template debe ser una cadena de texto no vacía")
            if not isinstance(parameter_values, dict):
                # Pydantic should handle this, but extra check doesn't hurt
                raise ValueError("parameter_values debe ser un diccionario")
            if not isinstance(customer_infoname, str) or not customer_infoname.strip():
                raise ValueError("customer_infoname debe ser una cadena de texto no vacía")

            # Optional: Validate if all named parameters in template exist in the dict
            # import re
            # found_params = set(re.findall(r':([a-zA-Z0-9_]+)', sql_template))
            # provided_params = set(parameter_values.keys())
            # if not found_params.issubset(provided_params):
            #     missing = found_params - provided_params
            #     print(f"⚠️ Warning: Missing parameters in input dict: {missing}")
                # Decide if this should be an error

            print(f"🔍 Ejecutando consulta parametrizada (nombrada) para cliente: {customer_infoname}")
            print(f"   Template: {sql_template[:100]}...") # Log snippet
            print(f"   Params Dict: {parameter_values}")
            data = self.execute_sql(sql_template, parameter_values)

            # Result validation
            if isinstance(data, list) and not data:
                print(f"⚠️ La consulta no retornó datos para el cliente: {customer_infoname}")

            return data
        except Exception as exc:
            error_msg = (
                f"Error ejecutando la consulta parametrizada (nombrada) para el cliente {customer_infoname}.\n"
                f"Template: {sql_template}\n"
                f"Parameters Dict: {parameter_values}\n"
                f"Error: {exc}\n"
                "Asegúrate de proporcionar los inputs en el formato correcto:\n"
                '{\n  "sql_template": "TU_TEMPLATE_SQL_CON_:nombre_param",\n  "parameter_values": {\"nombre_param\": \"VALOR\"},\n  "customer_infoname": "NOMBRE_CLIENTE"\n}'
            )
            print(f"❌ {error_msg}")
            return error_msg # Returning the error message

    def execute_sql(self, sql_template: str, params: Dict[str, Any]) -> Union[List[dict], str]:
        engine = create_engine(self.db_uri)
        with sessionmaker(bind=engine)() as session:
            try:
                # Execute with named parameters by passing the dictionary directly
                result = session.execute(text(sql_template), params)
                
                # Commit changes if any
                session.commit()

                if result.returns_rows:
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in result.fetchall()]
                    print(f"✅ Consulta ejecutada, {len(data)} filas retornadas.")
                    return data
                else:
                    print(f"✅ Query executed successfully (no rows returned). Template: {sql_template[:50]}...")
                    return f"Query executed successfully, {result.rowcount} rows affected."

            except Exception as e:
                session.rollback()
                print(f"❌ Error en execute_sql: {e}")
                raise e
            # Session automatically closed by context manager
