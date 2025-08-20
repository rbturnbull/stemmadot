from pathlib import Path
import typer
import re
import networkx as nx
import json
import tomli
from networkx.drawing import nx_agraph

app = typer.Typer()

def clean_name(name: str) -> str:
    """Clean the node name by removing any trailing punctuation."""
    if ":" in name:
        name = f'"{name}"'
    return name.strip()

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
            if n in visited:
                edge = (n, node)
            else:
                edge = (node, n)
            output.add_edge(*edge)
            output.edges[edge[0], edge[1]]["color"] = color            

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
    output_file:Path, 
    root: str = None,
    mixture_edge_color: str = "red",
    root_color: str = "red",
    hypothetical_node_color: str = "gray",
    colors: Path = None,
    dotted: int = 33,
    dashed: int = 67,
    engine: str = "dot",
):
    graph = nx.DiGraph()

    # Read the .stem file from STEMMA and create a graph using networkx
    with open(stem_file) as f:
        for line in f:
            if m := re.match(r"Link: (.*?) ([-=])> (.*?)\s+\|", line):
                start = clean_name(m.group(1).split(" ")[0])
                end = clean_name(m.group(3).split(" ")[0])

                graph.add_edge(start, end)
                if m.group(2) == "=":
                    graph.edges[start, end]['color'] = mixture_edge_color

    # Create a new graph that is rooted at the first node
    if root:
        rerooted = nx.DiGraph()
        reroot_inward(root, graph, rerooted)
        reroot_outward(root, graph, rerooted)    
        graph = rerooted    

    # Read input file again to get the mixed nodes and their percentages
    mixed_node = None
    with open(stem_file) as f:
        for line in f:
            if m := re.match(r"Mixed Node\s(.*?)\s", line):
                mixed_node = clean_name(m.group(1))
            if mixed_node:
                if m := re.match(r"\s+\d+\s(.*?)\s*: --->\s*\d+\s+(\d+)%", line):
                    start = clean_name(m.group(1))
                    percentage = m.group(2) + "%"
                    edge = (start, mixed_node)
                    if not edge in graph.edges:
                        edge = (mixed_node, start)

                    if not edge in graph.edges:
                        raise Exception(f"edge not found: {start} {mixed_node}")

                    graph.edges[edge]["label"] = percentage
                    graph.edges[edge]["fontcolor"] = mixture_edge_color

                    # Determine the style based on the percentage
                    percentage_int = int(percentage[:-1])
                    if percentage_int < dotted:
                        style = "dotted"
                    elif percentage_int < dashed:
                        style = "dashed"
                    else:
                        style = "solid"
                    graph.edges[edge]["style"] = style

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

    # Write the graph to a .dot file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    A = nx_agraph.to_agraph(graph)

    # Global layout knobs
    if engine == "dot":  # great for DAGs
        A.graph_attr.update(
            ranksep="1.5 equally",  # more vertical space between ranks
            # nodesep="0.5",          # more space between nodes in same rank
            splines="spline",
            # concentrate="true",
            dpi="200",
        )
    elif engine in {"sfdp", "neato", "fdp"}:
        A.graph_attr.update(
            overlap="false",  # avoid node overlaps
            sep="+2",         # padding between nodes (points)
            splines="spline",
            dpi="200",
        )
        if engine in {"neato", "fdp"}:
            A.graph_attr.update(K="1.2")  # spread out a bit more

    # Default node/edge cosmetics (optional)
    A.node_attr.update(shape="ellipse", fontsize="20")
    A.edge_attr.update(penwidth="1.2")

    fmt = output_file.suffix.lower().lstrip(".")
    # Map jpg -> jpg
    if fmt == "jpeg": fmt = "jpg"

    # Choose engine program and render
    prog = engine  # "dot", "sfdp", "neato", or "fdp"
    A.draw(str(output_file), format=fmt, prog=prog)

