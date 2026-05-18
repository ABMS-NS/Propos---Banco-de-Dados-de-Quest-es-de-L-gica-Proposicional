import re


def extrair_variaveis(formula: str) -> list[str]:
    return sorted(set(re.findall(r'[A-Z]', formula)))


def extrair_operadores(formula: str) -> list[str]:
    ops = []
    if '->' in formula:
        ops.append('->')
    if '<->' in formula:
        ops.append('<->')
    if '^' in formula:
        ops.append('^')
    if 'v' in formula or '|' in formula:
        ops.append('v')
    if '~' in formula or '¬' in formula:
        ops.append('~')
    return ops


def calcular_complexidade(formula: str) -> int:
    return (formula.count('->') + formula.count('<->')
            + formula.count('^') + formula.count('v')
            + formula.count('|') + formula.count('~')
            + formula.count('¬'))


def classificar_tipos(formula: str) -> list[str]:
    tipos = []
    if '->' in formula or '→' in formula:
        tipos.append('INFERENCIA')
    if formula.count('~') >= 2 or formula.count('¬') >= 2:
        tipos.append('CIRCUNSTANCIAS_FALSAS')
    if formula.count('^') >= 2 or formula.count('&') >= 2:
        tipos.append('TABELA_VERDADE')
    if 'v' in formula or '|' in formula:
        tipos.append('EQUIVALENCIA')
    if not tipos:
        tipos.append('VALOR_VERDADE')
    return tipos


def enriquecer_formula(formula_str: str, id_prefix: str = "q") -> dict:
    variaveis = extrair_variaveis(formula_str)
    operadores = extrair_operadores(formula_str)
    return {
        "id": f"{id_prefix}{len(variaveis)}",
        "formula": formula_str,
        "variaveis": variaveis,
        "operadores": operadores,
        "complexidade": calcular_complexidade(formula_str),
        "tipos_recomendados": classificar_tipos(formula_str),
        "num_variaveis": len(variaveis)
    }
