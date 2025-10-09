from django.urls import path
from . import views

urlpatterns = [
    path('planilha/', views.export_page_view, name='pagina_exportacao'),
    path('exportar-tabelas/', views.export_all_tables_to_xlsx, name='exportar_tabelas_xlsx'),
    path('gerar-planilha-familias/', views.gerar_planilha_familias_view, name='gerar_planilha_familias'),
    path('exportar_faturamento/', views.exportar_faturamento_view, name='exportar_faturamento_xlsx'),
]