__author__ = 'Claudio Costa'
# -*- coding: utf-8 -*-
#!/usr/bin/env python
import collections
import re
from collections import deque

f = open("sintatico.c", "r")
statements = f.read()
f.close()

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

def tokenize(code):
    keywords = {'a'}
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


#MATRIZ SINTATICA                                    TRANSIÇÕES
#               0    1      2      3      4      5     6     7
Matriz =     [['', 'a'   , '('  , ')'  , ','  , '$' , 'S' , 'L'],  #0
              [0 , 'E2' , ''   , ''   , ''   , ''  ,  1  , '' ],  #1
              [1 , ''    , ''   , ''   , ''   , 'OK', ''  , '' ],  #2
              [2 , ''    , 'E3' , 'R2' , 'R2' , 'R2', ''  , '' ],  #3
              [3 , 'E2'  , ''   , ''   , ''   , ''  ,  5  ,  4 ],  #4
              [4 , ''    , ''   , 'E6' , ''   , ''  , ''  , '' ],  #5
              [5 , ''    , ''   , 'R4' , 'E7' , 'R4', ''  , '' ],  #6
              [6 , ''    , ''   , 'R1' , 'R1' , 'R1', ''  , '' ],  #7
              [7 , 'E2'  , ''   , ''   , ''   , ''  ,  5  ,  8 ],  #8
              [8 , ''    , ''   , 'R3' , ''   , 'R3', ''  , '' ]]  #9

def transicoes(linha, regra):
    if linha == 0 and regra == 'S':
        return 1
    elif (linha == 3 or linha == 7) and regra == 'S':
        return 5
    elif linha == 3 and regra == 'L':
        return 4
    elif linha == 7 and regra == 'L':
        return 8


def analisadorSLR(cadeia):

    print(cadeia)
    pilha = []
    pilha.append(0)
    print(pilha)
    print(cadeia[0])

    while pilha is not []:
#-----------------------------LINHA 1-----------------------------------------------------------------------
        if pilha[-1] == 1 and cadeia[0] == '$':   #se o ultimo el da pilha =1 e cadeia vazia
            print("Compilação efetuada com Sucesso!!!")
            break
#-----------------------------LINHA 0-----------------------------------------------------------------------
        elif pilha[-1] == 0 and cadeia[0] == 'a':    #linha 0 e token = a
            pilha.append('a')
            pilha.append(2)
            cadeia.popleft()
#-----------------------------LINHA 2-----------------------------------------------------------------------
        elif pilha[-1] == 2 and cadeia[0] == '(':
            pilha.append('(')
            pilha.append(3)
            cadeia.popleft()
        elif pilha[-1] == 2 and (cadeia[0] == ')' or cadeia[0] == ',' or cadeia[0] == '$'):
            pilha.pop()
            pilha.pop()
            pilha.append('S')
            pilha.append(transicoes(pilha[len(pilha)-2],pilha[-1]))
#-----------------------------LINHA 3-----------------------------------------------------------------------
        elif pilha[-1] == 3 and cadeia[0] == 'a':
            pilha.append('a')
            pilha.append(2)
            cadeia.popleft()
#-----------------------------LINHA 4-----------------------------------------------------------------------
        elif pilha[-1] == 4 and cadeia[0] == ')':
            pilha.append(')')
            pilha.append(6)
            cadeia.popleft()
#-----------------------------LINHA 5-----------------------------------------------------------------------
        elif pilha[-1] == 5 and cadeia[0] == ',':
            pilha.append(',')
            pilha.append(7)
            cadeia.popleft()
        elif pilha[-1] == 5 and (cadeia[0] == ')' or cadeia[0] == '$'):
            pilha.pop()
            pilha.pop()
            pilha.append('L')
            pilha.append(transicoes(pilha[len(pilha)-2],pilha[-1]))
#-----------------------------LINHA 6-----------------------------------------------------------------------
        elif pilha[-1] == 6 and (cadeia[0] == ')' or cadeia[0] == ',' or cadeia[0] == '$'):
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.append('S')
            pilha.append(transicoes(pilha[len(pilha)-2],pilha[-1]))
#-----------------------------LINHA 7-----------------------------------------------------------------------
        elif pilha[-1] == 7 and cadeia[0] == 'a':    #linha 0 e token = a
            pilha.append('a')
            pilha.append(2)
            cadeia.popleft()
#-----------------------------LINHA 8-----------------------------------------------------------------------
        elif pilha[-1] == 8 and (cadeia[0] == ')' or cadeia[0] == '$'):
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.pop()
            pilha.append('L')
            pilha.append(transicoes(pilha[len(pilha)-2],pilha[-1]))
        print(pilha)

analisadorSLR(tokens)