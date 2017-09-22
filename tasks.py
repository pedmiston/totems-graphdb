from invoke import task
import json
import pandas

import graph
from tasks.paths import Path, R_PKG, TOTEMS, ITEM_IMAGES


@task
def load(ctx, delete_first=False):
    """Make the totems landscape as a graph database."""
    graph.load(delete_first=delete_first)


@task
def tree(ctx, max_number=None, max_generation=None, name=None, view_off=False):
    """Visualize the totems landscape in a figure.

    Examples:

        inv graph.tree
        inv graph.tree -n landscape-sample --max-generation 6
        inv graph.tree -n landscape-tools --max-number 100
    """
    viz = graph.make_landscape(image_dir=ITEM_IMAGES,
                               max_number=max_number,
                               max_generation=max_generation)
    viz.format = 'png'
    name = name or 'landscape'
    output = Path(R_PKG, 'inst/extdata/', name+'.gv')
    viz.render(output, view=not view_off)


@task
def inventory(ctx, item_numbers=None, name=None, view_off=False):
    """Visualize a inventory with a figure."""
    if item_numbers is None:
        item_numbers = [1, 2, 3, 4, 5, 6,
                        11, 12, 13, 14, 15, 16, 17,
                        23, 24]
    else:
        print('parsing item_numbers: ', item_numbers)
        item_numbers = list(map(int, item_numbers.split(',')))
        print('parsed item_numbers: ', item_numbers)
    viz = graph.make_inventory(image_dir=ITEM_IMAGES, item_numbers=item_numbers)
    viz.format = 'png'
    name = name or 'inventory'
    output = Path(R_PKG, 'inst/extdata/', name+'.gv')
    viz.render(output, view=not view_off)
