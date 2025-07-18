# Projeto de Gestão de Biblioteca Digital com SQL e Python

Este repositório contém um projeto de um sistema de gerenciamento de biblioteca digital. A aplicação permite catalogar livros, gerenciar autores e interagir com o banco de dados através de uma interface de console em Python.

## Visão Geral do Projeto

O objetivo deste projeto é demonstrar habilidades fundamentais em design de banco de dados, escrita de consultas SQL e integração de um banco de dados com uma aplicação Python.

### Funcionalidades

* **Banco de Dados SQL:**
    * Criação de um esquema relacional com tabelas para Livros, Autores, Usuários e Empréstimos.
    * Uso de chaves primárias e estrangeiras para garantir a integridade dos dados.
    * Scripts SQL para criação, inserção de dados e consultas complexas.
* **Aplicação Python:**
    * Conexão com um banco de dados SQLite.
    * Interface de linha de comando (CLI) para interagir com o sistema.
    * Funcionalidades para adicionar e listar livros no acervo.

## Estrutura do Banco de Dados

O banco de dados foi modelado com as seguintes entidades e relacionamentos:

* **Autores**: Armazena informações sobre os autores.
* **Livros**: Catálogo de livros, com um relacionamento para a tabela `Autores`.
* **Usuarios**: Registra os usuários da biblioteca.
* **Emprestimos**: Registra os empréstimos, conectando `Livros` e `Usuarios`.

<!--
![Diagrama do Banco de Dados](URL_PARA_UMA_IMAGEM_DO_SEU_DIAGRAMA)
*(Opcional, mas altamente recomendado: crie um diagrama simples em uma ferramenta como dbdiagram.io ou draw.io, salve como imagem e adicione ao seu repositório para exibir aqui.)*
-->
## Tecnologias Utilizadas

* **Linguagem de Banco de Dados:** SQL (SQLite)
* **Linguagem de Programação:** Python 3
* **Bibliotecas Python:** `sqlite3`

## Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/AngelicaBGLuciano/projeto-biblioteca.git]
    cd projeto-biblioteca
    ```

2.  **Navegue até a pasta da aplicação:**
    ```bash
    cd app
    ```

3.  **Execute o script Python:**
    ```bash
    python biblioteca_app.py
    ```
    A aplicação será iniciada no seu terminal e o arquivo `biblioteca.db` será criado automaticamente.

## Exemplos de Consultas SQL

A pasta `/database` contém exemplos de consultas SQL para extrair informações úteis, como:

* Listar todos os livros de um determinado autor.
* Encontrar quais livros estão atualmente emprestados.
* Identificar empréstimos com devolução atrasada.

---
*Desenvolvido por Angélica Luciano*
