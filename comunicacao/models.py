from django.db import models

class Texto(models.Model):
    titulo = models.CharField(max_length=100, unique=True, help_text="Um nome curto para identificar o texto na lista. Ex: Lembrete Amigável")
    template = models.TextField(help_text="O conteúdo do texto. Para cobranças, use {nome} para o primeiro nome e {valor} para o valor.")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Texto"
        verbose_name_plural = "Textos"
        ordering = ['titulo']