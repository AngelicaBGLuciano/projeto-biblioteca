-- Arquivo: consultas.sql
-- Descrição: Exemplos de consultas SQL para extrair informações do banco da biblioteca.

-- Listar todos os livros e seus respectivos autores.
SELECT
    L.Titulo,
    A.Nome AS Autor
FROM Livros L
JOIN Autores A ON L.AutorID = A.AutorID;


-- Contar quantos livros cada autor tem no acervo.
SELECT
    A.Nome AS Autor,
    COUNT(L.LivroID) AS QuantidadeDeLivros
FROM Autores A
LEFT JOIN Livros L ON A.AutorID = L.AutorID
GROUP BY A.Nome
ORDER BY QuantidadeDeLivros DESC;


-- Listar os livros que estão atualmente emprestados, mostrando quem os pegou e quando devem devolver.
SELECT
    L.Titulo AS LivroEmprestado,
    U.Nome AS NomeDoUsuario,
    E.DataEmprestimo,
    E.DataDevolucaoPrevista
FROM Emprestimos E
JOIN Livros L ON E.LivroID = L.LivroID
JOIN Usuarios U ON E.UsuarioID = U.UsuarioID
WHERE E.DataDevolucaoReal IS NULL;


-- Identificar quais livros estão com a devolução atrasada.
SELECT
    L.Titulo AS LivroAtrasado,
    U.Nome AS NomeDoUsuario,
    E.DataDevolucaoPrevista
FROM Emprestimos E
JOIN Livros L ON E.LivroID = L.LivroID
JOIN Usuarios U ON E.UsuarioID = U.UsuarioID
WHERE E.DataDevolucaoReal IS NULL AND E.DataDevolucaoPrevista < DATE('now');


--  Quais usuários pegaram mais livros emprestados
SELECT
    U.Nome AS Usuario,
    COUNT(E.EmprestimoID) AS TotalDeEmprestimos
FROM Usuarios U
JOIN Emprestimos E ON U.UsuarioID = E.UsuarioID
GROUP BY U.Nome
ORDER BY TotalDeEmprestimos DESC;