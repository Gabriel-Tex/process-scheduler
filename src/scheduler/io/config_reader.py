"""
Leitura do arquivo de configuração — LeitorConfig.

Responsabilidades:
    - Ler config/config.txt (ou caminho fornecido via argumento).
    - Parsear linhas no formato:  chave:valor
    - Ignorar linhas em branco e comentários (linhas iniciando com '#').
    - Ser tolerante a espaços em branco extras ao redor de ':' e no fim da linha.
    - Retornar uma instância de Configuracao com os valores lidos.
    - Aplicar valores padrão (quantum=2, aging=1) para chaves ausentes.
    - Levantar ValueError com mensagem clara para valores inválidos
      (ex.: quantum=0, aging negativo).

Interface pública:
    LeitorConfig.ler(caminho: str | Path) -> Configuracao
"""
