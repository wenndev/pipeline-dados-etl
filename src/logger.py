"""
Esse arquivo cria o registrador de logs do projeto — o responsável por registrar
mensagens do que tá acontecendo no programa (avisos, erros, informações),
tanto na tela (console) quanto salvas num arquivo .log.

obter_logger(nome) devolve esse logger pronto pra usar. Se ele já tiver
sido criado antes com o mesmo nome, devolve o mesmo (evita duplicar as
mensagens no console/arquivo).

A pasta de logs (log_dir) vem do config.py e é criada automaticamente
se ainda não existir.
"""

import logging
from pathlib import Path

from config import obter_configuracoes


def obter_logger(nome: str = "pipeline") -> logging.Logger:
    logger = logging.getLogger(nome)

    if logger.handlers:
        return logger

    configuracoes = obter_configuracoes()
    configuracoes.log_dir.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    file_path = Path(configuracoes.log_dir, f"{nome}.log")
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)

    return logger
