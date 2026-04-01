import os
import sys

print("=== Debug Information ===")
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"App location: {os.path.dirname(os.path.abspath(__file__))}")

# Check .env in multiple locations
possible_paths = [
    '.env',
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.getcwd(), '.env'),
]

for path in possible_paths:
    exists = os.path.exists(path)
    print(f"\n.env at '{path}': {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
    if exists:
        try:
            with open(path, 'r') as f:
                content = f.read()
                print(f"   Contains 'OPENAI_API_KEY': {'✅ YES' if 'OPENAI_API_KEY' in content else '❌ NO'}")
        except:
            print(f"   Could not read file")