# Constants for the application

ITEMS_PER_PAGE = 10

LITROS_EQUIVALENTES_KG = 956.0
GAS_KG_DEFAULT = 1.0
CUSTO_DEFAULT = 290.00

CILINDRO_STATUS = ["ativo", "esgotado"]

# Padrão de cores por tipo (CSS classes e gradients)
COR_TIPO = {
    "cilindro": {
        "class": "green",
        "gradient": "linear-gradient(135deg, #10b981, #34d399)",
        "badge": "success"
    },
    "elemento": {
        "class": "blue", 
        "gradient": "linear-gradient(135deg, #3b82f6, #60a5fa)",
        "badge": "primary"
    },
    "amostra": {
        "class": "pink",
        "gradient": "linear-gradient(135deg, #ec4899, #f472b6)",
        "badge": "pink"
    },
    "ativos": {
        "class": "purple",
        "gradient": "linear-gradient(135deg, #8b5cf6, #a78bfa)",
        "badge": "purple"
    },
    "admin": {
        "class": "danger",
        "gradient": "linear-gradient(135deg, #ef4444, #f87171)",
        "badge": "danger"
    }
}

ELEMENTOS_PADRAO = [
    {"nome": "Antimônio", "consumo_lpm": 1.5},
    {"nome": "Alumínio", "consumo_lpm": 4.5},
    {"nome": "Arsênio", "consumo_lpm": 1.5},
    {"nome": "Bário", "consumo_lpm": 4.5},
    {"nome": "Cádmio", "consumo_lpm": 1.5},
    {"nome": "Chumbo", "consumo_lpm": 2.0},
    {"nome": "Cobalto", "consumo_lpm": 1.5},
    {"nome": "Cobre", "consumo_lpm": 1.5},
    {"nome": "Cromo", "consumo_lpm": 4.5},
    {"nome": "Estanho FAAS", "consumo_lpm": 4.5},
    {"nome": "Estanho HG", "consumo_lpm": 1.5},
    {"nome": "Ferro", "consumo_lpm": 2.0},
    {"nome": "Manganês", "consumo_lpm": 1.5},
    {"nome": "Mercúrio", "consumo_lpm": 0},
    {"nome": "Molibdênio", "consumo_lpm": 4.5},
    {"nome": "Níquel", "consumo_lpm": 1.5},
    {"nome": "Prata", "consumo_lpm": 1.5},
    {"nome": "Selênio", "consumo_lpm": 2.0},
    {"nome": "Zinco", "consumo_lpm": 1.5},
    {"nome": "Tálio", "consumo_lpm": 1.5},
]
