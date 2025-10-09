from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cadastros.models import Turma, Turma_Funcionario, Aluno_Turma, Aluno, Funcionarios, Presenca_Aluno, Presenca_Funcionario, Responsavel, Faturamento, Gastos, Familia, Parceiro
from utils import data_atual
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import date
from decimal import Decimal, InvalidOperation
from comunicacao.models import Texto
from datetime import datetime


def home(request):
    return render(request, 'home.html')
# TURMA - HOME E PERFIL ---------------------------------
#Feito (necessita de melhorias)
@login_required
def turmas_home(request):
    turma_busca = request.GET.get('turma', '')
    parceiro_id = request.GET.get('parceiro', None)
    modalidade_selecionada = request.GET.get('modalidade', None)


    parceiros = Parceiro.objects.annotate(
        total_turmas_ativas=Count('turmas', filter=Q(turmas__status=True), distinct=True),
        total_alunos_modalidade=Count('turmas__aluno_turma', filter=Q(turmas__status=True)),
        total_alunos_unicos=Count('turmas__aluno_turma__aluno', filter=Q(turmas__status=True), distinct=True)
    ).order_by('nome')
    
    if parceiro_id:
        parceiros = parceiros.filter(id=parceiro_id)

    turmas = Turma.objects.filter(status=True).select_related('parceiro').order_by('modalidade', 'turma', 'hora_inicio')
    
    if turma_busca:
        turmas = turmas.filter(turma__icontains=turma_busca)
    
    if parceiro_id:
        turmas = turmas.filter(parceiro_id=parceiro_id)
        
    if modalidade_selecionada:
        turmas = turmas.filter(modalidade=modalidade_selecionada)
    
    opcoes_modalidade = Turma.modalidades
    todos_parceiros_para_filtro = Parceiro.objects.all().order_by('nome')

    context = {
        'parceiros': parceiros,
        'turmas': turmas,
        'opcoes_modalidade': opcoes_modalidade,
        'todos_parceiros_para_filtro': todos_parceiros_para_filtro,
        'turma_busca': turma_busca,
        'parceiro_selecionado_id': parceiro_id,
        'modalidade_selecionada': modalidade_selecionada,
    }
    return render(request, 'turmas_home.html', context)

#Feito (Mudança sugerida pela IA - Olhar depois sobre ORM do Django para a filtragem de dados)
@login_required
def perfil_turma(request, id_turma):
    data_hoje = timezone.localdate()
    turma = get_object_or_404(Turma.objects.select_related('parceiro'), id=id_turma)
    mes_selecionado_str = request.GET.get('mes', '') 
    
    chamadas_query = Presenca_Aluno.objects.filter(
        turma=turma,
        data__year=data_hoje.year
    )

    if mes_selecionado_str:
        try:
            ano, mes = map(int, mes_selecionado_str.split('-'))
            chamadas_query = Presenca_Aluno.objects.filter(
                turma=turma,
                data__year=ano,
                data__month=mes
            )
        except (ValueError, TypeError):
            pass

    chamadas_datas = chamadas_query.values_list('data', flat=True).distinct().order_by('-data')

    dias_semana_map = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'}
    historico_chamadas = []
    for data_chamada in chamadas_datas:
        historico_chamadas.append({
            'data': data_chamada,
            'dia_semana': dias_semana_map[data_chamada.weekday()]
        })

    vinculos_professores = Turma_Funcionario.objects.filter(turma=turma).select_related('funcionario').order_by('funcionario__nome', 'dia_semana')
    funcionarios_disponiveis = Funcionarios.objects.all().order_by('nome')
    dias_semana_choices = Turma_Funcionario.dias_semana
    lista_dias = sorted(list(set(v.get_dia_semana_display() for v in vinculos_professores)))
    lista_alunos = Aluno.objects.filter(aluno_turma__turma=turma).order_by('nome')
    alunos_disponiveis = Aluno.objects.exclude(id__in=lista_alunos.values('id')).order_by('nome')

    context = {
        'turma': turma,
        'data': data_hoje.strftime('%Y-%m-%d'),
        'vinculos_professores': vinculos_professores,
        'funcionarios_disponiveis': funcionarios_disponiveis,
        'dias_semana_choices': dias_semana_choices,
        'lista_alunos': lista_alunos,
        'alunos_disponiveis': alunos_disponiveis,
        'quantidade_alunos': lista_alunos.count(),
        'lista_dias': ", ".join(lista_dias) if lista_dias else "Dias não definidos",
        'historico_chamadas': historico_chamadas,
        'mes_selecionado': mes_selecionado_str,
    }

    return render(request, 'turma.html', context)

