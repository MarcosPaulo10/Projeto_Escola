from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Familia, Responsavel, Aluno, Funcionarios, Turma, Faturamento, Gastos, Responsavel_Aluno, Aluno_Turma, Turma_Funcionario, Parceiro
from utils import data_atual
from django.db import transaction
from django.contrib.auth.decorators import login_required


# MENU DE CADASTROS -------------------------------
def cadastros_home(request):
    return render(request, 'cadastros_home.html')

# CADASTRO DE RESPONSÁVEIS NO BD ------------------
#
# # Preencher
def cad_responsavel(request):
    # mudar isso para apenas uma view (usar o if request.method == "POST")
    return render (request, 'cad_responsavel.html')
#
# # Salvar
def cad_responsavel_save(request):
    
    nome = request.POST.get('nome')
    cpf_cnpj = request.POST.get('cpfcnpj') 
    boleto = request.POST.get('boleto')
    
    # Transforma o cpf/cnpj em Null para o BD
    if len(cpf_cnpj.strip()) == 0:
        cpf_cnpj = None
        
    # Verifica se nome está em branco/vazio/apenas espaços
    if len(nome.strip()) == 0:
        messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO RESPONSÁVEL!!!!')
        return redirect('cad_responsavel')
    
    # Transformar o None do checkbox em False
    if boleto is None:
        boleto = False
    
    # Cria o Responsavel no BD
    Responsavel.objects.create(
        nome = nome,
        cpf_cnpj = cpf_cnpj,
        tipo_responsavel = request.POST.get('tipo_responsavel'),
        telefone = request.POST.get('telefone'),
        e_mail = request.POST.get('email'),
        boleto = boleto,
        obs = request.POST.get('obs')
    )
    
    return redirect ('cad_responsavel')
#
# # Editar
def editar_responsavel(request, id_responsavel):
    
    responsavel = Responsavel.objects.get(id=id_responsavel)
    
    if request.method == 'POST':
        
        nome = request.POST.get('nome')
        cpf_cnpj = request.POST.get('cpfcnpj') 
        boleto = request.POST.get('boleto')
        
        # Transforma o cpf/cnpj em Null para o BD
        if len(cpf_cnpj.strip()) == 0:
            cpf_cnpj = None
            
        # Verifica se nome está em branco/vazio/apenas espaços
        if len(nome.strip()) == 0:
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO RESPONSÁVEL!!!!')
            return render (request, 'editar_responsavel.html', {'responsavel': responsavel})
        
        # Transformar o None do checkbox em False
        if boleto is None:
            boleto = False
                    
        
        responsavel.nome = nome
        responsavel.cpf_cnpj = cpf_cnpj
        responsavel.tipo_responsavel = request.POST.get('tipo_responsavel')
        responsavel.telefone = request.POST.get('telefone')
        responsavel.e_mail = request.POST.get('e_mail')
        responsavel.boleto = boleto
        responsavel.obs = request.POST.get('obs')
        responsavel.save()
        
        
        return redirect(f"/coordenacao/perfil_responsavel/{id_responsavel}")
    
    return render (request, 'editar_responsavel.html', {'responsavel': responsavel})
# ------------------------------------------------


# CADASTRO E EDIÇÃO DE ALUNOS NO BD ------------------
#
# # Preencher
def cad_aluno(request):
    return render (request, 'cad_aluno.html')
#
# # Salvar
def cad_aluno_save(request):
    
    nome = request.POST.get('nome')
    ativo = request.POST.get('ativo')
    turma_escola = request.POST.get('turma_escola')
    
    # Verifica se nome está em branco/vazio/apenas espaços
    if len(nome.strip()) == 0:
        messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO ALUNO!!!!')
        return redirect('cad_aluno')
    
    # Transforma o turma_escola em Null para o BD
    if len(turma_escola.strip()) == 0:
        turma_escola = None
    
    # Transformar o None do checkbox em False
    if ativo is None:
        ativo = False
    
    Aluno.objects.create(
        nome = nome,
        turma_escola = turma_escola,
        ativo = ativo,
        obs = request.POST.get('obs')
    )
    
    return render (request, 'cad_aluno.html')
