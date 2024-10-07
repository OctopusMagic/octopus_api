esta_contingencia = False


def obtener_contingencia():
    return esta_contingencia


def activar_contingencia():
    global esta_contingencia
    esta_contingencia = True


def desactivar_contingencia():
    global esta_contingencia
    esta_contingencia = False