# 2 VIEW PARA ADICIONAR UM ALUNO NA TURMA
@login_required
def adicionar_aluno_turma(request, id_turma):
    if request.method == 'POST':
        turma = get_object_or_404(Turma, id=id_turma)
        aluno_id = request.POST.get('aluno_id')

        if aluno_id:
            aluno = get_object_or_404(Aluno, id=aluno_id)

            # get_or_create previne duplicatas caso o aluno já esteja na turma
            _, created = Aluno_Turma.objects.get_or_create(aluno=aluno, turma=turma)
            
            if created:
                messages.success(request, f'Aluno "{aluno.nome}" adicionado à turma.')
            else:
                messages.warning(request, f'Aluno "{aluno.nome}" já estava na turma.')
        else:
            messages.error(request, 'Nenhum aluno selecionado.')

    return redirect('perfil_turma', id_turma=id_turma)


# 3 VIEW PARA REMOVER UM ALUNO DA TURMA
@login_required
def remover_aluno_turma(request, id_turma, id_aluno):
    # Encontra e deleta a ligação específica na tabela Aluno_Turma
    link = get_object_or_404(Aluno_Turma, turma_id=id_turma, aluno_id=id_aluno)
    nome_aluno = link.aluno.nome
    link.delete()
    
    messages.info(request, f'Aluno "{nome_aluno}" removido da turma.')
    return redirect('perfil_turma', id_turma=id_turma)

@login_required
def adicionar_funcionario_turma(request, id_turma):
    if request.method == 'POST':
        turma = get_object_or_404(Turma, id=id_turma)
        
        funcionario_id = request.POST.get('funcionario_id')
        dia_semana = request.POST.get('dia_semana')
        valor_aula_str = request.POST.get('valor_aula')

        # Validação
        if not all([funcionario_id, dia_semana, valor_aula_str]):
            messages.error(request, 'Todos os campos (Funcionário, Dia e Valor) são obrigatórios.')
            return redirect('perfil_turma', id_turma=id_turma)

        funcionario = get_object_or_404(Funcionarios, id=funcionario_id)
        
        # Previne adicionar a mesma pessoa no mesmo dia
        if Turma_Funcionario.objects.filter(turma=turma, funcionario=funcionario, dia_semana=dia_semana).exists():
            messages.warning(request, f'{funcionario.nome} já está atribuído(a) a esta turma na {dict(Turma_Funcionario.dias_semana)[dia_semana]}.')
        else:
            Turma_Funcionario.objects.create(
                turma=turma, 
                funcionario=funcionario, 
                dia_semana=dia_semana, 
                valor_aula=valor_aula_str.replace(',', '.')
            )
            messages.success(request, f'{funcionario.nome} foi adicionado(a) à turma.')

    return redirect('perfil_turma', id_turma=id_turma)

@login_required
def remover_funcionario_turma(request, id_vinculo):
    # O id_vinculo é o ID da tabela Turma_Funcionario
    vinculo = get_object_or_404(Turma_Funcionario, id=id_vinculo)
    id_turma_redirect = vinculo.turma.id # Pega o ID da turma antes de deletar
    
    nome_funcionario = vinculo.funcionario.nome
    dia = vinculo.get_dia_semana_display()

    vinculo.delete()
    
    messages.info(request, f'O vínculo de {nome_funcionario} na {dia} foi removido.')
    return redirect('perfil_turma', id_turma=id_turma_redirect)
# -----------------------------------------------------------


# ALUNO - HOME E PERFIL ---------------------------------
@login_required
def alunos_home(request):
    alunos_filtrar = request.GET.get('nome')
    parceiros_data = []
    parceiros = Parceiro.objects.all().order_by('nome')
    
    for parceiro in parceiros:
        alunos_do_parceiro = Aluno.objects.filter(
            aluno_turma__turma__parceiro=parceiro
        ).distinct().order_by('nome')
        
        if alunos_filtrar:
            alunos_do_parceiro = alunos_do_parceiro.filter(nome__icontains=alunos_filtrar)
        
        if alunos_do_parceiro.exists():
            parceiros_data.append({
                'parceiro': parceiro,
                'alunos': alunos_do_parceiro
            })
            
    context = {
        'parceiros_data': parceiros_data
    }
    return render(request, 'alunos_home.html', context)

