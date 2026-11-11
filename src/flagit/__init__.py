import importlib.metadata

try:
    version = importlib.metadata.version("flagit")
except importlib.metadata.PackageNotFoundError:
    version = "unknown"