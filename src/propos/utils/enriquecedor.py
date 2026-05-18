import json
import re
from pathlib import Path

from .analise import enriquecer_formula


TEMA_KEYWORDS: list[tuple[str, str, list[str]]] = [
    ("investigacao", "policial", ["detetive", "roubo", "crime", "ladrão",
     "investigador", "investigação", "investiga", "testemunha",
     "depoimento", "tráfego", "ladrao"]),
    ("medicina", "saude", ["médico", "diagnóstico", "paciente",
     "sintomas", "eletrocardiograma", "arritmia", "doença",
     "hospital"]),
    ("engenharia", "infraestrutura", ["engenheiro", "ponte",
     "estrutural", "estrutura", "concreto", "tensões"]),
    ("tecnologia", "software", ["programador", "bug", "sistema",
     "pagamentos", "algoritmo", "desenvolvedor", "código",
     "segurança digital"]),
    ("direito", "juridico", ["juiz", "advogado", "testemunhas",
     "jurisprudência", "defesa", "precedentes"]),
    ("estrategia", "militar", ["estrategista", "militar", "rotas",
     "emboscada", "tático"]),
    ("biologia", "natureza", ["biólogo", "espécies", "ecossistema",
     "floresta", "espécie", "orquídea"]),
    ("educacao", "escolar", ["professor", "escola", "alunos",
     "olimpíada", "matemática", "inspetor escolar"]),
    ("navegacao", "transporte", ["capitão", "navio", "tempestade",
     "piloto", "avião", "pouso", "astronauta", "trajetória",
     "cometa"]),
    ("ciencia", "espacial", ["cientista", "espacial", "exoplaneta",
     "sinal", "extraterrestre"]),
    ("astronomia", "espacial", ["astrônomo", "estrela"]),
    ("culinaria", "alimentacao", ["chef", "cozinha", "molho"]),
    ("arqueologia", "historia", ["arqueólogo", "ruínas",
     "civilização", "escava", "túmulo", "faraônico"]),
    ("biblioteconomia", "cultura", ["bibliotecário", "obras raras",
     "enciclopédias", "referências"]),
    ("urbanismo", "cidades", ["urbanista", "ciclovias", "metrô",
     "metrópole"]),
    ("meteorologia", "clima", ["meteorologista", "frente fria",
     "pressão atmosférica", "raios"]),
    ("quimica", "laboratorio", ["químico", "reagentes", "polímero",
     "titulação", "ácido"]),
    ("historia", "cultura", ["historiador", "cronistas", "batalha",
     "manuscritos"]),
    ("jornalismo", "comunicacao", ["jornalista", "corrupção",
     "prefeitura"]),
    ("botanica", "natureza", ["botânico", "orquídea", "amazônia"]),
    ("geologia", "natureza", ["geólogo", "sísmica", "falha tectônica",
     "rocha", "deslizamento"]),
    ("arquitetura", "cidades", ["arquiteto", "museu", "iluminação"]),
    ("musica", "arte", ["músico", "harmonia", "composição",
     "melodia", "teoria modal"]),
    ("esporte", "saude", ["treinador", "atletismo", "biomecânica",
     "corredor"]),
    ("agricultura", "natureza", ["agricultor", "solo", "sensores",
     "irrigar", "umidade"]),
    ("games", "software", ["desenvolvedor de jogos", "jogos",
     "dificuldade"]),
    ("fiscalizacao", "governo", ["inspetor", "documentos",
     "fronteira"]),
]


def classificar_contexto(texto: str) -> tuple[str, str, list[str]]:
    texto_lower = texto.lower()
    melhor_tema = "geral"
    melhor_dominio = "geral"
    maior_pontos = 0
    tags_encontradas = []

    for tema, dominio, keywords in TEMA_KEYWORDS:
        pontos = sum(1 for kw in keywords if kw in texto_lower)
        if pontos > maior_pontos:
            maior_pontos = pontos
            melhor_tema = tema
            melhor_dominio = dominio
            tags_encontradas = [kw for kw in keywords if kw in texto_lower]

    return melhor_tema, melhor_dominio, tags_encontradas


def enriquecer_contextos(origem: str, destino: str):
    with open(origem, 'r', encoding='utf-8') as f:
        contextos_str = json.load(f)

    enriquecidos = []
    for i, texto in enumerate(contextos_str, 1):
        tema, dominio, tags = classificar_contexto(texto)
        ctx = {
            "id": f"c{i:03d}",
            "texto": texto,
            "tema": tema,
            "dominio": dominio,
            "tags": tags,
            "props_min": 2,
            "props_max": 4
        }
        enriquecidos.append(ctx)

    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(enriquecidos, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(enriquecidos)} contextos enriquecidos salvos em: {destino}")


def enriquecer_questoes(origem: str, destino: str):
    with open(origem, 'r', encoding='utf-8') as f:
        formulas_str = json.load(f)

    enriquecidas = []
    for i, formula in enumerate(formulas_str, 1):
        dados = enriquecer_formula(formula, id_prefix="q")
        dados["id"] = f"q{i:03d}"
        enriquecidas.append(dados)

    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(enriquecidas, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(enriquecidas)} questões enriquecidas salvas em: {destino}")


def main():
    import sys
    base = Path(__file__).resolve().parent.parent.parent.parent

    origem_ctx = base / "dados" / "contextos_legado.json"
    destino_ctx = base / "dados" / "contextos.json"
    origem_q = base / "dados" / "questoes_legado.json"
    destino_q = base / "dados" / "questoes.json"

    if not origem_ctx.exists():
        print(f"Arquivo não encontrado: {origem_ctx}")
        sys.exit(1)
    if not origem_q.exists():
        print(f"Arquivo não encontrado: {origem_q}")
        sys.exit(1)

    enriquecer_contextos(str(origem_ctx), str(destino_ctx))
    enriquecer_questoes(str(origem_q), str(destino_q))

    print("\n✓ Enriquecedor concluído com sucesso!")


if __name__ == "__main__":
    main()
