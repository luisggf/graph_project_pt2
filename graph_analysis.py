import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random
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

        # Filtrar os deputados
        filtered_deputies = []
        for node in betweenness_centrality:
            filtered_deputies.append(node)

        # Criar um dicionário das centralidades filtradas
        filtered_centralities = {}
        for node in filtered_deputies:
            filtered_centralities[node] = betweenness_centrality[node]

        sorted_centralities = dict(sorted(filtered_centralities.items(), key=lambda item: item[1], reverse=True))
        plt.bar(sorted_centralities.keys(), sorted_centralities.values())
        plt.xlabel('Deputados')
        plt.ylabel('Centralidade')
        plt.title(f'Medida de Centralidade para Deputados dos partidos {parties},  ({year}, Threshold: {threshold})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'./graphics/centralidade_grafico_{year}_{parties}.pdf')
        plt.show()



    # plotagem heatmap
    def get_heatmap(graph_normalized, politician_df, parties, year):
        diff_centralities_matrix = []
        nodes = list(graph_normalized.adj_list.keys())
        
        # mapear politicos e seus partidos
        politician_to_party = {}
        for _, row in politician_df.iterrows():
            politician_name = row['Politician']
            party_name = row['Party']
            politician_to_party[politician_name] = party_name

        # ordenação por partido
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
        
        # é pesado mas fazer o que né
        df = pd.DataFrame(diff_centralities_matrix, index=nodes, columns=nodes)
        
        plt.figure(figsize=(10, 8))
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
        plt.savefig(f'./graphics/heatmap_{year}_{parties}.pdf')
        plt.show()


    # gerar grafo de acordo com o partido de cada politico
    def draw_weighted_graph(weighted_graph, politician_df, year, parties):
        G = nx.Graph()

        for node1 in weighted_graph.adj_list:
            G.add_node(node1)
            for node2, weight in weighted_graph.adj_list[node1].items():
                G.add_edge(node1, node2, weight=weight)

        party_colors = set_dict_colours()
        node_colors = []
        for node in G.nodes():
            politician_row = politician_df.loc[politician_df['Politician'] == node]
            party = politician_row['Party'].iloc[0]
            color = party_colors[party]
            node_colors.append(color)

        pos = nx.spring_layout(G)

        edge_weights = []
        for _, _, data in G.edges(data=True):
            weight = data['weight']
            edge_weights.append(weight)
        
        legend_labels = []
        for party in party_colors:
            if party in politician_df['Party'].unique():
                legend_labels.append(plt.Line2D([], [], color=party_colors[party], marker='o', markersize=8, label=party))

        plt.figure(figsize=(12, 10))
        nx.draw(G, pos, node_size=70, edge_color='grey', width=edge_weights,
                node_color=node_colors, with_labels=True, font_size = 8)
        plt.title('Visualização do Grafo Ponderado de Relações de Votos entre Deputados por Partido')
        plt.legend(handles=legend_labels, loc='upper right')
        plt.tight_layout()
        plt.savefig(f'./graphics/grafo_{year}_{parties}.pdf')
        plt.show()


    def create_copy(self):
        copied_graph = Weighted_Graph()
        copied_graph.adj_list = {node: {neighbor: weight for neighbor, weight in adj.items()} for node, adj in self.adj_list.items()}
        return copied_graph


# dicionário para cobrir todos partidos possiveis e poder plotar o grafo
def set_dict_colours():
    party_colors = {
        'MDB': generate_random_color(),
        'PTB': generate_random_color(),
        'PDT': generate_random_color(),
        'PT': generate_random_color(),
        'PCdoB': generate_random_color(),
        'PSB': generate_random_color(),
        'PSDB': generate_random_color(),
        'AGIR': generate_random_color(),
        'PMN': generate_random_color(),
        'CIDADANIA': generate_random_color(),
        'PV': generate_random_color(),
        'AVANTE': generate_random_color(),
        'PP': generate_random_color(),
        'PSTU': generate_random_color(),
        'PCB': generate_random_color(),
        'PRTB': generate_random_color(),
        'DC': generate_random_color(),
        'PCO': generate_random_color(),
        'PODE': generate_random_color(),
        'REPUBLICANOS': generate_random_color(),
        'PSOL': generate_random_color(),
        'PL': generate_random_color(),
        'PSD': generate_random_color(),
        'PATRIOTA': generate_random_color(),
        'SOLIDARIEDADE': generate_random_color(),
        'NOVO': generate_random_color(),
        'REDE': generate_random_color(),
        'PMB': generate_random_color(),
        'UP': generate_random_color(),
        'UNIÃO': generate_random_color()
    }
    return party_colors

def generate_random_color():
    color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color

# interface em terminal
def get_user_input():
    while True:
        try:
            start_year = int(input("Digite o ano de análise (2002 a 2023): "))
            if start_year < 2002 or start_year > 2023:
                print("Ano inválido. Digite um ano entre 2002 e 2023.")
                continue

            chosen_parties = input("Digite os partidos de análise separados por vírgula: ").split(',')
            chosen_parties = [party.strip().upper() for party in chosen_parties]

            threshold_str = input("Digite o valor do threshold (0 a 1 ou 0 a 100%): ")
            threshold = float(threshold_str)
            if 0 <= threshold <= 1:
                threshold = threshold
            elif 0 <= threshold <= 100:
                threshold = threshold / 100
            else:
                print("Valor inválido para o threshold. Deve ser um valor entre 0 e 1 ou 0 e 100%.")
                continue

            return start_year, chosen_parties, threshold

        except ValueError:
            print("Entrada inválida. Certifique-se de fornecer valores numéricos válidos.")
            
# interface em terminal
def interactive_interface(graph, graph_normalized, graph_threshold, df2, chosen_parties, start_year, threshold):
    while True:
        print("Escolha o gráfico para plotar:")
        print("1 - Gráfico de Centralidade")
        print("2 - Heatmap")
        print("3 - Grafo Ponderado")
        print("0 - Sair")
        choice = input("Digite o número da opção desejada: ")

        if choice == '0':
            break
        elif choice == '1':
            graph_threshold.get_centrality_graphic(chosen_parties, start_year, threshold)
        elif choice == '2':
            graph_normalized.get_heatmap(df2, chosen_parties, start_year)
        elif choice == '3':
            graph_threshold.draw_weighted_graph(df2)
        else:
            print("Opção inválida. Digite novamente.")