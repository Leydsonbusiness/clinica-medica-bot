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
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    data_nasc TEXT NOT NULL,
    genero TEXT,
    telefone TEXT,
    data_cadastro TEXT
)  
""")
    conn.commit()
    conn.close()

def inserir_paciente(nome, cpf, data_nasc, genero, telefone, data_cadastro):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pacientes (nome, cpf, data_nasc, genero, telefone, data_cadastro)
    VALUES (?, ?, ?, ?, ?, ?)
""", (nome, cpf, data_nasc, genero, telefone, data_cadastro))
    conn.commit()
    conn.close()