#
# # Editar
def editar_aluno(request, id_aluno):
    
    aluno = Aluno.objects.get(id=id_aluno)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        ativo = request.POST.get('ativo')
        turma_escola = request.POST.get('turma_escola')
        obs = request.POST.get('obs')
        
        # Verifica se nome está em branco/vazio/apenas espaços
        if len(nome.strip()) == 0:
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO ALUNO!!!!')
            return render (request, 'editar_aluno.html', {'aluno': aluno})
        
        # Transforma o turma_escola em Null para o BD
        if len(turma_escola.strip()) == 0:
            turma_escola = None
        
        # Transformar o None do checkbox em False
        if ativo is None:
            ativo = False
        
        # Altero os campos do Objeto e Salvo
        aluno.nome = nome
        aluno.turma_escola = turma_escola
        aluno.ativo = ativo
        aluno.obs = obs
        aluno.save()
        
        return redirect(f"/coordenacao/perfil_aluno/{id_aluno}")
    
    return render (request, 'editar_aluno.html', {'aluno': aluno})
# -------------------------------------------


# CADASTRO DE TURMAS NO BD -----------------
#
@login_required
def cad_turma(request):
    if request.method == 'POST':
        turma_nome = request.POST.get('turma')
        parceiro_id = request.POST.get('parceiro') # Mudou de 'escola' para 'parceiro'
        
        # Validação principal
        if not turma_nome or len(turma_nome.strip()) == 0:
            messages.error(request, 'PREENCHA O NOME DA TURMA!')
            return redirect('cad_turma')
        
        if not parceiro_id: # Verifica se um parceiro foi selecionado
            messages.error(request, 'SELECIONE UM PARCEIRO!')
            return redirect('cad_turma')
        
        # Pega os outros dados do formulário
        status = request.POST.get('status')
        estendido = request.POST.get('estendido')
        modalidade = request.POST.get('modalidade')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')

        # Criação do Objeto Turma com a chave estrangeira
        Turma.objects.create(
            turma=turma_nome,
            modalidade=modalidade,
            parceiro_id=parceiro_id,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            status=True if status else False,
            estendido=True if estendido else False
        )
        
        messages.success(request, 'Turma cadastrada com sucesso!')
        return redirect('cad_turma')
    
    else: # Método GET
        # Busca todos os parceiros para listar no formulário
        parceiros = Parceiro.objects.all().order_by('nome')
        context = {
            'parceiros': parceiros
        }
        return render(request, 'cad_turma.html', context)
#
# # Editar
@login_required
def editar_turma(request, id_turma):
    turma = get_object_or_404(Turma, id=id_turma)
    
    if request.method == 'POST':
        parceiro_id = request.POST.get('parceiro')

        # Validações
        if not parceiro_id:
            messages.error(request, 'SELECIONE UM PARCEIRO!')
            # Reenvia a lista de parceiros em caso de erro
            parceiros = Parceiro.objects.all().order_by('nome')
            return render(request, 'editar_turma.html', {'turma': turma, 'parceiros': parceiros})
        
        # Atualiza os campos do objeto
        turma.turma = request.POST.get('turma')
        turma.modalidade = request.POST.get('modalidade')
        turma.parceiro_id = parceiro_id # Atualiza a chave estrangeira
        turma.hora_inicio = request.POST.get('hora_inicio')
        turma.hora_fim = request.POST.get('hora_fim')
        turma.status = True if request.POST.get('status') else False
        turma.estendido = True if request.POST.get('estendido') else False
        turma.save()
        
        messages.success(request, 'Turma atualizada com sucesso!')
        return redirect('perfil_turma', id_turma=id_turma)
    
    # Método GET
    parceiros = Parceiro.objects.all().order_by('nome')
    context = {
        'turma': turma,
        'parceiros': parceiros
    }
    return render(request, 'editar_turma.html', context)
# -------------------------------------------


# CADASTROS DE FUNCIONÁRIOS NO BD -----------------
#
# # Preencher
def cad_funcionario(request):
    return render (request, 'cad_funcionario.html')
#
# # Salvar
def cad_funcionario_save(request):
    
    nome = request.POST.get('nome')
    cpf_cnpj = request.POST.get('cpfcnpj')
    status = request.POST.get('status')
    email = request.POST.get('email')
    
    # Verifica se nome está em branco/vazio/apenas espaços
    if len(nome.strip()) == 0:
        messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO FUNCIONÁRIO!!!!')
        return redirect('cad_funcionario')
    
    # Transforma o cpf/cnpj em Null para o BD (MOTIVO: campo unico)
    if len(cpf_cnpj.strip()) == 0:
        cpf_cnpj = None
        
    # Transforma o e-mail em Null para o BD (MOTIVO: campo unico !!!!POSSO TIRAR O UNIQUE DESSE CAMPO DEPOIS)
    if len(email.strip()) == 0:
        email = None
    
    # Transformar o None do checkbox em False
    if status is None:
        status = False
    
    Funcionarios.objects.create(
    nome = nome,
    cpf_cnpj = cpf_cnpj,
    telefone = request.POST.get('telefone'),
    e_mail = email,
    endereco = request.POST.get('endereco'),
    status = status,
    chave_pix = request.POST.get('pix'),
    obs = request.POST.get('obs')
    )
    
    return redirect('cad_funcionario')
