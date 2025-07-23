import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path


# Função para limpar ANSI e emojis
def limpar_ansi_emojis(texto: str) -> str:
    # Remove códigos ANSI
    texto = re.sub(r"\033\[[0-9;]*m", "", texto)
    # Remove emojis (faixa unicode comum)
    texto = re.sub(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
        "",
        texto,
    )
    # Remove alguns emojis simples (ex: rocket, check, cross, etc)
    texto = re.sub(
        r"[\u2705\u274C\u26A0\u26D4\u26F7\u26F9\u26FD\u2708\u2709\u270A-\u270D\u2728\u2733\u2734\u2744\u2753-\u2755\u2757\u2764]",
        "",
        texto,
    )
    # Remove tabs
    texto = texto.replace("\t", "").replace("⏰", "")
    return texto


# Formatter customizado para arquivo
class FormatterSemAnsi(logging.Formatter):
    def format(self, record):
        # Não altera o record global, só a mensagem formatada para o arquivo
        msg_original = str(record.msg)
        record_copy = logging.makeLogRecord(record.__dict__.copy())
        record_copy.msg = limpar_ansi_emojis(msg_original)
        return super().format(record_copy)


# Códigos ANSI para cor/negrito/itálico
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GRAY = "\033[90m"


def configurar_logging() -> logging.Logger:
    """
    Configura o sistema de logging para salvar em arquivo e exibir na tela.
    Cria apenas um arquivo por dia usando a data no nome.

    Returns:
        Logger configurado
    """
    # Criar pasta de logs se não existir
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Nome do arquivo de log com apenas a data (um arquivo por dia)
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"comparador_codigos_{data_hoje}.log"

    # Configurar logger
    logger = logging.getLogger("comparador_codigos")
    logger.setLevel(logging.INFO)

    # Limpar handlers existentes (evitar duplicação)
    logger.handlers.clear()

    # Formatter para arquivo (sem ANSI/emojis)
    file_formatter = FormatterSemAnsi(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Formatter para console (mantém cores/emojis)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Verificar se é a primeira execução do dia
    arquivo_existe = log_file.exists()
    timestamp_atual = datetime.now().strftime("%H:%M:%S")

    if not arquivo_existe:
        # Primeira execução do dia - criar cabeçalho
        logger.info("=" * 100)
        logger.info(f"📅 NOVO DIA DE LOGS - {data_hoje}")
        logger.info("=" * 100)

    # Log de início da sessão
    logger.info("")
    logger.info("-" * 80)
    logger.info(f"🚀 NOVA EXECUÇÃO INICIADA - {timestamp_atual}")
    logger.info(f"📁 Arquivo de log: {log_file}")
    logger.info("-" * 80)

    return logger


def extrair_somente_digitos_numericos(texto_com_formatacao: str) -> str:
    """
    Remove todos os caracteres não numéricos de uma string, mantendo apenas dígitos.

    Args:
        texto_com_formatacao: String que pode conter dígitos, letras, símbolos e espaços

    Returns:
        String contendo exclusivamente os dígitos numéricos extraídos

    Example:
        >>> extrair_somente_digitos_numericos("123-45.67 89")
        "12345678"
    """
    return re.sub(r"\D", "", texto_com_formatacao)


def analisar_tipo_codigo(codigo_limpo: str) -> str:
    """
    Analisa o tipo de código baseado no tamanho ou padrão.
    Agora identifica também chaves PIX (CPF, CNPJ, email, telefone, EVP ou QR Code).
    """
    tamanho = len(codigo_limpo)

    # Verifica se é chave PIX (CPF, CNPJ, telefone, EVP)
    if re.fullmatch(r"\d{11}", codigo_limpo):
        return "PIX (CPF)"
    if re.fullmatch(r"\d{14}", codigo_limpo):
        return "PIX (CNPJ)"
    if re.fullmatch(r"\d{10,13}", codigo_limpo):
        return "PIX (Telefone)"
    # Verifica se é chave EVP (chave aleatória PIX)
    if re.fullmatch(r"[a-fA-F0-9]{32}", codigo_limpo):
        return "PIX (Chave Aleatória EVP)"
    # Verifica se é email (não só dígitos)
    if "@" in codigo_limpo:
        return "PIX (Email)"
    # Verifica se é payload de QR Code PIX (começa com "000201")
    if codigo_limpo.startswith("000201"):
        return "PIX (QR Code)"
    # Códigos de barras tradicionais
    if tamanho == 44:
        return "Código de Arrecadação (44 dígitos)"
    if tamanho == 47:
        return "Boleto Bancário (47 dígitos)"
    if tamanho == 48:
        return "Código de Arrecadação Estendido (48 dígitos)"
    return f"Código não padrão ({tamanho} dígitos)"


def limpar_codigo(codigo: str) -> str:
    """
    Limpa o código conforme o tipo detectado:
    - Para código de barras: mantém só dígitos.
    - Para PIX: mantém o original (apenas tira espaços nas pontas).
    """
    # Detecta tipo PIX antes de limpar
    if (
        "@" in codigo
        or codigo.startswith("000201")
        or re.fullmatch(r"[a-fA-F0-9]{32}", codigo)
    ):
        return codigo.strip()
    # Para CPF, CNPJ, telefone (só dígitos)
    return extrair_somente_digitos_numericos(codigo)


def comparar_codigos(
    codigo1: str, codigo2: str, logger: logging.Logger
) -> tuple[bool, dict]:
    """
    Compara dois códigos, tratando PIX e código de barras corretamente.
    """
    logger.info("🔄 Iniciando comparação de códigos...")

    # Limpar códigos conforme tipo
    codigo1_limpo = limpar_codigo(codigo1)
    codigo2_limpo = limpar_codigo(codigo2)

    logger.info(f"{YELLOW}{BOLD}🔍 Limpeza concluída:{RESET}")
    logger.info(f"   Código 1: {codigo1_limpo} ({len(codigo1_limpo)} caracteres)")
    logger.info(f"   Código 2: {codigo2_limpo} ({len(codigo2_limpo)} caracteres)")

    # Analisar tipos
    tipo_codigo1 = analisar_tipo_codigo(codigo1_limpo)
    tipo_codigo2 = analisar_tipo_codigo(codigo2_limpo)

    # Preparar detalhes da comparação
    detalhes = {
        "codigo1_original": codigo1,
        "codigo2_original": codigo2,
        "codigo1_limpo": codigo1_limpo,
        "codigo2_limpo": codigo2_limpo,
        "tamanho_codigo1": len(codigo1_limpo),
        "tamanho_codigo2": len(codigo2_limpo),
        "tipo_codigo1": tipo_codigo1,
        "tipo_codigo2": tipo_codigo2,
        "sao_equivalentes": codigo1_limpo == codigo2_limpo,
    }

    # logger.info("📊 Análise de tipos concluída:")
    # logger.info(f"   Código 1: {tipo_codigo1}")
    # logger.info(f"   Código 2: {tipo_codigo2}")

    return detalhes["sao_equivalentes"], detalhes


def exibir_resultado_comparacao(detalhes: dict, logger: logging.Logger) -> None:
    """
    Exibe o resultado da comparação de forma formatada usando logger.

    Args:
        detalhes: Dicionário com os detalhes da comparação
        logger: Logger para registrar os resultados
    """

    logger.info("")
    logger.info(f"{CYAN}{BOLD}🔍 COMPARAÇÃO DE CÓDIGOS{RESET}")
    logger.info(f"{GRAY}{'─' * 40}{RESET}")

    logger.info(f"{BOLD}📊 CÓDIGO 1:{RESET}")
    logger.info(f"  {ITALIC}Original:{RESET}\t {detalhes['codigo1_original']}")
    logger.info(f"  {ITALIC}Limpo:{RESET}\t {detalhes['codigo1_limpo']}")
    logger.info(f"  {ITALIC}Tamanho:{RESET}\t {detalhes['tamanho_codigo1']} dígitos")
    logger.info(f"  {ITALIC}Tipo:{RESET}\t\t {detalhes['tipo_codigo1']}")

    logger.info("")
    logger.info(f"{BOLD}📋 CÓDIGO 2:{RESET}")
    logger.info(f"  {ITALIC}Original:{RESET}\t {detalhes['codigo2_original']}")
    logger.info(f"  {ITALIC}Limpo:{RESET}\t {detalhes['codigo2_limpo']}")
    logger.info(f"  {ITALIC}Tamanho:{RESET}\t {detalhes['tamanho_codigo2']} dígitos")
    logger.info(f"  {ITALIC}Tipo:{RESET}\t\t {detalhes['tipo_codigo2']}")

    logger.info("")
    logger.info(f"{YELLOW}{BOLD}🎯 RESULTADO DA COMPARAÇÃO:{RESET}")
    if detalhes["sao_equivalentes"]:
        logger.info(f"  Status: ✅ {GREEN}{BOLD}CÓDIGOS SÃO EQUIVALENTES!{RESET}")
        logger.info(
            f"  {ITALIC}Os códigos representam o mesmo documento após remoção da formatação.{RESET}"
        )
    else:
        logger.warning(f"  Status: 🚫 {RED}{BOLD}CÓDIGOS SÃO DIFERENTES!{RESET}")
        logger.warning(
            f"  {ITALIC}Os códigos representam documentos diferentes.{RESET}"
        )
        if detalhes["tamanho_codigo1"] != detalhes["tamanho_codigo2"]:
            logger.warning(
                f"  {YELLOW}Diferença de tamanho: {detalhes['tamanho_codigo1']} vs {detalhes['tamanho_codigo2']} dígitos{RESET}"
            )

    logger.info(f"{GRAY}{'─' * 40}{RESET}")


def exibir_resultado_resumido(detalhes: dict, logger: logging.Logger) -> None:
    """
    Exibe resultado resumido usando logger.

    Args:
        detalhes: Dicionário com os detalhes da comparação
        logger: Logger para registrar os resultados
    """
    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    status = (
        f"✅ {GREEN}{BOLD}IGUAIS{RESET}"
        if detalhes["sao_equivalentes"]
        else f"🚫 {RED}{BOLD}DIFERENTES{RESET}"
    )
    logger.info(f"Resultado: {status}")
    logger.info(
        f"Código 1: {ITALIC}{detalhes['codigo1_limpo']}{RESET} ({detalhes['tamanho_codigo1']} dígitos)"
    )
    logger.info(
        f"Código 2: {ITALIC}{detalhes['codigo2_limpo']}{RESET} ({detalhes['tamanho_codigo2']} dígitos)"
    )


def criar_parser_argumentos() -> argparse.ArgumentParser:
    """
    Cria o parser para argumentos da linha de comando.

    Returns:
        Parser configurado com os argumentos necessários
    """
    parser = argparse.ArgumentParser(
        description="Compara dois códigos de barras extraindo apenas os dígitos",
        epilog="""
Exemplos de uso:
  # Argumentos nomeados:
  python comparador_codigos.py --codigo1 '123-456-789' --codigo2 '123456789'
  
  # Argumentos posicionais:
  python comparador_codigos.py '123-456-789' '123456789' --detalhado
  
  # Argumentos curtos:
  python comparador_codigos.py -c1 '123-456' -c2 '123456' -d
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Argumentos posicionais
    parser.add_argument(
        "codigo1_pos", nargs="?", help="Primeiro código (argumento posicional)"
    )

    parser.add_argument(
        "codigo2_pos", nargs="?", help="Segundo código (argumento posicional)"
    )

    # Argumentos nomeados
    parser.add_argument(
        "--codigo1",
        "-c1",
        help="Primeiro código para comparação (pode conter formatação)",
    )

    parser.add_argument(
        "--codigo2",
        "-c2",
        help="Segundo código para comparação (pode conter formatação)",
    )

    parser.add_argument(
        "--silencioso",
        "-s",
        action="store_true",
        help="Executa em modo silencioso (apenas retorna código de saída)",
    )

    parser.add_argument(
        "--detalhado",
        "-d",
        action="store_true",
        default=True,
        help="Exibe informações detalhadas sobre cada código",
    )

    return parser


def main() -> int:
    """
    Função principal que processa argumentos e executa a comparação.

    Returns:
        Código de saída: 0 se códigos são iguais, 1 se diferentes, 2 se erro
    """
    logger = None

    try:
        # Configurar logging
        logger = configurar_logging()

        # Configurar parser e processar argumentos
        parser = criar_parser_argumentos()
        args = parser.parse_args()

        # Determinar códigos a usar (posicionais ou nomeados)
        codigo1 = args.codigo1 or args.codigo1_pos
        codigo2 = args.codigo2 or args.codigo2_pos

        # Validar se ambos os códigos foram fornecidos
        if not codigo1 or not codigo2:
            logger.error("🚫 Erro: Dois códigos devem ser fornecidos")
            logger.error("Use: --codigo1 e --codigo2 OU dois argumentos posicionais")
            return 2

        # Validar se os códigos não estão vazios
        if not codigo1.strip() or not codigo2.strip():
            logger.error("🚫 Erro: Códigos não podem estar vazios")
            return 2

        # Log dos códigos a serem comparados
        logger.info("")
        logger.info(f"{YELLOW}{BOLD}📤 Códigos para comparação:{RESET}")
        logger.info(f"   Código 1: {codigo1}")
        logger.info(f"   Código 2: {codigo2}")

        # Executar comparação
        sao_iguais, detalhes = comparar_codigos(codigo1, codigo2, logger)

        # Exibir resultado conforme o modo
        if args.silencioso:
            # Modo silencioso: apenas log e código de saída
            logger.info(
                f"🔇 Modo silencioso - Resultado: {'IGUAIS' if sao_iguais else 'DIFERENTES'}"
            )
        elif args.detalhado:
            # Modo detalhado: mostrar todos os detalhes
            exibir_resultado_comparacao(detalhes, logger)
        else:
            # Modo padrão: resultado resumido
            logger.info("")
            exibir_resultado_resumido(detalhes, logger)

        # Log final da sessão
        resultado_final = "IGUAIS" if sao_iguais else "DIFERENTES"
        timestamp_fim = datetime.now().strftime("%H:%M:%S")
        logger.info("")
        logger.info(f"🏁 Execução finalizada - Resultado: {resultado_final}")
        logger.info(f"⏰ Fim da sessão: {timestamp_fim}")
        logger.info("-" * 80)

        # Retornar código de saída apropriado
        return 0 if sao_iguais else 1

    except KeyboardInterrupt:
        if logger:
            logger.warning("⚠️ Operação cancelada pelo usuário")
        else:
            print("⚠️ Operação cancelada pelo usuário", file=sys.stderr)
        return 2
    except Exception as e:
        if logger:
            logger.error(f"🚫 Erro inesperado: {e}")
        else:
            print(f"🚫 Erro inesperado: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