#Feito (necessita de melhorias)
@login_required
def perfil_aluno(request, id_aluno):
    aluno = get_object_or_404(Aluno.objects.select_related('familia'), id=id_aluno)
    vinculos_aluno = Aluno_Turma.objects.filter(aluno=aluno).select_related('turma__parceiro')
    parceiros = sorted(list({v.turma.parceiro for v in vinculos_aluno if v.turma.parceiro}), key=lambda p: p.nome)
    responsaveis_familia = []
    irmaos = []
    
    if aluno.familia:
        responsaveis_familia = aluno.familia.responsaveis.all().order_by('nome')
        irmaos = aluno.familia.alunos.exclude(id=aluno.id).order_by('nome')

    context = {
        'aluno': aluno,
        'vinculos_aluno': vinculos_aluno,
        'responsaveis_familia': responsaveis_familia,
        'irmaos': irmaos,
        'parceiros': parceiros,
    }
    
    return render(request, 'aluno.html', context)
    
def update_aluno_status(request, id_aluno):
    aluno = Aluno.objects.get(id=id_aluno)
    aluno.ativo = not aluno.ativo
    aluno.save()
    
    url = f"/coordenacao/perfil_aluno/{id_aluno}"

    return redirect(url)
# -----------------------------------------------------------


# RESPONSÁVEL - HOME E PERFIL ---------------------------------
@login_required 
def perfil_responsavel(request, id_responsavel):
    responsavel = get_object_or_404(Responsavel, id=id_responsavel)
    
    alunos_vinculados = Aluno.objects.filter(
        responsavel_aluno__responsavel=responsavel
    ).distinct().order_by('nome')
    
    context = {
        'responsavel': responsavel, 
        'alunos': alunos_vinculados,
        'resp': 1
    }
    
    return render(request, 'responsavel.html', context)
    
@login_required
def responsaveis_home(request):
    responsaveis_filtrar = request.GET.get('nome')
    
    parceiros_data = []
    parceiros = Parceiro.objects.all().order_by('nome')
    
    for parceiro in parceiros:
        responsaveis_do_parceiro = Responsavel.objects.filter(
            responsavel_aluno__aluno__aluno_turma__turma__parceiro=parceiro
        ).distinct().order_by('nome')
        
        if responsaveis_filtrar:
            responsaveis_do_parceiro = responsaveis_do_parceiro.filter(nome__icontains=responsaveis_filtrar)
        
        if responsaveis_do_parceiro.exists():
            parceiros_data.append({
                'parceiro': parceiro,
                'responsaveis': responsaveis_do_parceiro
            })
            
    context = {
        'parceiros_data': parceiros_data
    }
    return render(request, 'responsaveis_home.html', context)
# -----------------------------------------------------------


# FUNCIONÁRIO - HOME E PERFIL ---------------------------------
@login_required
def funcionarios_home(request):
    funcionarios_filtrar = request.GET.get('nome')
    
    parceiros_data = []
    parceiros = Parceiro.objects.all().order_by('nome')
    
    for parceiro in parceiros:
        funcionarios_do_parceiro = Funcionarios.objects.filter(
            turma_funcionario__turma__parceiro=parceiro
        ).distinct().order_by('nome')
        
        if funcionarios_filtrar:
            funcionarios_do_parceiro = funcionarios_do_parceiro.filter(nome__icontains=funcionarios_filtrar)
        
        # Adiciona à lista final apenas se houver funcionários para o parceiro (após o filtro)
        if funcionarios_do_parceiro.exists():
            parceiros_data.append({
                'parceiro': parceiro,
                'funcionarios': funcionarios_do_parceiro
            })
            
    context = {
        'parceiros_data': parceiros_data
    }
    return render(request, 'funcionarios_home.html', context)

@login_required
def perfil_funcionario(request, id_funcionario):
    funcionario = get_object_or_404(Funcionarios, id=id_funcionario)
    
    turmas = Turma_Funcionario.objects.filter(
        funcionario=funcionario
    ).select_related('turma').order_by('turma__turma')
    
    context = {
        'funcionario': funcionario, 
        'turmas': turmas, 
        'perfil': 3
    }
    
    return render(request, 'funcionario.html', context)
# -----------------------------------------------------------


