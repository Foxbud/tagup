"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from lark import Tree


class DiscardNode(Exception):
	pass


class PostOrderTraverser:
	def traverse(self, node):
		f = getattr(self, node.data)
		node.children = self._traverse_children(node)
		new_node = f(node)

		return new_node

	def _traverse_children(self, node):
		new_children = []
		for child in node.children:
			if isinstance(child, Tree):
				try:
					new_children.append(self.traverse(child))
				except DiscardNode as e:
					pass
			else:
				new_children.append(child)

		return new_children

	def __getattr__(self, name):
		return self.__default__

	def __default__(self, node):
		return node


class PreOrderTraverser(PostOrderTraverser):
	def traverse(self, node):
		f = getattr(self, node.data)
		new_node = f(node)
		new_node.children = self._traverse_children(new_node)

		return new_node