#
# # Editar
def editar_funcionario(request, id_funcionario):
    
    funcionario = Funcionarios.objects.get(id=id_funcionario)
    
    if request.method == "POST":
        nome = request.POST.get('nome')
        cpf_cnpj = request.POST.get('cpfcnpj')
        status = request.POST.get('status')
        email = request.POST.get('email')
        
        # Verifica se nome está em branco/vazio/apenas espaços
        if len(nome.strip()) == 0:
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA O NOME DO FUNCIONÁRIO!!!!')
            return render (request, 'editar_funcionario.html', {'funcionario': funcionario})
        
        # Transforma o cpf/cnpj em Null para o BD (MOTIVO: campo unico)
        if len(cpf_cnpj.strip()) == 0:
            cpf_cnpj = None
            
        # Transforma o e-mail em Null para o BD (MOTIVO: campo unico !!!!POSSO TIRAR O UNIQUE DESSE CAMPO DEPOIS)
        if len(email.strip()) == 0:
            email = None
        
        # Transformar o None do checkbox em False
        if status is None:
            status = False
        
        # Altero os campos do Objeto e Salvo
        funcionario.nome = nome
        funcionario.cpf_cnpj = cpf_cnpj
        funcionario.telefone = request.POST.get('telefone')
        funcionario.e_mail = email
        funcionario.endereco = request.POST.get('endereco')
        funcionario.status = status
        funcionario.chave_pix = request.POST.get('pix')
        funcionario.obs = request.POST.get('obs')
        funcionario.save()
    
        return redirect(f"/coordenacao/funcionario/{id_funcionario}")
    
    return render (request, 'editar_funcionario.html', {'funcionario': funcionario})
# ------------------------------------------------


# CADASTROS DE PAGAMENTOS NO BD --------------------------
def cad_pagamentos(request):
    return render(request, 'cad_pagamentos.html')

def cad_recebido(request):
    
    alunos = Aluno.objects.all().order_by('nome')
    
    if request.method == "POST":
        aluno = request.POST.get('aluno_id')
        valor = request.POST.get('valor')
        tipo_pagamento =  request.POST.get('tipo_pagamento')
        status =  request.POST.get('status')
        mes = request.POST.get('mes')
        ano = request.POST.get('ano')
        
        if aluno == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O ALUNO!!!!')
            return redirect('cad_recebido')
    
        if valor == '':
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA COM O VALOR!!!!')
            return redirect('cad_recebido')
        
        if not tipo_pagamento or not mes or not ano:
            messages.add_message(request, messages.constants.ERROR, 'FAÇA TODAS AS ESCOLHAS (TIPO/MÊS/ANO)!!!!')
            return redirect('cad_recebido')
        
        if not status:
            status = False
         
        Faturamento.objects.create(
        aluno = Aluno.objects.get(id=aluno),
        valor = valor,
        tipo_pagamento = tipo_pagamento,
        status = status,
        mes = mes,
        ano = ano
        )
        
    return render(request, 'cad_recebido.html', {"alunos": alunos})

def cad_pago(request):
    
    data = data_atual()
    funcionarios = Funcionarios.objects.all().order_by('nome').filter(status=1)
    
    if request.method == 'POST':
        funcionario = request.POST.get('funcionario')
        valor = request.POST.get('valor')
        
        if funcionario == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O FUNCIONÁRIO!!!!')
            return redirect('cad_pago')
    
        if valor == '':
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA COM O VALOR!!!!')
            return redirect('cad_pago')
        
        Gastos.objects.create(
            funcionario = Funcionarios.objects.get(id=funcionario),
            valor = valor,
            obs = request.POST.get('obs'),
            data = request.POST.get('data')
        )
        
    return render(request, 'cad_pago.html', {'data_atual': data, 'funcionarios': funcionarios})
# -----------------------------------------------------------



