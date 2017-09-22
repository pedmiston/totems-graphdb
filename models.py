from py2neo import Node, Relationship
from graph.util import path_to_image


def Item(number, label, generation, score=None):
    assert isinstance(number, int), 'py2neo only likes native python ints'
    return Node('Item', number=number, label=label, generation=generation,
                score=score, image=path_to_image(label))

def Recipe(code):
    return Node('Recipe', code=code)

def Creates(recipe, result):
    return Relationship(recipe, 'CREATES', result)

def Requires(recipe, requirement):
    return Relationship(recipe, 'REQUIRES', requirement)

def Inherits(result, requirement):
    return Relationship(result, 'INHERITS', requirement)
