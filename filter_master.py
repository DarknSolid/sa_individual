from node import Node


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