# MENSALIDADES - GERAR, HOME, UPDATE ---------------------------------
# Gera a lista de mensalidades em um determinado mês
@login_required
def gerar_cobrancas(request):
    if request.method == 'POST':
        mes_str = request.POST.get('mes') # Formato 'YYYY-MM'
        ano, mes = map(int, mes_str.split('-'))
        
        familias_a_cobrar = Familia.objects.filter(
            alunos__aluno_turma__divisão_pagamento='men'
        ).distinct()

        cobrancas_criadas = 0
        for familia in familias_a_cobrar:
            valor_total = Aluno_Turma.objects.filter(
                aluno__familia=familia,
                divisão_pagamento='men'
            ).aggregate(Sum('valor'))['valor__sum'] or 0

            if valor_total > 0:
                Faturamento.objects.get_or_create(
                    familia=familia,
                    mes_referencia=date(ano, mes, 1),
                    tipo_pagamento='par',
                    defaults={
                        'valor_previsto': valor_total,
                        'data_vencimento': date(ano, mes, 10),
                    }
                )
                cobrancas_criadas += 1

        messages.success(request, f'{cobrancas_criadas} cobranças foram geradas ou já existiam para o mês {mes}/{ano}.')
        return redirect('gerar_cobrancas')

    return render(request, 'gerar_cobrancas.html')


# VIEW PARA A TELA PRINCIPAL DE COBRANÇAS
@login_required
def cobrancas_mensais(request):
    mes_selecionado_str = request.GET.get('mes', '') 
    termo_busca = request.GET.get('busca', '')
    texto_selecionado_id = request.GET.get('msg', None)
    parceiro_id = request.GET.get('parceiro', None)

    faturamentos = Faturamento.objects.filter(
        tipo_pagamento='par'
    ).select_related(
        'familia__responsavel_contato'
    ).prefetch_related(
        'familia__alunos', 'familia__responsaveis'
    )

    if mes_selecionado_str:
        try:
            ano, mes = map(int, mes_selecionado_str.split('-'))
            faturamentos = faturamentos.filter(mes_referencia=date(ano, mes, 1))
        except (ValueError, TypeError):
            pass

    if termo_busca:
        faturamentos = faturamentos.filter(
            Q(familia__alunos__nome__icontains=termo_busca) |
            Q(familia__responsaveis__nome__icontains=termo_busca)
        ).distinct()

    if parceiro_id:
        faturamentos = faturamentos.filter(
            familia__alunos__aluno_turma__turma__parceiro_id=parceiro_id
        ).distinct()

    cobrancas_abertas = faturamentos.filter(pago=False).order_by('-data_vencimento')
    cobrancas_pagas = faturamentos.filter(pago=True).order_by('-data_pagamento')

    textos_disponiveis = Texto.objects.all()
    mensagem_template = ""
    if texto_selecionado_id:
        try:
            mensagem_template = textos_disponiveis.get(id=texto_selecionado_id).template
        except Texto.DoesNotExist:
            mensagem_template = ""

    for cobranca in cobrancas_abertas:
        if mensagem_template:
            responsavel = cobranca.familia.responsavel_contato
            primeiro_nome = responsavel.nome.split()[0] if responsavel and responsavel.nome else "Responsável"
            valor_formatado = f"{cobranca.valor_previsto:.2f}".replace('.', ',')
            cobranca.mensagem_whatsapp = mensagem_template.replace('{nome}', primeiro_nome).replace('{valor}', valor_formatado)
        else:
            cobranca.mensagem_whatsapp = ""

    todos_parceiros = Parceiro.objects.all().order_by('nome')

    context = {
        'cobrancas_abertas': cobrancas_abertas,
        'cobrancas_pagas': cobrancas_pagas,
        'mes_selecionado': mes_selecionado_str,
        'termo_busca': termo_busca,
        'textos_disponiveis': textos_disponiveis,
        'msg_selecionada_id': texto_selecionado_id,
        'todos_parceiros': todos_parceiros,
        'parceiro_selecionado_id': parceiro_id,
    }
    return render(request, 'cobrancas_mensais.html', context)



