import ast
from typing import Union


class DeAlias(ast.NodeTransformer):
    """
    Naive implementation
    Can't handle cases such as name shadowing
    """

    def __init__(self) -> None:
        self._alias_table: dict[str, str] = {}
        super().__init__()

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """
        import numpy as np =>
        Import(
            names=[
                alias(name='numpy', asname='np')])

        :param node:
        :return:
        """
        for alias in node.names:  # type: ast.alias
            if alias.asname is not None:
                self._alias_table[alias.asname] = alias.name
                alias.asname = None
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.Import, ast.ImportFrom]:
        """
        from torch.nn.utils.rnn import pack_padded_sequence as a, pad_sequence as b =>
        ImportFrom(
            module='torch.nn.utils.rnn',
            names=[
                alias(name='pack_padded_sequence', asname='a'),
                alias(name='pad_sequence', asname='b')],
            level=0),

        :param node:
        :return:
        """
        if node.level != 0:
            # We can't handle relative imports
            return node

        for alias in node.names:  # type: ast.alias
            if alias.asname is not None:
                self._alias_table[alias.asname] = f'{node.module}.{alias.name}'
            else:
                self._alias_table[alias.name] = f'{node.module}.{alias.name}'

        return ast.Import(names=[ast.alias(name=node.module, asname=None)])

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """
        这里更像是一个“作弊”，把 Name 里面 id 暴力替换，替换可能为 "xx.xx.xx"，这是在正常代码解析中看不到的
        :param node:
        :return:
        """
        node.id = self._alias_table.get(node.id, node.id)
        return node


def de_alias(source: str) -> str:
    """
    Transform source code so that aliases are replaced
    by corresponding regular names.
    """

    tree = ast.parse(source)
    # print(ast.dump(tree, indent=4))
    # new_tree = DeAlias().visit(tree)
    new_tree = ast.fix_missing_locations(DeAlias().visit(tree))
    return ast.unparse(new_tree)


if __name__ == "__main__":
    print(de_alias("import torch; torch.nn.Module"))
    print('------------------------------------------------')
    print(de_alias("import numpy as np; np.random.seed()"))
    print('------------------------------------------------')
    print(de_alias("from torch.nn.utils.rnn import pack_padded_sequence as a, pad_sequence as b; b.__annotations__"))
    print('------------------------------------------------')
    print(de_alias('from torch import nn; from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence; full_conn1 = pack_padded_sequence.Linear(in_features, hidden_features)'))
