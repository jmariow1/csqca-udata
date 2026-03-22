import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import os
import sys

# Função para garantir que o ícone funcione dentro do .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LabQCAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratório - Análise csQCA")
        self.root.geometry("800x600")
        
        # Configuração do Ícone da Janela
        icon_file = resource_path("1000068048.ico")
        try:
            self.root.iconbitmap(icon_file)
        except:
            pass # Falha silenciosa se não achar o ícone em dev

        # Variáveis
        self.df = None
        self.file_path = ""

        # Layout Principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Cabeçalho
        lbl_title = tk.Label(main_frame, text="Análise csQCA Simplificada", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # Botão Upload
        btn_upload = tk.Button(main_frame, text="Carregar Arquivo CSV", command=self.upload_file, bg="#005f73", fg="white", font=("Arial", 11))
        btn_upload.pack(pady=5)
        
        self.lbl_status = tk.Label(main_frame, text="Nenhum arquivo carregado", fg="gray")
        self.lbl_status.pack()

        # Área de Botões de Ação
        action_frame = tk.Frame(main_frame)
        action_frame.pack(pady=20)

        self.btn_truth = tk.Button(action_frame, text="Gerar Tabela Verdade", command=self.generate_truth_table, state="disabled", width=20)
        self.btn_truth.pack(side="left", padx=10)

        self.btn_venn = tk.Button(action_frame, text="Gerar Diagrama de Venn", command=self.generate_venn, state="disabled", width=20)
        self.btn_venn.pack(side="left", padx=10)

        # Área de Resultados (Tabela)
        self.tree_frame = tk.Frame(main_frame)
        self.tree_frame.pack(expand=True, fill="both")
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(side="left", expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def upload_file(self):
        file = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if file:
            try:
                self.df = pd.read_csv(file)
                self.file_path = file
                self.lbl_status.config(text=f"Arquivo carregado: {os.path.basename(file)} ({len(self.df)} linhas)")
                self.btn_truth.config(state="normal")
                self.btn_venn.config(state="normal")
                messagebox.showinfo("Sucesso", "Dados carregados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo: {e}")

    def generate_truth_table(self):
        if self.df is not None:
            # Lógica csQCA: Agrupar combinações idênticas de variáveis
            # Assumindo que a última coluna é o Resultado (Outcome) e as outras são Condições
            cols = list(self.df.columns)
            conditions = cols[:-1]
            outcome = cols[-1]

            # Agrupa pelas condições e conta frequência e consistência do resultado
            truth_table = self.df.groupby(conditions)[outcome].agg(['count', 'mean']).reset_index()
            truth_table.rename(columns={'count': 'Nº Casos', 'mean': 'Consistência'}, inplace=True)
            
            # Exibir na GUI
            self.display_table(truth_table)

    def generate_venn(self):
        if self.df is not None:
            cols = list(self.df.columns)
            # Simples implementação para 2 ou 3 primeiras variáveis para visualização
            # QCA completo requereria configurações complexas, aqui focamos na visualização de conjuntos
            
            plt.figure(figsize=(8, 8))
            plt.title("Interseção das Condições (Visualização de Conjuntos)")
            
            # Convertendo para booleanos se não forem
            data_bool = self.df.astype(bool)
            
            if len(cols) >= 3:
                # Pega as 3 primeiras colunas para o diagrama
                set1 = set(data_bool[data_bool.iloc[:, 0] == 1].index)
                set2 = set(data_bool[data_bool.iloc[:, 1] == 1].index)
                set3 = set(data_bool[data_bool.iloc[:, 2] == 1].index)
                
                v = venn3([set1, set2, set3], set_labels=(cols[0], cols[1], cols[2]))
            
            elif len(cols) == 2:
                set1 = set(data_bool[data_bool.iloc[:, 0] == 1].index)
                set2 = set(data_bool[data_bool.iloc[:, 1] == 1].index)
                v = venn2([set1, set2], set_labels=(cols[0], cols[1]))
            
            else:
                messagebox.showwarning("Aviso", "São necessárias pelo menos 2 variáveis para um Diagrama de Venn.")
                return

            plt.show()

    def display_table(self, df_display):
        # Limpa tabela anterior
        self.tree.delete(*self.tree.get_children())
        
        self.tree["column"] = list(df_display.columns)
        self.tree["show"] = "headings"
        
        for col in self.tree["column"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        df_rows = df_display.to_numpy().tolist()
        for row in df_rows:
            # Formata floats para 2 casas decimais
            formatted_row = [f"{x:.2f}" if isinstance(x, float) else x for x in row]
            self.tree.insert("", "end", values=formatted_row)

if __name__ == "__main__":
    root = tk.Tk()
    app = LabQCAApp(root)
    root.mainloop()