from __future__ import annotations

import typing as tp
from collections import namedtuple
from string import ascii_uppercase as alphabet
from math import inf as INFINITY

Sentence = tp.NewType("Sentence", list[str])


PrintedTree = namedtuple('PrintedTree', ('sentences', 'children'))


class TreeError(Exception):
    def __init__(self, msg: str, *args, **kwargs):
        logger.error(msg)
        super().__init__(msg, *args, **kwargs)


class Tree(object):
    child_limit = 2

    # Class methods

    # gen_name should be changed before implementing the possibility of changing the child limit
    # @classmethod
    # def set_child_limit(cls, amount: int) -> None:
    #     """Sets the limit of children in the class to the given amount"""
    #     assert isinstance(amount, int)
    #     cls.child_limit = amount


    def __init__(self, start_statement: Sentence, branch_name: str = 'A', parent: Tree = None, leaves_dict: dict[str, Tree] = None, closed: tp.Union[None, tuple[int]] = None, used: tp.Set[int] = set()):
        """The representation of one node in a tree; non-diverging rules add to this one's statement list. It's accounted for in the interface

        :param start_statement: The first statement to insert into the node
        :type start_statement: Sentence
        :param branch_name: Name of the branch; use `gen_name` on the parent to find the name, defaults to 'A'
        :type branch_name: str, optional
        :param parent: Parent node
        :type parent: Tree, optional
        :param leaves_dict: If the tree has a dict of leaves it can be stored here; when not provided system will create an empty dict
        :type leaves_dict: dict[str, Tree], optional
        :param closed: Stores information about the closing sentences of this leaf, defaults to None
        :type closed: tuple[int], optional
        :param used: A set for storing IDs of sentences which can't be used again in this branch, defaults to an empty set
        :type used: tp.Set[int], optional
        """
        self.name = branch_name
        self.statements = [start_statement]
        self.parent = parent
        self.children = []
        self.closed = closed
        self.used = used
        if leaves_dict is None:
            leaves_dict = dict()
        leaves_dict[branch_name] = self
        self.leaves = leaves_dict

    # Technical

    @staticmethod
    def _distalph(letter_a: str, letter_b: str) -> int:
        """Calculates distance between two letters"""
        assert len(letter_a) == 1 and len(
            letter_b) == 1, "_distalph only checks chars"
        return alphabet.index(letter_a) - alphabet.index(letter_b)


    def gen_name(self) -> tuple[str]:
        """Generates two possible names for the children of this node"""
        if self.parent:
            dist = self._distalph(self.name, self.parent.getchildren(
                0).name) + self._distalph(self.name, self.parent.getchildren(-1).name)
            assert dist != 0
            new = abs(dist)//2
            if dist < 0:
                if self.leaves:
                    assert not alphabet[new] in self.leaves.keys()
                return self.name, alphabet[new]
            else:
                if self.leaves:
                    assert not alphabet[25-new] in self.leaves.keys()
                return alphabet[25-new], self.name
        else:
            return 'A', 'Z'


    # Tree reading


    def getroot(self) -> Tree:
        if self.parent:
            return self.parent.getroot()
        else:
            return self


    def getchildren(self, index=None) -> tuple[Tree]:
        if not index is None:
            return self.children[index]
        else:
            return tuple(self.children)


    def getbranch(self) -> tuple[str, bool]:
        """Returns all the sentences in this node's branch and information about branch's closure"""
        return self._getbranch(), self.closed


    def _getbranch(self):
        """Returns all the sentences in this node's branch; `getbranch` is recommended"""
        if self.parent:
            return self.parent._getbranch() + self.statements
        else:
            return self.statements


    def gettree(self):
        """Creates recursively a named tuple with the sentences"""
        if self.children:
            children = (i.gettree() for i in self.children)
        else:
            children = None
        return PrintedTree(sentences=self.statements, children=children)


    def getleaves(self, *names: tp.Iterable[str]) -> list[Tree]:
        """Returns all or chosen leaves (if names are provided as args)

        :return: List of the leaves
        :rtype: list[Tree]
        """
        if names:
            return [self.leaves.get(i, None) for i in names]
        else:
            return list(self.leaves.values())


    def getopen(self, *names: tp.Iterable[str]) -> tp.Iterator[Tree]:
        """Returns all or chosen open leaves (if names are provided as args)

        :return: Iterator of the leaves
        :rtype: tp.Iterator[Tree]
        """
        return (i for i in self.getleaves(*names) if not i.closed)


    def getbranch_neighbour(self, left_right: str):
        """Return left/right neighbour of the branch

        :param left_right: 'L/Left' or 'R/Right'
        :type left_right: str
        :raises TreeError: left_right is not a valid direction
        :return: A leaf of the neighbour branch
        :rtype: Tree
        """
        min_dist = INFINITY
        obj_w_min = None
        if left_right.upper() in ('R', 'RIGHT'):
            for i in self.leaves.items():
                dist = self._distalph(i[0], self.name)
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    obj_w_min = i[1]
            return obj_w_min

        # Copy of the previous part, but with different distance computing
        elif left_right.upper() in ('L', 'LEFT'):
            for i in self.leaves.items():
                dist = self._distalph(self.name, i[0])
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    obj_w_min = i[1]
            return obj_w_min

        else:
            raise TreeError(f"'{left_right}' is not a valid direction")
            return None


    def getnode_neighbour(self, left_right: str) -> tp.Union[Tree]:
        """Return left/right neighbour of the node 

        :param left_right: 'L/Left' or 'R/Right'
        :type left_right: str
        :raises TreeError: left_right is not a valid direction
        :return: The neighbour
        :rtype: Tree
        """
        if not self.parent:
            return None

        # Find neighbour's index
        index = self.parent.getchildren().index(self)
        if left_right.upper() in ('R', 'RIGHT'):
            index += 1
        elif left_right.upper() in ('L', 'LEFT'):
            index -= 1
        else:
            raise TreeError(f"'{left_right}' is not a valid direction")

        # Get neighbour
        if index >= len(self.parent.getchildren()) or index < 0:
            if (parent_neigh := self.parent.getnode_neighbour(left_right)):
                if parent_neigh.getchildren():
                    return parent_neigh.getchildren(-1*(index < 0))
                else:
                    return parent_neigh
            else:
                return None
        else:
            return self.parent.getchildren(index)


    def is_finished(self):
        """Checks if all branches are closed"""
        return all((i.closed for i in self.leaves.values()))


    # Tree modification


    def _add_statements(self, statements: tuple[Sentence]) -> None:
        """Adds statement(s) to the node

        :param statements: statement(s)
        :type statements: Sentence
        """
        self.statements.extend(statements)


    def _add_children(self, *statements: tp.Iterable[tuple[Sentence]]):
        """Adds statements as children of the node"""
        names = self.gen_name()
        for i, sentence in enumerate(statements):
            self.children.append(Tree(
                sentence[0], names[i], self, leaves_dict=self.leaves, closed=self.closed, used=self.used.copy()))
            if (to_add := sentence[1:]):
                self.children[-1].append((to_add,))


    def append(self, statements: tuple[tuple[Sentence]]):
        """Prefered way of adding new statements. Use a tuple with tuples filled with sentences.
        Every tuple of strings is interpreted as a new branch. If there is only one statement it will be added to the existing node. 

        :param statements: Statements grouped into branches
        :type statements: tuple[tuple[str]]
        :raises TreeError: Too much branches to append
        """
        assert isinstance(statements, tuple)
        if len(statements) == 1:
            self._add_statements(*statements)
        elif len(statements) == self.child_limit:
            self._add_children(*statements)
        else:
            raise TreeError(
                f'Trying to append {len(statements)} branches to the tree')


    def close(self, contradicting: int, contradicting2: int = None) -> None:
        """Closes the branch using the last

        :param contradicting: ID of the colliding sentence
        :type contradicting: int
        :param contradicting2: Use if you already have ID of the second colliding sentence
        :type contradicting2: int, optional
        """
        if contradicting2:
            self.closed = (contradicting2, contradicting)
        else:
            self.closed = (len(self.getbranch())-1, contradicting)


    def add_used(self, used: int) -> None:
        """
        Adds the statement ID to the used statements set
        Should only be used after non-reusable rules
        """
        assert used not in self.used
        self.used.add(used)
