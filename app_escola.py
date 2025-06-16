import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ------------------ BANCO DE DADOS ------------------

def conectar():
    return sqlite3.connect("cadastro.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL UNIQUE,
            turma_id INTEGER,
            FOREIGN KEY(turma_id) REFERENCES turmas(id)
        )
    """)
    conn.commit()
    conn.close()

def get_turmas_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turmas")
    turmas = cursor.fetchall()
    conn.close()
    return turmas

def get_alunos_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT alunos.nome, alunos.matricula, turmas.nome
        FROM alunos
        JOIN turmas ON alunos.turma_id = turmas.id
    """)
    alunos = cursor.fetchall()
    conn.close()
    return alunos

def adicionar_turma(nome):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (nome,))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Turma já existe!")
    finally:
        conn.close()

def adicionar_aluno(nome, matricula, turma_nome):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma_nome,))
        turma_id = cursor.fetchone()
        if turma_id:
            cursor.execute("INSERT INTO alunos (nome, matricula, turma_id) VALUES (?, ?, ?)", (nome, matricula, turma_id[0]))
            conn.commit()
        else:
            messagebox.showerror("Erro", "Turma não encontrada")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Matrícula já cadastrada!")
    finally:
        conn.close()

def excluir_aluno(matricula):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alunos WHERE matricula = ?", (matricula,))
    conn.commit()
    conn.close()

def excluir_turma(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM turmas WHERE nome = ?", (nome,))
    turma = cursor.fetchone()
    if turma:
        turma_id = turma[0]
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = ?", (turma_id,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Não é possível excluir turma com alunos cadastrados")
        else:
            cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
            conn.commit()
    conn.close()

# ------------------ INTERFACE GRÁFICA ------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro Acadêmico")
        self.root.geometry("700x500")

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.frame_turmas = ttk.Frame(self.tabs)
        self.frame_alunos = ttk.Frame(self.tabs)
        self.tabs.add(self.frame_turmas, text="Turmas")
        self.tabs.add(self.frame_alunos, text="Alunos")

        self.criar_frame_turmas()
        self.criar_frame_alunos()

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_help)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

    def criar_frame_turmas(self):
        ttk.Label(self.frame_turmas, text="Nome da Turma:").pack(pady=5)
        self.nome_turma_entry = ttk.Entry(self.frame_turmas)
        self.nome_turma_entry.pack(pady=5)

        ttk.Button(self.frame_turmas, text="Adicionar Turma", command=self.adicionar_turma).pack(pady=5)
        ttk.Button(self.frame_turmas, text="Excluir Turma", command=self.excluir_turma).pack(pady=5)

        self.lista_turmas = ttk.Treeview(self.frame_turmas, columns=("Nome",), show="headings")
        self.lista_turmas.heading("Nome", text="Turma")
        self.lista_turmas.pack(fill="both", expand=True, pady=10)
        self.atualizar_lista_turmas()

    def criar_frame_alunos(self):
        ttk.Label(self.frame_alunos, text="Nome do Aluno:").pack(pady=5)
        self.nome_aluno_entry = ttk.Entry(self.frame_alunos)
        self.nome_aluno_entry.pack(pady=5)

        ttk.Label(self.frame_alunos, text="Matrícula:").pack(pady=5)
        self.matricula_entry = ttk.Entry(self.frame_alunos)
        self.matricula_entry.pack(pady=5)

        ttk.Label(self.frame_alunos, text="Turma:").pack(pady=5)
        self.turma_combobox = ttk.Combobox(self.frame_alunos)
        self.turma_combobox.pack(pady=5)

        ttk.Button(self.frame_alunos, text="Adicionar Aluno", command=self.adicionar_aluno).pack(pady=5)
        ttk.Button(self.frame_alunos, text="Excluir Aluno", command=self.excluir_aluno).pack(pady=5)

        self.lista_alunos = ttk.Treeview(self.frame_alunos, columns=("Nome", "Matrícula", "Turma"), show="headings")
        self.lista_alunos.heading("Nome", text="Nome do Aluno")
        self.lista_alunos.heading("Matrícula", text="Matrícula")
        self.lista_alunos.heading("Turma", text="Turma")
        self.lista_alunos.pack(fill="both", expand=True, pady=10)
        self.atualizar_lista_alunos()

    def adicionar_turma(self):
        nome = self.nome_turma_entry.get()
        if nome:
            adicionar_turma(nome)
            self.atualizar_lista_turmas()
            self.atualizar_combobox_turmas()

    def excluir_turma(self):
        selecionado = self.lista_turmas.selection()
        if selecionado:
            nome = self.lista_turmas.item(selecionado[0], 'values')[0]
            excluir_turma(nome)
            self.atualizar_lista_turmas()
            self.atualizar_combobox_turmas()

    def adicionar_aluno(self):
        nome = self.nome_aluno_entry.get()
        matricula = self.matricula_entry.get()
        turma = self.turma_combobox.get()
        if nome and matricula and turma:
            adicionar_aluno(nome, matricula, turma)
            self.atualizar_lista_alunos()

    def excluir_aluno(self):
        selecionado = self.lista_alunos.selection()
        if selecionado:
            matricula = self.lista_alunos.item(selecionado[0], 'values')[1]
            excluir_aluno(matricula)
            self.atualizar_lista_alunos()

    def atualizar_lista_turmas(self):
        for i in self.lista_turmas.get_children():
            self.lista_turmas.delete(i)
        for turma in get_turmas_db():
            self.lista_turmas.insert('', 'end', values=(turma[1],))

    def atualizar_lista_alunos(self):
        for i in self.lista_alunos.get_children():
            self.lista_alunos.delete(i)
        for aluno in get_alunos_db():
            self.lista_alunos.insert('', 'end', values=aluno)

    def atualizar_combobox_turmas(self):
        turmas = [t[1] for t in get_turmas_db()]
        self.turma_combobox['values'] = turmas

    def show_help(self):
        ajuda = tk.Toplevel(self.root)
        ajuda.title("Ajuda")
        ajuda.geometry("400x200")
        tk.Label(ajuda, text="Alunos wyden", font=("Arial", 12)).pack(expand=True)

if __name__ == '__main__':
    criar_tabelas()
    root = tk.Tk()
    app = App(root)
    app.atualizar_combobox_turmas()
    root.mainloop()