# VÍNCULO ALUNO RESPONSAVEL ---------------------------------
def vinculo_aluno_responsavel(request):

    alunos = Aluno.objects.all().order_by('nome')
    responsaveis = Responsavel.objects.all().order_by('nome')
        
    if request.method == "POST":
        aluno = request.POST.get('aluno_id')
        responsavel = request.POST.get('responsavel_id')
        
        if aluno == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O ALUNO!!!!')
            return redirect('vinculo_aluno_responsavel')
        
        if responsavel == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O RESPONSÁVEL!!!!')
            return redirect('vinculo_aluno_responsavel')
        
        Responsavel_Aluno.objects.create(
            aluno = Aluno.objects.get(id=aluno),
            responsavel = Responsavel.objects.get(id=responsavel)
        )
    
    return render (request, 'vinc_aluno_responsavel.html', {'alunos': alunos, 'responsaveis': responsaveis})

def apagar_alun_resp(request, id_aluno, id_responsavel, perfil):
    
    vinculo = Responsavel_Aluno.objects.get(aluno=id_aluno, responsavel=id_responsavel)
    vinculo.delete()
    
    if perfil != 1:
        return redirect(f'/coordenacao/perfil_aluno/{id_aluno}')
    else:
        print('Vinculo apagado! Volta pro Resp')
        return redirect(f'/coordenacao/perfil_responsavel/{id_responsavel}')
    
# -----------------------------------------------------------


# VÍNCULO DE ALUNO COM TURMA --------------------------
@login_required
def vinculo_aluno_turma(request):
    if request.method == "POST":
        aluno_id = request.POST.get('aluno_id')
        turma_id = request.POST.get('turma_id')
        valor = request.POST.get('valor')
        div_pagamento = request.POST.get('div_pagamento')
        
        if not all([aluno_id, turma_id, valor, div_pagamento]):
            messages.error(request, 'Todos os campos são obrigatórios!')
            return redirect('vinculo_aluno_turma')
        
        Aluno_Turma.objects.create(
            aluno_id=aluno_id,
            turma_id=turma_id,
            valor=valor,
            divisão_pagamento=div_pagamento,
        )
        messages.success(request, f'Aluno vinculado com sucesso!')
        return redirect('perfil_aluno', id_aluno=aluno_id)

    # --- LÓGICA GET ATUALIZADA ---
    aluno_id_selecionado = request.GET.get('aluno')
    
    # Verifica se um aluno foi pré-selecionado pela URL
    if aluno_id_selecionado:
        # Se sim, busca APENAS esse aluno. Usamos .filter() para manter o formato de lista.
        alunos = Aluno.objects.filter(id=aluno_id_selecionado)
    else:
        # Se não, busca todos os alunos ativos (para o caso de acesso genérico)
        alunos = Aluno.objects.filter(ativo=True).order_by('nome')
    
    turmas = Turma.objects.filter(status=True).order_by('modalidade', 'turma')
    opcoes_divisao = Aluno_Turma.div_pag
        
    context = {
        'alunos': alunos, # Esta lista agora terá 1 ou N alunos
        'turmas': turmas,
        'opcoes_divisao': opcoes_divisao,
        'aluno_id_selecionado': aluno_id_selecionado,
    }
    return render(request, 'vinc_aluno_turma.html', context)

def apagar_alun_turm(request, id_aluno, id_turma, perfil):
    
    vinculo = Aluno_Turma.objects.get(aluno=id_aluno, turma=id_turma)
    vinculo.delete()
    
    if perfil != 1:
        return redirect(f'/coordenacao/perfil_aluno/{id_aluno}')
    else:
        return redirect(f'/coordenacao/turma/{id_turma}')
# -----------------------------------------------------


# VÍNCULO DE FUNCIONÁRIO COM TURMA --------------------------
def vinculo_funcionario_turma(request):
    
    funcionarios = Funcionarios.objects.all().order_by('nome').filter(status=1)
    turmas = Turma.objects.all().order_by('turma').filter(status=1)
        
    if request.method == "POST":
        funcionario = request.POST.get('funcionario_id')
        turma = request.POST.get('turma_id')
        valor = request.POST.get('valor')
        dias_semana = request.POST.get('dias_semana')
        
        if funcionario == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O FUNCIONARIO!!!!')
            return redirect('vinculo_funcionario_turma')
        
        if turma == '':
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA A TURMA!!!!')
            return redirect('vinculo_funcionario_turma')
        
        if valor == '':
            messages.add_message(request, messages.constants.ERROR, 'PREENCHA COM O VALOR!!!!')
            return redirect('vinculo_funcionario_turma')
        
        if not dias_semana:
            messages.add_message(request, messages.constants.ERROR, 'ESCOLHA O DIA DA SEMANA!!!!')
            return redirect('vinculo_funcionario_turma')
        
        Turma_Funcionario.objects.create(
            funcionario = Funcionarios.objects.get(id=funcionario),
            turma = Turma.objects.get(id=turma),
            valor_aula = valor,
            dia_semana = dias_semana,
        )
        
    return render (request, 'vinc_funcionario_turma.html', {'funcionarios': funcionarios, 'turmas': turmas})

