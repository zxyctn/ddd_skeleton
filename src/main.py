from src.app.application import Application
from src.modules.example.entrypoint import example

app = Application()
app.add(example)

example_app = app.get(example.name)
