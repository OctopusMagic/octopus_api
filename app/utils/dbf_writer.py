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
