import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def hierarchical_layout(G):
    """Erstellt ein hierarchisches Layout für den Graphen im Dendrogramm-Stil."""
    # Finde die Wurzel (Node ohne eingehende Kanten)
    roots = [n for n in G.nodes() if G.in_degree(n) == 0]
    if not roots:
        return nx.spring_layout(G)
    
    root = roots[0]
    pos = {}
    levels = {}
    
    # BFS um Level zu bestimmen
    queue = [(root, 0)]
    visited = {root}
    
    while queue:
        node, level = queue.pop(0)
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
        
        # Kinder zum Queue hinzufügen
        children = list(G.successors(node))
        for child in children:
            if child not in visited:
                visited.add(child)
                queue.append((child, level + 1))
    
    # Positionen berechnen
    max_level = max(levels.keys())
    level_height = 2.0  # Größerer vertikaler Abstand zwischen den Ebenen
    
    # Berechne die maximale Anzahl von Knoten in einer Ebene
    max_nodes_in_level = max(len(nodes) for nodes in levels.values())
    
    for level in levels:
        nodes = levels[level]
        n_nodes = len(nodes)
        # Horizontale Verteilung mit gleichmäßigen Abständen
        for i, node in enumerate(nodes):
            # Berechne die Position basierend auf der maximalen Anzahl von Knoten
            x = (i - (n_nodes - 1) / 2) * (max_nodes_in_level / n_nodes)
            y = -level * level_height
            pos[node] = (x, y)
    
    return pos

def erstelle_organigramm(csv_datei):
    """Erstellt ein Organigramm aus einer CSV-Datei mit networkx."""

    try:
        # CSV-Datei einlesen
        df = pd.read_csv(csv_datei, sep=';')

        # Graph erstellen
        G = nx.DiGraph()

        # Knoten und Kanten hinzufügen
        for _, row in df.iterrows():
            mitarbeiter = f"{row['Vorname']} {row['Name']}"
            vorgesetzter = row['Vorgesetzter']

            G.add_node(mitarbeiter)  # Mitarbeiter als Knoten hinzufügen

            if pd.notna(vorgesetzter):  # Vorgesetzten-Beziehung als Kante hinzufügen
                G.add_edge(vorgesetzter, mitarbeiter)

        # Größere Figur erstellen
        plt.figure(figsize=(30, 20))
        
        # Hierarchisches Layout erstellen
        pos = hierarchical_layout(G)
        
        # Knoten zeichnen
        nx.draw(G, pos,
                with_labels=True,
                node_color='lightblue',
                node_size=3000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                arrowsize=20,
                width=2,
                connectionstyle='arc3,rad=0')  # Gerade Linien für dendrogramm-ähnliche Darstellung

        # Titel hinzufügen
        plt.title("Organigramm", pad=20, size=16)

        # Organigramm anzeigen
        plt.show()

    except FileNotFoundError:
        print(f"Fehler: Die Datei '{csv_datei}' wurde nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# Beispielaufruf
erstelle_organigramm("/Users/grossn/Development/python/Firma Organigramm/organigramm.csv")
