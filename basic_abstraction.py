import networkx as nx
import matplotlib.pyplot as plt
from imports_finder import *
from pathlib import Path
from typing import List, Set
from utils import *
from module_metrics import get_LOC_of_file


class Node:
    def __init__(self, file_path: str, module_name: str, imports: Set[str], lines_of_code: int):
        self.file_path = file_path
        self.module_name = module_name
        self.lines_of_code = lines_of_code
        self.imports = imports


def create_nodes():
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    nodes = []
    for file in files:
        file_path = str(file)
        imports = imports_from_file(file_path)
        module_name = module_name_from_file_path(file_path)
        lines_of_code = get_LOC_of_file(file_path)

        nodes.append(Node(file_path=file_path, module_name=module_name, imports=imports, lines_of_code=lines_of_code))

    return nodes


def dependencies_digraph_2(nodes: List[Node]):
    G = nx.DiGraph()

    for node in nodes:
        if node.module_name not in G.nodes:
            G.add_node(node.module_name)

        for imp in node.imports:
            G.add_edge(node.module_name, imp)

    return G


def top_level_module(module_name, depth=1):
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
#fm.add_condition(lambda item: item.startswith("zeeguu."))

nodes = create_nodes()
# merge nodes based on depth

for node in nodes:
    print(f'{node.lines_of_code} - {node.module_name}')

DG = dependencies_digraph_2(nodes=nodes)
ADG = abstracted_to_top_level(DG)
system_ADG = keep_nodes(ADG, filterMaster=fm)
draw_graph_with_labels(system_ADG, (8, 4))

