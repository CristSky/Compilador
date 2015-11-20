__author__ = 'Claudio Costa'
# -*- coding: utf-8 -*-
#!/usr/bin/env python

import collections
import re
from collections import deque

f = open("sintatico1.c", "r")
statements = f.read()
f.close()

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

def tokenize(code):
    keywords = {'id'}
    token_specification = [
        ('COMMENT', r'(?://[A-Za-z0-9_]+\n)|(#.*?\n)'),  # comentario com // ou #
        ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
        ('ASSIGN', r':='),  # Assignment operator
        ('END', r';'),  # Statement terminator
        ('ID', r'[A-Za-z0-9_]+'),  # Identifiers
        ('OP', r'[+\-*/%]'),  # Arithmetic operators
        ('NEWLINE', r'\n'),  # Line endings
        ('SKIP', r'[ \t\r\n]+'),  # Skip over spaces and tabs
        ('MISMATCH', r'./'),  # Any other character
        ('STRING', r'(".*?")'),
        ('SPECIAL', r'[<>(){}.,\[\]]'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'NEWLINE' or kind == 'COMMENT':
            line_start = mo.end()
            line_num += 1
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError('%r unexpected on line %d' % (value, line_num))
        else:
            if kind == 'ID' and value in keywords:
                kind = value
            column = mo.start() - line_start
            yield Token(kind, value, line_num, column)


tokens = deque()
for token in tokenize(statements):
    print(token)
    tokens.append(token.value)
tokens.append('$')

def analisadorSintatico(cadeia):
#MATRIZ SINTATICA
#               0    1      2       3      4      5      6     7     8
    Matriz = [['', '+'   , '-'  , '/'  , '*'  , 'id', '(' , ')', '$'],  #0
              ['E', 'MT+', 'MT-', ''   , ''   , 'MT', 'MT', '' , '' ],  #1
              ['M', 'MT+', 'MT-', ''   , ''   , ''  , ''  , 'y', 'y'],  #2
              ['T', ''   , ''   , ''   , ''   , 'GF', 'GF', '' , '' ],  #3
              ['G', 'y'  , 'y'  , 'GF/', 'GF*', ''  , ''  , 'y', 'y'],  #4
              ['F', ''   , ''   , ''   , ''   , 'id',')E(', '' , '']]  #5

    print(cadeia)
    pilha = []
    pilha.append('$')
    pilha.append('E')
    print(pilha)

    while pilha is not []:
        if pilha[-1] == '$' and cadeia[0] == '$':
            print("Compilação efetuada com Sucesso!!!")
            break
        elif pilha[-1] == cadeia[0]:    #Se achou o token
            pilha.pop()
            cadeia.popleft()
#-----------------------------REGRA E -----------------------------------------------------------------------
        elif pilha[-1] == 'E':
            if cadeia[0] == '+':
                pilha.pop()
                pilha = pilha + list(Matriz[1][1])
            elif cadeia[0] == '-':
                pilha.pop()
                pilha = pilha + list(Matriz[1][2])
            elif cadeia[0] == 'id':
                pilha.pop()
                pilha = pilha + list(Matriz[1][5])
            elif cadeia[0] == '(':
                pilha.pop()
                pilha = pilha + list(Matriz[1][6])
            elif cadeia[0] == '/' or cadeia[0] == '*' or cadeia[0] == ')' or cadeia[0] == '$':
                print("Erro de Compilação token não esperado: " + cadeia[0])
                break
#-----------------------------REGRA M -----------------------------------------------------------------------
        elif pilha[-1] == 'M':
            if cadeia[0] == '+':
                pilha.pop()
                pilha = pilha + list(Matriz[2][1])
            elif cadeia[0] == '-':
                pilha.pop()
                pilha = pilha + list(Matriz[2][2])
            elif cadeia[0] == ')' or cadeia[0] == '$':
                pilha.pop()
            elif cadeia[0] == '/' or cadeia[0] == '*' or cadeia[0] == 'id' or cadeia[0] == '(':
                print("Erro de Compilção token não esperado: "+ cadeia[0])
                break
#-----------------------------REGRA T -----------------------------------------------------------------------
        elif pilha[-1] == 'T':
            if cadeia[0] == 'id':
                pilha.pop()
                pilha = pilha + list(Matriz[3][5])
            elif cadeia[0] == '(':
                pilha.pop()
                pilha = pilha + list(Matriz[3][6])
            elif cadeia[0] == '+' or cadeia[0] == '-' or cadeia[0] == '/' or cadeia[0] == '*' or cadeia[0] == ')' or cadeia[0] == '$':
                print("Erro de Compilção token não esperado: " + cadeia[0])
                break
#-----------------------------REGRA G -----------------------------------------------------------------------
        elif pilha[-1] == 'G':
            if cadeia[0] == '+' or cadeia[0] == '-' or cadeia[0] == ')' or cadeia[0] == '$':
                pilha.pop()
            elif cadeia[0] == '/':
                pilha.pop()
                pilha = pilha + list(Matriz[4][3])
            elif cadeia[0] == '*':
                pilha.pop()
                pilha = pilha + list(Matriz[4][4])
            elif cadeia[0] == 'id' or cadeia[0] == '(':
                print("Erro de Compilação token não esperado: " + cadeia[0])
                break
#-----------------------------REGRA F -----------------------------------------------------------------------
        elif pilha[-1] == 'F':
            if cadeia[0] == 'id':
                pilha.pop()
                pilha.append(Matriz[5][5])
            elif cadeia[0] == '(':
                pilha.pop()
                pilha = pilha + list(Matriz[5][6])
            elif cadeia[0] == '+' or cadeia[0] == '-' or cadeia[0] == '/' or cadeia[0] == '*' or cadeia[0] == ')' or cadeia[0] == '$':
                print("Erro de Compilção token não esperado: " + cadeia[0])
                break
        elif pilha[-1] == '$' and (not cadeia[0] == '$'):
            print("Erro de Compilção token não esperado: " + cadeia[0])
            break
        elif cadeia[0] == '$' and (not pilha[-1] == '$'):
            print("Erro de Compilção token não esperado: " + cadeia[0])
            break
        print(cadeia[0])
        print(pilha)

analisadorSintatico(tokens)
