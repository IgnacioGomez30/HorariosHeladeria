"""Comprobación B01 de los recursos necesarios para resolver horarios sin red."""

from datetime import datetime, timedelta
from importlib.resources import files
from zoneinfo import ZoneInfo


def test_datos_iana_de_mendoza_disponibles_en_el_paquete():
    archivo = files("tzdata.zoneinfo").joinpath("America", "Argentina", "Mendoza")
    with archivo.open("rb") as datos:
        mendoza = ZoneInfo.from_file(datos, key="America/Argentina/Mendoza")

    apertura_demo = datetime(2027, 2, 1, 19, tzinfo=mendoza)
    assert apertura_demo.utcoffset() == timedelta(hours=-3)
