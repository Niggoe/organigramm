import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# HTML template for the webpage
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Organigramm</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Organigramm</h1>
        {{ plot | safe }}
    </div>
</body>
</html>
'''

def create_organigram():
    # Read in all persons from the database
    # Read CSV file using pandas
    df = pd.read_csv("organigramm.csv", sep=";")
    
    # Create a dictionary to store the hierarchy relationships
    vorgesetzter2reportingline = {}
    
    # Finde die Top-Level Manager (diejenigen, die keine Vorgesetzten sind)
    all_employees = set()
    all_supervisors = set()
    
    for index, row in df.iterrows():
        employee = row['Vorname'] + " " + row['Name']
        supervisor = row['Vorgesetzter']
        all_employees.add(employee)
        if pd.notna(supervisor):
            all_supervisors.add(supervisor)
    
    # Finde die Top-Level Manager (diejenigen, die Vorgesetzte sind, aber keine Vorgesetzten haben)
    top_level_managers = all_supervisors - all_employees
    
    # Create nodes and edges for the hierarchy
    for index, row in df.iterrows():
        employee = row['Vorname'] + " " + row['Name']
        supervisor = row['Vorgesetzter']
        
        # Add to dictionary
        if pd.notna(supervisor):
            if supervisor in vorgesetzter2reportingline:
                vorgesetzter2reportingline[supervisor].append(employee)
            else:
                vorgesetzter2reportingline[supervisor] = [employee]
    
    # Wenn keine Top-Level Manager gefunden wurden, nehmen wir den ersten Vorgesetzten als Top-Level Manager
    if not top_level_managers:
        first_supervisor = next(iter(all_supervisors))
        top_level_managers = {first_supervisor}
    
    # Füge einen künstlichen Root-Knoten hinzu und verbinde ihn mit den Top-Level Managern
    vorgesetzter2reportingline["Schalke 04"] = list(top_level_managers)
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add edges to the graph
    for supervisor, employees in vorgesetzter2reportingline.items():
        for employee in employees:
            G.add_edge(supervisor, employee)
    
    # Erstelle die Daten für das Sunburst-Diagramm
    ids = []
    labels = []
    parents = []
    
    # Füge den Root-Knoten hinzu
    root_node = "Schalke 04"
    ids.append(root_node)
    labels.append(root_node)
    parents.append("")
    
    # Füge alle anderen Knoten hinzu
    for edge in G.edges():
        supervisor, employee = edge
        ids.append(employee)
        labels.append(employee)
        parents.append(supervisor)
    
    # Erstelle das Sunburst-Diagramm
    fig = go.Figure()
    
    fig.add_trace(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>" +
                     "Vorgesetzter: %{parent}<br>" +
                     "<extra></extra>",
        marker=dict(
            colors=['#1f77b4'] + ['#ff7f0e'] * (len(ids) - 1),
            line=dict(color='white', width=1)
        )
    ))
    
    # Aktualisiere das Layout
    fig.update_layout(
        title='Organizational Hierarchy',
        showlegend=False,
        margin=dict(b=20,l=5,r=5,t=40),
        height=800,
        width=1000
    )
    
    # Konvertiere das Plot zu HTML
    return fig.to_html(full_html=False)

@app.route('/')
def index():
    plot = create_organigram()
    return render_template_string(HTML_TEMPLATE, plot=plot)

if __name__ == '__main__':
    # Ensure the CSV file exists
    if not os.path.exists('organigramm.csv'):
        print("Error: organigramm.csv not found!")
        exit(1)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8050, debug=True)


