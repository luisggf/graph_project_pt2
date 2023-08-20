import tkinter as tk
from graph_analysis import *
from tkinter import simpledialog, messagebox

class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise de Grafos")
        
        # Estilo para rótulos
        label_style = {"font": ("Helvetica", 8, "bold")}

        self.centrality_var = tk.IntVar()
        self.heatmap_var = tk.IntVar()
        self.graph_var = tk.IntVar()

        self.year_label = tk.Label(root, text="Ano:")
        self.year_label.pack(anchor=tk.W, padx=5)
        
        self.year_entry = tk.Entry(root)
        self.year_entry.pack(anchor=tk.W, padx=5)
        
        self.parties_label = tk.Label(root, text="Partidos (separados por vírgula):")
        self.parties_label.pack(anchor=tk.W, padx=5)
        
        self.parties_entry = tk.Entry(root)
        self.parties_entry.pack(anchor=tk.W, padx=5)
        
        self.threshold_label = tk.Label(root, text="Threshold (0 a 1):")
        self.threshold_label.pack(anchor=tk.W, padx=5)
        
        self.threshold_entry = tk.Entry(root)
        self.threshold_entry.pack(anchor=tk.W, padx=5)

        self.centrality_var = tk.IntVar()
        self.centrality_checkbutton = tk.Checkbutton(root, text="Centrality", variable=self.centrality_var, compound=tk.LEFT, **label_style)
        self.centrality_checkbutton.pack(anchor=tk.W, padx=5)

        self.heatmap_var = tk.IntVar()
        self.heatmap_checkbutton = tk.Checkbutton(root, text="HeatMap", variable=self.heatmap_var, compound=tk.LEFT, **label_style)
        self.heatmap_checkbutton.pack(anchor=tk.W, padx=5)

        self.graph_var = tk.IntVar()
        self.graph_checkbutton = tk.Checkbutton(root, text="Graph", variable=self.graph_var, compound=tk.LEFT, **label_style)
        self.graph_checkbutton.pack(anchor=tk.W, padx=5)

        plot_button_style = {"font": ("Helvetica", 14, "bold"), "bg": "#4CAF50", "fg": "white"}
        self.plot_button = tk.Button(root, text="Plotar", command=self.plot_graph, **plot_button_style)
        self.plot_button.pack(anchor=tk.W, padx=5, pady=8)
        self.success_label = tk.Label(root, text="", fg="green", **label_style)
        self.success_label.pack(anchor=tk.W, padx=5)
        


    def plot_graph(self):
        try:
            graph = Weighted_Graph()
            graph_normalized = Weighted_Graph()
            graph_threshold = Weighted_Graph()
            
            year_str = self.year_entry.get()
            year = int(year_str)
            if 2002 <= year <= 2023:
                pass
            else:
                messagebox.showerror("Erro", "Ano inválido. Digite um ano entre 2002 e 2023.")
                return
            
            parties = self.parties_entry.get().split(',')
            parties = [party.strip().upper() for party in parties]
            
            threshold_str = self.threshold_entry.get()
            threshold = float(threshold_str)
            if 0 <= threshold <= 1:
                pass
            elif 0 <= threshold <= 100:
                threshold = threshold / 100
            else:
                messagebox.showerror("Erro", "Valor inválido para o threshold. Deve ser um valor entre 0 e 1 ou 0 e 100%.")
                return
            
            df1, df2 = graph.read_dataframes_by_year(year, parties)
            graph_normalized = graph.set_normalized_graph(df1, df2)
            graph_normalized_copy = graph_normalized.create_copy()
            graph_threshold = graph_normalized_copy.apply_threshold(threshold)

            if self.centrality_var.get() == 1:
                graph_threshold.get_centrality_graphic(parties, year, threshold)
            if self.heatmap_var.get() == 1:
                graph_normalized.get_heatmap(df2, parties, year)
            if self.graph_var.get() == 1:
                graph_threshold.draw_weighted_graph(df2, year, parties)

            self.success_label.config(text="Gráfico plotado e salvo com sucesso!")
  
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos")