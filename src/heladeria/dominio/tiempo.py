"""Jornadas imputadas por fecha operativa y presencia en minutos UTC reales."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from importlib.resources import files
from itertools import pairwise
from zoneinfo import ZoneInfo

from tzdata import IANA_VERSION as VERSION_IANA


ZONA_LOCAL = "America/Argentina/Mendoza"
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_MINUTO = timedelta(minutes=1)
# from_file garantiza la misma base de reglas incluso si el SO ofrece otra.
with files("tzdata.zoneinfo").joinpath(*ZONA_LOCAL.split("/")).open("rb") as archivo:
    _ZONA = ZoneInfo.from_file(archivo, key=ZONA_LOCAL)


def _en_minutos(utc: datetime) -> int:
    minutos, resto = divmod(utc - _EPOCH, _MINUTO)
    if resto:
        raise ValueError("El instante histórico no se puede representar en minutos UTC.")
    return minutos


def minuto_local(fecha: date, hora: time, *, ocurrencia: int | None = None) -> int:
    """Resuelve un reloj civil del local. En una repetición, 0 es la primera vez."""
    if type(fecha) is not date or not isinstance(hora, time):
        raise ValueError("Se requiere fecha civil y hora local explícitas.")
    if hora.tzinfo is not None or hora.second or hora.microsecond:
        raise ValueError("Se requiere una hora civil sin zona y con precisión de minuto.")
    if ocurrencia is not None and (type(ocurrencia) is not int or ocurrencia not in (0, 1)):
        raise ValueError("La ocurrencia debe ser 0 o 1.")
    reloj = datetime.combine(fecha, hora)
    candidatos = {}
    for fold in (0, 1):
        utc = reloj.replace(tzinfo=_ZONA, fold=fold).astimezone(timezone.utc)
        vuelta = utc.astimezone(_ZONA)
        if vuelta.replace(tzinfo=None) == reloj and vuelta.fold == fold:
            candidatos[fold] = utc
    if not candidatos:
        raise ValueError(f"Hora local inexistente: {reloj}.")
    if ocurrencia is None:
        if len(candidatos) > 1:
            raise ValueError(f"Hora local ambigua: {reloj}. Indicar la ocurrencia.")
        ocurrencia = 0
    if ocurrencia not in candidatos:
        raise ValueError(f"El reloj local {reloj} carece de esa ocurrencia.")
    return _en_minutos(candidatos[ocurrencia])


def fecha_hora_local(instante: int) -> datetime:
    """Incluye fecha civil, desplazamiento UTC y ocurrencia para presentación."""
    if type(instante) is not int:
        raise ValueError("Se requieren minutos UTC enteros.")
    return (_EPOCH + instante * _MINUTO).astimezone(_ZONA)


@dataclass(frozen=True, order=True)
class Intervalo:
    """Intervalo físico semiabierto [inicio, fin), también usado como bloque."""

    inicio: int
    fin: int

    def __post_init__(self):
        if type(self.inicio) is not int or type(self.fin) is not int:
            raise ValueError("Los extremos deben expresarse en minutos UTC enteros.")
        if self.inicio >= self.fin:
            raise ValueError(f"Intervalo sin duración positiva [{self.inicio}, {self.fin}).")

    @property
    def minutos(self) -> int:
        return self.fin - self.inicio

    def contiene(self, instante: int) -> bool:
        return self.inicio <= instante < self.fin

    def interseccion(self, otro: 'Intervalo') -> 'Intervalo | None':
        inicio = max(self.inicio, otro.inicio)
        fin = min(self.fin, otro.fin)
        return Intervalo(inicio, fin) if inicio < fin else None


def dia_civil(fecha: date) -> Intervalo:
    """Todo el día físico, incluidas ambas ocurrencias de una hora repetida."""
    if type(fecha) is not date:
        raise ValueError("Se requiere una fecha civil.")
    # En Mendoza los saltos hacia adelante se producen en el borde del día.
    # El desplazamiento previo (fold=0) sitúa el borde en el primer instante
    # real de esa fecha, aun cuando la primera hora civil mostrada sea 01:00.
    def borde(dia: date) -> int:
        medianoche = datetime.combine(dia, time.min, tzinfo=_ZONA)
        return _en_minutos(medianoche.astimezone(timezone.utc))

    return Intervalo(borde(fecha), borde(fecha + timedelta(days=1)))


@dataclass(frozen=True)
class Jornada:
    persona_id: str
    fecha_operativa: date
    bloques: tuple[Intervalo, ...]

    def __post_init__(self):
        if not isinstance(self.persona_id, str) or not self.persona_id.strip():
            raise ValueError("Falta la identidad de la jornada.")
        if type(self.fecha_operativa) is not date:
            raise ValueError("Se requiere una fecha operativa explícita.")
        bloques = tuple(sorted(self.bloques))
        if not bloques or not all(isinstance(b, Intervalo) for b in bloques):
            raise ValueError("Una jornada requiere al menos un bloque real.")
        for anterior, siguiente in pairwise(bloques):
            solape = anterior.interseccion(siguiente)
            if solape:
                raise ValueError(f"Bloques superpuestos de {self.persona_id} "
                                 f"el {self.fecha_operativa}: {solape}.")
        object.__setattr__(self, "bloques", bloques)

    @property
    def minutos(self) -> int:
        return sum(b.minutos for b in self.bloques)

    @property
    def inicio(self) -> int:
        return self.bloques[0].inicio

    @property
    def fin(self) -> int:
        return self.bloques[-1].fin


def descanso(anterior: Jornada, siguiente: Jornada) -> int:
    """Reposo entre dos jornadas de una persona, en orden operativo."""
    if anterior.persona_id != siguiente.persona_id:
        raise ValueError("El descanso requiere jornadas de la misma persona.")
    if anterior.fecha_operativa >= siguiente.fecha_operativa:
        raise ValueError(f"Fechas operativas repetidas o desordenadas para {anterior.persona_id}.")
    if siguiente.inicio < anterior.fin:
        raise ValueError(f"Jornadas incompatibles de {anterior.persona_id}: "
                         f"la del {siguiente.fecha_operativa} inicia en {siguiente.inicio}, "
                         f"antes del fin {anterior.fin} de la del {anterior.fecha_operativa}.")
    return siguiente.inicio - anterior.fin


@dataclass(frozen=True)
class Agenda:
    """Jornadas conocidas, incluidos los vecinos de ambos bordes de la consulta."""

    jornadas: tuple[Jornada, ...]

    def __post_init__(self):
        jornadas = tuple(sorted(self.jornadas, key=lambda j: (j.persona_id, j.fecha_operativa)))
        for anterior, siguiente in pairwise(jornadas):
            if anterior.persona_id == siguiente.persona_id:
                descanso(anterior, siguiente)
        object.__setattr__(self, "jornadas", jornadas)

    def presentes(self, instante: int) -> frozenset[str]:
        """Personas asignadas a un bloque que contiene este minuto físico."""
        return frozenset(j.persona_id for j in self.jornadas
                         if any(b.contiene(instante) for b in j.bloques))

    def minutos_operativos(self, persona_id: str, desde: date, hasta: date) -> int:
        """Trabajo imputado a las fechas operativas en [desde, hasta)."""
        if desde > hasta:
            raise ValueError("Rango de fechas invertido.")
        return sum(j.minutos for j in self.jornadas
                   if j.persona_id == persona_id and desde <= j.fecha_operativa < hasta)

    def minutos_de_presencia(self, persona_id: str, ventana: Intervalo) -> int:
        """Interseca la ventana física con los bloques, incluso de otras fechas."""
        minutos = 0
        for jornada in self.jornadas:
            if jornada.persona_id == persona_id:
                for bloque in jornada.bloques:
                    comun = ventana.interseccion(bloque)
                    if comun:
                        minutos += comun.minutos
        return minutos
