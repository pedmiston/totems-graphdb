from os import environ
from py2neo import Graph, Unauthorized
from py2neo.packages.httpstream.http import SocketError


def connect_to_graph_db():
    if 'NEO4J_PASSWORD' not in environ:
        raise Unauthorized('must set NEO4J_PASSWORD env variable')

    try:
        graph = Graph(password=environ['NEO4J_PASSWORD'])
    except SocketError:
        raise AssertionError('probably need to start Neo4j with `neo4j start`')

    return graph
