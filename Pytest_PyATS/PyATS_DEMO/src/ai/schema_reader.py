# src/ai/schema_reader.py

def read_operation(entry: dict):
    issue = entry.get("issue", {})

    return {
        "device": entry.get("device"),
        "role": entry.get("role"),
        "protocol": issue.get("protocol"),
        "summary": issue.get("summary"),
        "detail": issue.get("detail"),
        "actions": entry.get("actions", []),
        "metadata": entry.get("metadata", {}),
    }