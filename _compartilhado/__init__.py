"""Ferramentas compartilhadas dos validadores da Estrutura Final de Skills.

Importado pelos `evals/validate_workflow.py` de cada pacote. Não contém regra de
negócio de nenhum Departamento: só o motor de schema e as verificações de pacote
que a `GUIA-DE-EXPANSAO-E-MIGRACAO.md` exige de todo pacote migrado.

Uso a partir de um validador de pacote:

    STRUCTURE_ROOT = <raiz da Estrutura Final de Skills>
    sys.path.insert(0, str(STRUCTURE_ROOT))
    from _compartilhado.validador_schema import validate_schema
    from _compartilhado.verificacoes_pacote import validate_frontmatter
"""

__all__ = ["validador_schema", "verificacoes_pacote"]
