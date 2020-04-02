import json
import numpy as np
import itertools
from typing import List, Tuple, Any


NODE = Tuple[str, Any]
PATH = List[str]
PATH_CONTEXT = List[NODE or PATH]


class ModuleHandler:
    def __init__(self, path: str, json_dict=None):
        if json_dict is not None:
            self.data = json_dict
        else:
            with open(path) as f:
                self.data = json.load(f)

        self.tree = dict()
        self.__build_tree()

    '''
    build tree representation of AST in dictionary 
    without all the additional info from AST
    AST tree in .json file would look something like this:
        tree = {0: [1, 3, 4],
                1: [2],
                2: [],
                3: [],
                4: [5],
                5: []}
    but as we need to find path from the leaves to the root
    tree looks like this:
        tree = {0: [1, 3, 4],
            1: [0, 2],
            2: [1],
            3: [0],
            4: [0, 5],
            5: [4]}
    '''

    def __add_children_to_tree(self, node: dict):
        for child in node['children']:
            self.tree[str(node['master_index'])].append(
                str(child['master_index'])
            )
            self.tree[str(child['master_index'])] = list(
                str(node['master_index'])
            )
            if 'children' in child:
                self.__add_children_to_tree(child)

    def __build_tree(self):
        self.tree['0'] = list()

        for node in self.data['nodes']:
            self.tree['0'].append(str(node['master_index']))
            # edge back to the root
            self.tree[str(node['master_index'])] = list('0')
            if 'children' in node:
                self.__add_children_to_tree(node)

    def __get_child_nodes(self, node: dict) -> List[NODE]:
        nodes = list()

        if 'children' in node:
            for child in node['children']:
                nodes += [(str(child['master_index']),
                           child['container'])] + self.__get_child_nodes(child)

        return nodes

    # all nodes from AST + root as a list of tuples
    def get_all_nodes(self) -> List[NODE]:
        nodes = [('0', 'root')]
        for node in self.data['nodes']:
            nodes += [(str(node['master_index']),
                       node['container'])] + self.__get_child_nodes(node)

        return nodes

    def __get_child_terminals(self, node: dict) -> List[NODE]:
        terminals = list()

        for child in node['children']:
            if 'children' not in child:
                terminals.append((str(child['master_index']),
                                  child['container']))
            else:
                terminals += self.__get_child_terminals(child)

        return terminals

    # all terminal nodes from AST as a list of tuples
    def get_terminals(self) -> List[NODE]:
        terminals = list()

        # there are some cases when root has only one child
        # in that case root is also terminal
        if len(self.tree['0']) == 1:
            terminals.append(('0', 'root'))

        for node in self.data['nodes']:
            if 'children' not in node:
                terminals.append((str(node['master_index']),
                                  node['container']))
            else:
                terminals += self.__get_child_terminals(node)

        return terminals

    def __get_terminal_pairs(self) -> Any:
        terminals = self.get_terminals()
        pairs = np.asarray(list(itertools.combinations(terminals, 2)))

        return pairs

    # find path between 2 given terminals
    def __find_path(self, start: str, end: str, visited=None) -> PATH or None:
        if start == end:
            return [start]

        visited = visited or set()
        for node in self.tree[start]:
            if node not in visited:
                visited.add(node)

                new_path = self.__find_path(node, end, visited)
                if new_path is not None:
                    return [start] + new_path

        return None

    @staticmethod
    def __add_arrows(path: List[str]) -> PATH:
        path_with_arrows = list()
        for i in range(len(path) - 1):
            path_with_arrows.append(path[i])
            if path[i] > path[i + 1]:
                path_with_arrows.append('up')
            else:
                path_with_arrows.append('down')

        path_with_arrows.append(path[-1])
        return path_with_arrows

    def get_paths(self) -> List[PATH]:
        terminal_pairs = self.__get_terminal_pairs()
        paths = list()
        for pair in terminal_pairs:
            path = self.__find_path(pair[0][0], pair[1][0])
            path = self.__add_arrows(path)
            paths.append(path[1:-1])

        return paths

    # all possible paths between terminals (leaves) without the actual leaves
    def get_context_paths(self) -> List[PATH_CONTEXT]:
        terminal_pairs = self.__get_terminal_pairs()
        context_paths = list()
        for pair in terminal_pairs:
            terminal_from = (str(pair[0][0]), str(pair[0][1]))
            terminal_to = (str(pair[1][0]), str(pair[1][1]))
            path = self.__find_path(pair[0][0], pair[1][0])
            path = self.__add_arrows(path)
            context_paths.append([terminal_from, path[1:-1], terminal_to])

        return context_paths
