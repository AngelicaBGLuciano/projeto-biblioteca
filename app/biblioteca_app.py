import sqlite3
import tkinter as tk
from tkinter import ttk  # ttk oferece widgets com um visual mais moderno
from tkinter import messagebox

# --- LÓGICA DO BANCO DE DADOS (praticamente a mesma de antes) ---

def conectar_bd():
    """Conecta ao banco de dados SQLite e o cria se não existir."""
    conn = sqlite3.connect('biblioteca.db')
    conn.execute("PRAGMA foreign_keys = 1")
    # Cria as tabelas se não existirem (aqui é um bom lugar para garantir isso)
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
        
        self.root = root
        self.root.title("Sistema de Gestão da Biblioteca")
        self.root.geometry("700x500") # Define o tamanho da janela

        # --- Frames para organizar a tela ---
        frame_form = ttk.Frame(self.root, padding="10")
        frame_form.pack(pady=10, padx=10, fill="x")

        frame_lista = ttk.Frame(self.root, padding="10")
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Widgets do Formulário de Adição ---
        ttk.Label(frame_form, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = ttk.Entry(frame_form, width=40)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_autor = ttk.Entry(frame_form, width=40)
        self.entry_autor.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Ano:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_ano = ttk.Entry(frame_form, width=10)
        self.entry_ano.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_form, text="Gênero:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_genero = ttk.Entry(frame_form, width=20)
        self.entry_genero.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        self.btn_adicionar = ttk.Button(frame_form, text="Adicionar Livro", command=self.adicionar_livro)
        self.btn_adicionar.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Widgets da Lista de Livros ---
        ttk.Label(frame_lista, text="Acervo de Livros").pack()

        # Criando a Listbox com uma barra de rolagem
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox_livros = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=15)
        self.listbox_livros.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_livros.yview)

        # Populando a lista com os dados existentes
        self.popular_lista_livros()
        
        # Fecha a conexão com o banco ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def popular_lista_livros(self):
        """Busca os livros no banco e os exibe na Listbox."""
        # Limpa a lista atual
        self.listbox_livros.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        query = """
        SELECT L.Titulo, A.Nome, L.AnoPublicacao, L.Genero
        FROM Livros L JOIN Autores A ON L.AutorID = A.AutorID ORDER BY L.Titulo;
        """
        cursor.execute(query)
        for livro in cursor.fetchall():
            # Formata a string para exibição
            texto_exibicao = f'"{livro[0]}"  |  Autor: {livro[1]}  |  Ano: {livro[2]}  |  Gênero: {livro[3]}'
            self.listbox_livros.insert(tk.END, texto_exibicao)

    def adicionar_livro(self):
        """Pega os dados dos campos de entrada e os adiciona ao banco."""
        titulo = self.entry_titulo.get()
        autor_nome = self.entry_autor.get()
        ano = self.entry_ano.get()
        genero = self.entry_genero.get()
        
        if not titulo or not autor_nome:
            messagebox.showerror("Erro de Validação", "Os campos Título e Autor são obrigatórios.")
            return

        try:
            cursor = self.conn.cursor()
            
            # Verifica se o autor já existe, se não, adiciona
            cursor.execute("SELECT AutorID FROM Autores WHERE Nome = ?", (autor_nome,))
            autor = cursor.fetchone()
            if autor:
                autor_id = autor[0]
            else:
                cursor.execute("INSERT INTO Autores (Nome) VALUES (?)", (autor_nome,))
                autor_id = cursor.lastrowid

            # Insere o livro
            cursor.execute(
                "INSERT INTO Livros (Titulo, AutorID, AnoPublicacao, Genero) VALUES (?, ?, ?, ?)",
                (titulo, autor_id, int(ano), genero)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' adicionado com sucesso!")
            self.limpar_campos()
            self.popular_lista_livros() # Atualiza a lista na tela
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Ocorreu um erro: {e}")
        except ValueError:
            messagebox.showerror("Erro de Validação", "O ano de publicação deve ser um número.")

    def limpar_campos(self):
        """Limpa os campos do formulário."""
        self.entry_titulo.delete(0, tk.END)
        self.entry_autor.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.entry_genero.delete(0, tk.END)
        
    def on_closing(self):
        """Chamado quando a janela é fechada."""
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"):
            self.conn.close()
            self.root.destroy()

# --- Bloco Principal para Executar a Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaGUI(root)
    root.mainloop() # Inicia o loop de eventos da interface gráfica