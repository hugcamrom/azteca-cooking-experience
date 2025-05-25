from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

try:
    with driver.session(database="azteca") as session:
        greeting = session.run("RETURN '🎉 Neo4j connection successful!' AS message")
        print(greeting.single()["message"])
finally:
    driver.close()                                          
# Ensure you have the required packages installed: