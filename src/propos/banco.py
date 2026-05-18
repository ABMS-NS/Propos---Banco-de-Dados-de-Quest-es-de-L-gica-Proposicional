import json
import random
from pathlib import Path

from .modelos import Contexto, FormulaQuestao
from .utils.analise import (
    calcular_complexidade,
    classificar_tipos,
    extrair_operadores,
    extrair_variaveis,
)


class BancoQuestoes:
    def __init__(self):
        self.contextos: dict[str, Contexto] = {}
        self.questoes: dict[str, FormulaQuestao] = {}

    # ─── CARGA ───────────────────────────────────────────────

    def carregar_contextos_json(self, caminho: str | Path):
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, dict) and "contextos" in dados:
            dados = dados["contextos"]
        for item in dados:
            ctx = Contexto(**item)
            self.contextos[ctx.id] = ctx

    def carregar_questoes_json(self, caminho: str | Path):
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, dict) and "questoes" in dados:
            dados = dados["questoes"]
        for item in dados:
            q = FormulaQuestao(**item)
            if not q.variaveis:
                q.variaveis = extrair_variaveis(q.formula)
            if not q.operadores:
                q.operadores = extrair_operadores(q.formula)
            if q.complexidade == 0:
                q.complexidade = calcular_complexidade(q.formula)
            if not q.tipos_recomendados:
                q.tipos_recomendados = classificar_tipos(q.formula)
            q.num_variaveis = len(q.variaveis)
            self.questoes[q.id] = q

    def carregar_json_legado(
        self, caminho_contextos: str | Path, caminho_questoes: str | Path
    ):
        with open(caminho_contextos, "r", encoding="utf-8") as f:
            ctxs_str = json.load(f)
        for i, texto in enumerate(ctxs_str, 1):
            ctx_id = f"c{i:03d}"
            self.contextos[ctx_id] = Contexto(id=ctx_id, texto=texto)

        with open(caminho_questoes, "r", encoding="utf-8") as f:
            formulas_str = json.load(f)
        for i, formula in enumerate(formulas_str, 1):
            q_id = f"q{i:03d}"
            self.questoes[q_id] = FormulaQuestao(
                id=q_id,
                formula=formula,
                variaveis=extrair_variaveis(formula),
                operadores=extrair_operadores(formula),
                complexidade=calcular_complexidade(formula),
                tipos_recomendados=classificar_tipos(formula),
                num_variaveis=len(extrair_variaveis(formula)),
            )

    # ─── FILTROS ─────────────────────────────────────────────

    def filtrar_questoes(
        self,
        *,
        operador: str | None = None,
        complexidade_max: int | None = None,
        complexidade_min: int | None = None,
        num_variaveis: int | None = None,
        tipo: str | None = None,
    ) -> list[FormulaQuestao]:
        resultados = list(self.questoes.values())
        if operador:
            resultados = [q for q in resultados if operador in q.operadores]
        if complexidade_max is not None:
            resultados = [q for q in resultados if q.complexidade <= complexidade_max]
        if complexidade_min is not None:
            resultados = [q for q in resultados if q.complexidade >= complexidade_min]
        if num_variaveis is not None:
            resultados = [q for q in resultados if q.num_variaveis == num_variaveis]
        if tipo:
            resultados = [q for q in resultados if tipo in q.tipos_recomendados]
        return resultados

    def filtrar_contextos(
        self,
        *,
        tema: str | None = None,
        dominio: str | None = None,
        tag: str | None = None,
        props_min: int | None = None,
        props_max: int | None = None,
    ) -> list[Contexto]:
        resultados = list(self.contextos.values())
        if tema:
            resultados = [c for c in resultados if c.tema == tema]
        if dominio:
            resultados = [c for c in resultados if c.dominio == dominio]
        if tag:
            resultados = [c for c in resultados if tag in c.tags]
        if props_min is not None:
            resultados = [c for c in resultados if c.props_min <= props_min]
        if props_max is not None:
            resultados = [c for c in resultados if c.props_max >= props_max]
        return resultados

    # ─── COMBINAÇÃO ──────────────────────────────────────────

    def contextos_compatíveis(self, questao: FormulaQuestao) -> list[Contexto]:
        return [
            c
            for c in self.contextos.values()
            if c.props_min <= questao.num_variaveis <= c.props_max
        ]

    def questoes_compatíveis(self, contexto: Contexto) -> list[FormulaQuestao]:
        return [
            q
            for q in self.questoes.values()
            if contexto.props_min <= q.num_variaveis <= contexto.props_max
        ]

    def sortear_combinacao(
        self,
        *,
        tema: str | None = None,
        complexidade_max: int | None = None,
        tipo: str | None = None,
    ) -> tuple[FormulaQuestao, Contexto]:
        questoes = self.filtrar_questoes(
            complexidade_max=complexidade_max,
            tipo=tipo,
        )
        random.shuffle(questoes)

        for q in questoes:
            ctxs = self.contextos_compatíveis(q)
            if tema:
                ctxs = [c for c in ctxs if c.tema == tema]
            if ctxs:
                return q, random.choice(ctxs)

        raise ValueError(
            "Nenhuma combinação compatível encontrada com os filtros fornecidos"
        )

    # ─── LISTAGEM ────────────────────────────────────────────

    def listar_temas(self) -> list[str]:
        temas = set(c.tema for c in self.contextos.values() if c.tema)
        return sorted(temas)

    def listar_dominios(self) -> list[str]:
        dominios = set(c.dominio for c in self.contextos.values() if c.dominio)
        return sorted(dominios)

    def listar_operadores(self) -> list[str]:
        ops = set()
        for q in self.questoes.values():
            ops.update(q.operadores)
        return sorted(ops)

    def listar_tipos(self) -> list[str]:
        tipos = set()
        for q in self.questoes.values():
            tipos.update(q.tipos_recomendados)
        return sorted(tipos)

    # ─── ESTATÍSTICAS ────────────────────────────────────────

    def estatisticas(self) -> dict:
        distribuicao_tipos: dict[str, int] = {}
        for q in self.questoes.values():
            for t in q.tipos_recomendados:
                distribuicao_tipos[t] = distribuicao_tipos.get(t, 0) + 1

        distribuicao_temas: dict[str, int] = {}
        for c in self.contextos.values():
            tema = c.tema or "sem_tema"
            distribuicao_temas[tema] = distribuicao_temas.get(tema, 0) + 1

        complexidades = [q.complexidade for q in self.questoes.values()]
        vars_count = [q.num_variaveis for q in self.questoes.values()]

        return {
            "total_questoes": len(self.questoes),
            "total_contextos": len(self.contextos),
            "complexidade_media": (
                sum(complexidades) / len(complexidades) if complexidades else 0
            ),
            "complexidade_min": min(complexidades) if complexidades else 0,
            "complexidade_max": max(complexidades) if complexidades else 0,
            "variaveis_media": (sum(vars_count) / len(vars_count) if vars_count else 0),
            "distribuicao_tipos": distribuicao_tipos,
            "distribuicao_temas": distribuicao_temas,
        }

    # ─── EXPORTAÇÃO ──────────────────────────────────────────

    def exportar_json(self, caminho: str | Path):
        dados = {
            "contextos": [
                {
                    "id": c.id,
                    "texto": c.texto,
                    "tema": c.tema,
                    "dominio": c.dominio,
                    "tags": c.tags,
                    "props_min": c.props_min,
                    "props_max": c.props_max,
                }
                for c in self.contextos.values()
            ],
            "questoes": [
                {
                    "id": q.id,
                    "formula": q.formula,
                    "variaveis": q.variaveis,
                    "operadores": q.operadores,
                    "complexidade": q.complexidade,
                    "tipos_recomendados": q.tipos_recomendados,
                    "num_variaveis": q.num_variaveis,
                }
                for q in self.questoes.values()
            ],
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
