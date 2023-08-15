from graph_analysis import *

# declaracao teste inicial de variaveis
start_year = 2023
threshold = 0.3
chosen_parties = ['PT', 'PSOL']
graph = Weighted_Graph()
graph_normalized = Weighted_Graph()
graph_inverted = Weighted_Graph()
graph_threshold = Weighted_Graph()

# leitura e filtragem inicial de dataframes
df1, df2 = graph.read_dataframes_by_year(start_year, chosen_parties)
# criação de todas filtragens
graph_normalized = graph.set_normalized_graph(df1, df2)
# graph_threshold = graph_normalized.apply_threshold(threshold)
# graph_inverted = graRph_threshold.weight_inversion()


# graph_threshold.get_centrality_graphic(chosen_parties, start_year, threshold)
graph_normalized.get_heatmap(df2, chosen_parties, start_year)
