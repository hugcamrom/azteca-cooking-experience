import csv
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

# Neo4j connection via .env
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

# Load bookings from CSV
def load_bookings_from_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

# Push safely to Neo4j
def push_to_neo4j(bookings):
    with driver.session(database="azteca") as session:
        for row in bookings:
            session.run("""
                MERGE (student:Student {name: $name})
                MERGE (class:Class {name: $class_type})
                MERGE (student)-[b:BOOKED {preferred_date: $preferred_date}]->(class)
                ON CREATE SET 
                    b.language = $language,
                    b.email = $email,
                    b.notes = $notes
            """, {
                "name": row["name"],
                "class_type": row["class_type"],
                "preferred_date": row["preferred_date"],
                "language": row["language"],
                "email": row["email"],
                "notes": row["notes"]
            })
    print("✅ Live sync complete (no duplicates)")

# Run sync
if __name__ == "__main__":
    bookings = load_bookings_from_csv("bookings_sample.csv")
    push_to_neo4j(bookings)
# Ensure you have the required packages installed: