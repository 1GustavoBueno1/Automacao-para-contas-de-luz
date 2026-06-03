from playwright.sync_api import sync_playwright
import dotenv
import os
import time

dotenv.load_dotenv()
EMAIL = os.getenv('EMAIL')
SENHA = os.getenv('SENHA')

def login():
    pagina.get_by_text('Já tenho o novo cadastro').click()
    pagina.get_by_role('button', name='Entrar com e-mail').click()
    pagina.locator('input[type=\"email\"]').fill(EMAIL)
    pagina.locator('input[name=\"undefined\"]').fill(SENHA)
    pagina.get_by_role('button', name='Entrar').click()
    print('Login efetuado com sucesso!')

def abaixar_primeiras_6_contas():
    for n in range(1, 6):
        pagina.get_by_role("button", name="Selecionar unidade").nth(n).click()
        with pagina.expect_download() as download_info:
            pagina.get_by_role("button", name="receipt_long 2ª via de conta").click()
            input("Aperte enter para a proxima")
        pagina.goto('https://conecte.celesc.com.br/contrato/selecao')

with sync_playwright() as play:
    browser = play.chromium.launch(headless = False)
    pagina = browser.new_page(accept_downloads= True)
    pagina.goto("https://conecte.celesc.com.br/autenticacao/login")
    login()
    pagina.get_by_role("button", name="Selecionar unidade").first.click()
    with pagina.expect_download() as download_info:
            pagina.get_by_role("button", name="receipt_long 2ª via de conta").click()
    download = download_info.value
    pagina.goto('https://conecte.celesc.com.br/contrato/selecao')
    time.sleep(20)
    browser.close()