from pathlib import Path
import typer
import re
import networkx as nx

app = typer.Typer()


def fix_inward(node, source, output, visited=None):
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
            fix_inward(n, source, output, visited)


def fix_outward(node, source, output, visited=None):
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
            fix_outward(n, source, output, visited)


# def reroot(source, node, output=None, visited=None):
#     output = output or nx.DiGraph()
#     breakpoint()

#     visited = visited or []
#     visited.append(node)
#     for edge in source.edges(node):
#         color = source.edges[edge].get("color", "black")
#         if edge[0] == node:
#             n = edge[1]
#         elif edge[1] == node:
#             n = edge[0]
#         else:
#             raise Exception("Problem reading edge.")
        
#         needs_rooting = n not in visited
#         if not output.has_edge(node, n) and not output.has_edge(n, node):
#             output.add_edge(node, n)
#             output.edges[node, n]["color"] = color
        
#         if needs_rooting:
#             reroot(source, n, output, visited)

#     return output


@app.command()
def to_dot(
    stem_file: Path, 
    dot_file:Path, 
    root: str = None,
    mixture_color: str = "red",
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
                    graph.edges[start, end]['color'] = mixture_color


    # Create a new graph that is rooted at the first node
    if root:
        rerooted = nx.DiGraph()
        fix_inward(root, graph, rerooted)
        fix_outward(root, graph, rerooted)    
        graph = rerooted    

    # TODO Colorize the nodes

    # Write the graph to a .dot file
    nx.drawing.nx_pydot.write_dot(graph, dot_file)
