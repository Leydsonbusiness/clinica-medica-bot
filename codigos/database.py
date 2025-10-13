#base de dados SQLite 
import sqlite3

def conectar():
    return sqlite3.connect("database.db")

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome varchar(100) TEXT NOT NULL,
    cpf varchar(19) TEXT UNIQUE NOT NULL,
    data_nasc TEXT NOT NULL,
    genero TEXT,
    telefone TEXT,
    idade INTEGER
    data_cadastro TIMESTAMP DEFAUT CURRENT_TIMESTAMP,
)  
""")
    conn.commit()
    conn.close()

def inserir_paciente(nome, cpf, data_nasc, genero, telefone, idade, data_cadastro):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pacientes (nome, cpf, data_nasc, genero, telefone, idade, data_cadastro)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (nome, cpf, data_nasc, genero, telefone, idade, data_cadastro))
    conn.commit()
    conn.close()