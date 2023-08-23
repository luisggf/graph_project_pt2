from tooltip import *
from graph_analysis import *
from tkinter import simpledialog, messagebox
from math import ceil


class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise de Grafos")
        label_style = {"font": ("Helvetica", 8, "bold")}

        party_colors = set_dict_colours()

        self.centrality_var = tk.IntVar()
        self.heatmap_var = tk.IntVar()
        self.graph_var = tk.IntVar()

        self.year_label = tk.Label(root, text="Ano:")
        self.year_label.pack(anchor=tk.W, padx=5)
        
        self.year_entry = tk.Entry(root)
        self.year_entry.pack(anchor=tk.W, padx=5)

        # implementação de multiseleção de partidos
        self.parties_label = tk.Label(root, text="Partidos:")
        self.parties_label.pack(anchor=tk.W, padx=5, pady=(15,5))

        party_buttons_frame = tk.Frame(root)
        party_buttons_frame.pack()

        party_buttons_per_column = 10  
        num_columns = ceil(len(party_colors) / party_buttons_per_column)
        columns = []
        self.party_buttons = {}
        for i in range(num_columns):
            column_frame = tk.Frame(party_buttons_frame)
            column_frame.pack(side=tk.LEFT, padx=10) 
            columns.append(column_frame)

        column_index = 0
        for party, color in party_colors.items():
            
            button = tk.Button(columns[column_index], text=party, command=lambda p=party: self.toggle_party(p, party_colors), **label_style)
            button.pack(anchor=tk.W, padx=5, pady=2)
            button.config(width=12)  
            self.party_buttons[party] = button

            column_index += 1
            if column_index >= num_columns:
                column_index = 0
        
        self.threshold_label = tk.Label(root, text="Threshold (0 a 1):")
        self.threshold_label.pack(anchor=tk.W, padx=5, pady=(20,0))

        self.threshold_frame = tk.Frame(root)
        self.threshold_frame.pack(anchor=tk.W, padx=5)

        self.threshold_entry = tk.Entry(self.threshold_frame)
        self.threshold_entry.grid(row=0, column=0, padx=(0, 5))  # Campo de entrada na primeira coluna com margem à direita

        threshold_help_button_style = {"font": ("Helvetica", 7, "bold"), "bg": "#4CAF50", "fg": "white"}
        self.threshold_help_button = tk.Button(self.threshold_frame, text="?", command=self.show_threshold_tooltip, **threshold_help_button_style)
        self.threshold_help_button.grid(row=0, column=1) 

        self.centrality_var = tk.IntVar()
        self.centrality_checkbutton = tk.Checkbutton(root, text="Centrality", variable=self.centrality_var, compound=tk.LEFT, **label_style)
        self.centrality_checkbutton.pack(anchor=tk.W, padx=5, pady=(10,0))

        self.heatmap_var = tk.IntVar()
        self.heatmap_checkbutton = tk.Checkbutton(root, text="HeatMap", variable=self.heatmap_var, compound=tk.LEFT, **label_style)
        self.heatmap_checkbutton.pack(anchor=tk.W, padx=5)

        self.graph_var = tk.IntVar()
        self.graph_checkbutton = tk.Checkbutton(root, text="Graph", variable=self.graph_var, compound=tk.LEFT, **label_style)
        self.graph_checkbutton.pack(anchor=tk.W, padx=5)

        plot_button_style = {"font": ("Helvetica", 14, "bold"), "bg": "#4CAF50", "fg": "white"}
        self.plot_button = tk.Button(root, text="Plotar", command=self.plot_graph, **plot_button_style)
        self.plot_button.pack(anchor=tk.W, padx=5, pady=(15,0))
        self.success_label = tk.Label(root, text="", fg="green", **label_style)
        self.success_label.pack(anchor=tk.W, padx=5)


    def plot_graph(self):
        try:
            graph = Weighted_Graph()
            graph_normalized = Weighted_Graph()
            graph_threshold = Weighted_Graph()
            
            party_colors = set_dict_colours()
            parties = self.get_selected_parties()
            # se nenhum partido foi selecionado, preenche com lista de 40 partidos
            if not parties:
                for party, color in party_colors.items():
                    parties.append(party)

            # se em parties tiver algum partido que não exista na lista estatica a remove 
            # (muitos partidos foram renomeados ou nao existem mais)
            for party in parties:
                if party not in party_colors:
                    parties.remove(party)

            year_str = self.year_entry.get()
            year = int(year_str)
            if 2002 <= year <= 2023:
                pass
            else:
                messagebox.showerror("Erro", "Ano inválido. Digite um ano entre 2002 e 2023.")
                return
            
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

            for party in parties:
                if party not in df2['Party'].unique():
                    messagebox.showerror("Erro", f"Partido {party} não existe para o ano: {year}")
                    return

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

    
    def show_threshold_tooltip(self):
        tooltip_text = (
            "Threshold é um tipo de filtragem que remove valores de peso entre deputados\n"
            "menores que o valor especificado. Você pode inserir um valor entre 0 e 1 ou\n"
            "0 e 100%, que representa a porcentagem de concordância necessária para\n"
            "que uma conexão entre deputados seja mantida no grafo."
        )
        tooltip = Tooltip(self.threshold_help_button, tooltip_text)

    def toggle_party(self, party, party_colors):
        if self.party_buttons[party]['relief'] == tk.SUNKEN:
            self.party_buttons[party]['relief'] = tk.RAISED
            self.party_buttons[party]['bg'] = '#f0f0f0'
        else:
            self.party_buttons[party]['relief'] = tk.SUNKEN
            self.party_buttons[party]['bg'] = party_colors[party]  # Set the original color


    def get_selected_parties(self):
        selected_parties = [party for party, button in self.party_buttons.items() if button['relief'] == tk.SUNKEN]
        return selected_parties
    