# VIEW AUXILIAR PARA ATUALIZAR UMA COBRANÇA
@login_required
def atualizar_cobranca(request, faturamento_id):
    if request.method == 'POST':
        cobranca = get_object_or_404(Faturamento, id=faturamento_id)
        cobranca.valor_previsto = request.POST.get('valor_previsto')
        cobranca.obs = request.POST.get('obs')

        if 'marcar_pago' in request.POST:
            valor_str = request.POST.get('valor_previsto')
            try:
                valor_decimal = Decimal(valor_str)
                if valor_decimal <= 0:
                    messages.error(request, "Para marcar como pago, o Valor deve ser maior que zero.")
                else:
                    cobranca.pago = True
                    cobranca.data_pagamento = timezone.now().date()
                    cobranca.valor_pago = valor_decimal
                    messages.success(request, 'Cobrança marcada como paga!')
            except (InvalidOperation, TypeError, ValueError):
                messages.error(request, "Valor inválido. Insira um número válido para o pagamento.")

        elif 'marcar_nao_pago' in request.POST:
            cobranca.pago = False
            cobranca.data_pagamento = None
            cobranca.valor_pago = None
            messages.info(request, 'Cobrança reaberta e movida para "Em Aberto".')
        else:
            messages.success(request, 'Cobrança atualizada com sucesso!')
            
        cobranca.save()

        params = request.POST.get('redirect_params')
        base_url = reverse('cobrancas_mensais')
        redirect_url = f'{base_url}?{params}' if params else base_url
        return redirect(redirect_url)
    
    return redirect('cobrancas_mensais')

# SUA VIEW APAGAR_COBRANCA - COM REDIRECT CORRIGIDO
@login_required
def apagar_cobranca(request, faturamento_id):
    cobranca = get_object_or_404(Faturamento, id=faturamento_id)
    cobranca.delete()
    messages.success(request, 'Cobrança apagada com sucesso.')
    
    params = request.GET.urlencode()
    base_url = reverse('cobrancas_mensais')
    redirect_url = f'{base_url}?{params}' if params else base_url
    return redirect(redirect_url)

@login_required
def view_faturamento_avulso(request):
    if request.method == 'POST':
        familia_id = request.POST.get('familia')
        valor = request.POST.get('valor_previsto')
        tipo = request.POST.get('tipo_pagamento')
        pago = request.POST.get('pago')
        data_vencimento_str = request.POST.get('data_vencimento')

        if not familia_id or not valor or not tipo or not data_vencimento_str:
            messages.error(request, 'Os campos Família, Tipo, Valor e Vencimento são obrigatórios!')
            return redirect('cad_faturamento_avulso')
        
        ano, mes, dia = map(int, data_vencimento_str.split('-'))
        
        faturamento = Faturamento.objects.create(
            familia_id=familia_id,
            valor_previsto=valor,
            tipo_pagamento=tipo,
            data_vencimento=date(ano, mes, dia),
            mes_referencia=date(ano, mes, 1),
            obs=request.POST.get('obs'),
            pago=True if pago else False
        )
        
        if faturamento.pago:
            faturamento.data_pagamento = timezone.now().date()
            faturamento.valor_pago = valor
            faturamento.save()
            
        messages.success(request, 'Receita cadastrada com sucesso!')
        return redirect('cad_faturamento_avulso')

    familias = Familia.objects.all().order_by('id')
    faturamentos_avulsos = Faturamento.objects.exclude(tipo_pagamento='par').order_by('-data_vencimento')
    
    context = {
        'familias': familias,
        'faturamentos': faturamentos_avulsos,
        'tipos_pagamento': Faturamento.TIPOS_PAGAMENTO
    }
    return render(request, 'faturamento_avulso.html', context)

@login_required
def editar_faturamento(request, faturamento_id):
    faturamento = get_object_or_404(Faturamento, id=faturamento_id)
    
    if request.method == 'POST':
        faturamento.familia_id = request.POST.get('familia')
        faturamento.valor_previsto = request.POST.get('valor_previsto')
        faturamento.tipo_pagamento = request.POST.get('tipo_pagamento')
        faturamento.data_vencimento = request.POST.get('data_vencimento')
        faturamento.obs = request.POST.get('obs')
        
        pago_check = request.POST.get('pago')
        
        if pago_check:
            faturamento.pago = True
            faturamento.data_pagamento = faturamento.data_pagamento or timezone.now().date()
            faturamento.valor_pago = faturamento.valor_pago or faturamento.valor_previsto
        else:
            faturamento.pago = False
            faturamento.data_pagamento = None
            faturamento.valor_pago = None

        faturamento.save()
        messages.success(request, 'Faturamento atualizado com sucesso!')
        return redirect('cad_faturamento_avulso')

    familias = Familia.objects.all()
    context = {
        'faturamento': faturamento,
        'familias': familias,
        'tipos_pagamento': Faturamento.TIPOS_PAGAMENTO
    }
    return render(request, 'editar_faturamento.html', context)


