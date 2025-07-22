import logging
from os import path


log_file = path.join("ressorces/providence.log")

logging.basicConfig(
    level= logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ressources/providence.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)