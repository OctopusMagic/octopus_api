from tortoise import models, fields


class DTE(models.Model):

    codGeneracion = fields.CharField(max_length=255, null=False)
    selloRecibido = fields.CharField(max_length=255, null=True)
    estado = fields.CharField(max_length=255, null=False)
    documento = fields.TextField(null=False)
    fhProcesamiento = fields.DatetimeField(null=False, auto_now_add=True)
    observaciones = fields.TextField(null=True)
    tipo_dte = fields.CharField(max_length=255, null=False)

    class Meta:
        table = 'dte_generados'