# --- GASTOS / DESPESAS ---

@login_required
def view_gastos(request):
    if request.method == 'POST':
        # Validação
        if not request.POST.get('descricao') or not request.POST.get('valor') or not request.POST.get('data'):
            messages.error(request, 'Os campos Descrição, Valor e Data são obrigatórios!')
            return redirect('cad_gastos')

        funcionario_id = request.POST.get('funcionario')
        
        Gastos.objects.create(
            categoria=request.POST.get('categoria'),
            descricao=request.POST.get('descricao'),
            valor=request.POST.get('valor'),
            data=request.POST.get('data'),
            funcionario_id=funcionario_id if funcionario_id else None,
            obs=request.POST.get('obs')
        )
        messages.success(request, 'Despesa cadastrada com sucesso!')
        return redirect('cad_gastos')
    
    gastos = Gastos.objects.all().order_by('-data')
    funcionarios = Funcionarios.objects.filter(status=True).order_by('nome')
    context = {
        'gastos': gastos,
        'categorias': Gastos.CATEGORIAS_GASTO,
        'funcionarios': funcionarios
    }
    return render(request, 'gastos.html', context)

@login_required
def editar_gasto(request, gasto_id):
    gasto = get_object_or_404(Gastos, id=gasto_id)
    if request.method == 'POST':
        gasto.categoria = request.POST.get('categoria')
        gasto.descricao = request.POST.get('descricao')
        gasto.valor = request.POST.get('valor')
        gasto.data = request.POST.get('data')
        
        funcionario_id = request.POST.get('funcionario')
        gasto.funcionario_id = funcionario_id if funcionario_id else None
        
        gasto.obs = request.POST.get('obs')
        gasto.save()
        
        messages.success(request, 'Despesa atualizada com sucesso!')
        return redirect('cad_gastos')

    funcionarios = Funcionarios.objects.filter(status=True).order_by('nome')
    context = {
        'gasto': gasto,
        'categorias': Gastos.CATEGORIAS_GASTO,
        'funcionarios': funcionarios
    }
    return render(request, 'editar_gasto.html', context)

@login_required
def apagar_gasto(request, gasto_id):
    gasto = get_object_or_404(Gastos, id=gasto_id)
    gasto.delete()
    messages.success(request, 'Despesa apagada com sucesso.')
    return redirect('cad_gastos')
# -----------------------------------------------------------

# CHAMADA - HOME, GERAR, PERFIL, UPDATE ---------------------------------
@login_required
def chamada_home(request):
    
    chamadas = Presenca_Aluno.objects.all()
    
    '''presencas_alunos = Presenca_Aluno.objects.all()
    
    presencas_professores = Presenca_Funcionario.objects
    
    turmas_filtrar = request.GET.get('turma')
    
    data_filtrar = request.GET.get('data')

    if turmas_filtrar:
        turmas = turmas.filter(turma__icontains = turmas_filtrar)
        
    
    alunos_filtrar = request.GET.get('nome')

    if alunos_filtrar:
        alunos_santo = alunos_santo.filter(nome__icontains = alunos_filtrar)
        alunos_externato = alunos_externato.filter(nome__icontains = alunos_filtrar)'''
        
    return render(request, 'chamada_home.html')

# Gera a lista de chamada de uma determinada turma e redireciona para a view da chamada
@login_required
def gerar_chamada(request, id_turma, data):
    aluno_ids = Aluno_Turma.objects.filter(turma_id=id_turma).values_list('aluno_id', flat=True)
    professor_ids = Turma_Funcionario.objects.filter(turma_id=id_turma).values_list('funcionario_id', flat=True).distinct()
    if not Presenca_Aluno.objects.filter(data=data, turma_id=id_turma).exists():
        for aluno_id in aluno_ids:
            Presenca_Aluno.objects.create(aluno_id=aluno_id, turma_id=id_turma, data=data)
            
        for professor_id in professor_ids:
            Presenca_Funcionario.objects.create(funcionario_id=professor_id, turma_id=id_turma, data=data)
            
      
    return redirect('chamada', id_turma=id_turma, data=data)
