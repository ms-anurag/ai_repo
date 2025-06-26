from datetime import datetime
import json
import os
from pathlib import Path

# Sample function to collect metadata and content for a given file
def get_file_details(folder_path, relative_path):
    file_path = Path(folder_path) / relative_path
    stat = file_path.stat()
    metadata = {
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "file_type": file_path.suffix,
    }
    return {
        "file_name": file_path.name,
        "relative_path": str(file_path),
        "metadata": metadata,
    }

# Function to create a full JSON structure for all files in the scanned repo
def create_repo_json(repo_summary, output_file="repo_summary.json"):
    folder_path = os.getcwd()
    output_file = os.path.join(folder_path, output_file)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(repo_summary, f, indent=2)

    return output_file

# Function to generate input for selected file context to be sent to Azure LLM
def create_single_file_prompt(folder_path, selected_rel_path, overall_repo_summary):
    detail = get_file_details(folder_path, selected_rel_path)
    prompt = {
        "messages": [
            {"role": "system", "content": "You are an AI code assistant."},
            {"role": "user", "content": (
                f"Here is the summary of the overall repo:\n"
                f"{json.dumps(overall_repo_summary, indent=2)}\n\n"
                f"Now analyze this selected file:\n\n"
                f"File name: {detail['file_name']}\n"
                f"Relative path: {detail['relative_path']}\n"
                f"Metadata: {json.dumps(detail['metadata'], indent=2)}\n"
                f"Content:\n{detail['content']}"
            )}
        ]
    }
    return prompt

