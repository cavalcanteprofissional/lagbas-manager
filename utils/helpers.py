from datetime import datetime, timedelta
from utils.config import LITROS_EQUIVALENTES_KG


def formatar_tempo(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


def calcular_tempo_total(horas: int, minutos: int, segundos: int) -> int:
    return horas * 3600 + minutos * 60 + segundos


def calcular_consumo_litros(consumo_lpm: float, segundos: int) -> float:
    return consumo_lpm * (segundos / 60)


def calcular_consumo_kg(litros: float) -> float:
    return litros / LITROS_EQUIVALENTES_KG


def calcular_consumo_porcentagem(consumo_litros: float, capacidade_litros: float) -> float:
    if capacidade_litros == 0:
        return 0
    return (consumo_litros / capacidade_litros) * 100


def formatar_data(data: str) -> str:
    if not data:
        return ""
    try:
        dt = datetime.fromisoformat(data.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except:
        return data


def formatar_data_hora(data: str, hora: str) -> str:
    try:
        dt = datetime.fromisoformat(data.replace("Z", "+00:00"))
        return f"{dt.strftime('%d/%m/%Y')} {hora}"
    except:
        return f"{data} {hora}"


def validar_codigo(codigo: str) -> bool:
    return bool(codigo and codigo.strip())


def validar_data(data: str) -> bool:
    if not data:
        return False
    try:
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except:
        return False


def get_status_color(status: str) -> str:
    colors = {
        "ativo": "green",
        "em_uso": "blue",
        "esgotado": "red",
        "inativo": "gray"
    }
    return colors.get(status, "gray")


def calcular_dias_em_uso(data_inicio: str) -> int:
    if not data_inicio:
        return 0
    try:
        inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        return (datetime.now() - inicio).days
    except:
        return 0
