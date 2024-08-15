import datetime
import json

import dbf

from app.config.cfg import DBF

def update_records(data):
    tabla = dbf.Table(DBF)
    tabla.open(mode=dbf.READ_WRITE)

    for dte in data:
        for record in dbf.Process(tabla):
            if str(record.fld5).strip() == dte["codGeneracion"]:
                record.fld7 = dte["selloRecibido"]
                record.fld9 = dte["estado"]

    tabla.close()


def reconciliar_dbf(data):
    tabla = dbf.Table(DBF)
    tabla.open(mode=dbf.READ_WRITE)
    codigos_no_encontrados = []

    for dte in data:
        for record in dbf.Process(tabla):
            if str(record.fld5).strip() == dte.codGeneracion:
                record.fld7 = dte.selloRecibido
                record.fld9 = dte.estado
                break
        else:
            codigos_no_encontrados.append(dte.codGeneracion)

    for cod in codigos_no_encontrados:
        dte = next((d for d in data if d.codGeneracion == cod), None)
        datos = json.loads(dte.documento)
        fechEmi = datos["identificacion"]["fecEmi"]
        fechEmi = datetime.datetime.strptime(fechEmi, "%Y-%m-%d")
        fhProcesamiento = dte.fhProcesamiento

        if datos["identificacion"]["tipoDte"] == "07":
            montoTotal = datos["resumen"]["totalIVAretenido"]
        elif datos["identificacion"]["tipoDte"] == "14":
            montoTotal = datos["resumen"]["totalCompra"]
        else:
            montoTotal = datos["resumen"]["montoTotalOperacion"]

        tabla.append((
            "",
            dbf.Date(fechEmi.year, fechEmi.month, fechEmi.day),
            datos["identificacion"]["horEmi"],
            montoTotal,
            dte.codGeneracion,
            datos["identificacion"]["numeroControl"],
            dte.selloRecibido,
            dbf.Date(fhProcesamiento.year, fhProcesamiento.month, fhProcesamiento.day),
            dte.estado,
        ))

    tabla.close()
