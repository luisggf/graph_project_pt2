from graph_analysis import *
import matplotlib.pyplot as plt

# declaracao teste inicial de variaveis
start_year = 2023
threshold = 0.9
chosen_parties = ['PT', 'PSOL']
graph = Weighted_Graph()
graph_normalized = Weighted_Graph()
graph_inverted = Weighted_Graph()
graph_threshold = Weighted_Graph()

# leitura e filtragem inicial de dataframes
df1, df2 = graph.read_dataframes_by_year(start_year, chosen_parties)
# criação de todas filtragens
graph_normalized = graph.set_normalized_graph(df1, df2)
graph_threshold = graph_normalized.apply_threshold(threshold)
graph_inverted = graph_threshold.weight_inversion()

# plotagem primeiro grafico
graph_threshold = graph_threshold.to_networkx()
betweenness_centrality = nx.betweenness_centrality(graph_threshold)
filtered_deputies = [node for node in betweenness_centrality]
filtered_centralities = {node: betweenness_centrality[node] for node in filtered_deputies}
sorted_centralities = dict(sorted(filtered_centralities.items(), key=lambda item: item[1], reverse=True))
plt.bar(sorted_centralities.keys(), sorted_centralities.values())
plt.xlabel('Deputados')
plt.ylabel('Centralidade')
plt.title('Medida de Centralidade para Deputados do PT e PSOL (2023, Threshold 90%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('./grafics/centralidade_grafico_2023_psol_pt.png')
plt.show()