#
# Chamada de um turma e dia específico 
@login_required
def chamada(request, id_turma, data):
    
    presencas_alunos = Presenca_Aluno.objects.filter(turma_id=id_turma, data=data).order_by('aluno__nome')
    
    partes = data.split("-")
    data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}" 
    
    turma = Turma.objects.get(id=id_turma)
        
    presencas_professores = Presenca_Funcionario.objects.filter(turma=id_turma, data=data).order_by('funcionario__nome')
    
    return render(request, 'chamada.html', {'id_turma': id_turma, 'data': data, 'data_formatada': data_formatada, 'presencas_alunos': presencas_alunos, 'presencas_professores': presencas_professores, 'turma': turma})

@login_required
def update_presenca(request, id, id_turma, data, alun_prof):
    if alun_prof == 'alun':
        presenca = Presenca_Aluno.objects.get(id=id)
        presenca.status = not presenca.status
        presenca.save()
    else:
        presenca = Presenca_Funcionario.objects.get(id=id)
        presenca.status = not presenca.status
        presenca.save()

    return redirect('chamada', id_turma=id_turma, data=data)
# -----------------------------------------------------------

@login_required
def familia_home(request):
    busca_termo = request.GET.get('busca', '')
    
    familias = Familia.objects.prefetch_related(
        'responsaveis',
        'alunos__aluno_turma_set__turma__parceiro'
    ).distinct()

    if busca_termo:
        familias = familias.filter(
            Q(responsaveis__nome__icontains=busca_termo) |
            Q(alunos__nome__icontains=busca_termo)
        )

    familias_data = []
    for familia in familias:
        parceiros = set()
        valor_mensal_total = 0
        valores_anuais = []
        valores_semestrais = []
        valores_outros = []

        for aluno in familia.alunos.all():
            for matricula in aluno.aluno_turma_set.all():
                if matricula.turma and matricula.turma.parceiro:
                    parceiros.add(matricula.turma.parceiro.nome)
                
                if matricula.valor:
                    if matricula.divisão_pagamento == 'men':
                        valor_mensal_total += matricula.valor
                    elif matricula.divisão_pagamento == 'anu':
                        valores_anuais.append(matricula.valor)
                    elif matricula.divisão_pagamento == 'sem':
                        valores_semestrais.append(matricula.valor)
                    elif matricula.divisão_pagamento == 'out':
                        valores_outros.append(matricula.valor)

        familias_data.append({
            'familia_obj': familia,
            'parceiros': list(parceiros),
            'valor_mensal': valor_mensal_total,
            'valores_anuais': valores_anuais,
            'valores_semestrais': valores_semestrais,
            'valores_outros': valores_outros,
        })

    context = {
        'familias_data': familias_data,
        'busca_termo': busca_termo,
    }
    return render(request, 'familia_home.html', context)


# VIEW DO PERFIL
@login_required
def perfil_familia(request, id_familia):
    familia = get_object_or_404(Familia, id=id_familia)
    responsaveis_da_familia = familia.responsaveis.all().order_by('nome')
    alunos_da_familia = familia.alunos.all().order_by('nome')
    responsaveis_disponiveis = Responsavel.objects.filter(familia__isnull=True).order_by('nome')
    alunos_disponiveis = Aluno.objects.filter(familia__isnull=True).order_by('nome')

    context = {
        'familia': familia,
        'responsaveis_da_familia': responsaveis_da_familia,
        'alunos_da_familia': alunos_da_familia,
        'responsaveis_disponiveis': responsaveis_disponiveis,
        'alunos_disponiveis': alunos_disponiveis,
    }
    return render(request, 'familia.html', context)


@login_required
def definir_papeis_familia(request, id_familia):
    if request.method == 'POST':
        familia = get_object_or_404(Familia, id=id_familia)
        financeiro_id = request.POST.get('role_financeiro')
        contato_id = request.POST.get('role_contato')
        familia.responsavel_financeiro_id = financeiro_id if financeiro_id else None
        familia.responsavel_contato_id = contato_id if contato_id else None
        
        familia.save()
        messages.success(request, 'Papéis da família atualizados com sucesso!')
    return redirect('perfil_familia', id_familia=id_familia)



