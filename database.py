#banco de dados SQLite 

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    data_nasc TEXT NOT NULL,
    genero TEXT,
    telefone INTEGER,
    idade INTEGER,
    doencas TEXT,
    remedios TEXT,
    alergias TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
    conn.commit()
    conn.close()

def inserir_paciente(nome, cpf, data_nasc, genero, telefone, idade, doencas, remedios, alergias):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pacientes (nome, cpf, data_nasc, genero, telefone, idade, doencas, remedios, alergias)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (nome, cpf, data_nasc, genero, telefone, idade, doencas, remedios, alergias))
    
    conn.commit()
    conn.close()

def identificar_cpf(cpf):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes WHERE cpf = ?", (cpf,))
    pacientes = cursor.fetchall()

    conn.close()
    return pacientes