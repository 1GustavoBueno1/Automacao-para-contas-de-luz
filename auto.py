from playwright.sync_api import sync_playwright
import dotenv
import os

dotenv.load_dotenv()
EMAIL = os.getenv('CELESC_EMAIL')
SENHA = os.getenv('CELESC_SENHA')

# Pasta (ja existente) onde as segundas vias de conta serao salvas.
# Caminho absoluto baseado na localizacao deste arquivo, para funcionar independente de onde o script for executado.
PASTA_CONTAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contas")

def login():
    pagina.get_by_text('Já tenho o novo cadastro').click()
    pagina.get_by_role('button', name='Entrar com e-mail').click()
    pagina.locator('input[type="email"]').fill(EMAIL)
    pagina.locator('input[name="undefined"]').fill(SENHA)
    pagina.get_by_role('button', name='Entrar').click()
    print('Login efetuado com sucesso!')

def salvar_conta(download, indice):
    """Salva o arquivo baixado dentro da pasta de contas com um nome unico."""
    # Garante que a pasta existe (rede de seguranca caso seja apagada).
    os.makedirs(PASTA_CONTAS, exist_ok=True)
    # Nome que o site sugeriu para o arquivo (ex.: "segunda_via.pdf").
    nome_original = download.suggested_filename or f"conta_{indice}.pdf"
    # Prefixo com o indice da unidade para nenhum arquivo sobrescrever o outro.
    nome_final = f"unidade_{indice}_{nome_original}"
    caminho = os.path.join(PASTA_CONTAS, nome_final)
    # save_as espera o download terminar e copia o arquivo para o destino final.
    download.save_as(caminho)
    print(f"Conta da unidade {indice} salva em: {caminho}")
    return caminho
def verifica_se_existe_algum_botao(botao):
    if botao.count > 0:
        return True
    return False
def baixar_conta_da_unidade(indice):
    """Seleciona uma unidade, baixa a 2a via e salva na pasta de contas."""
    pagina.get_by_role("button", name="Selecionar unidade").nth(indice).click()
    # O bloco 'expect_download' captura o download disparado pelo clique abaixo.
    verifica_se_existe_algum_botao()
    with pagina.expect_download() as download_info:
        dowload = pagina.get_by_role("button", name="receipt_long 2ª via de conta")
        if verifica_se_existe_algum_botao(dowload):
            pagina.get_by_role("button", name="receipt_long 2ª via de conta").click()
            salvar_conta(download_info.value, indice)
            pagina.goto('https://conecte.celesc.com.br/contrato/selecao')
        else:
            pagina.goto('https://conecte.celesc.com.br/contrato/selecao')
            print('conta nao possui fatura aberta')
    salvar_conta(download_info.value, indice)


with sync_playwright() as play:
    browser = play.chromium.launch(headless=False)
    pagina = browser.new_page(accept_downloads=True)
    pagina.goto("https://conecte.celesc.com.br/autenticacao/login")
    login()
    pagina.get_by_role('button', name='Selecionar').first.click()
    # Baixa e salva as 6 primeiras unidades (indices 1 a 6).
    for indice in range(1, 7):
        baixar_conta_da_unidade(indice)

    print("Todas as contas foram baixadas!")
    browser.close()
