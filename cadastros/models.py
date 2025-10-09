from django.db import models


# BASE / PESSOAS --------------------------------------------------------
class Parceiro(models.Model):
    TIPOS_PARCEIRO = (
        ('escola', 'Escola'),
        ('clube', 'Clube'),
        ('condominio', 'Condomínio'),
        ('empresa', 'Empresa'),
        ('outro', 'Outro'),
    )

    tipo = models.CharField(max_length=10, choices=TIPOS_PARCEIRO, default='escola')
    nome = models.CharField(max_length=60, unique=True)
    cnpj = models.CharField(max_length=14, null=True, unique=True,  blank=True)
    telefone = models.CharField(max_length=11, null=True, blank=True)
    e_mail = models.CharField(max_length=30, null=True, unique=True,  blank=True)
    chave_pix = models.CharField(max_length=100, null=True, blank=True)
    contrato = models.FileField(upload_to='parceiros/contratos/', null=True, blank=True)
    obs = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
class Familia(models.Model):
    
    responsavel_financeiro = models.ForeignKey(
        'Responsavel', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='responsavel_financeiro',
        help_text="Responsável pela assinatura de contrato e pagamentos."
    )
    
    responsavel_contato = models.ForeignKey(
        'Responsavel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsavel_contato',
        help_text="Responsável pela comunicação do dia a dia (avisos, etc.)."
    )
    
    class Meta:
        verbose_name = "Família"
        verbose_name_plural = "Famílias"
        
    def __str__(self):
        return f"Família #{self.id}"

class Responsavel(models.Model):
    tipos_responsavel = (
        ('pai', 'Pai'),
        ('mae', 'Mãe'),
        ('avó', 'Avó'),
        ('avô', 'Avô'),
        ('tio', 'Tio'),
        ('tia', 'Tia'),
        ('out', 'Outro')
    )
    
    nome = models.CharField(max_length=50)
    tipo_responsavel = models.CharField(max_length=3, choices=tipos_responsavel, null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=14, null=True, unique=True,  blank=True)
    telefone = models.CharField(max_length=11, null=True, blank=True)
    e_mail = models.CharField(max_length=40, null=True,  blank=True)
    boleto = models.BooleanField(default=0)
    obs = models.TextField(null=True, blank=True)
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='responsaveis', null=True, blank=True)
    
    def __str__(self):
        return self.nome
    
class Aluno(models.Model):
    nome = models.CharField(max_length=50)
    turma_escola = models.CharField(max_length=10, blank=True, null=True)
    ativo = models.BooleanField(default=1)
    obs = models.TextField(null=True, blank=True)
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='alunos', null=True, blank=True)  
    
    def __str__(self):
        return self.nome
    
class Turma(models.Model):
    modalidades = (
        ('j', 'Judô'),
        ('b', 'Ballet'),
        ('f', 'Futsal'),
        ('x', 'Xadrez')
    )
    
    turma = models.CharField(max_length=50)
    modalidade = models.CharField(max_length=1, choices=modalidades)
    parceiro = models.ForeignKey(Parceiro, on_delete=models.PROTECT, related_name='turmas', null=True, blank=True)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    status = models.BooleanField(default=1)
    estendido = models.BooleanField(default=0)
    
    def __str__(self):
        modalidade_nome = dict(self.modalidades).get(self.modalidade, self.modalidade)
        return f"{self.turma} - {modalidade_nome} - {self.parceiro.nome} - {self.hora_inicio:%H:%M}"
    
class Funcionarios(models.Model):
    nome = models.CharField(max_length=50)
    cpf_cnpj = models.CharField(max_length=14, null=True, unique=True,  blank=True)
    telefone = models.CharField(max_length=11, null=True, blank=True)
    e_mail = models.CharField(max_length=30, null=True, unique=True,  blank=True)
    endereco = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=1)
    chave_pix = models.CharField(max_length=32)
    obs = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nome
# --------------------------------------------------------------------


# VÍNCULOS --------------------------------------------------------
class Responsavel_Aluno(models.Model):
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    
class Aluno_Turma(models.Model):
    div_pag = (
        ('men', 'Mensal'),
        ('anu', 'Anual'),
        ('sem', 'Semestral'),
        ('out', 'Outro')
    )
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    divisão_pagamento = models.CharField(max_length=3, choices=div_pag, null=True)
    
class Turma_Funcionario(models.Model):
    dias_semana =(
        ('seg', 'Segunda-Feira'),
        ('ter', 'Terça-Feira'),
        ('qua', 'Quarta-Feira'),
        ('qui', 'Quinta-Feira'),
        ('sex', 'Sexta-Feira')
    )
    
    funcionario = models.ForeignKey(Funcionarios, on_delete=models.SET_NULL, null=True, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=dias_semana)
    valor_aula = models.DecimalField(max_digits=10, decimal_places=2)
# --------------------------------------------------------------------


# PAGAMENTOS --------------------------------------------------------
# Model atualizado
class Faturamento(models.Model):
    TIPOS_PAGAMENTO = (
        ('par', 'Parcela da Atividade'),
        ('mat', 'Matrícula'),
        ('cam', 'Camiseta'),
        ('col', 'Colant'),
        ('kim', 'Kimono'),
        ('eve', 'Evento'),
        ('out', 'Outro'),
    )
    
    familia = models.ForeignKey(Familia, on_delete=models.PROTECT, related_name='faturamentos')
    valor_previsto = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor original ou editado com desconto.")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_pagamento = models.CharField(max_length=3, choices=TIPOS_PAGAMENTO)
    pago = models.BooleanField(default=False)
    mes_referencia = models.DateField(help_text="Primeiro dia do mês de referência da cobrança.")
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    obs = models.TextField(null=True, blank=True)
    
    def __str__(self):
        status_str = "Pago" if self.pago else "Em Aberto"
        return f"{self.familia} - R${self.valor_previsto} ({self.mes_referencia.strftime('%m/%Y')}) - {status_str}"
    
class Gastos(models.Model):
    CATEGORIAS_GASTO = (
        ('funcionario', 'Pagamento de Funcionário'),
        ('uniforme', 'Compra de Uniforme/Material'),
        ('imposto', 'Impostos'),
        ('contabilidade', 'Serviços (Contabilidade, etc)'),
        ('banco', 'Taxas Bancárias'),
        ('outro', 'Outro'),
    )

    categoria = models.CharField(max_length=15, choices=CATEGORIAS_GASTO, default='outro')
    descricao = models.CharField(max_length=100, null=True, blank=True)
    funcionario = models.ForeignKey(Funcionarios, on_delete=models.SET_NULL, null=True, blank=True) # Tornar opcional
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    comprovante = models.FileField(upload_to='comprovantes', blank=True, null=True)
    obs = models.TextField(null=True, blank=True)
    data = models.DateField()
# --------------------------------------------------------------------


# PRESENÇAS --------------------------------------------------------
class Presenca_Aluno(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False)
    data = models.DateField()
    
class Presenca_Funcionario(models.Model):
    funcionario = models.ForeignKey(Funcionarios, on_delete=models.SET_NULL, null=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False)
    data = models.DateField()
    
class Faltas_Justificadas(models.Model):
    presenca_funcionario = models.ForeignKey(Presenca_Funcionario, on_delete=models.CASCADE)
    documento = models.FileField(upload_to='atestado', blank=True, null=True)
    atestado = models.BooleanField(default=0)
    obs = models.TextField()
# --------------------------------------------------------------------