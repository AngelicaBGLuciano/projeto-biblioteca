import sqlite3
import tkinter as tk
from tkinter import ttk, font, messagebox
from ttkthemes import ThemedTk
from datetime import date, timedelta
import re

def conectar_bd():
    """Conecta ao banco de dados SQLite e cria as tabelas se não existirem."""
    conn = sqlite3.connect('biblioteca.db')
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    # Garante que todas as tabelas necessárias existem
    sql_script = """
    CREATE TABLE IF NOT EXISTS Autores (AutorID INTEGER PRIMARY KEY, Nome TEXT NOT NULL, Nacionalidade TEXT);
    CREATE TABLE IF NOT EXISTS Livros (LivroID INTEGER PRIMARY KEY, Titulo TEXT NOT NULL, AutorID INTEGER, AnoPublicacao INTEGER, Genero TEXT, QuantidadeDisponivel INTEGER DEFAULT 1, FOREIGN KEY (AutorID) REFERENCES Autores(AutorID));
    CREATE TABLE IF NOT EXISTS Usuarios (UsuarioID INTEGER PRIMARY KEY, Nome TEXT NOT NULL, Email TEXT UNIQUE NOT NULL, DataCadastro TEXT);
    CREATE TABLE IF NOT EXISTS Emprestimos (EmprestimoID INTEGER PRIMARY KEY, LivroID INTEGER, UsuarioID INTEGER, DataEmprestimo TEXT NOT NULL, DataDevolucaoPrevista TEXT NOT NULL, DataDevolucaoReal TEXT, FOREIGN KEY (LivroID) REFERENCES Livros(LivroID), FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID));
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
        self.root.geometry("1100x800")

        self.setup_styles()

        # --- ESTRUTURA PRINCIPAL COM ABAS ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_acervo = ttk.Frame(notebook, padding="10")
        self.tab_emprestimos = ttk.Frame(notebook, padding="10")

        notebook.add(self.tab_acervo, text='Gerenciar Acervo')
        notebook.add(self.tab_emprestimos, text='Usuários e Empréstimos')

        self.criar_tab_acervo(self.tab_acervo)
        self.criar_tab_emprestimos(self.tab_emprestimos)

        self.atualizar_todas_listas()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def criar_tab_acervo(self, parent_tab):
        frame_form = ttk.LabelFrame(parent_tab, text="Gerenciar Livro", padding="15")
        frame_form.pack(pady=(0, 20), padx=10, fill="x")
        frame_controles = ttk.LabelFrame(parent_tab, text="Controles do Acervo", padding="15")
        frame_controles.pack(pady=10, padx=10, fill="x")
        frame_lista = ttk.Frame(parent_tab, padding="10")
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)
        frame_form.columnconfigure(1, weight=1)
        
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
        self.btn_adicionar_livro = ttk.Button(frame_botoes_form, text="Adicionar Livro", command=self.adicionar_livro)
        self.btn_adicionar_livro.pack(side="left", padx=10)
        self.btn_salvar = ttk.Button(frame_botoes_form, text="Salvar Alterações", command=self.salvar_alteracoes)
        self.btn_salvar.pack(side="left", padx=10)
        self.btn_limpar = ttk.Button(frame_botoes_form, text="Limpar Formulário", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        ttk.Label(frame_controles, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_pesquisa = ttk.Entry(frame_controles, width=25, font=self.entry_font)
        self.entry_pesquisa.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_pesquisar = ttk.Button(frame_controles, text="Pesquisar", command=self.pesquisar_livro)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(frame_controles, text="Filtrar por Gênero:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_genero = ttk.Combobox(frame_controles, state="readonly", width=20, font=self.entry_font)
        self.combo_genero.pack(side=tk.LEFT)
        self.combo_genero.bind("<<ComboboxSelected>>", self.filtrar_por_genero)

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        self.listbox_livros = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=15, font=self.label_font, bg=self.COR_FUNDO_WIDGETS, fg=self.COR_TEXTO, selectbackground=self.COR_SELECAO_LISTA, selectforeground=self.COR_TEXTO_SELECAO, borderwidth=0, highlightthickness=0, activestyle='none')
        self.listbox_livros.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_livros.yview)
        self.listbox_livros.bind('<<ListboxSelect>>', self.on_livro_select)

    def criar_tab_emprestimos(self, parent_tab):
        frame_esquerda = ttk.Frame(parent_tab)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=(0,10))
        frame_direita = ttk.Frame(parent_tab)
        frame_direita.pack(side="right", fill="both", expand=True, padx=(10,0))
        
        frame_usuarios = ttk.LabelFrame(frame_esquerda, text="Gerenciar Usuários", padding="15")
        frame_usuarios.pack(fill="x", expand=True)
        ttk.Label(frame_usuarios, text="Nome:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario_nome = ttk.Entry(frame_usuarios, width=30)
        self.entry_usuario_nome.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(frame_usuarios, text="E-mail:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_usuario_email = ttk.Entry(frame_usuarios, width=30)
        self.entry_usuario_email.grid(row=1, column=1, sticky="ew", pady=5)
        self.btn_adicionar_usuario = ttk.Button(frame_usuarios, text="Adicionar Usuário", command=self.adicionar_usuario)
        self.btn_adicionar_usuario.grid(row=2, column=0, columnspan=2, pady=10)
        
        frame_lista_usuarios = ttk.LabelFrame(frame_esquerda, text="Usuários Cadastrados", padding="10")
        frame_lista_usuarios.pack(fill="both", expand=True, pady=(20,0))
        scrollbar_usuarios = ttk.Scrollbar(frame_lista_usuarios)
        scrollbar_usuarios.pack(side="right", fill="y")
        self.listbox_usuarios = tk.Listbox(frame_lista_usuarios, yscrollcommand=scrollbar_usuarios.set, bg=self.COR_FUNDO_WIDGETS, fg=self.COR_TEXTO)
        self.listbox_usuarios.pack(fill="both", expand=True)
        scrollbar_usuarios.config(command=self.listbox_usuarios.yview)

        frame_novo_emprestimo = ttk.LabelFrame(frame_direita, text="Novo Empréstimo", padding="15")
        frame_novo_emprestimo.pack(fill="x", expand=True)
        ttk.Label(frame_novo_emprestimo, text="Livro Disponível:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_livros_emprestimo = ttk.Combobox(frame_novo_emprestimo, state="readonly", width=40)
        self.combo_livros_emprestimo.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(frame_novo_emprestimo, text="Usuário:").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_usuarios_emprestimo = ttk.Combobox(frame_novo_emprestimo, state="readonly", width=40)
        self.combo_usuarios_emprestimo.grid(row=1, column=1, sticky="ew", pady=5)
        
        self.btn_efetuar_emprestimo = ttk.Button(frame_novo_emprestimo, text="Efetuar Empréstimo", command=self.efetuar_emprestimo)
        self.btn_efetuar_emprestimo.grid(row=2, column=0, columnspan=2, pady=10)

        frame_emprestimos_ativos = ttk.LabelFrame(frame_direita, text="Empréstimos Ativos", padding="10")
        frame_emprestimos_ativos.pack(fill="both", expand=True, pady=(20,0))
        self.tree_emprestimos = ttk.Treeview(frame_emprestimos_ativos, columns=("livro", "usuario", "data_emprestimo", "data_devolucao"), show="headings")
        self.tree_emprestimos.heading("livro", text="Livro"); self.tree_emprestimos.heading("usuario", text="Usuário")
        self.tree_emprestimos.heading("data_emprestimo", text="Data Empréstimo"); self.tree_emprestimos.heading("data_devolucao", text="Devolução Prevista")
        self.tree_emprestimos.column("livro", width=200); self.tree_emprestimos.pack(fill="both", expand=True, side="left")
        scrollbar_emprestimos = ttk.Scrollbar(frame_emprestimos_ativos, orient="vertical", command=self.tree_emprestimos.yview)
        scrollbar_emprestimos.pack(fill="y", side="right"); self.tree_emprestimos.configure(yscrollcommand=scrollbar_emprestimos.set)
        self.btn_registrar_devolucao = ttk.Button(frame_emprestimos_ativos, text="Registrar Devolução", command=self.registrar_devolucao)
        self.btn_registrar_devolucao.pack(pady=10)
        
    def setup_styles(self):
        """Configura a paleta de cores e estilos da aplicação."""
        self.COR_FUNDO = "#F0F2F5"; self.COR_FUNDO_WIDGETS = "#FFFFFF"; self.COR_TEXTO = "#2C3E50"
        self.COR_SELECAO_LISTA = "#0078D7"; self.COR_TEXTO_SELECAO = "#FFFFFF"

        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.entry_font = font.Font(family="Segoe UI", size=10)
        
        style = ttk.Style(self.root)
        self.root.configure(bg=self.COR_FUNDO)
        style.configure('.', font=self.label_font, background=self.COR_FUNDO, foreground=self.COR_TEXTO)
        style.configure('TFrame', background=self.COR_FUNDO)
        style.configure('TLabel', background=self.COR_FUNDO, foreground=self.COR_TEXTO)
        style.configure('TLabelFrame', background=self.COR_FUNDO, borderwidth=1)
        style.configure('TLabelFrame.Label', font=self.header_font, background=self.COR_FUNDO, foreground=self.COR_TEXTO)
        style.configure('TButton', font=self.label_font, padding=8)
        
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
            self.listbox_livros.insert(tk.END, f'"{livro[1]}"  |  Autor: {livro[2]}')
    
    def on_livro_select(self, event):
        selection_indices = self.listbox_livros.curselection()
        if not selection_indices: return
        livro_selecionado = self.lista_de_livros_atual[selection_indices[0]]
        self.livro_selecionado_id = livro_selecionado[0]
        self.limpar_campos(limpar_id=False)
        self.entry_titulo.insert(0, livro_selecionado[1]); self.entry_autor.insert(0, livro_selecionado[2]); self.entry_ano.insert(0, livro_selecionado[3]); self.entry_genero.insert(0, livro_selecionado[4])

    def salvar_alteracoes(self):
        if not self.livro_selecionado_id: messagebox.showerror("Erro", "Nenhum livro selecionado."); return
        titulo = self.entry_titulo.get(); autor_nome = self.entry_autor.get(); ano = self.entry_ano.get(); genero = self.entry_genero.get()
        if not titulo or not autor_nome: messagebox.showerror("Erro de Validação", "Título e Autor são obrigatórios."); return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,)); autor = cursor.fetchone()
            if autor: autor_id = autor[0]
            else: cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,)); autor_id = cursor.lastrowid
            cursor.execute("UPDATE Livros SET Titulo = ?, AutorID = ?, AnoPublicacao = ?, Genero = ? WHERE LivroID = ?", (titulo, autor_id, int(ano), genero, self.livro_selecionado_id))
            self.conn.commit(); messagebox.showinfo("Sucesso", "Livro atualizado!"); self.limpar_campos(); self.atualizar_todas_listas()
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def adicionar_livro(self):
        titulo = self.entry_titulo.get(); autor_nome = self.entry_autor.get(); ano = self.entry_ano.get(); genero = self.entry_genero.get()
        if not titulo or not autor_nome: messagebox.showerror("Erro de Validação", "Título e Autor são obrigatórios."); return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,)); autor = cursor.fetchone()
            if autor: autor_id = autor[0]
            else: cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,)); autor_id = cursor.lastrowid
            cursor.execute("INSERT INTO Livros (Titulo, AutorID, AnoPublicacao, Genero) VALUES (?, ?, ?, ?)", (titulo, autor_id, int(ano), genero))
            self.conn.commit(); messagebox.showinfo("Sucesso", "Livro adicionado!"); self.limpar_campos(); self.atualizar_todas_listas()
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
    def pesquisar_livro(self):
        termo = self.entry_pesquisa.get().strip(); query = "SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID"
        if not termo: self.popular_lista_livros(); return
        palavras = termo.split(); condicoes = []; params = []
        for p in palavras: termo_like = f"%{p}%"; condicoes.append("(L.Titulo LIKE ? OR A.Nome LIKE ?)"); params.extend([termo_like, termo_like])
        query_final = query + " WHERE " + " AND ".join(condicoes) + " ORDER BY L.Titulo;" if condicoes else query + " ORDER BY L.Titulo;"
        self.popular_lista_livros(query_final, tuple(params))
        if not self.lista_de_livros_atual: messagebox.showinfo("Pesquisa", f"Nenhum livro encontrado para '{termo}'.")

    def carregar_generos(self):
        cursor = self.conn.cursor(); cursor.execute("SELECT DISTINCT Genero FROM Livros WHERE Genero IS NOT NULL AND Genero != '' ORDER BY Genero")
        self.combo_genero['values'] = ["Todos os Gêneros"] + [row[0] for row in cursor.fetchall()]; self.combo_genero.set("Todos os Gêneros")

    def filtrar_por_genero(self, event):
        genero = self.combo_genero.get(); self.limpar_campos()
        if genero == "Todos os Gêneros": self.popular_lista_livros()
        else: self.popular_lista_livros("SELECT L.LivroID, L.Titulo, A.Nome, L.AnoPublicacao, L.Genero FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID WHERE L.Genero = ? ORDER BY L.Titulo;", (genero,))

    def limpar_campos(self, limpar_id=True):
        if limpar_id: self.livro_selecionado_id = None
        self.entry_titulo.delete(0, tk.END); self.entry_autor.delete(0, tk.END); self.entry_ano.delete(0, tk.END); self.entry_genero.delete(0, tk.END)
        if self.listbox_livros.curselection(): self.listbox_livros.selection_clear(0, tk.END)

    def adicionar_usuario(self):
        # Usado .strip() para remover espaços em branco extras no início e no fim
        nome = self.entry_usuario_nome.get().strip()
        email = self.entry_usuario_email.get().strip()

        if not nome or not email:
            messagebox.showerror("Erro de Validação", "Nome e E-mail são obrigatórios.")
            return

        # --- VALIDAÇÃO DE E-MAIL ---
        # Define o padrão que um e-mail válido deve seguir
        padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Verifica se o e-mail digitado corresponde ao padrão
        if not re.match(padrao_email, email):
            messagebox.showerror("E-mail Inválido", "Por favor, insira um endereço de e-mail válido (ex: nome@provedor.com).")
            return # Interrompe a função se o e-mail for inválido
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Usuarios (Nome, Email, DataCadastro) VALUES (?, ?, ?)", (nome, email, date.today()))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso!")
            self.entry_usuario_nome.delete(0, tk.END)
            self.entry_usuario_email.delete(0, tk.END)
            self.atualizar_todas_listas()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Este e-mail já está cadastrado no sistema.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    def popular_lista_usuarios(self):
        self.listbox_usuarios.delete(0, tk.END)
        cursor = self.conn.cursor(); cursor.execute("SELECT Nome, Email FROM Usuarios ORDER BY Nome")
        for usuario in cursor.fetchall(): self.listbox_usuarios.insert(tk.END, f"{usuario[0]} ({usuario[1]})")
    
    def carregar_comboboxes_emprestimo(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT LivroID, Titulo FROM Livros WHERE QuantidadeDisponivel > 0 ORDER BY Titulo")
        self.livros_disponiveis = cursor.fetchall()
        self.combo_livros_emprestimo['values'] = [l[1] for l in self.livros_disponiveis]
        cursor.execute("SELECT UsuarioID, Nome FROM Usuarios ORDER BY Nome")
        self.usuarios_cadastrados = cursor.fetchall()
        self.combo_usuarios_emprestimo['values'] = [u[1] for u in self.usuarios_cadastrados]

    def efetuar_emprestimo(self):
        livro_selecionado = self.combo_livros_emprestimo.get(); usuario_selecionado = self.combo_usuarios_emprestimo.get()
        if not livro_selecionado or not usuario_selecionado: messagebox.showerror("Erro", "Selecione um livro e um usuário."); return
        try:
            livro_id = [l[0] for l in self.livros_disponiveis if l[1] == livro_selecionado][0]
            usuario_id = [u[0] for u in self.usuarios_cadastrados if u[1] == usuario_selecionado][0]
            cursor = self.conn.cursor()
            data_emprestimo = date.today(); data_devolucao = data_emprestimo + timedelta(days=14)
            cursor.execute("INSERT INTO Emprestimos (LivroID, UsuarioID, DataEmprestimo, DataDevolucaoPrevista) VALUES (?, ?, ?, ?)", (livro_id, usuario_id, data_emprestimo, data_devolucao))
            cursor.execute("UPDATE Livros SET QuantidadeDisponivel = QuantidadeDisponivel - 1 WHERE LivroID = ?", (livro_id,))
            self.conn.commit(); messagebox.showinfo("Sucesso", "Empréstimo realizado!")
            self.atualizar_todas_listas()
            self.combo_livros_emprestimo.set(''); self.combo_usuarios_emprestimo.set('')
        except IndexError: messagebox.showerror("Erro", "Ocorreu um erro ao obter ID do livro ou usuário.")
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def popular_treeview_emprestimos(self):
        for i in self.tree_emprestimos.get_children(): self.tree_emprestimos.delete(i)
        cursor = self.conn.cursor()
        query = "SELECT E.EmprestimoID, L.Titulo, U.Nome, E.DataEmprestimo, E.DataDevolucaoPrevista, L.LivroID FROM Emprestimos E JOIN Livros L ON E.LivroID = L.LivroID JOIN Usuarios U ON E.UsuarioID = U.UsuarioID WHERE E.DataDevolucaoReal IS NULL ORDER BY E.DataDevolucaoPrevista;"
        cursor.execute(query)
        for row in cursor.fetchall():
            self.tree_emprestimos.insert("", "end", iid=row[0], values=(row[1], row[2], row[3], row[4]), tags=(row[5],))

    def registrar_devolucao(self):
        selecionado = self.tree_emprestimos.focus()
        if not selecionado: messagebox.showerror("Erro", "Selecione um empréstimo."); return
        emprestimo_id = selecionado; livro_id = self.tree_emprestimos.item(selecionado)['tags'][0]
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Emprestimos SET DataDevolucaoReal = ? WHERE EmprestimoID = ?", (date.today(), emprestimo_id))
            cursor.execute("UPDATE Livros SET QuantidadeDisponivel = QuantidadeDisponivel + 1 WHERE LivroID = ?", (livro_id,))
            self.conn.commit(); messagebox.showinfo("Sucesso", "Devolução registrada!"); self.atualizar_todas_listas()
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
    def atualizar_todas_listas(self):
        self.popular_lista_livros(); self.popular_lista_usuarios()
        self.carregar_comboboxes_emprestimo(); self.popular_treeview_emprestimos()
        self.carregar_generos()

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja fechar o sistema?"): self.conn.close(); self.root.destroy()
        
# --- Bloco Principal para Executar a Aplicação ---
if __name__ == "__main__":
    root = ThemedTk(theme="adapta", themebg=True)
    app = BibliotecaGUI(root)
    root.mainloop()

    