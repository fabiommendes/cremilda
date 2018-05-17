from itertools import chain
from collections import Counter


class SemanticError(Exception):
    """
    Exceção levantada para erros de semântica.
    """


class SemanticAnalysis:
    """
    Funções úteis para análise semântica.
    """

    def __init__(self, ir):
        self.ir = ir

    def find_repeated_symbols(self):
        """
        Encontra todos os símbolos repetidos em imports, definições 
        de variáveis e funções.
        """
        counter = Counter(self.ir.symbols)
        return {name for name, count in counter.items() if count >= 2}

    def run(self):
        """
        Realiza todas as verificações da análise semântica.
        """
        
        # Verifica se não existem símbolos repetidos
        repeated = self.find_repeated_symbols()
        if repeated:
            raise SemanticError(f'repeated symbols: {repeated}')
