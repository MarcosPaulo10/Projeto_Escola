from django.contrib import admin
from .models import (
    Parceiro, Familia, Responsavel, Aluno, Turma, Funcionarios,
    Aluno_Turma, Turma_Funcionario, Faturamento, Gastos,
    Presenca_Aluno, Presenca_Funcionario, Faltas_Justificadas
)


### Seções para editar modelos relacionados dentro de outros modelos--------------------
class ResponsavelInline(admin.TabularInline):
    """Permite adicionar/editar Responsáveis diretamente na página de uma Família."""
    model = Responsavel
    extra = 1
    autocomplete_fields = ['familia']

class AlunoInline(admin.TabularInline):
    """Permite adicionar/editar Alunos diretamente na página de uma Família."""
    model = Aluno
    extra = 1
    autocomplete_fields = ['familia']

class AlunoTurmaInline(admin.TabularInline):
    """Permite vincular um Aluno a uma Turma (e vice-versa)."""
    model = Aluno_Turma
    extra = 1
    autocomplete_fields = ['aluno', 'turma']

class TurmaFuncionarioInline(admin.TabularInline):
    """Permite vincular um Funcionário a uma Turma (e vice-versa)."""
    model = Turma_Funcionario
    extra = 1
    autocomplete_fields = ['funcionario', 'turma']

class TurmaInline(admin.TabularInline):
    """Mostra as turmas de um Parceiro diretamente na página do Parceiro."""
    model = Turma
    extra = 0
    show_change_link = True

class FaltasJustificadasInline(admin.StackedInline):
    """Permite justificar uma falta diretamente no registro de presença do funcionário."""
    model = Faltas_Justificadas
    extra = 0
### -----------------------------------------------------------------------------


### Admins normais --------------------------------------------------------------
@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'telefone', 'e_mail')
    list_filter = ('tipo',)
    search_fields = ('nome', 'cnpj')
    inlines = [TurmaInline]

@admin.register(Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_responsavel_financeiro', 'display_responsavel_contato', 'get_alunos')
    search_fields = ('responsaveis__nome', 'alunos__nome', 'id')
    autocomplete_fields = ('responsavel_financeiro', 'responsavel_contato')
    inlines = [ResponsavelInline, AlunoInline]
    list_display_links = ('id', 'display_responsavel_financeiro')

    @admin.display(description='Responsável Financeiro')
    def display_responsavel_financeiro(self, obj):
        return obj.responsavel_financeiro.nome if obj.responsavel_financeiro else "Não definido"

    @admin.display(description='Responsável de Contato')
    def display_responsavel_contato(self, obj):
        return obj.responsavel_contato.nome if obj.responsavel_contato else "Não definido"
        
    @admin.display(description='Alunos')
    def get_alunos(self, obj):
        return ", ".join([aluno.nome for aluno in obj.alunos.all()])

@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'familia', 'telefone', 'e_mail', 'boleto')
    list_filter = ('tipo_responsavel', 'boleto')
    search_fields = ('nome', 'cpf_cnpj', 'e_mail', 'telefone', 'familia__id')
    autocomplete_fields = ['familia']

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'familia', 'turma_escola', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('ativo',)
    search_fields = ('nome', 'familia__responsaveis__nome', 'familia__id')
    inlines = [AlunoTurmaInline]
    autocomplete_fields = ['familia']

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('turma', 'modalidade', 'parceiro', 'hora_inicio', 'hora_fim', 'status', 'get_student_count')
    list_filter = ('modalidade', 'parceiro', 'status')
    search_fields = ('turma', 'parceiro__nome')
    inlines = [AlunoTurmaInline, TurmaFuncionarioInline]

    @admin.display(description='Nº Alunos')
    def get_student_count(self, obj):
        return obj.aluno_turma_set.count()

@admin.register(Funcionarios)
class FuncionariosAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'e_mail', 'status')
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('nome', 'cpf_cnpj', 'e_mail')
    inlines = [TurmaFuncionarioInline]

@admin.register(Faturamento)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('familia', 'valor_previsto', 'mes_referencia', 'data_vencimento', 'pago')
    list_editable = ('pago',)
    list_filter = ('pago', 'tipo_pagamento', 'mes_referencia')
    search_fields = ('familia__responsaveis__nome', 'familia__alunos__nome', 'familia__id')
    autocomplete_fields = ('familia',)
    date_hierarchy = 'mes_referencia'

@admin.register(Gastos)
class GastosAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data', 'funcionario')
    list_filter = ('categoria', 'data', 'funcionario')
    search_fields = ('descricao', 'funcionario__nome')
    autocomplete_fields = ('funcionario',)
    date_hierarchy = 'data'

@admin.register(Presenca_Aluno)
class PresencaAlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data', 'status')
    list_editable = ('status',)
    list_filter = ('data', 'status', 'turma')
    search_fields = ('aluno__nome', 'turma__turma')
    autocomplete_fields = ('aluno', 'turma')
    date_hierarchy = 'data'

@admin.register(Presenca_Funcionario)
class PresencaFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'turma', 'data', 'status')
    list_editable = ('status',)
    list_filter = ('data', 'status', 'turma')
    search_fields = ('funcionario__nome', 'turma__turma')
    inlines = [FaltasJustificadasInline]
    autocomplete_fields = ('funcionario', 'turma')
    date_hierarchy = 'data'
### -----------------------------------------------------------------------------