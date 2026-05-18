"""
Utilitários para adicionar novas questões e contextos ao banco.
"""
import json
from pathlib import Path

from .utils.analise import extrair_variaveis, extrair_operadores
from .utils.analise import calcular_complexidade, classificar_tipos
from .utils.enriquecedor import classificar_contexto


def _proximo_id(ids_existentes: set[str], prefixo: str) -> str:
    """Gera o próximo ID sequencial (c001, c002, ... ou q001, q002, ...)."""
    if not ids_existentes:
        return f"{prefixo}001"
    
    numeros = [
        int(iid.removeprefix(prefixo))
        for iid in ids_existentes
        if iid.startswith(prefixo)
    ]
    if not numeros:
        return f"{prefixo}001"
    
    return f"{prefixo}{max(numeros) + 1:03d}"


def adicionar_questao(
    formula: str,
    arquivo_json: str | Path,
) -> dict:
    """
    Adiciona uma nova fórmula ao banco de questões.
    
    A fórmula é analisada automaticamente para extrair:
    - variáveis proposicionais
    - operadores lógicos
    - complexidade
    - tipos de questão recomendados
    
    Args:
        formula: String da fórmula lógica (ex: "P -> (Q ^ R)")
        arquivo_json: Caminho do arquivo questoes.json
    
    Returns:
        dict: A entrada criada (com id, formula, variaveis, etc.)
    """
    # Carrega questões existentes
    with open(arquivo_json, "r", encoding="utf-8") as f:
        questoes = json.load(f)
    
    ids_existentes = {q["id"] for q in questoes}
    
    novo_id = _proximo_id(ids_existentes, "q")
    
    variaveis = extrair_variaveis(formula)
    operadores = extrair_operadores(formula)
    
    entrada = {
        "id": novo_id,
        "formula": formula,
        "variaveis": variaveis,
        "operadores": operadores,
        "complexidade": calcular_complexidade(formula),
        "tipos_recomendados": classificar_tipos(formula),
        "num_variaveis": len(variaveis),
    }
    
    questoes.append(entrada)
    
    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(questoes, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Questão {novo_id} adicionada: {formula}")
    return entrada


def adicionar_contexto(
    texto: str,
    arquivo_json: str | Path,
    tema: str | None = None,
    dominio: str | None = None,
    tags: list[str] | None = None,
    props_min: int = 2,
    props_max: int = 4,
) -> dict:
    """
    Adiciona um novo contexto ao banco.
    
    Se tema/dominio/tags não forem fornecidos, tenta classificar
    automaticamente por palavras-chave.
    
    Args:
        texto: Descrição do contexto em linguagem natural
        arquivo_json: Caminho do arquivo contextos.json
        tema: Tema manual (ex: "medicina"). Se None, classifica automaticamente
        dominio: Domínio manual. Se None, classifica automaticamente
        tags: Lista de tags. Se None, extrai automaticamente
        props_min: Mínimo de proposições que este contexto suporta
        props_max: Máximo de proposições que este contexto suporta
    
    Returns:
        dict: A entrada criada
    """
    with open(arquivo_json, "r", encoding="utf-8") as f:
        contextos = json.load(f)
    
    ids_existentes = {c["id"] for c in contextos}
    novo_id = _proximo_id(ids_existentes, "c")
    
    # Classificação automática se não forneceram tema
    if tema is None or dominio is None or tags is None:
        tema_auto, dominio_auto, tags_auto = classificar_contexto(texto)
    
    entrada = {
        "id": novo_id,
        "texto": texto,
        "tema": tema if tema else tema_auto,
        "dominio": dominio if dominio else dominio_auto,
        "tags": tags if tags is not None else tags_auto,
        "props_min": props_min,
        "props_max": props_max,
    }
    
    contextos.append(entrada)
    
    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(contextos, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Contexto {novo_id} adicionado: {texto}")
    return entrada


def adicionar_varias_questoes(
    formulas: list[str],
    arquivo_json: str | Path,
) -> list[dict]:
    """
    Adiciona várias fórmulas de uma vez ao banco.
    
    Args:
        formulas: Lista de strings de fórmulas lógicas
        arquivo_json: Caminho do arquivo questoes.json
    
    Returns:
        list[dict]: Lista das entradas criadas
    """
    entradas = []
    for formula in formulas:
        entradas.append(
            adicionar_questao(formula, arquivo_json)
        )
    return entradas


def adicionar_varios_contextos(
    textos: list[str],
    arquivo_json: str | Path,
) -> list[dict]:
    """
    Adiciona vários contextos de uma vez ao banco.
    
    Args:
        textos: Lista de strings de contextos
        arquivo_json: Caminho do arquivo contextos.json
    
    Returns:
        list[dict]: Lista das entradas criadas
    """
    entradas = []
    for texto in textos:
        entradas.append(
            adicionar_contexto(texto, arquivo_json)
        )
    return entradas


# ─── CLI ────────────────────────────────────────────────

def cli_adicionar_questao():
    """CLI interativo para adicionar uma questão."""
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Uso: python -m propos.adicionador questao 'P -> (Q ^ R)'")
        print("      python -m propos.adicionador contexto 'Um médico...'")
        sys.exit(1)
    
    tipo = sys.argv[1]
    base = Path(__file__).resolve().parent.parent.parent
    dados = base / "dados"
    
    if tipo == "questao" and len(sys.argv) >= 3:
        formula = sys.argv[2]
        adicionar_questao(formula, dados / "questoes.json")
    elif tipo == "contexto" and len(sys.argv) >= 3:
        texto = sys.argv[2]
        adicionar_contexto(texto, dados / "contextos.json")
    else:
        print(f"Argumentos inválidos: {sys.argv}")
        sys.exit(1)


if __name__ == "__main__":
    cli_adicionar_questao()
