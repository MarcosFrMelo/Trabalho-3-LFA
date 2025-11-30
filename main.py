#Feito por Marcos Freire de Melo e Luiz Felipe da Paz Leal


import tkinter as tk
from tkinter import scrolledtext
import copy

def tokenizar(prod):
    tokens = []
    i = 0
    while i < len(prod):
        c = prod[i]
        if c.isspace():
            i += 1
            continue
        if c.isupper():
            j = i
            while j < len(prod) and prod[j].isupper():
                j += 1
            k = j
            while k < len(prod) and prod[k] == "'":
                k += 1
            tokens.append(prod[i:k])
            i = k
            continue
        if prod[i] in '()+-*=/<>[]{}.,;':
            tokens.append(prod[i])
            i += 1
            continue
        j = i
        while j < len(prod) and (prod[j].islower() or prod[j].isdigit()):
            j += 1
        if j > i:
            tokens.append(prod[i:j])
            i = j
            continue
        tokens.append(prod[i])
        i += 1
    return tokens

def juntar_tokens(tokens):
    s = ""
    for t in tokens:
        s += t
    return s if s else "ε"

def ler_gramatica(texto):
    gramatica = {}
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if not linha or "->" not in linha:
            continue
        esq, dir = linha.split("->", 1)
        esq = esq.strip()
        producoes = [p.strip() for p in dir.split("|")]
        gramatica[esq] = [tokenizar(p) for p in producoes]
    return gramatica

def imprimir_gramatica(G):
    saida = ""
    for A, prods in G.items():
        saida += A + " -> " + " | ".join(juntar_tokens(p) for p in prods) + "\n"
    return saida

def remover_recursao(gram):
    nts = list(gram.keys())
    G = copy.deepcopy(gram)

    for i in range(len(nts)):
        A = nts[i]

        for j in range(i):
            B = nts[j]
            novas = []
            for prod in G[A]:
                if prod and prod[0] == B:
                    resto = prod[1:]
                    for beta in G[B]:
                        novas.append(beta + resto)
                else:
                    novas.append(prod)
            G[A] = novas

        alfa = []
        beta = []

        for prod in G[A]:
            if prod and prod[0] == A:
                alfa.append(prod[1:])
            else:
                beta.append(prod)

        if alfa:
            A_p = A + "'"
            if beta:
                G[A] = [b + [A_p] for b in beta]
            else:
                G[A] = [[A_p]]
            G[A_p] = [a + [A_p] for a in alfa] + [[]]

    return G

def maior_prefixo_str(lista_str):
    if not lista_str:
        return ""
    prefixo = lista_str[0]
    for s in lista_str[1:]:
        while not s.startswith(prefixo):
            prefixo = prefixo[:-1]
            if prefixo == "":
                return ""
    return prefixo

def fatorar(G):
    mudou = True
    while mudou:
        mudou = False
        novo = {}

        for A, prods in G.items():
            if len(prods) <= 1:
                novo[A] = prods
                continue

            prod_strs = [juntar_tokens(p) for p in prods]
            prefixo = maior_prefixo_str(prod_strs)

            if prefixo and len(prefixo) > 0:
                ocorrencias = sum(1 for s in prod_strs if s.startswith(prefixo))
                if ocorrencias < 2:
                    novo[A] = prods
                    continue

                mudou = True
                A_p = A + "'"

                prefixo_tokens = tokenizar(prefixo)
                grupos = []
                for s in prod_strs:
                    sufixo_str = s[len(prefixo):]
                    if sufixo_str == "":
                        grupos.append([]) 
                    else:
                        grupos.append(tokenizar(sufixo_str))

                novo[A] = [prefixo_tokens + [A_p]]
                novo[A_p] = grupos
            else:
                novo[A] = prods

        G = novo
    return G

def processar():
    texto = entrada.get("1.0", tk.END)
    G = ler_gramatica(texto)

    saida = "=== Gramática Inicial ===\n"
    saida += imprimir_gramatica(G) + "\n"

    G2 = remover_recursao(G)
    saida += "=== Sem Recursão à Esquerda ===\n"
    saida += imprimir_gramatica(G2) + "\n"

    G3 = fatorar(G2)
    saida += "=== Fatorada ===\n"
    saida += imprimir_gramatica(G3)

    resultado.delete("1.0", tk.END)
    resultado.insert(tk.END, saida)

janela = tk.Tk()
janela.title("Eliminação de Recursão e Fatoração")

tk.Label(janela, text="Digite a gramática:").pack()

entrada = scrolledtext.ScrolledText(janela, width=80, height=10)
entrada.pack()

botao = tk.Button(janela, text="Processar", command=processar)
botao.pack(pady=6)

tk.Label(janela, text="Resultado:").pack()

resultado = scrolledtext.ScrolledText(janela, width=80, height=20)
resultado.pack()

janela.mainloop()
