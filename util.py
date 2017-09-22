import unipath


def max_generation(items):
    """Get the max generation from a list of Item nodes."""
    try:
        max_generation = max([node['generation'] for node in items])
    except TypeError:
        raise MissingGeneration()
    return max_generation


class MissingGeneration(Exception):
    """One or more items did not have generations."""


def path_to_image(stem):
    return unipath.Path(stem + '.jpg')
