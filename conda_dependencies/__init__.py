from conda.cli.python_api import run_command as conda_cli
from conda.exceptions import PackagesNotFoundError
import json
from collections import defaultdict
from graphviz import Digraph


def get_depends(package, version='', channels=[]):
    args = []
    for channel in channels:
        args.extend(['-c', channel])
    args.extend(['--override-channels', '--info', '--json'])
    if version and version[0] not in ('>', '<', '=', '!'):
        version = '=' + version
    for arch in ('linux-64', 'noarch'):
        new_args = args.copy()
        new_args.append(f'{package}{version or ""}[subdir={arch}]')
        try:
            result = conda_cli('search', *new_args)
            result = json.loads(result[0])
            pkg = result[package][-1]
            return pkg['depends'], pkg['channel']
        except PackagesNotFoundError:
            print(f'Package not found: {package}{version}[subdir={arch}]')
    return [], 'Unknown'


def get_dependencies(package, version, channels=[], ignore=[], hightlights=[],
                     debug=False):
    found_packages = defaultdict(set)
    to_process = [(package, version)]
    processed = []
    graph = Digraph()
    graph.node(package, color='red')

    graphs = {}

    while to_process:
        package, version = to_process.pop(0)
        if package in ignore:
            continue
        if debug:
            print(f'Processing {package} {version}...')
        found_packages[package].add(version)
        processed.append(package)

        depends, channel = get_depends(package, version, channels)

        # graph.node(package)
        subgraph = graphs.get(channel)
        if not subgraph:
            subgraph = Digraph(name='cluster_' + channel)
            subgraph.attr(label=channel)
            graphs[channel] = subgraph
        if package in hightlights:
            subgraph.node(package, color='blue')
        else:
            subgraph.node(package)
        if debug:
            print(depends)
        for dep in depends:
            split = dep.split(' ')
            if len(split) == 2:
                pkg, ver = tuple(split)
            elif len(split) == 3:
                pkg, ver, build = tuple(split)
            else:
                pkg = split[0]
                ver = None
            found_packages[pkg].add(ver)
            if pkg not in processed and pkg not in ignore:
                graph.node(pkg)
                to_process.append((pkg, ver))
                processed.append(pkg)
            if pkg not in ignore:
                graph.edge(package, pkg, label=None)
                if pkg == 'pandas':
                    print(package, ver)
    for k, v in graphs.items():
        graph.subgraph(v)
    return found_packages, graph

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--channel', action='append', type=str,
                        dest='channels', metavar='CHANNEL',
                        default=[])
    parser.add_argument('-i', '--ignore', action='append', type=str,
                        dest='ignore', metavar='PKG',
                        default=[],
                        help='Ignore packages (such as libgcc-ng, libstdcxx-ng, or python)')
    parser.add_argument('--hl', '--highlight', action='append', type=str,
                        dest='highlight', metavar='PKG',
                        default=[], help='Highlight packages in blue')
    parser.add_argument('-v', '--verbose', action='store_const', default=False,
                        const=True)
    parser.add_argument('-g', '--graph', action='append', type=str,
                        dest='graph', metavar='ENGINE',
                        default=[],
                        help='Which graphviz engines to use (dot, fdp, circo, twopi, etc')
    parser.add_argument('package')
    parser.add_argument('version')
    parser.add_argument('output')

    ns = parser.parse_args()
    dependencies, graph = get_dependencies(ns.package, ns.version, ns.channels,
                                           ns.ignore, ns.hightlight, ns.verbose)
    for key, val in dependencies.items():
        print(f'{key} => {val}')
    graph.format = 'png'
    for engine in ns.graph:
        print(f"Rendering {engine}...")
        graph.engine = engine
        graph.render(ns.output + '.' + engine)


if __name__ == '__main__':
    main()