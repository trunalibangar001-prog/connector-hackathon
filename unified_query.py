import json

# Gmail data load
with open("gmail_output.json", "r", encoding="utf-8") as file:
    gmail_data = json.load(file)

# Drive data load
with open("drive_output.json", "r", encoding="utf-8") as file:
    drive_data = json.load(file)

print("\n===== CONNECTOR QUERY =====")
print("Available sources: Gmail, Google Drive")

query = input("\nEnter your query: ").lower()

if "email" in query or "gmail" in query:
    print("\n--- Gmail Data ---")
    print(json.dumps(gmail_data, indent=2))

elif "drive" in query or "file" in query:
    print("\n--- Google Drive Data ---")
    print(json.dumps(drive_data, indent=2))

else:
    print("\nSorry, I could not find data for this query.")

print("\nQuery completed!")