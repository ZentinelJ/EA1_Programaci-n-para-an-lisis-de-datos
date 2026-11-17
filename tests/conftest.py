import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# speed_scrapy/ (la externa): permite importar el paquete interno
# speed_scrapy.items, speed_scrapy.pipelines, etc.
sys.path.insert(0, str(RAIZ / "speed_scrapy"))
# Raiz del repo: permite importar la aplicacion web (paquete app)
sys.path.insert(0, str(RAIZ))