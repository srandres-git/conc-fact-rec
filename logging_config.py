import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configura el logging de la aplicación. Es idempotente: si el logger raíz
    ya tiene handlers (p. ej. por un rerun de Streamlit), no vuelve a agregarlos."""
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
