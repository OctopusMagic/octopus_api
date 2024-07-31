from tortoise import models, fields


class DatosEmpresa(models.Model):

    id = fields.IntField(pk=True)
    nombre = fields.CharField(max_length=255, null=False)
    nit = fields.CharField(max_length=255, null=False)
    nrc = fields.CharField(max_length=255, null=False)
    codActividad = fields.CharField(max_length=255, null=False)
    descActividad = fields.TextField(null=False)
    nombreComercial = fields.CharField(max_length=255, null=False)
    tipoEstablecimiento = fields.CharField(max_length=255, null=False)
    departamento = fields.CharField(max_length=255, null=False)
    municipio = fields.CharField(max_length=255, null=False)
    complemento = fields.CharField(max_length=255, null=False)
    telefono = fields.CharField(max_length=255, null=False)
    correo = fields.CharField(max_length=255, null=False)
    codEstableMH = fields.CharField(max_length=255, null=True)
    codEstable = fields.CharField(max_length=255)
    codPuntoVentaMH = fields.CharField(max_length=255, null=True)
    codPuntoVenta = fields.CharField(max_length=255)

    class Meta:
        table = 'datos_empresa'
