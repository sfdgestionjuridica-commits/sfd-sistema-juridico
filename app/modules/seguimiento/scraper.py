def consultar_estado(radicado: str) -> str:
    """
    Simulación del estado del proceso.
    Luego se reemplaza por scraping real.
    """

    if radicado.endswith("1"):
        return "AUTO ADMITE DEMANDA"
    elif radicado.endswith("2"):
        return "INADMITE - SUBSANAR"
    else:
        return "SIN CAMBIOS"