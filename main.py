from playwright.sync_api import sync_playwright


PERFIL = "./perfil_celesc"


with sync_playwright() as p:
    subir_browser = p.chromium.launch_persistent_context(PERFIL,
    headless = False,
    accept_downloads = True
    )
    pagina = subir_browser.pages[0] if subir_browser else subir_browser.new_page()
    pagina.goto('https://conecte.celesc.com.br/autenticacao/login')
    input("Aperte enter..")
    print("deu boa")
    subir_browser.close()