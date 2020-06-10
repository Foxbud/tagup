"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from lark import Tree


class DiscardNode(Exception):
    pass


class BaseTraverser:
    preprocess_hook_template = 'preprocess_{name}_node'
    postprocess_hook_template = 'postprocess_{name}_node'

    def __init__(self, hook_manager):
        self.hook_manager = hook_manager

    def traverse(self, node):
        raise NotImplementedError

    def traverse_children(self, node):
        new_children = []
        for child in node.children:
            if isinstance(child, Tree):
                try:
                    new_children.append(self.traverse(child))
                except DiscardNode:
                    pass
            else:
                new_children.append(child)

        return new_children

    def process(self, node):
        node_name = node.data
        try:
            processor = getattr(self, node_name)
        except AttributeError:
            pass
        else:
            node = self.preprocess_hook(node, node_name)
            node = processor(node)
            node = self.postprocess_hook(node, node_name)

        return node

    def preprocess_hook(self, node, node_name):
        hook_name = self.preprocess_hook_template.format(name=node_name)
        try:
            hook = getattr(self.hook_manager, hook_name)
        except AttributeError:
            pass
        else:
            node = hook(node)

        return node

    def postprocess_hook(self, node, node_name):
        hook_name = self.postprocess_hook_template.format(name=node_name)
        try:
            hook = getattr(self.hook_manager, hook_name)
        except AttributeError:
            pass
        else:
            node = hook(node)

        return node


class PostOrderTraverser(BaseTraverser):
    def traverse(self, node):
        node.children = self.traverse_children(node)
        node = self.process(node)

        return node


class PreOrderTraverser(BaseTraverser):
    def traverse(self, node):
        node = self.process(node)
        node.children = self.traverse_children(node)

        return node
