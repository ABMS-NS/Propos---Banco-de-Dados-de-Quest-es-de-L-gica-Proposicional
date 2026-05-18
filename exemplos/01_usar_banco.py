import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from propos import BancoQuestoes

banco = BancoQuestoes()

banco.carregar_contextos_json(BASE / "dados" / "contextos.json")
banco.carregar_questoes_json(BASE / "dados" / "questoes.json")

# ─── Estatísticas ─────────────────────────────────────
stats = banco.estatisticas()
print("ESTATÍSTICAS DO BANCO")
print(f"  Questões: {stats['total_questoes']}")
print(f"  Contextos: {stats['total_contextos']}")
print(f"  Complexidade média: {stats['complexidade_media']:.1f}")
print(f"  Complexidade min/max: {stats['complexidade_min']}/{stats['complexidade_max']}")
print(f"  Variáveis média: {stats['variaveis_media']:.1f}")
print()
print("  Temas disponíveis:", ", ".join(banco.listar_temas()))
print("  Tipos de questão:", ", ".join(banco.listar_tipos()))
print("  Operadores:", ", ".join(banco.listar_operadores()))
print()

# ─── Filtrar questões simples (só condicionais) ───────
condicionais = banco.filtrar_questoes(operador="->")
print(f"Questões com '->': {len(condicionais)}")

# ─── Filtrar questões de complexidade baixa ────────────
faceis = banco.filtrar_questoes(complexidade_max=2, num_variaveis=2)
print(f"Questões fáceis (complexidade <=2, 2 variáveis): {len(faceis)}")
for q in faceis:
    print(f"    {q.id}: {q.formula}")
print()

# ─── Sortear combinação contexto + fórmula ─────────────
print("COMBINAÇÕES SORTEADAS:")
for tema in ["investigacao", "medicina", "tecnologia"]:
    try:
        formula, contexto = banco.sortear_combinacao(tema=tema)
        print(f"  [{tema}]")
        print(f"    Contexto: {contexto.texto}")
        print(f"    Fórmula:  {formula.formula}")
        print(f"    Variáveis: {', '.join(formula.variaveis)}")
        print(f"    Tipos:     {', '.join(formula.tipos_recomendados)}")
        print()
    except ValueError as e:
        print(f"  [{tema}] {e}")
        print()

# ─── Exportar banco completo ───────────────────────────
banco.exportar_json(BASE / "dados" / "banco_completo.json")
print("✓ Banco exportado para dados/banco_completo.json")
