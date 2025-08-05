-- Arquivo: criacao_tabelas.sql
-- Descrição: Script para criar todas as tabelas do banco de dados da biblioteca.

-- Remove as tabelas se elas já existirem, para garantir um início limpo.
DROP TABLE IF EXISTS Emprestimos;
DROP TABLE IF EXISTS Livros;
DROP TABLE IF EXISTS Usuarios;
DROP TABLE IF EXISTS Autores;


-- Tabela de Autores: armazena informações dos escritores.
CREATE TABLE Autores (
    AutorID         INTEGER PRIMARY KEY, -- Identificador único para cada autor
    Nome            TEXT NOT NULL,       -- Nome completo do autor
    Nacionalidade   TEXT
);

-- Tabela de Usuários: armazena informações dos membros da biblioteca.
CREATE TABLE Usuarios (
    UsuarioID       INTEGER PRIMARY KEY, -- Identificador único para cada usuário
    Nome            TEXT NOT NULL,
    Email           TEXT UNIQUE NOT NULL,-- O e-mail deve ser único
    DataCadastro    TEXT
);

-- Tabela de Livros: o acervo da biblioteca.
CREATE TABLE Livros (
    LivroID                 INTEGER PRIMARY KEY, -- Identificador único para cada livro
    Titulo                  TEXT NOT NULL,
    AutorID                 INTEGER,             -- Chave estrangeira que se conecta à tabela Autores
    AnoPublicacao           INTEGER,
    Genero                  TEXT,
    QuantidadeDisponivel    INTEGER DEFAULT 1,
    FOREIGN KEY (AutorID) REFERENCES Autores(AutorID)
);

-- Tabela de Empréstimos: registra as transações de empréstimo.
-- Esta é uma tabela de junção que conecta Livros e Usuarios.
CREATE TABLE Emprestimos (
    EmprestimoID            INTEGER PRIMARY KEY, -- Identificador único para cada transação
    LivroID                 INTEGER,
    UsuarioID               INTEGER,
    DataEmprestimo          TEXT NOT NULL,
    DataDevolucaoPrevista   TEXT NOT NULL,
    DataDevolucaoReal       TEXT,                -- Permanece nulo (NULL) até o livro ser devolvido
    FOREIGN KEY (LivroID) REFERENCES Livros(LivroID),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID)
);