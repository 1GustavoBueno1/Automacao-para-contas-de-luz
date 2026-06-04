from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import dotenv
import os
import re

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
    pagina.get_by_role("button", name="Selecionar arrow_right_alt").first.click()

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

def fechar_popup_agora_nao():
    nome = re.compile(r"Agora\s*não", re.IGNORECASE)
    botao = pagina.get_by_role("button", name=nome).or_(pagina.get_by_text(nome)).first
    try:
        botao.click(timeout=3000)
        print("Popup 'Agora não' fechado.")
    except PlaywrightTimeoutError:
        pass  # popup nao apareceu desta vez

def baixar_conta_da_unidade(indice):
    """Seleciona uma unidade, baixa a 2a via (se houver) e salva na pasta de contas."""
    pagina.get_by_role("button", name="Selecionar unidade").nth(indice).click()
    # Fecha o popup "Agora não" caso ele apareca.
    fechar_popup_agora_nao()
    botao_2via = pagina.get_by_role("button", name="receipt_long 2ª via de conta")
    # unidade o botao ainda nao esta no DOM, entao precisamos AGUARDAR ele aparecer.
    # Se nao aparecer dentro do tempo limite, a unidade nao tem fatura aberta.
    try:
        botao_2via.wait_for(state="visible", timeout=10000)
    except PlaywrightTimeoutError:
        print(f"Unidade {indice}: sem fatura aberta, pulando.")
        pagina.goto('https://conecte.celesc.com.br/contrato/selecao')
        return

    # Apenas o clique que dispara o download fica dentro do 'expect_download'.
    with pagina.expect_download() as download_info:
        botao_2via.click()

    # download_info.value so fica disponivel DEPOIS que o bloco 'with' termina.
    salvar_conta(download_info.value, indice)
    pagina.goto('https://conecte.celesc.com.br/contrato/selecao')


with sync_playwright() as play:
    browser = play.chromium.launch(headless=False)
    pagina = browser.new_page(accept_downloads=True)
    pagina.goto("https://conecte.celesc.com.br/autenticacao/login")
    login()
    # Baixa e salva as 6 primeiras unidades (indices 1 a 6).
    for indice in range(1, 7):
        baixar_conta_da_unidade(indice)
    print("Todas as contas foram baixadas!")
    browser.close()
