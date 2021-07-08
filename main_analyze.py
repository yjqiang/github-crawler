"""
解析仓库代码，统计 api
"""
import ast
import zipfile
from os import listdir
from os.path import isfile, join
import shutil


import utils
from analyser.de_alias_code import de_alias


def create_parents(root: ast.AST) -> dict[ast.AST, ast.AST]:
    """
    原来的树只有父节点指向自节点，现在提供一个反查接口
    :param root:
    :return:
    """
    parents = {}
    for cur_node in ast.walk(root):
        for child in ast.iter_child_nodes(cur_node):
            parents[child] = cur_node
    return parents


def find_grandparent(node, parents: dict[ast.AST, ast.AST]) -> list[ast.AST]:
    """
    找到所有的父节点
    :param node:
    :param parents:
    :return:
    """
    parent = node
    result = [parent]
    while True:
        tmp = parents[parent]
        if not isinstance(tmp, ast.Attribute):
            return result
        parent = tmp
        result.append(parent)


def main():
    result = {}
    path = "download_repos"
    tmp_path = 'tmp'
    shutil.rmtree(tmp_path)
    zip_files_paths = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f.endswith('.zip')]
    print(len(zip_files_paths))
    for zip_file_path in zip_files_paths:
        print(f'HANDLING {zip_file_path}')
        # 解压
        with zipfile.ZipFile(zip_file_path, 'r') as f:
            f.extractall(tmp_path)

        files_files = utils.get_all_files(tmp_path)  # 获取所有文件

        for file_path in files_files:
            # 仅处理 python 文件
            if not file_path.endswith('.py'):
                continue

            with open(file_path, encoding='utf-8') as f:
                try:
                    source = f.read()
                    ast.parse(source)
                except Exception as e:
                    print(f'ERROR {e} {file_path}')
                    continue


            source = de_alias(source)
            # list_lines = source.split('\n')
            # print('\n'.join([f'{i:<5}:    {line}' for i, line in enumerate(list_lines, start=1)]))

            tree = ast.parse(source)
            # print(ast.dump(tree, indent=4))
            parents = create_parents(tree)
            for node in ast.walk(tree):  # type: ast.AST
                if isinstance(node, ast.Name) and node.id == 'torch':  # 查询嵌套 torch.xx.xx
                    list_nodes = find_grandparent(node, parents)

                    items = []
                    for cur_node in list_nodes:
                        assert isinstance(cur_node, (ast.Name, ast.Attribute))
                        items.append(cur_node.id if isinstance(cur_node, ast.Name) else cur_node.attr)
                    usage = '.'.join(items)
                    result[usage] = result.get(usage, 0) + 1
                    # print(ast.dump(node, indent=4))

        shutil.rmtree(tmp_path)
        print(result)
    utils.save_json('data.json', {
        'result': result,
    })


if __name__ == "__main__":
    main()
