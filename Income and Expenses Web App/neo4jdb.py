from py2neo import Graph, Node
from decouple import config

def create_connection(uri, user, password):
    return Graph(uri, auth=(user, password))

def insert_data(graph, period, incomes, expenses, comment):
    tx = graph.begin()

    # Create or find Period node
    period_node = Node("Period", key=period)
    tx.merge(period_node, "Period", "key")

    # Create or find Income nodes and relationships
    for income, amount in incomes.items():
        income_node = Node("Income", name=income, amount=amount)
        tx.merge(income_node, "Income", "name")
        tx.merge((period_node, "HAS_INCOME", income_node))

    # Create or find Expense nodes and relationships
    for expense, amount in expenses.items():
        expense_node = Node("Expense", name=expense, amount=amount)
        tx.merge(expense_node, "Expense", "name")
        tx.merge((period_node, "HAS_EXPENSE", expense_node))

    # Add Comment property to Period node
    period_node["comment"] = comment

    tx.commit()

def fetch_all_periods(graph):
    query = "MATCH (p:Period) RETURN p.key AS period"
    result = graph.run(query).data()
    return [item["period"] for item in result]


def get_period(graph, period):
    query = f"MATCH (p:Period)-[:HAS_INCOME|HAS_EXPENSE]->(item) WHERE p.key = '{period}' RETURN p.key AS period, COLLECT(item) AS items"
    result = graph.run(query).data()

    if result:
        period_data = result[0]
        return {
            "key": period_data["period"],
            "incomes": {item["name"]: item["amount"] for item in period_data["items"] if "Income" in item.labels},
            "expenses": {item["name"]: item["amount"] for item in period_data["items"] if "Expense" in item.labels},
            "comment": period_data.get("comment", "")
        }
    else:
        return None

def get_period_data(graph, period):
    query = f"MATCH (p:Period)-[:HAS_INCOME|HAS_EXPENSE]->(item) WHERE p.key = '{period}' RETURN p.key AS period, COLLECT(item) AS items"
    result = graph.run(query).data()

    if result:
        period_data = result[0]
        return {
            "key": period_data["period"],
            "incomes": {item["name"]: item["amount"] for item in period_data["items"] if "Income" in item.labels},
            "expenses": {item["name"]: item["amount"] for item in period_data["items"] if "Expense" in item.labels},
            "comment": period_data.get("comment", "")
        }
    else:
        return None

def get_graph():
    uri = config('NEO4J_URI')
    username = config('NEO4J_USERNAME')
    password = config('NEO4J_PASSWORD')
    return create_connection(uri, username, password)

