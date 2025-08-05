-- Arquivo: insercao_dados.sql
-- Descrição: Script para inserir dados de exemplo no banco de dados da biblioteca.

-- Inserindo Autores
INSERT INTO Autores (Nome, Nacionalidade) VALUES
('George Orwell', 'Britânico'),
('J.K. Rowling', 'Britânico'),
('Isaac Asimov', 'Russo-Americano'),
('J.R.R. Tolkien', 'Sul-Africano'),
('Clarice Lispector', 'Brasileira');

-- Inserindo Usuários
INSERT INTO Usuarios (Nome, Email, DataCadastro) VALUES
('Ana Silva', 'ana.silva@email.com', '2024-01-15'),
('Bruno Costa', 'bruno.costa@email.com', '2024-02-20'),
('Carlos Dias', 'carlos.dias@email.com', '2024-05-10');

-- Inserindo Livros
-- Note que o AutorID corresponde ao ID inserido na tabela Autores.
INSERT INTO Livros (Titulo, AutorID, AnoPublicacao, Genero, QuantidadeDisponivel) VALUES
('1984', 1, 1949, 'Distopia', 3),
('A Revolução dos Bichos', 1, 1945, 'Sátira Política', 2),
('Harry Potter e a Pedra Filosofal', 2, 1997, 'Fantasia', 5),
('Eu, Robô', 3, 1950, 'Ficção Científica', 4),
('O Senhor dos Anéis: A Sociedade do Anel', 4, 1954, 'Fantasia', 3),
('A Hora da Estrela', 5, 1977, 'Ficção', 2);

-- Inserindo Empréstimos
-- Empréstimo ativo (sem data de devolução real)
INSERT INTO Emprestimos (LivroID, UsuarioID, DataEmprestimo, DataDevolucaoPrevista) VALUES
(1, 1, '2025-07-20', '2025-08-03'); -- Ana pegou '1984'

-- Empréstimo atrasado (data prevista passou e ainda não foi devolvido)
INSERT INTO Emprestimos (LivroID, UsuarioID, DataEmprestimo, DataDevolucaoPrevista) VALUES
(3, 2, '2025-07-10', '2025-07-24'); -- Bruno pegou 'Harry Potter'

-- Empréstimo já finalizado (com data de devolução real)
INSERT INTO Emprestimos (LivroID, UsuarioID, DataEmprestimo, DataDevolucaoPrevista, DataDevolucaoReal) VALUES
(5, 1, '2025-06-01', '2025-06-15', '2025-06-14'); -- Ana pegou 'O Senhor dos Anéis' e devolveu