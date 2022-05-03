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


def top_level_module(module_name, depth=1):
    components = module_name.split(".")
    r = ".".join(components[:depth])
    return r


def merge_nodes_to_top_level(nodes: List[Node], depth=1) -> List[Node]:
    merged = dict()

    for node in nodes:
        new_module_name = top_level_module(node.module_name, depth)
        node.module_name = new_module_name

        if new_module_name not in merged:
            merged[new_module_name] = node
        else:
            existing_node = merged.get(new_module_name)
            existing_node.lines_of_code += node.lines_of_code
            existing_node.imports.update(node.imports)

    # fix imports
    ls = [v for k, v in merged.items()]
    for node in ls:
        new_imports = set()
        for imp in node.imports:
            top_level_import = top_level_module(imp, depth)
            if top_level_import != node.module_name:
                new_imports.add(top_level_import)
        node.imports = new_imports

    return ls


class FilterMaster:
    def __init__(self):
        self._node_conditions = []
        self._graph_conditions = []

    def add_node_condition(self, condition):
        self._node_conditions.append(condition)

    def add_graph_condition(self, condition):
        self._graph_conditions.append(condition)

    def runNode(self, node:Node) -> bool:
        # all conditions must pass
        for condition in self._node_conditions:
            if not condition(node):
                return False
        return True

    def runGraphNode(self, node:str) -> bool:
        # all conditions must pass
        for condition in self._graph_conditions:
            if not condition(node):
                return False
        return True


def keep_nodes(nodes: List[Node], filterMaster):
    filtered_nodes = []

    for node in nodes:
        if filterMaster.runNode(node):
            filtered_nodes.append(node)
    return filtered_nodes


def dependencies_digraph(nodes: List[Node], filterMaster: FilterMaster):
    G = nx.DiGraph()

    for node in nodes:
        if node.module_name not in G.nodes:
            G.add_node(node.module_name)

        for imp in node.imports:
            # an import should have an edge drawn from the node if the import is a node
            is_imp_a_node = any(n.module_name == imp for n in nodes)
            if is_imp_a_node or filterMaster.runGraphNode(imp):
                G.add_edge(node.module_name, imp)

    return G


def draw_graph_with_labels(G, weights, figsize=(10, 10)):
    plt.figure(figsize=figsize)
    nx.draw(G,
            node_size=weights,
            with_labels=True,
            node_color='#00d4e9')
    plt.show()


fm = FilterMaster()
# is_system_module:
fm.add_node_condition(lambda node: node.module_name.startswith("zeeguu."))
fm.add_graph_condition(lambda name: name.startswith("zeeguu."))

nodes = create_nodes()
nodes_merged = merge_nodes_to_top_level(nodes=nodes, depth=2)
nodes_filtered = keep_nodes(nodes_merged, filterMaster=fm)
for node in nodes_filtered:
    print(f'{node.lines_of_code}: {node.module_name}')
DG = dependencies_digraph(nodes=nodes_filtered, filterMaster=fm)

weights = [n.lines_of_code for n in nodes_filtered]
draw_graph_with_labels(DG, weights=weights, figsize=(8, 4))
