from graphdb.main import Landscape

def test_get_guess_from_item():
    landscape = Landscape()
    required_items = landscape.get_recipe(30)
    assert set(required_items) == set([25, 29])
