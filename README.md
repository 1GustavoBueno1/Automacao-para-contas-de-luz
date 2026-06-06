# Autocelesc

Bot de automação que faz login no portal **[Conecte CELESC](https://conecte.celesc.com.br)** e baixa automaticamente a **2ª via de conta** de todas as unidades (imóveis) cadastradas na sua conta, salvando cada PDF na pasta `contas/`.

Feito com [Playwright](https://playwright.dev/python/) controlando um navegador Chromium real.

> ⚠️ Projeto de uso pessoal/educacional. Use apenas com a **sua própria conta**.

---

## ✨ O que ele faz

- Faz login no portal da CELESC usando e-mail e senha (lidos de um arquivo `.env`).
- Percorre cada unidade cadastrada e, se houver fatura em aberto, baixa a 2ª via.
- Salva cada PDF em `contas/` com nome único (`unidade_<n>_<arquivo>.pdf`), sem sobrescrever.
- Lida com situações comuns do site:
  - aguarda o spinner de carregamento desaparecer;
  - fecha o popup **"Agora não"** quando ele aparece;
  - pula unidades **sem fatura aberta** (tira um screenshot de debug se o download não for gerado);
  - usa `slow_mo` (pequena pausa entre cliques) para parecer mais "humano" e reduzir o risco de bloqueio por automação.

---

## 📂 Estrutura do projeto

```
Autocelesc/
├── auto.py            # Script principal: login + download das 2ªs vias
├── main.py            # Utilitário para abrir o navegador com perfil persistente (login manual / debug)
├── requirements.txt   # Dependências Python
├── .env               # Suas credenciais (NÃO versionado)
├── contas/            # PDFs baixados (criada automaticamente, NÃO versionada)
└── perfil_celesc/     # Perfil persistente do Chromium usado pelo main.py (NÃO versionado)
```

---

## 🔧 Pré-requisitos

- **Python 3.8+**
- Conta no portal Conecte CELESC

---

## 🚀 Instalação

1. Clone o repositório e entre na pasta:

   ```bash
   git clone <url-do-repositorio>
   cd Autocelesc
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # Linux / macOS
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Instale o navegador usado pelo Playwright (apenas na primeira vez):

   ```bash
   playwright install chromium
   ```

---

## 🔑 Configuração

Crie um arquivo `.env` na raiz do projeto com as suas credenciais da CELESC:

```env
CELESC_EMAIL=seu-email@exemplo.com
CELESC_SENHA=sua-senha
```

> O arquivo `.env` está no `.gitignore` e **não** é enviado para o repositório.

---

## ▶️ Como usar

Rode o script principal:

```bash
python auto.py
```

O navegador abrirá (em modo visível), fará o login e baixará as 2ªs vias. Ao final, os PDFs estarão na pasta `contas/`.

### `main.py` (opcional)

`main.py` abre o Chromium com um **perfil persistente** (`perfil_celesc/`) e pausa esperando você apertar Enter. É útil para fazer login manualmente uma vez, inspecionar o site ou depurar seletores:

```bash
python main.py
```

---

## ⚙️ Ajustes úteis

No `auto.py`:

- **Quantidade de unidades** — o laço percorre os índices de 1 a 42:

  ```python
  for indice in range(1, 43):
  ```

  Ajuste o intervalo conforme o número de unidades da sua conta. Se houver bloqueio por IP no meio do processo, basta retomar a partir do índice em que parou.

- **Velocidade / risco de bloqueio** — `slow_mo=800` adiciona ~0,8s de pausa antes de cada ação. Aumente esse valor para reduzir o risco de bloqueio (ban por IP); diminua para ir mais rápido.

  ```python
  browser = play.chromium.launch(headless=False, slow_mo=800)
  ```

- **Modo headless** — troque `headless=False` por `headless=True` para rodar sem abrir a janela do navegador.

---

## ⚠️ Observações

- O site pode aplicar **bloqueio por IP** se detectar muitas requisições automatizadas em sequência. Em caso de bloqueio, aguarde um tempo e retome a partir da unidade onde parou.
- A estrutura/seletores do site da CELESC podem mudar a qualquer momento, o que pode exigir ajustes no script.

---

## 📝 Licença

Uso pessoal e educacional.
