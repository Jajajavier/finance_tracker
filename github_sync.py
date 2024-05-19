import os
import json
import base64
from tkinter import simpledialog, Tk, messagebox

CONFIG_FILE = "github_config.txt"
DATA_FILE = "transactions.txt"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

def get_github_config():
    config = load_config()
    if config is None:
        root = Tk()
        root.withdraw()
        repo = simpledialog.askstring("GitHub Repository", "Enter your GitHub repository (e.g., username/repo):")
        token = simpledialog.askstring("GitHub Token", "Enter your GitHub personal access token:", show="*")
        config = {"repo": repo, "token": token}
        save_config(config)
    return config

def run_curl_command(command):
    process = os.popen(command)
    output = process.read()
    process.close()
    return output

def get_file_sha(repo, token):
    url = f"https://api.github.com/repos/{repo}/contents/{DATA_FILE}"
    headers = f"-H \"Authorization: token {token}\" -H \"Accept: application/vnd.github.v3+json\""
    command = f"curl {headers} {url}"
    output = run_curl_command(command)
    response = json.loads(output)
    return response.get("sha") if "sha" in response else None

def download_file(repo, token):
    url = f"https://api.github.com/repos/{repo}/contents/{DATA_FILE}"
    headers = f"-H \"Authorization: token {token}\" -H \"Accept: application/vnd.github.v3.raw\""
    command = f"curl {headers} -o {DATA_FILE} {url}"
    output = run_curl_command(command)
    return os.path.exists(DATA_FILE)

def commit_and_push():
    config = get_github_config()
    repo = config["repo"]
    token = config["token"]

    if not os.path.exists(DATA_FILE):
        if not download_file(repo, token):
            messagebox.showerror("Error", "Failed to download transactions.txt from GitHub.")
            return

    with open(DATA_FILE, "rb") as file:
        content = file.read()
    encoded_content = base64.b64encode(content).decode()

    commit_message = "Update transactions"
    url = f"https://api.github.com/repos/{repo}/contents/{DATA_FILE}"
    headers = f"-H \"Authorization: token {token}\" -H \"Accept: application/vnd.github.v3+json\""

    file_sha = get_file_sha(repo, token)

    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": file_sha
    }

    json_data = json.dumps(data)
    # Escaping double quotes in JSON data for the curl command
    json_data_escaped = json_data.replace('"', '\\"')
    command = f'curl {headers} -X PUT -d "{json_data_escaped}" {url}'
    output = run_curl_command(command)
    response = json.loads(output)
    if response.get("commit"):
        messagebox.showinfo("Success", "Transactions synchronized with GitHub.")
    else:
        messagebox.showerror("Error", f"Failed to synchronize with GitHub: {response}")

if __name__ == "__main__":
    commit_and_push()
