from tortoise import models, fields


class Auth(models.Model):

    id = fields.IntField(pk=True)
    nit = fields.CharField(max_length=255, null=False)
    nrc = fields.CharField(max_length=255, null=False)
    api_password = fields.CharField(max_length=255, null=False)
    certificate_password = fields.CharField(max_length=255, null=False)

    class Meta:
        table = 'auth'
