# Validation utility functions
import re


def safe_int(value, default=None):
    """Converte valor para int com fallback seguro."""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=None):
    """Converte valor para float com fallback seguro."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def validar_codigo_cilindro(codigo):
    """Valida se o código segue o formato CIL-XXX."""
    return bool(re.match(r'^CIL-\d{3}$', codigo.upper()))


def formatar_tempo_chama(hora, minuto, segundo):
    """Formata tempo de chama para HH:MM:SS."""
    h = hora.zfill(2) if hora else "00"
    m = minuto.zfill(2) if minuto else "00"
    s = segundo.zfill(2) if segundo else "00"
    return f"{h}:{m}:{s}"


def remover_duplicatas_por_campo(items, campo):
    """Remove itens duplicados baseado em um campo específico."""
    unicos = []
    vistos = set()
    for item in items:
        valor = item.get(campo, "").lower()
        if valor not in vistos:
            vistos.add(valor)
            unicos.append(item)
    return unicos
