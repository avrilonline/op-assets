import json
import os
import subprocess
from datetime import datetime

os.chdir('/home/admin/.openclaw/workspace/op-assets.avril.onl')
DATA_FILE = 'data.json'

with open(DATA_FILE, 'r') as f:
    data = json.load(f)

# Find first un-generated item
target_item = None
for item in data:
    if not item.get('image'):
        target_item = item
        break

if not target_item:
    print("All images generated.")
    exit(0)

print(f"Generating for: {target_item['title']}")

# Setup prompt
# Combine the base description of the character with the prompt so the model is fully aligned
prompt = f"Use the provided image as a strict style and character reference for this generation. The subject is a 3D minimalist spherical robot face, matte lime-green textured surface, two vertical glossy black pill-shaped eyes with subtle inner mesh details, glowing neon blue rim light from behind, dark moody background, high-end Apple-inspired industrial design, clean, symmetric. Now, generate this exact character in this specific scenario/composition: {target_item['prompt']}"

# Filename
safe_title = "".join(c if c.isalnum() else "-" for c in target_item['title']).lower()
filename = f"assets/{safe_title}.png"

os.makedirs('assets', exist_ok=True)

# Run generator
# Aspects from the json are like '16:9', '9:16', '1:1'
aspect = target_item.get('aspect', '1:1')

cmd = [
    "uv", "run",
    "/home/admin/.npm-global/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py",
    "--prompt", prompt,
    "--filename", filename,
    "-i", "ref.jpg",
    "--resolution", "2K"
]

if aspect in ["1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"]:
    cmd.extend(["--aspect-ratio", aspect])

print(f"Running: {' '.join(cmd)}")
res = subprocess.run(cmd, capture_output=True, text=True)

if res.returncode != 0:
    print("Error running generation:")
    print(res.stderr)
    exit(1)

print("Success.")

# Update data
target_item['image'] = filename
with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Commit
subprocess.run(["git", "add", "data.json", filename], check=True)
subprocess.run(["git", "commit", "-m", f"Generate image for {target_item['title']}"], check=True)

print(f"MEDIA:./{filename}")
# Push to remote
subprocess.run(["git", "push", "origin", "master"], check=True)