@login_required
def adicionar_membro_familia(request, id_familia):
    if request.method == 'POST':
        familia = get_object_or_404(Familia, id=id_familia)
        
        aluno_id = request.POST.get('aluno_id')
        responsavel_id = request.POST.get('responsavel_id')

        if aluno_id:
            aluno = get_object_or_404(Aluno, id=aluno_id)
            aluno.familia = familia
            aluno.save()
            messages.success(request, f'Aluno "{aluno.nome}" adicionado à família.')

        if responsavel_id:
            responsavel = get_object_or_404(Responsavel, id=responsavel_id)
            responsavel.familia = familia
            responsavel.save()
            messages.success(request, f'Responsável "{responsavel.nome}" adicionado à família.')

    return redirect('perfil_familia', id_familia=id_familia)


@login_required
def remover_membro_familia(request, id_membro, tipo_membro):
    familia = None
    if tipo_membro == 'responsavel':
        membro = get_object_or_404(Responsavel, id=id_membro)
        familia = membro.familia
        
        if familia.responsaveis.count() <= 1:
            messages.error(request, 'Não é possível remover o último responsável da família.')
            return redirect('perfil_familia', id_familia=familia.id)
        
        if familia.responsavel_financeiro == membro:
            familia.responsavel_financeiro = None
        if familia.responsavel_contato == membro:
            familia.responsavel_contato = None
        familia.save()

    elif tipo_membro == 'aluno':
        membro = get_object_or_404(Aluno, id=id_membro)
        familia = membro.familia
    
    else:
        messages.error(request, 'Tipo de membro inválido.')
        return redirect(request.META.get('HTTP_REFERER', 'cadastros_home'))

    membro.familia = None
    membro.save()
    
    messages.info(request, f'Membro "{membro.nome}" removido da família.')
    return redirect('perfil_familia', id_familia=familia.id)

# -----------------------------------------------------------
def parceiros_home(request):
    busca_nome = request.GET.get('nome', '')

    if busca_nome:
        parceiros = Parceiro.objects.filter(nome__icontains=busca_nome).order_by('nome')
    else:
        parceiros = Parceiro.objects.all().order_by('nome')

    context = {
        'parceiros': parceiros
    }
    return render(request, 'parceiros_home.html', context)


def perfil_parceiro(request, id_parceiro):
    parceiro = get_object_or_404(Parceiro, id=id_parceiro)
    
    context = {
        'parceiro': parceiro
    }
    return render(request, 'parceiro.html', context)

@login_required
def editar_parceiro(request, id_parceiro):
    parceiro = get_object_or_404(Parceiro, id=id_parceiro)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        if not nome or len(nome.strip()) == 0:
            messages.error(request, 'O campo NOME é obrigatório.')
            return render(request, 'editar_parceiro.html', {'parceiro': parceiro})

        parceiro.tipo = request.POST.get('tipo')
        parceiro.nome = nome
        parceiro.cnpj = request.POST.get('cnpj') or None
        parceiro.telefone = request.POST.get('telefone') or None
        parceiro.e_mail = request.POST.get('email') or None
        parceiro.chave_pix = request.POST.get('chave_pix') or None
        parceiro.obs = request.POST.get('obs') or None

        if 'contrato' in request.FILES:
            parceiro.contrato = request.FILES.get('contrato')
        
        parceiro.save()
        messages.success(request, 'Parceiro atualizado com sucesso!')
        return redirect('perfil_parceiro', id_parceiro=parceiro.id)

    context = {
        'parceiro': parceiro
    }
    return render(request, 'editar_parceiro.html', context)

@login_required
def apagar_chamada(request, id_turma, data):
    turma = get_object_or_404(Turma, id=id_turma)
    
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        presencas_alunos = Presenca_Aluno.objects.filter(turma=turma, data=data_obj)
        num_alunos_apagados = presencas_alunos.count()
        presencas_alunos.delete()
        presencas_funcionarios = Presenca_Funcionario.objects.filter(turma=turma, data=data_obj)
        num_func_apagados = presencas_funcionarios.count()
        presencas_funcionarios.delete()

        if num_alunos_apagados > 0 or num_func_apagados > 0:
            messages.success(request, f'A chamada do dia {data_obj.strftime("%d/%m/%Y")} foi apagada com sucesso. ({num_alunos_apagados} registros de alunos e {num_func_apagados} de professores removidos).')
        else:
            messages.info(request, f'Não havia registros de chamada para apagar no dia {data_obj.strftime("%d/%m/%Y")}.')

    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao tentar apagar a chamada: {e}')

    return redirect('perfil_turma', id_turma=id_turma)