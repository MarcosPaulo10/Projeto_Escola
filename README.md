# Sistema de Gestão de Escola Esportiva

Um sistema de gestão para escolas de esportes ou atividades extras, desenvolvido em Django para otimizar a administração de turmas, alunos, finanças, comunicação, entre outros.

## 🚀 Sobre o Projeto

Este é um projeto solo, desenvolvido por mim para atender a uma necessidade real da empresa em questão . O sistema nasceu da necessidade de organizar informações de alunos, turmas e pagamentos que antes eram descentralizadas ou dados inexistentes.

O projeto iniciou-se de forma simples, utilizando a interface Admin do Django e os Models como um banco de dados relacional. Com o tempo, evoluiu com a implementação de novas funcionalidades. O desenvolvimento tem sido realizado por iniciativa própria, sem remuneração, como um projeto pessoal para aplicar e aprofundar conhecimentos em desenvolvimento web com Python e Django.

### Metodologia

O sistema está em contínuo desenvolvimento. O modelo de engenharia de software mais próximo do aplicado é o de **prototipagem** (apesar de não ter utilizado de fato), onde funcionalidades são adicionadas e refinadas de forma incremental. Por ser um protótipo em evolução, é possível que o código contenha resquícios de versões anteriores ou estruturas preparadas para futuras implementações.

## 🔧 Tecnologias Utilizadas

* **Python**
* **Django**
* **SQLite3**
* **HTML, CSS com TailwindCSS**
* **JavaScript (Alpine.js)**
* **Pandas & Faker** (para geração de dados de teste)

## ⚙️ Configuração e Instalação

Para executar este projeto localmente, siga os passos abaixo:

1. **Clone o repositório:**
   **Bash**

   ```
   git clone [URL_DO_SEU_REPOSITORIO]
   cd [NOME_DA_PASTA_DO_PROJETO]
   ```
2. **Crie e ative um ambiente virtual:**
   **Bash**

   ```
   # Criar o ambiente
   python -m venv .venv

   # Ativar no Windows
   .\.venv\Scripts\activate

   # Ativar no macOS/Linux
   source .venv/bin/activate
   ```
3. **Instale as dependências:**
   O arquivo `requirements.txt` contém todos os pacotes necessários.
   **Bash**

   ```
   pip install -r requirements.txt
   ```
4. **Execute o servidor:**
   **Bash**

   ```
   python manage.py runserver
   ```

   O site estará disponível em `http://127.0.0.1:8000/`.

## 💡 Como Utilizar e Testar

### Acesso Administrativo

Para ter uma visão completa da gestão de dados e explorar a interface administrativa nativa do Django, acesse a rota `/admin`.

* **Usuário:** `test`
* **Senha:** `test`

### Banco de Dados

O arquivo `db.sqlite3` incluído no projeto já vem populado com dados fictícios. Estes dados foram gerados através de um script Python utilizando a biblioteca  **Faker** . O script de geração não foi projetado para ser robusto, mas fornece uma base de dados sólida o suficiente para utilizar, visualizar e testar todas as funcionalidades do sistema.

### Conteúdo da Landing Page

O conteúdo de texto e o design da landing page institucional são baseados na identidade visual e nas informações da empresa real para a qual o sistema foi projetado.
