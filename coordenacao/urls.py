from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),
    
    # Caminhos(paths) para urls relacionadas ao ALUNO:
    path('alunos', views.alunos_home, name='alunos_home'),
    path('perfil_aluno/<int:id_aluno>/', views.perfil_aluno, name='perfil_aluno'),
    path('update_aluno_status/<int:id_aluno>', views.update_aluno_status, name='update_aluno_status'),
    
    # Caminhos(paths) para urls relacionadas ao REPONSÁVEL:
    path('responsaveis', views.responsaveis_home, name='responsaveis_home'),
    path('perfil_responsavel/<int:id_responsavel>/', views.perfil_responsavel, name='perfil_responsavel'),
    
    # Caminhos(paths) para urls relacionadas ao FUNCIONÁRIO:
    path('funcionarios', views.funcionarios_home, name='funcionarios_home'),
    path('perfil_funcionario/<int:id_funcionario>', views.perfil_funcionario, name='perfil_funcionario'),
    
    # Caminhos(paths) para urls relacionadas à TURMA:
    path('turmas', views.turmas_home, name='turmas_home'),
    path('turma/<int:id_turma>', views.perfil_turma, name='perfil_turma'),
    path('turma/<int:id_turma>/adicionar_aluno/', views.adicionar_aluno_turma, name='adicionar_aluno_turma'),
    path('turma/<int:id_turma>/remover_aluno/<int:id_aluno>/', views.remover_aluno_turma, name='remover_aluno_turma'),
    path('turma/<int:id_turma>/adicionar_funcionario/', views.adicionar_funcionario_turma, name='adicionar_funcionario_turma'),
    path('turma/remover_funcionario/<int:id_vinculo>/', views.remover_funcionario_turma, name='remover_funcionario_turma'),
    
    
    # Caminhos(paths) para urls relacionadas à MENSALIDADE:
    path('gerar/', views.gerar_cobrancas, name='gerar_cobrancas'),
    path('cobrancas/', views.cobrancas_mensais, name='cobrancas_mensais'),
    path('atualizar_cobranca/<int:faturamento_id>/', views.atualizar_cobranca, name='atualizar_cobranca'),
    path('apagar_cobranca/<int:faturamento_id>/', views.apagar_cobranca, name='apagar_cobranca'),
    path('cobranca_avulsa/', views.view_faturamento_avulso, name='cad_faturamento_avulso'),
    path('editar_cobranca/<int:faturamento_id>/', views.editar_faturamento, name='editar_faturamento'),
    path('gastos/', views.view_gastos, name='cad_gastos'),
    path('gastos/editar/<int:gasto_id>/', views.editar_gasto, name='editar_gasto'),
    path('gastos/apagar/<int:gasto_id>/', views.apagar_gasto, name='apagar_gasto'),

    
    
    # Caminhos(paths) para urls relacionadas à CHAMADA:
    path('gerar_chamada/<int:id_turma>/<str:data>', views.gerar_chamada, name='gerar_chamada'),
    path('chamada/<int:id_turma>/<str:data>', views.chamada, name='chamada'),
    path('chamada_home', views.chamada_home, name='chamada_home'),
    path('update_presenca/<int:id>/<int:id_turma>/<str:data>/<str:alun_prof>', views.update_presenca, name='update_presenca'),
    path('apagar_chamada/<int:id_turma>/<str:data>/', views.apagar_chamada, name='apagar_chamada'),
    
    # Caminhos(paths) para urls relacionadas à FAMÍLIA:
    path('familias/', views.familia_home, name='familias_dashboard'),
    path('perfil_familia/<int:id_familia>/', views.perfil_familia, name='perfil_familia'),
    path('familia/definir_papeis/<int:id_familia>/', views.definir_papeis_familia, name='definir_papeis_familia'),
    path('familia/adicionar_membro/<int:id_familia>/', views.adicionar_membro_familia, name='adicionar_membro_familia'),
    path('familia/remover_membro/<int:id_membro>/<str:tipo_membro>/', views.remover_membro_familia, name='remover_membro_familia'),

    # Caminhos(paths) para urls relacionadas ao PARCEIRO:
    path('parceiros/', views.parceiros_home, name='parceiros_home'),
    path('perfil_parceiro/<int:id_parceiro>/', views.perfil_parceiro, name='perfil_parceiro'),
    path('parceiro/editar/<int:id_parceiro>/', views.editar_parceiro, name='editar_parceiro'),
]