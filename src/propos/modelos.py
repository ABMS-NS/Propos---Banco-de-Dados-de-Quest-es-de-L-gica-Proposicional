from dataclasses import dataclass, field


@dataclass
class Contexto:
    id: str
    texto: str
    tema: str = ""
    dominio: str = ""
    tags: list[str] = field(default_factory=list)
    props_min: int = 2
    props_max: int = 4


@dataclass
class FormulaQuestao:
    id: str
    formula: str
    variaveis: list[str] = field(default_factory=list)
    operadores: list[str] = field(default_factory=list)
    complexidade: int = 0
    tipos_recomendados: list[str] = field(default_factory=list)
    num_variaveis: int = 0
