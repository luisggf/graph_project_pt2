import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr


class Weighted_Graph:
    def __init__(self):
        self.adj_list = {}
        self.node_count = 0
        self.edge_count = 0

    def add_node(self, node):
        if node not in self.adj_list:
            self.adj_list[node] = {}
            self.node_count += 1

    def add_edge(self, node1, node2, weight):
        if node1 not in self.adj_list:
            self.add_node(node1)
        if node2 not in self.adj_list:
            self.add_node(node2)
        self.adj_list[node1][node2] = weight
        self.edge_count += 1

    def add_two_way_edge(self, node1, node2, weight):
        self.add_edge(node1, node2, weight)
        self.add_edge(node2, node1, weight)

    def remove_node(self, node):
        for node2 in self.adj_list:
            if node in self.adj_list[node2]:
                self.adj_list[node2].pop(node)
                self.edge_count -= 1
        self.edge_count -= len(self.adj_list[node])
        self.node_count -= 1
        self.adj_list.pop(node)

    def remove_edge(self, node1, node2):
        try:
            del self.adj_list[node1][node2]
            self.edge_count -= 1
        except KeyError as e:
            print(f"WARN: Node {e} does not exist")
        except ValueError as e:
            print(f"WARN: Edge {node1} -> {node2} does not exist")

    def there_is_edge(self, node1, node2):
        if node1 == node2:
            return False
        if node1 in self.adj_list and node2 in self.adj_list[node1]:
            return True
        return False

    def get_edge_weight(self, node1, node2):
        if node1 in self.adj_list and node2 in self.adj_list[node1]:
            return self.adj_list[node1][node2]
        return None

    def degree_out(self, node):
        return len(self.adj_list[node])
    
    def union(self, other_graph):
        result_graph = Weighted_Graph()

        for node in self.adj_list:
            result_graph.add_node(node)

        for node in other_graph.adj_list:
            if node not in result_graph.adj_list:
                result_graph.add_node(node)

        for node1 in self.adj_list:
            for node2, weight in self.adj_list[node1].items():
                result_graph.add_edge(node1, node2, weight)

        for node1 in other_graph.adj_list:
            for node2, weight in other_graph.adj_list[node1].items():
                if node1 not in result_graph.adj_list or node2 not in result_graph.adj_list[node1]:
                    result_graph.add_edge(node1, node2, weight)

        return result_graph
    
    def get_neighbors(self, node):
        try:
            return iter(self.adj_list[node])
        except KeyError:
            print("Node doesnt exist!")



    def read_dataframes_by_year(self, year, chosen_parties):

        graph_filename = f'./dataset/graph{year}.csv'
        politicians_filename = f'./dataset/politicians{year}.csv'
        try:
            graph_df = pd.read_csv(graph_filename, delimiter=';', header=None, names=['Source', 'Target', 'Weight'])
            politicians_df = pd.read_csv(politicians_filename, delimiter=';', header=None, names=['Politician', 'Party', 'Value'])
            
            if chosen_parties:
                politicians_df = politicians_df[politicians_df['Party'].isin(chosen_parties)]

            # Filtrar linhas do graph_df com base nos deputados presentes no politicians_df
            common_politicians = politicians_df['Politician'].tolist()
            graph_df = graph_df[(graph_df['Source'].isin(common_politicians)) & (graph_df['Target'].isin(common_politicians))]

        except FileNotFoundError:
            print(f"Arquivo não encontrado para o ano {year}")
        return graph_df, politicians_df

    
    def set_normalized_graph(self, graph_df, politicians_df):   
        for _, line in graph_df.iterrows():
            self.add_two_way_edge(line['Source'], line['Target'], line['Weight'])
        
        votes_dict = {}
        for _, row in politicians_df.iterrows():
            politician = row['Politician']
            value = row['Value']
            votes_dict[politician] = value

        for node1 in self.adj_list:
            for node2 in self.adj_list[node1]:
                if node1 in votes_dict:
                    votes_nodes1 = votes_dict[node1]
                if node2 in votes_dict:
                    votes_nodes2 = votes_dict[node2]
                normalization_factor = min(votes_nodes1, votes_nodes2)
                normalized_weight = self.adj_list[node1][node2] / normalization_factor
                self.adj_list[node1][node2] = normalized_weight

        return self

    def apply_threshold(self, threshold):  
        to_delete = []      
        for nodes in self.adj_list:
            for neighbors in self.adj_list[nodes]:
                if self.adj_list[nodes][neighbors] < threshold:
                    to_delete.append((nodes, neighbors))
        for node, neighbor in to_delete:
            self.remove_edge(node, neighbor)
        return self
    
    def weight_inversion(self):  
        for nodes in self.adj_list:
            for neighbors in self.adj_list[nodes]:
                weight = self.adj_list[nodes][neighbors]
                self.adj_list[nodes][neighbors] = 1 - weight
        return self
    
    def to_networkx(self):
        G = nx.Graph()
        
        for source, neighbors in self.adj_list.items():
            for target, weight in neighbors.items():
                G.add_edge(source, target, weight=weight)
        return G
    
    # plotagem primeiro grafico
    def get_centrality_graphic(graph_threshold, parties, year, threshold):
        graph_threshold = graph_threshold.to_networkx()
        betweenness_centrality = nx.betweenness_centrality(graph_threshold)
        filtered_deputies = [node for node in betweenness_centrality]
        filtered_centralities = {node: betweenness_centrality[node] for node in filtered_deputies}
        sorted_centralities = dict(sorted(filtered_centralities.items(), key=lambda item: item[1], reverse=True))
        plt.bar(sorted_centralities.keys(), sorted_centralities.values())
        plt.xlabel('Deputados')
        plt.ylabel('Centralidade')
        plt.title(f'Medida de Centralidade para Deputados dos partidos {parties}  ({year}, Threshold: {threshold})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'./graphics/centralidade_grafico_{year}_{parties}.png')
        plt.show()

    # plotagem heatmap
    def get_heatmap(graph_normalized, politician_df, parties, year):
        diff_centralities_matrix = []
        nodes = list(graph_normalized.adj_list.keys())
        
        # Criar um mapeamento entre os nomes dos políticos e seus partidos
        politician_to_party = {row['Politician']: row['Party'] for _, row in politician_df.iterrows()}
        
        # Ordenar os nós (políticos) por partido e, em seguida, por nome
        nodes.sort(key=lambda node: politician_to_party.get(node, ''))

        for dep1 in nodes:
            row = []
            for dep2 in nodes:
                if graph_normalized.there_is_edge(dep1, dep2):
                    diff = graph_normalized.adj_list[dep1][dep2]
                    row.append(diff)
                else:
                    row.append(0)  # Se não houver conexão, o peso é 0
            diff_centralities_matrix.append(row)
        
        df = pd.DataFrame(diff_centralities_matrix, index=nodes, columns=nodes)
        
        plt.figure(figsize=(8, 8))
        heatmap = sns.heatmap(df, vmin=0, vmax=1, cmap='inferno')
        
        # Definir rótulos nos eixos x e y
        x_labels = [f'{node}-({politician_to_party.get(node, "")})' for node in nodes]
        y_labels = [f'{node}-({politician_to_party.get(node, "")})' for node in nodes]
        
        heatmap.set_xticks(range(len(nodes)))
        heatmap.set_yticks(range(len(nodes)))
        heatmap.set_xticklabels(x_labels, rotation=90, ha='center', fontsize=8)
        heatmap.set_yticklabels(y_labels, rotation=0, ha='right', fontsize=8)
        
        plt.title(f'HeatMap dos Pesos Normalizados dos Partidos {parties}, Ano {year}')
        plt.tight_layout()
        plt.show()

    
