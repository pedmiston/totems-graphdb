import itertools

import pandas
from graphviz import Digraph
import unipath

from graph.graph_db import connect_to_graph_db
from graph.util import path_to_image


def make_landscape(image_dir, max_generation=None, max_number=None):
    """Create a figure of a totems landscape by writing a graphviz script."""
    graph = connect_to_graph_db()

    if max_generation is None:
        max_generation = graph.data("""
        MATCH (n:Item)
        RETURN max(n.generation) AS max_generation
        """)[0]['max_generation']

    if max_number is None:
        max_number = graph.data("""
        MATCH (n:Item)
        RETURN max(n.number) AS max_number
        """)[0]['max_number']

    query_kwargs = dict(max_generation=max_generation, max_number=max_number)

    items = pandas.DataFrame(graph.data("""
    MATCH (n:Item)
    WHERE n.number <= {max_number}
    AND n.generation <= {max_generation}
    RETURN n.generation as generation, n.label as label, n.image as image
    """.format(**query_kwargs)))

    edges = pandas.DataFrame(graph.data("""
    MATCH (result:Item) -[r:INHERITS]-> (requirement:Item)
    WHERE result.number <= {max_number} AND requirement.number < {max_number}
    AND result.generation <= {max_generation} AND requirement.generation < {max_generation}
    RETURN result.label as result, requirement.label as requirement
    """.format(**query_kwargs)))

    viz = Digraph(graph_attr=dict(rankdir='TB'),
                  node_attr=dict(fontname='Helvetica', fontsize='12',
                                 shape='none'))

    for item in items.itertuples():
        viz.node(item.label, label='', image=unipath.Path(image_dir, item.image))

    for edge in edges.itertuples():
        viz.edge(edge.requirement, edge.result)

    # Set rank for nodes by generation.
    # Insert { rank=same ... } calls for each generation into the dot source.
    rank_fmt = '{{ rank=same {labels} }}\n'
    for _, items_in_gen in items.groupby('generation'):
        spaced_labels = ' '.join(items_in_gen.label.tolist())
        viz.body.append(rank_fmt.format(labels=spaced_labels))

    return viz


def make_inventory(image_dir, item_numbers, seed=None):
    """Create a figure of a particular inventory."""
    graph = connect_to_graph_db()
    query_kwargs = dict(item_numbers=item_numbers)

    items = pandas.DataFrame(graph.data("""
    MATCH (n:Item)
    WHERE n.number in {item_numbers}
    RETURN n.label as label, n.image as image
    """.format(**query_kwargs)))

    viz = Digraph(graph_attr=dict(rankdir='TB'),
                  node_attr=dict(fontname='Helvetica', fontsize='12',
                                 shape='none'),
                  edge_attr=dict(style='invis'))

    for item in items.itertuples():
        viz.node(item.label, label='', image=unipath.Path(image_dir, item.image))

    edges = itertools.combinations(items.label.tolist(), 2)
    for from_edge, to_edge in edges:
        viz.edge(from_edge, to_edge)

    viz.body.append('layout = circo\n')
    return viz
