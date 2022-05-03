import networkx as nx
import matplotlib.pyplot as plt
from imports_finder import *
from pathlib import Path
from typing import List, Set
from utils import *
from module_metrics import module_LOC


class Node:
    def __init__(self, module_name: str, imports: Set[str], LOC: int):
        self.module_name = module_name
        self.LOC = LOC
        self.imports = imports


def create_nodes():
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    nodes = dict()
    for file in files:
        file_path = str(file)
        imports = imports_from_file(file_path)
        module_name = module_name_from_file_path(file_path)
        loc = module_LOC(module_name)

        if module_name not in nodes:
            nodes[module_name] = Node(module_name=module_name, imports=imports, LOC=loc)
        else:
            node = nodes.get(module_name)
            node.imports.update(imports)
            node.LOC += loc

    return nodes


def dependencies_digraph_2(nodes: List[Node]):
    G = nx.DiGraph()

    for node in nodes:
        if node.module_name not in G.nodes:
            G.add_node(node.module_name)

        for imp in node.imports:
            G.add_edge(node.module_name, imp)

    return G


def dependencies_digraph():
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")

    G = nx.DiGraph()

    for file in files:
        file_path = str(file)
        module_name = module_name_from_file_path(file_path)
        if module_name not in G.nodes:
            G.add_node(module_name)

        for each in imports_from_file(file_path):
            G.add_edge(module_name, each)

    return G


# a function to draw a graph
def draw_graph(G, size, **args):
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()


def top_level_module(module_name, depth=2):
    components = module_name.split(".")
    r = ".".join(components[:depth])
    return r


def abstracted_to_top_level(G):
    aG = nx.DiGraph()
    for each in G.edges():
        src = top_level_module(each[0])
        dst = top_level_module(each[1])

        if src != dst:
            aG.add_edge(src, dst)

    return aG


class FilterMaster:
    def __init__(self):
        self._conditions = []

    def add_condition(self, condition):
        self._conditions.append(condition)

    def run(self, item) -> bool:
        # all conditions must pass
        for condition in self._conditions:
            if not condition(item):
                return False
        return True


def keep_nodes(inputGraph, filterMaster):
    result = nx.DiGraph()

    for each in inputGraph.edges():
        src = each[0]
        dst = each[1]

        if filterMaster.run(src):
            result.add_node(src)

        if filterMaster.run(dst):
            result.add_node(dst)

        if filterMaster.run(src) and filterMaster.run(dst):
            result.add_edge(src, dst)

    return result


def draw_graph_with_labels(G, figsize=(10, 10)):
    plt.figure(figsize=figsize)
    nx.draw(G, with_labels=True, node_color='#00d4e9')
    plt.show()


fm = FilterMaster()
# is_system_module:
fm.add_condition(lambda item: item.startswith("zeeguu."))

DG = dependencies_digraph()
ADG = abstracted_to_top_level(DG)
system_ADG = keep_nodes(ADG, filterMaster=fm)
draw_graph_with_labels(system_ADG, (8, 4))
