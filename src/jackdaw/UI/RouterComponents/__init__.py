import os
import importlib

# Import all router components
for f in os.listdir(os.path.dirname(__file__)):
    if f.endswith(".py") and "__" not in f:
        module = f"jackdaw.UI.RouterComponents.{f.replace('.py', '')}"
        importlib.import_module(module)
