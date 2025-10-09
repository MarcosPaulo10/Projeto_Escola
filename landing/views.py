from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from coordenacao.views import alunos_home
        
def landingpage(request):
    return render(request, 'landingpage.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect(alunos_home)

    if request.method == "GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login(request, user)
            return redirect(alunos_home)
        else:
            return HttpResponse('Usuário ou Senha inválidos!')
    
@login_required    
def logout_view(request):
    logout(request)
    return redirect(landingpage)