#!/usr/bin/env python
"""
Alternativa: Constraint mais flexível para análises pontuais
"""

# Se você quiser manter alguma identificação única, pode usar:

# OPÇÃO 1: Constraint apenas por data/turno/linha/produto (sem propriedade)
# unique_together = [['date', 'shift', 'production_line', 'product']]

# OPÇÃO 2: Constraint por data/turno/linha/produto/propriedade (sem sequência)
# unique_together = [['date', 'shift', 'production_line', 'product', 'property']]

# OPÇÃO 3: Constraint por data/turno/linha/produto/sequência (sem propriedade)
# unique_together = [['date', 'shift', 'production_line', 'product', 'sequence']]

# OPÇÃO 4: Sem constraint (recomendado para flexibilidade máxima)
# unique_together = []

print("""
ALTERNATIVAS DE CONSTRAINT:

1. SEM CONSTRAINT (Recomendado):
   - Permite múltiplas análises da mesma propriedade
   - Máxima flexibilidade
   - Sem erro de constraint

2. CONSTRAINT POR DATA/TURNO/LINHA/PRODUTO:
   - Impede múltiplas análises no mesmo dia/turno/linha/produto
   - Permite múltiplas propriedades
   - Menos flexível

3. CONSTRAINT POR DATA/TURNO/LINHA/PRODUTO/PROPRIEDADE:
   - Impede múltiplas análises da mesma propriedade no mesmo dia
   - Permite diferentes propriedades
   - Moderadamente flexível

RECOMENDAÇÃO: Use SEM CONSTRAINT para máxima flexibilidade
""")





