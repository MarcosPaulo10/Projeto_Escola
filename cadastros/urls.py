from django.urls import path
from . import views

urlpatterns = [
    
    # PATHS/URLS --- HOME - CADASTROS
    path('', views.cadastros_home, name='cadastros_home'),
    
    # PATHS/URLS --- RESPONSAVEL
    path('cad_responsavel', views.cad_responsavel, name='cad_responsavel'),
    path('cad_responsavel_save', views.cad_responsavel_save, name='cad_responsavel_save'),
    path('editar_responsavel/<int:id_responsavel>', views.editar_responsavel, name='editar_responsavel'),
    
    # PATHS/URLS --- ALUNO
    path('cad_aluno', views.cad_aluno, name='cad_aluno'),
    path('cad_aluno_save', views.cad_aluno_save, name='cad_aluno_save'),
    path('editar_aluno/<int:id_aluno>', views.editar_aluno, name='editar_aluno'),
    
    # PATHS/URLS --- TURMA
    path('cad_turma', views.cad_turma, name='cad_turma'),
    path('editar_turma/<int:id_turma>', views.editar_turma, name='editar_turma'),
    
    # PATHS/URLS --- FUNCIONARIO
    path('cad_funcionario', views.cad_funcionario, name='cad_funcionario'),
    path('cad_funcionario_save', views.cad_funcionario_save, name='cad_funcionario_save'),
    path('editar_funcionario/<int:id_funcionario>', views.editar_funcionario, name='editar_funcionario'),
    
    # PATHS/URLS --- PAGAMENTOS
    path('cad_pagamentos', views.cad_pagamentos, name='cad_pagamentos'),
    
    path('cad_recebido', views.cad_recebido, name='cad_recebido'),
    #path('editar_recebido/<int:id_recebido>', views.editar_recebido, name='editar_recebido'),
    
    path('cad_pago', views.cad_pago, name='cad_pago'),
    #path('editar_pago/<int:id_pago>', views.editar_pago, name='editar_pago'),
    
    # PATHS/URLS --- VINCULO: ALUNO / RESPONSAVEL
    path('vinculo_aluno_responsavel', views.vinculo_aluno_responsavel, name='vinculo_aluno_responsavel'),
    path('apagar_alun_resp/<int:id_aluno>/<int:id_responsavel>/<int:perfil>', views.apagar_alun_resp, name='apagar_alun_resp'),
    
    # PATHS/URLS --- VINCULO: ALUNO / TURMA
    path('vinculo_aluno_turma', views.vinculo_aluno_turma, name='vinculo_aluno_turma'),
    path('apagar_alun_turm/<int:id_aluno>/<int:id_turma>/<int:perfil>', views.apagar_alun_turm, name='apagar_alun_turm'),
    

    # PATHS/URLS --- VINCULO: FUNCIONARIO / TURMA
    path('vinculo_funcionario_turma', views.vinculo_funcionario_turma, name='vinculo_funcionario_turma'),
    path('apagar_func_turm/<int:id_funcionario>/<int:id_turma>/<int:perfil>', views.apagar_func_turm, name='apagar_func_turm'),
    
    # PATHS/URLS --- FAMILIA
    path('vinculo_familia', views.familia_vincular_view, name='vinculo_familia'),

    # PATHS/URLS --- PARCEIRO
    path('parceiro/', views.cad_parceiro, name='cad_parceiro'),

]