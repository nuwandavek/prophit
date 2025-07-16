from fasthtml.common import serve
from src.prophit.app import create_app

app, rt = create_app()

if __name__ == "__main__":
    serve()
