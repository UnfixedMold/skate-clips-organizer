import subprocess

script_name = "app.py"
output_name = "OrganizeClips.exe"

subprocess.run([
    "pyinstaller",
    "--onefile",
    "--noconsole",
    "--name", output_name,
    script_name
], check=True)
