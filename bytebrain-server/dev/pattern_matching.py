from dataclasses import dataclass


@dataclass
class Button:
    name: str


@dataclass
class Click:
    position: tuple
    button: Button


click = Click(position=(1, 2), button=Button(name="hello"))

match click:
    case Click((x, y), z):
        print(x, y, z)