def apagar_func_turm(request, id_funcionario, id_turma, perfil):
    
    vinculos = Turma_Funcionario.objects.filter(funcionario=id_funcionario, turma=id_turma)
    
    for vinculo in vinculos:
        vinculo.delete()
    
    if perfil != 1:
        return redirect(f'/coordenacao/perfil_funcionario/{id_funcionario}')
    else:
        return redirect(f'/coordenacao/turma/{id_turma}')
# -----------------------------------------------------------
def familia_vincular_view(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 1. Pega as listas de IDs
                responsavel_ids = set(request.POST.getlist('responsavel_id'))
                aluno_ids = set(request.POST.getlist('aluno_id'))
                
                responsavel_ids.discard('')
                aluno_ids.discard('')

                if not responsavel_ids:
                    raise ValueError("Selecione pelo menos um responsável.")

                # 2. Cria a nova Família (agora sem campo 'nome')
                nova_familia = Familia.objects.create()

                # 3. Vincula os responsáveis e alunos
                Responsavel.objects.filter(id__in=responsavel_ids).update(familia=nova_familia)
                Aluno.objects.filter(id__in=aluno_ids).update(familia=nova_familia)

                # 4. Define os papéis (Financeiro e Contato)
                financeiro_id = request.POST.get('role_financeiro')
                contato_id = request.POST.get('role_contato')

                if len(responsavel_ids) == 1:
                    responsavel_unico_id = list(responsavel_ids)[0]
                    nova_familia.responsavel_financeiro_id = responsavel_unico_id
                    nova_familia.responsavel_contato_id = responsavel_unico_id
                else:
                    if not financeiro_id:
                        raise ValueError("Para múltiplos responsáveis, é obrigatório selecionar um Responsável Financeiro.")
                    nova_familia.responsavel_financeiro_id = financeiro_id
                    if contato_id:
                        nova_familia.responsavel_contato_id = contato_id
                
                # A LÓGICA DE GERAR NOME FOI REMOVIDA
                
                nova_familia.save()
            
                # Mensagem de sucesso atualizada
                messages.success(request, f'Família #{nova_familia.id} criada e vinculada com sucesso!')
                return redirect('vinculo_familia')

        except Exception as e:
            messages.error(request, f"Erro ao criar família: {e}")
            return redirect('vinculo_familia')

    context = {
        'responsaveis_disponiveis': Responsavel.objects.filter(familia__isnull=True),
        'alunos_disponiveis': Aluno.objects.filter(familia__isnull=True),
    }
    return render(request, 'vinc_familia.html', context)
# -----------------------------------------------------------
def cad_parceiro(request):
    if request.method == 'POST':
        # --- Lógica para salvar os dados ---
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        chave_pix = request.POST.get('chave_pix')
        obs = request.POST.get('obs')
        contrato = request.FILES.get('contrato') # Arquivos são pegos de request.FILES

        # Validação principal: verifica se o nome foi preenchido
        if not nome or len(nome.strip()) == 0:
            messages.error(request, 'O campo NOME é obrigatório.')
            return redirect('cad_parceiro')

        # Converte campos de texto vazios para None para salvar no banco
        if not cnpj or len(cnpj.strip()) == 0:
            cnpj = None
        if not telefone or len(telefone.strip()) == 0:
            telefone = None
        if not email or len(email.strip()) == 0:
            email = None
        if not chave_pix or len(chave_pix.strip()) == 0:
            chave_pix = None
        if not obs or len(obs.strip()) == 0:
            obs = None
            
        try:
            Parceiro.objects.create(
                tipo=request.POST.get('tipo'),
                nome=nome,
                cnpj=cnpj,
                telefone=telefone,
                e_mail=email,
                chave_pix=chave_pix,
                contrato=contrato,
                obs=obs
            )
            messages.success(request, 'Parceiro cadastrado com sucesso!')
        except Exception as e:
            # Captura erros de campos 'unique' (como CNPJ ou E-mail duplicado)
            messages.error(request, f'Ocorreu um erro: {e}')
        
        return redirect('parceiros_home')

    else:
        # --- Lógica para exibir a página pela primeira vez ---
        return render(request, 'cad_parceiro.html')
# -----------------------------------------------------------
