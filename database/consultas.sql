-- Arquivo: consultas.sql
-- Descrição: Exemplos de consultas SQL para extrair informações do banco da biblioteca.

-- Pergunta 1: Listar todos os livros e seus respectivos autores.
-- Habilidade demonstrada: JOIN básico.
SELECT
    L.Titulo,
    A.Nome AS Autor
FROM Livros L
JOIN Autores A ON L.AutorID = A.AutorID;


-- Pergunta 2: Contar quantos livros cada autor tem no acervo.
-- Habilidade demonstrada: GROUP BY, COUNT, JOIN.
SELECT
    A.Nome AS Autor,
    COUNT(L.LivroID) AS QuantidadeDeLivros
FROM Autores A
LEFT JOIN Livros L ON A.AutorID = L.AutorID
GROUP BY A.Nome
ORDER BY QuantidadeDeLivros DESC;


-- Pergunta 3: Listar os livros que estão atualmente emprestados, mostrando quem os pegou e quando devem devolver.
-- Habilidade demonstrada: Múltiplos JOINs, filtragem com WHERE e IS NULL.
SELECT
    L.Titulo AS LivroEmprestado,
    U.Nome AS NomeDoUsuario,
    E.DataEmprestimo,
    E.DataDevolucaoPrevista
FROM Emprestimos E
JOIN Livros L ON E.LivroID = L.LivroID
JOIN Usuarios U ON E.UsuarioID = U.UsuarioID
WHERE E.DataDevolucaoReal IS NULL;


-- Pergunta 4: Identificar quais livros estão com a devolução atrasada.
-- Habilidade demonstrada: Lógica com datas, usando a data atual.
SELECT
    L.Titulo AS LivroAtrasado,
    U.Nome AS NomeDoUsuario,
    E.DataDevolucaoPrevista
FROM Emprestimos E
JOIN Livros L ON E.LivroID = L.LivroID
JOIN Usuarios U ON E.UsuarioID = U.UsuarioID
WHERE E.DataDevolucaoReal IS NULL AND E.DataDevolucaoPrevista < DATE('now');


-- Pergunta 5: Quais usuários pegaram mais livros emprestados?
-- Habilidade demonstrada: Subquery ou CTE, GROUP BY, COUNT, ORDER BY.
SELECT
    U.Nome AS Usuario,
    COUNT(E.EmprestimoID) AS TotalDeEmprestimos
FROM Usuarios U
JOIN Emprestimos E ON U.UsuarioID = E.UsuarioID
GROUP BY U.Nome
ORDER BY TotalDeEmprestimos DESC;