import csv
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Neo4j driver from environment
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

# Read data from CSV
def load_bookings_from_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

# Push data to Neo4j
def push_to_neo4j(bookings):
    with driver.session(database="azteca") as session:
        for row in bookings:
            session.run("""
                MERGE (student:Student {name: $name})
                MERGE (class:Class {name: $class_type})
                MERGE (student)-[:BOOKED {
                    date: $preferred_date,
                    language: $language,
                    email: $email,
                    notes: $notes
                }]->(class)
            """, {
                "name": row["name"],
                "class_type": row["class_type"],
                "preferred_date": row["preferred_date"],
                "language": row["language"],
                "email": row["email"],
                "notes": row["notes"]
            })
    print("✅ Synced to Neo4j!")

# Run the sync
if __name__ == "__main__":
    bookings = load_bookings_from_csv("bookings_sample.csv")
    push_to_neo4j(bookings)
    driver.close()

