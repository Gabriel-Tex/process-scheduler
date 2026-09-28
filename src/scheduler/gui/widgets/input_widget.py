"""
Widget de entrada de processos — EntradaWidget (bônus).

Responsabilidades:
    - Renderizar uma tabela editável onde o usuário insere os processos.
    - Colunas: ID (auto) | Instante de Criação | Duração | Prioridade Estática.
    - Botões: Adicionar linha, Remover linha selecionada, Limpar tudo.
    - Validar campos na saída (chamar validação do domínio).
    - Expor método obter_processos() -> list[EspecificacaoProcesso] para o controlador.
"""
