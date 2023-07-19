from pathlib import Path
import typer
import re
import networkx as nx
import json
import tomli

app = typer.Typer()

def reroot_inward(node, source, output, visited=None):
    visited = visited or []
    visited.append(node)
    for edge in source.in_edges(node):
        color = source.edges[edge].get("color", "black")
        if edge[0] == node:
            n = edge[1]
        elif edge[1] == node:
            n = edge[0]
        else:
            raise Exception("Problem reading edge.")
        
        if not output.has_edge(node, n) and not output.has_edge(n, node):
            output.add_edge(node, n)
            output.edges[node, n]["color"] = color            

        if n not in visited:
            reroot_inward(n, source, output, visited)


def reroot_outward(node, source, output, visited=None):
    visited = visited or []
    visited.append(node)
    edges = list(source.in_edges(node)) + list(source.out_edges(node))
    for edge in edges:
        color = source.edges[edge].get("color", "black")
        if edge[0] == node:
            n = edge[1]
        elif edge[1] == node:
            n = edge[0]
        else:
            raise Exception("Problem reading edge.")
        
        if not output.has_edge(node, n) and not output.has_edge(n, node):
            output.add_edge(edge[0], edge[1])
            output.edges[edge[0], edge[1]]["color"] = color

        if n not in visited:
            reroot_outward(n, source, output, visited)


@app.command()
def to_dot(
    stem_file: Path, 
    dot_file:Path, 
    root: str = None,
    mixture_edge_color: str = "red",
    root_color: str = "red",
    hypothetical_node_color: str = "gray",
    colors: Path = None,
    dotted_percentage: int = 33,
    dashed_percentage: int = 67,
):
    graph = nx.DiGraph()

    # Read the .stem file from STEMMA and create a graph using networkx
    with open(stem_file) as f:
        for line in f:
            if m := re.match(r"Link: (.*?) ([-=])> (.*?)\s+\|", line):
                start = m.group(1)
                end = m.group(3)
                graph.add_edge(start, end)
                if m.group(2) == "=":
                    graph.edges[start, end]['color'] = mixture_edge_color

    # Create a new graph that is rooted at the first node
    if root:
        rerooted = nx.DiGraph()
        reroot_inward(root, graph, rerooted)
        reroot_outward(root, graph, rerooted)    
        graph = rerooted    

    # Parse colors file
    colors_dict = {}
    if colors:
        with open(colors, 'rb') as f:
            if colors.suffix == ".json":
                colors_dict = json.load(f)
            elif colors.suffix == ".toml":
                colors_dict = tomli.load(f)
            else:
                raise Exception("Unknown file type for colors file.")

    # Colorize the nodes
    for node in graph.nodes:
        graph.nodes[node]["label"] = node                            
        if node.startswith("["):
            graph.nodes[node]["color"] = hypothetical_node_color
            graph.nodes[node]["label"] = ""    
            graph.nodes[node]["shape"] = "circle"
            graph.nodes[node]["fixedsize"] = "true"
            graph.nodes[node]["style"] = "filled"
            graph.nodes[node]["fillcolor"] = hypothetical_node_color
        elif node == root:
            graph.nodes[node]["color"] = root_color

        for pattern, color in colors_dict.items():
            if re.match(pattern, node):
                graph.nodes[node]["color"] = color
                break # only use first match

    # Read input file again to get the mixed nodes and their percentages
    mixed_node = None
    with open(stem_file) as f:
        for line in f:
            if m := re.match(r"Mixed Node\s(.*?)\s", line):
                mixed_node = m.group(1)
            elif m:= re.match(r"Mixed %ages: (.*)$", line):
                for link in m.group(1).split():
                    start, percentage = link.split("=")
                    graph.edges[start, mixed_node]["label"] = percentage
                    percentage_int = int(percentage[:-1])
                    if percentage_int < dotted_percentage:
                        style = "dotted"
                    elif percentage_int < dashed_percentage:
                        style = "dashed"
                    else:
                        style = "solid"
                    graph.edges[start, mixed_node]["style"] = style

    # Write the graph to a .dot file
    nx.drawing.nx_pydot.write_dot(graph, dot_file)
