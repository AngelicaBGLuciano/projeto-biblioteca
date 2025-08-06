import sqlite3
import tkinter as tk
from tkinter import ttk, font
from ttkthemes import ThemedTk # Importação principal para o tema
from tkinter import messagebox

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

class BibliotecaGUI:
    def __init__(self, root):
        self.conn = conectar_bd()
        self.livro_selecionado_id = None
        self.lista_de_livros_atual = []

        self.root = root
        self.root.title("Sistema de Gestão da Biblioteca")
        self.root.geometry("950x750")

        self.setup_styles()

        # --- Frames para organizar a tela ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        frame_form = ttk.LabelFrame(main_frame, text="Gerenciar Livro", padding="15")
        frame_form.pack(pady=(0, 20), padx=10, fill="x")

        frame_controles = ttk.LabelFrame(main_frame, text="Controles do Acervo", padding="15")
        frame_controles.pack(pady=10, padx=10, fill="x")

        frame_lista = ttk.Frame(main_frame, padding="10")
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)
        
        frame_form.columnconfigure(1, weight=1)

        # --- Widgets do Formulário ---
        ttk.Label(frame_form, text="Título:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.entry_titulo = ttk.Entry(frame_form, width=50, font=self.entry_font)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=8, columnspan=3, sticky="ew")

        ttk.Label(frame_form, text="Autor:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.entry_autor = ttk.Entry(frame_form, width=50, font=self.entry_font)
        self.entry_autor.grid(row=1, column=1, padx=5, pady=8, columnspan=3, sticky="ew")
        
        ttk.Label(frame_form, text="Ano:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.entry_ano = ttk.Entry(frame_form, width=10, font=self.entry_font)
        self.entry_ano.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        
        ttk.Label(frame_form, text="Gênero:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.entry_genero = ttk.Entry(frame_form, width=20, font=self.entry_font)
        self.entry_genero.grid(row=3, column=1, padx=5, pady=8, sticky="w")
        
        frame_botoes_form = ttk.Frame(frame_form)
        frame_botoes_form.grid(row=4, column=0, columnspan=4, pady=(15, 5))
        
        self.btn_adicionar = ttk.Button(frame_botoes_form, text="Adicionar Livro", command=self.adicionar_livro)
        self.btn_adicionar.pack(side="left", padx=10)
        self.btn_salvar = ttk.Button(frame_botoes_form, text="Salvar Alterações", command=self.salvar_alteracoes)
        self.btn_salvar.pack(side="left", padx=10)
        self.btn_limpar = ttk.Button(frame_botoes_form, text="Limpar Formulário", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        # --- Widgets da Pesquisa e Filtro ---
        ttk.Label(frame_controles, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_pesquisa = ttk.Entry(frame_controles, width=25, font=self.entry_font)
        self.entry_pesquisa.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_pesquisar = ttk.Button(frame_controles, text="Pesquisar", command=self.pesquisar_livro)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(frame_controles, text="Filtrar por Gênero:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_genero = ttk.Combobox(frame_controles, state="readonly", width=20, font=self.entry_font)
        self.combo_genero.pack(side=tk.LEFT)
        self.combo_genero.bind("<<ComboboxSelected>>", self.filtrar_por_genero)

        # --- Widgets da Lista de Livros (com estilo manual) ---
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        self.listbox_livros = tk.Listbox(frame_lista,
            yscrollcommand=scrollbar.set,
            height=15,
            font=self.label_font,
            bg=self.COR_FUNDO_WIDGETS,
            fg=self.COR_TEXTO,
            selectbackground=self.COR_SELECAO_LISTA,
            selectforeground=self.COR_TEXTO_SELECAO,
            borderwidth=0,
            highlightthickness=0,
            activestyle='none')
        self.listbox_livros.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_livros.yview)
        self.listbox_livros.bind('<<ListboxSelect>>', self.on_livro_select)

        self.carregar_generos()
        self.popular_lista_livros()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configura a paleta de cores e estilos da aplicação."""
        # --- Paleta de Cores Refinada ---
        self.COR_FUNDO = "#F0F2F5"
        self.COR_FUNDO_WIDGETS = "#FFFFFF"
        self.COR_TEXTO = "#2C3E50"
        self.COR_SELECAO_LISTA = "#0078D7"
        self.COR_TEXTO_SELECAO = "#FFFFFF"

        # --- Fontes ---
        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.entry_font = font.Font(family="Segoe UI", size=10)
        
        # --- Aplicação dos Estilos ---
        style = ttk.Style(self.root)
        
        self.root.configure(bg=self.COR_FUNDO)
        style.configure('.', font=self.label_font, background=self.COR_FUNDO, foreground=self.COR_TEXTO)
        style.configure('TFrame', background=self.COR_FUNDO)
        style.configure('TLabel', background=self.COR_FUNDO, foreground=self.COR_TEXTO)
        style.configure('TLabelFrame', background=self.COR_FUNDO, borderwidth=1)
        style.configure('TLabelFrame.Label', font=self.header_font, background=self.COR_FUNDO, foreground=self.COR_TEXTO)

        # Estilo dos Botões comuns (agora se aplica a todos)
        style.configure('TButton', font=self.label_font, padding=8)
        
        # MUDANÇA 2: Removido o bloco de estilo para 'Accent.TButton' que não é mais usado
        
        # Estilo dos Campos de Entrada e Dropdown
        style.configure('TEntry', fieldbackground=self.COR_FUNDO_WIDGETS, foreground=self.COR_TEXTO, borderwidth=1, padding=5)
        style.map('TCombobox', fieldbackground=[('readonly', self.COR_FUNDO_WIDGETS)], foreground=[('readonly', self.COR_TEXTO)])

    def popular_lista_livros(self, query=None, params=()):
        self.listbox_livros.delete(0, tk.END)
        self.lista_de_livros_atual.clear()
        cursor = self.conn.cursor()
        if query is None:
            query = "SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID ORDER BY L.Titulo;"
        cursor.execute(query, params)
        self.lista_de_livros_atual = cursor.fetchall()
        for livro in self.lista_de_livros_atual:
            texto_exibicao = f'"{livro[1]}"  |  Autor: {livro[2]}  |  Ano: {livro[3]}  |  Gênero: {livro[4]}'
            self.listbox_livros.insert(tk.END, texto_exibicao)

    def on_livro_select(self, event):
        selection_indices = self.listbox_livros.curselection()
        if not selection_indices: return
        selected_index = selection_indices[0]
        livro_selecionado = self.lista_de_livros_atual[selected_index]
        self.livro_selecionado_id = livro_selecionado[0]
        self.limpar_campos(limpar_id=False)
        self.entry_titulo.insert(0, livro_selecionado[1])
        self.entry_autor.insert(0, livro_selecionado[2])
        self.entry_ano.insert(0, livro_selecionado[3])
        self.entry_genero.insert(0, livro_selecionado[4])

    def salvar_alteracoes(self):
        if self.livro_selecionado_id is None:
            messagebox.showerror("Erro", "Nenhum livro selecionado para editar.")
            return
        titulo = self.entry_titulo.get(); autor_nome = self.entry_autor.get(); ano = self.entry_ano.get(); genero = self.entry_genero.get()
        if not titulo or not autor_nome:
            messagebox.showerror("Erro de Validação", "Título e Autor são obrigatórios.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,))
            autor = cursor.fetchone()
            if autor: autor_id = autor[0]
            else:
                cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,)); autor_id = cursor.lastrowid
            update_query = "UPDATE Livros SET Titulo = ?, AutorID = ?, AnoPublicacao = ?, Genero = ? WHERE LivroID = ?"
            cursor.execute(update_query, (titulo, autor_id, int(ano), genero, self.livro_selecionado_id))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
            self.limpar_campos(); self.popular_lista_livros()
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")

    def adicionar_livro(self):
        titulo = self.entry_titulo.get(); autor_nome = self.entry_autor.get(); ano = self.entry_ano.get(); genero = self.entry_genero.get()
        if not titulo or not autor_nome:
            messagebox.showerror("Erro de Validação", "Título e Autor são obrigatórios.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,))
            autor = cursor.fetchone()
            if autor: autor_id = autor[0]
            else:
                cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,)); autor_id = cursor.lastrowid
            cursor.execute("INSERT INTO Livros (Titulo, AutorID, AnoPublicacao, Genero) VALUES (?, ?, ?, ?)", (titulo, autor_id, int(ano), genero))
            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' adicionado com sucesso!")
            self.limpar_campos(); self.popular_lista_livros(); self.carregar_generos()
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro ao adicionar: {e}")
        
    def pesquisar_livro(self):
        termo_pesquisa = self.entry_pesquisa.get().strip()
        if not termo_pesquisa:
            self.popular_lista_livros()
            return
        palavras = termo_pesquisa.split()
        query_base = "SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID"
        condicoes = []; params = []
        for palavra in palavras:
            termo_like = f"%{palavra}%"
            condicoes.append("(L.Titulo LIKE ? OR A.Nome LIKE ?)")
            params.extend([termo_like, termo_like])
        if condicoes:
            query_final = query_base + " WHERE " + " AND ".join(condicoes) + " ORDER BY L.Titulo;"
        else:
            query_final = query_base + " ORDER BY L.Titulo;"
        self.popular_lista_livros(query_final, tuple(params))
        if not self.lista_de_livros_atual:
            messagebox.showinfo("Pesquisa", f"Nenhum livro encontrado para '{termo_pesquisa}'.")

    def carregar_generos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT Genero FROM Livros WHERE Genero IS NOT NULL AND Genero != '' ORDER BY Genero")
        generos = [row[0] for row in cursor.fetchall()]
        self.combo_genero['values'] = ["Todos os Gêneros"] + generos
        self.combo_genero.set("Todos os Gêneros")

    def filtrar_por_genero(self, event):
        genero_selecionado = self.combo_genero.get()
        self.limpar_campos()
        if genero_selecionado == "Todos os Gêneros":
            self.popular_lista_livros()
        else:
            query = "SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID WHERE L.Genero = ? ORDER BY L.Titulo;"
            self.popular_lista_livros(query, (genero_selecionado,))

    def limpar_campos(self, limpar_id=True):
        if limpar_id: self.livro_selecionado_id = None
        self.entry_titulo.delete(0, tk.END); self.entry_autor.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END); self.entry_genero.delete(0, tk.END)
        if self.listbox_livros.curselection(): self.listbox_livros.selection_clear(0, tk.END)
        
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"):
            self.conn.close(); self.root.destroy()

# --- Bloco Principal para Executar a Aplicação ---
if __name__ == "__main__":
    root = ThemedTk(theme="adapta", themebg=True)
    app = BibliotecaGUI(root)
    root.mainloop()

