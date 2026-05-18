"""
Exemplo genérico de como consumir o banco de questões de outros projetos.

Mostra a API pública: qualquer projeto externo pode importar
`banco_questoes` e usar os mesmos métodos.
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from propos import BancoQuestoes
from propos.modelos import Contexto, FormulaQuestao

banco = BancoQuestoes()
banco.carregar_contextos_json(BASE / "dados" / "contextos.json")
banco.carregar_questoes_json(BASE / "dados" / "questoes.json")

# ─── API PÚBLICA ──────────────────────────────────────

print("COMBINAÇÃO ALEATÓRIA:")
formula, contexto = banco.sortear_combinacao()
print(f"  Contexto: {contexto.texto}")
print(f"  Fórmula:  {formula.formula}")
print()

print("FILTROS DISPONÍVEIS:")
for tipo in ["INFERENCIA", "TABELA_VERDADE", "EQUIVALENCIA"]:
    qs = banco.filtrar_questoes(tipo=tipo, complexidade_max=3)
    print(f"  {tipo}: {len(qs)} fórmulas (complexidade <= 3)")
print()

print("CONTEXTOS POR TEMA:")
investigacao = banco.filtrar_contextos(tema="investigacao")
medicina = banco.filtrar_contextos(tema="medicina")
print(f"  Investigação: {len(investigacao)}  |  Medicina: {len(medicina)}")

print()
print("COMPATIBILIDADE:")
q = banco.filtrar_questoes(num_variaveis=2)[0]
compat = banco.contextos_compatíveis(q)
print(f"  '{q.formula}' (2 vars) é compatível com {len(compat)} contextos")

print()
print("OBJETOS (dataclasses):")
q0: FormulaQuestao = list(banco.questoes.values())[0]
c0: Contexto = list(banco.contextos.values())[0]
print(f"  Contexto: id={c0.id}, tema={c0.tema}, tags={c0.tags}")
print(f"  Fórmula:  id={q0.id}, {q0.formula}, ops={q0.operadores}, tipo={q0.tipos_recomendados[0]}")
