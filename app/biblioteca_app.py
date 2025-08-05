import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# --- LÓGICA DO BANCO DE DADOS ---
def conectar_bd():
    conn = sqlite3.connect('biblioteca.db')
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    sql_script = """
    CREATE TABLE IF NOT EXISTS Autores (
        AutorID INTEGER PRIMARY KEY, Nome TEXT NOT NULL, Nacionalidade TEXT
    );
    CREATE TABLE IF NOT EXISTS Livros (
        LivroID INTEGER PRIMARY KEY, Titulo TEXT NOT NULL, AutorID INTEGER,
        AnoPublicacao INTEGER, Genero TEXT, QuantidadeDisponivel INTEGER DEFAULT 1,
        FOREIGN KEY (AutorID) REFERENCES Autores(AutorID)
    );
    """
    cursor.executescript(sql_script)
    conn.commit()
    return conn

# --- CLASSE DA APLICAÇÃO GRÁFICA ---
class BibliotecaGUI:
    def __init__(self, root):
        self.conn = conectar_bd()
        self.livro_selecionado_id = None # Armazena o ID do livro selecionado para edição
        self.lista_de_livros_atual = [] # Armazena os dados dos livros exibidos na lista

        self.root = root
        self.root.title("Sistema de Gestão da Biblioteca")
        self.root.geometry("850x650")

        # --- Frames ---
        frame_form = ttk.Frame(self.root, padding="10")
        frame_form.pack(pady=10, padx=10, fill="x")
        
        frame_pesquisa = ttk.Frame(self.root, padding="10")
        frame_pesquisa.pack(pady=5, padx=10, fill="x")

        frame_lista = ttk.Frame(self.root, padding="10")
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Widgets do Formulário de Adição/Edição ---
        ttk.Label(frame_form, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = ttk.Entry(frame_form, width=50)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

        ttk.Label(frame_form, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_autor = ttk.Entry(frame_form, width=50)
        self.entry_autor.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        
        ttk.Label(frame_form, text="Ano:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_ano = ttk.Entry(frame_form, width=10)
        self.entry_ano.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_form, text="Gênero:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_genero = ttk.Entry(frame_form, width=20)
        self.entry_genero.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Botões de ação do formulário
        self.btn_adicionar = ttk.Button(frame_form, text="Adicionar Livro", command=self.adicionar_livro)
        self.btn_adicionar.grid(row=4, column=0, pady=10, padx=5)
        
        self.btn_salvar = ttk.Button(frame_form, text="Salvar Alterações", command=self.salvar_alteracoes)
        self.btn_salvar.grid(row=4, column=1, pady=10, padx=5)
        
        self.btn_limpar = ttk.Button(frame_form, text="Limpar Formulário", command=self.limpar_campos)
        self.btn_limpar.grid(row=4, column=2, pady=10, padx=5)

        # --- Widgets da Pesquisa e Filtro ---
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_pesquisa = ttk.Entry(frame_pesquisa, width=25)
        self.entry_pesquisa.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_pesquisar = ttk.Button(frame_pesquisa, text="Pesquisar", command=self.pesquisar_livro)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=(0, 20))
        
        # --- Dropdown (Combobox) para Gêneros ---
        ttk.Label(frame_pesquisa, text="Filtrar por Gênero:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_genero = ttk.Combobox(frame_pesquisa, state="readonly", width=20)
        self.combo_genero.pack(side=tk.LEFT)
        self.combo_genero.bind("<<ComboboxSelected>>", self.filtrar_por_genero) # Evento ao selecionar

        # --- Widgets da Lista de Livros ---
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        self.listbox_livros = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=15)
        self.listbox_livros.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_livros.yview)
        self.listbox_livros.bind('<<ListboxSelect>>', self.on_livro_select) # Evento ao clicar num livro

        self.carregar_generos()
        self.popular_lista_livros()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def popular_lista_livros(self, query=None, params=()):
        self.listbox_livros.delete(0, tk.END)
        self.lista_de_livros_atual.clear() # Limpa a lista interna
        
        cursor = self.conn.cursor()
        if query is None:
            query = """
            SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero
            FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID ORDER BY L.Titulo;
            """
        
        cursor.execute(query, params)
        self.lista_de_livros_atual = cursor.fetchall() # Armazena todos os dados, incluindo o ID
        
        for livro in self.lista_de_livros_atual:
            texto_exibicao = f'"{livro[1]}"  |  Autor: {livro[2]}  |  Ano: {livro[3]}  |  Gênero: {livro[4]}'
            self.listbox_livros.insert(tk.END, texto_exibicao)

    def on_livro_select(self, event):
        selection_indices = self.listbox_livros.curselection()
        if not selection_indices: return

        selected_index = selection_indices[0]
        livro_selecionado = self.lista_de_livros_atual[selected_index]
        self.livro_selecionado_id = livro_selecionado[0] # Armazena o LivroID
        
        # Preenche os campos do formulário
        self.limpar_campos(limpar_id=False) # Limpa os campos antes de preencher
        self.entry_titulo.insert(0, livro_selecionado[1])
        self.entry_autor.insert(0, livro_selecionado[2])
        self.entry_ano.insert(0, livro_selecionado[3])
        self.entry_genero.insert(0, livro_selecionado[4])

    def salvar_alteracoes(self):
        if self.livro_selecionado_id is None:
            messagebox.showerror("Erro", "Nenhum livro selecionado para editar. Por favor, selecione um livro da lista.")
            return

        titulo = self.entry_titulo.get()
        autor_nome = self.entry_autor.get()
        ano = self.entry_ano.get()
        genero = self.entry_genero.get()
        
        if not titulo or not autor_nome:
            messagebox.showerror("Erro de Validação", "Os campos Título e Autor são obrigatórios.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,))
            autor = cursor.fetchone()
            if autor:
                autor_id = autor[0]
            else:
                cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,))
                autor_id = cursor.lastrowid
            
            update_query = """
            UPDATE Livros SET Titulo = ?, AutorID = ?, AnoPublicacao = ?, Genero = ?
            WHERE LivroID = ?
            """
            cursor.execute(update_query, (titulo, autor_id, int(ano), genero, self.livro_selecionado_id))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
            self.limpar_campos()
            self.popular_lista_livros()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")

    def pesquisar_livro(self):
        termo_pesquisa = self.entry_pesquisa.get()
        termo_like = f"%{termo_pesquisa}%"
        
        query = """
        SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero
        FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID
        WHERE L.Titulo LIKE ? OR A.Nome LIKE ?
        ORDER BY L.Titulo;
        """
        self.popular_lista_livros(query, (termo_like, termo_like))

    def carregar_generos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT Genero FROM Livros WHERE Genero IS NOT NULL ORDER BY Genero")
        generos = [row[0] for row in cursor.fetchall()]
        self.combo_genero['values'] = ["Todos os Gêneros"] + generos

    def filtrar_por_genero(self, event):
        genero_selecionado = self.combo_genero.get()
        self.limpar_campos()

        if genero_selecionado == "Todos os Gêneros":
            self.popular_lista_livros()
        else:
            query = """
            SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero
            FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID
            WHERE L.Genero = ? ORDER BY L.Titulo;
            """
            self.popular_lista_livros(query, (genero_selecionado,))
    
    def adicionar_livro(self):
       
        titulo = self.entry_titulo.get()
        autor_nome = self.entry_autor.get()
        ano = self.entry_ano.get()
        genero = self.entry_genero.get()
        if not titulo or not autor_nome:
            messagebox.showerror("Erro de Validação", "Os campos Título e Autor são obrigatórios.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,))
            autor = cursor.fetchone()
            if autor: autor_id = autor[0]
            else:
                cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,))
                autor_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO Livros (Titulo, AutorID, AnoPublicacao, Genero) VALUES (?, ?, ?, ?)",
                (titulo, autor_id, int(ano), genero))
            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' adicionado com sucesso!")
            self.limpar_campos()
            self.popular_lista_livros()
            self.carregar_generos() # Recarrega os generos caso um novo tenha sido adicionado
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao adicionar: {e}")

    def limpar_campos(self, limpar_id=True):
        if limpar_id:
            self.livro_selecionado_id = None
        self.entry_titulo.delete(0, tk.END)
        self.entry_autor.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.entry_genero.delete(0, tk.END)
        self.listbox_livros.selection_clear(0, tk.END) # Limpa a seleção visual
        
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"):
            self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaGUI(root)
    root.mainloop()