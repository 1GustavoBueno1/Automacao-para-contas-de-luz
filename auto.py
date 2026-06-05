from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
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

def esperar_carregamento(timeout=30000):
    """Espera o spinner de carregamento da CELESC desaparecer.

    Enquanto carrega, o site cobre a tela com <ui-celesc-loader> e o
    'loader-backdrop' intercepta os cliques, aqui esperamos esse backdrop ficar 'hidden'.
    """
    backdrop = pagina.locator(".loader-backdrop").first
    # as vezes o loader surge com um pequeno atraso. Damos uma
    # janelinha pra ele aparecer antes de esperar ele sumir.
    try:
        backdrop.wait_for(state="visible", timeout=2000)
    except PlaywrightTimeoutError:
        pass  # nao apareceu rapido; talvez nem va aparecer
    try:
        backdrop.wait_for(state="hidden", timeout=timeout)
    except PlaywrightTimeoutError:
        pass

def fechar_popup_agora_nao(timeout=6000):
    """Fecha o modal 'Agora não' se ele aparecer; ignora se nao aparecer.

    esse modal so surge DEPOIS que o loader some, e seu backdrop
    intercepta cliques. Por isso ele precisa ser fechado ANTES de tentar
    clicar na 2a via.

    """
    botao = pagina.get_by_text("Agora não").first
    try:
        botao.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError:
        return  # modal nao apareceu desta vez
    botao.click()
    print("Popup 'Agora não' fechado.")
    esperar_carregamento()  # fechar o modal pode disparar outro loader

def voltar_para_selecao():
    """Volta para a tela de selecao de unidades pelo botao 'Trocar imóvel'.

    Navegacao in-app (sem pagina.goto): nao recarrega o SPA inteiro a cada
    unidade, o que e mais leve e menos propenso a disparar bloqueio por bot.
    """
    pagina.get_by_text('Trocar imóvel').first.click()

def baixar_conta_da_unidade(indice):
    """Seleciona uma unidade, baixa a 2a via (se houver) e salva na pasta de contas."""
    pagina.get_by_role("button", name="Selecionar unidade").nth(indice).click()
    # Ordem importa: 1) espera o loader sumir; 2) so entao o modal "Agora não"
    # aparece -> fecha. Se fechar antes do loader, o modal nem nasceu ainda.
    esperar_carregamento()
    fechar_popup_agora_nao()
    botao_2via = pagina.get_by_role("button", name="receipt_long 2ª via de conta")
    # unidade o botao ainda nao esta no DOM, entao precisamos AGUARDAR ele aparecer.
    # timeout alto porque a tela da unidade pode demorar a carregar.
    # Se nao aparecer dentro do tempo limite, a unidade nao tem fatura aberta.
    try:
        botao_2via.wait_for(state="visible", timeout=15000)
    except PlaywrightTimeoutError:
        print(f"Unidade {indice}: sem fatura aberta, pulando.")
        voltar_para_selecao()
        return
    # Clicar na 2a via dispara a geracao do PDF (aparece um loader) e, em
    # seguida, o download. timeout maior porque a geracao pode demorar.
    try:
        with pagina.expect_download(timeout=60000) as download_info:
            botao_2via.click()
    except PlaywrightTimeoutError:
        os.makedirs(PASTA_CONTAS, exist_ok=True)
        caminho_debug = os.path.join(PASTA_CONTAS, f"debug_sem_download_unidade_{indice}.png")
        pagina.screenshot(path=caminho_debug)
        print(f"Unidade {indice}: 2a via nao gerou download (screenshot: {caminho_debug}). Pulando.")
        voltar_para_selecao()
        return
    # download_info.value so fica disponivel DEPOIS que o bloco 'with' termina.
    salvar_conta(download_info.value, indice)
    voltar_para_selecao()


with sync_playwright() as play:
    # slow_mo: pausa ~0,8s antes de cada acao, para o ritmo parecer mais
    # humano e reduzir o risco de bloqueio por automacao (ban de IP).
    browser = play.chromium.launch(headless=False, slow_mo=800)
    pagina = browser.new_page(accept_downloads=True)
    pagina.goto("https://conecte.celesc.com.br/autenticacao/login")
    login()
    # Baixa e salva as 6 primeiras unidades (indices 1 a 6).
    for indice in range(1, 7):
        baixar_conta_da_unidade(indice)
    print("Todas as contas foram baixadas!")
    browser.close()