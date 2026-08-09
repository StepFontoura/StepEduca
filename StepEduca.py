import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
import random
import string
import math
import pandas as pd
import base64
import urllib.parse
import time
import re

try:
    from google import genai
    from google.genai import types
    GOOGLE_GENAI_DISPONIVEL = True
except ImportError:
    GOOGLE_GENAI_DISPONIVEL = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_DISPONIVEL = True
except ImportError:
    FIREBASE_DISPONIVEL = False

# Configuração da página
st.set_page_config(
    page_title="StepEduca",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS de Nível Profissional e Regras Mágicas para Sticky
st.markdown("""
    <style>
    /* Ajuste do container para o banner colar no topo */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Fundo Escuro da Aplicação */
    .stApp {
        background-color: #0e1117;
        color: #f1f5f9;
    }
    
    /* Cabeçalho Contínuo - Logo colada à Esquerda e Tamanho Legível */
    .header-banner {
        background-color: #010B19; 
        padding: 10px 10px 10px 20px; 
        margin-top: 0;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 30px;
        border-bottom: 1px solid #1e293b;
        display: flex;
        justify-content: flex-start; 
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    @media (max-width: 768px) {
        .header-banner {
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 15px 20px;
            justify-content: center; 
        }
    }
    
    /* Card da Tela de Login */
    div[data-testid="stForm"] {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        border-top: 3px solid #ef4444 !important;
        border-radius: 12px !important;
        padding: 40px 30px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Ampliação das fontes dentro do formulário de login */
    div[data-testid="stForm"] label {
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #f1f5f9 !important;
    }
    div[data-testid="stForm"] input {
        font-size: 16px !important;
    }
    
    /* Botões Primários (Vermelho Padrão) */
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button {
        background-color: #ef4444 !important;
        color: white !important;
        border: none !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {
        background-color: #dc2626 !important;
    }
    
    /* Cards de Cursos */
    .card-curso {
        background-color: #111827;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        color: #f8fafc;
    }
    
    .mobile-frame-container {
        background: #030712;
        border-radius: 24px;
        padding: 15px;
        max-width: 520px;
        margin: 0 auto;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
        border: 4px solid #1e293b;
    }
    
    .link-box {
        background-color: #111827;
        border: 2px dashed #0284c7;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
    }
    
    /* Cores das caixas de gabarito */
    .gab-mc { background-color: #1e3a8a; border-left: 6px solid #3b82f6; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .gab-vf { background-color: #064e3b; border-left: 6px solid #10b981; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .gab-lac { background-color: #78350f; border-left: 6px solid #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .gab-dis { background-color: #4c1d95; border-left: 6px solid #8b5cf6; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    
    /* Ocultar barra superior original do Streamlit */
    header[data-testid="stHeader"] { background-color: transparent; }
    
    /* ==============================================================
       CSS MÁGICO PARA A COLUNA STICKY E ANIMAÇÕES (RESPIRAR + QUICAR)
       ============================================================== */
    /* Captura a coluna mãe que contém a classe painel-letras-sticky */
    div[data-testid="column"]:has(.painel-letras-sticky) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 40px !important;
        align-self: flex-start !important;
        z-index: 100 !important;
    }
    
    .painel-letras-sticky {
        background-color: #030712; 
        border-radius: 20px; 
        padding: 40px 20px; 
        text-align: center; 
        border: 4px dashed #38bdf8; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    @keyframes pulse-bounce {
        0% { transform: scale(1) translateY(0); filter: drop-shadow(0px 0px 5px rgba(255,255,255,0.2)); }
        50% { transform: scale(1.1) translateY(-25px); filter: drop-shadow(0px 0px 25px rgba(255,255,255,0.7)); }
        100% { transform: scale(1) translateY(0); filter: drop-shadow(0px 0px 5px rgba(255,255,255,0.2)); }
    }
    </style>
""", unsafe_allow_html=True)

# Função utilitária para localizar a logo
def obter_caminho_logo():
    possibilidades = ["StepEduca_Logo.png", "logo.png", "StepEduca_Logo.jpg", "StepEduca_Logo.jpeg"]
    for nome in possibilidades:
        if os.path.exists(nome):
            return nome
    return None

# Renderização do Banner de Cabeçalho (Páginas Internas)
def renderizar_cabecalho():
    caminho_logo = obter_caminho_logo()
    img_html = "<h2 style='color: #38bdf8; margin: 0;'>🎓 STEP EDUCA</h2>"
    
    if caminho_logo:
        try:
            with open(caminho_logo, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            mime_type = "image/jpeg" if caminho_logo.lower().endswith(('.jpg', '.jpeg')) else "image/png"
            img_html = f'<img src="data:{mime_type};base64,{encoded_string}" style="height: 135px; width: auto; object-fit: contain; margin-left: 0px;">'
        except Exception:
            pass
            
    st.markdown(f"""
        <div class="header-banner">
            {img_html}
        </div>
    """, unsafe_allow_html=True)

@st.cache_resource
def inicializar_firebase():
    if not FIREBASE_DISPONIVEL:
        return None, "Biblioteca firebase_admin não instalada."
    
    json_credencial = "credenciais_firebase.json"
    
    if not os.path.exists(json_credencial):
        arquivos = [f for f in os.listdir('.') if f.endswith('.json') and ('firebase' in f.lower() or 'stepeduca' in f.lower())]
        if arquivos:
            json_credencial = arquivos[0]
        else:
            return None, f"Arquivo JSON de credenciais não encontrado na pasta {os.getcwd()}"

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(json_credencial)
            firebase_admin.initialize_app(cred)
        return firestore.client(), None
    except Exception as e:
        return None, str(e)

db, erro_firebase = inicializar_firebase()

def gerar_codigo_aula():
    return f"STP-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

def carregar_configuracoes_usuario(usuario):
    configs = {
        "api_key": "AIzaSyBpfGI8Z75Qe6Mtnd5yjmJNGaEUJ6Xg6B8",
        "nivel_dificuldade": "Médio / Intermediário",
        "qtd_slides": 6,
        "qtd_questoes": 8,
        "formato_questoes": "Misturar todos os formatos (25% cada)",
        "escola_unidade": "SENAI Sorriso"
    }
    if db is not None and usuario:
        try:
            doc = db.collection('configuracoes_professores').document(usuario.lower()).get()
            if doc.exists:
                dados = doc.to_dict()
                configs["api_key"] = dados.get("api_key", configs["api_key"])
                configs["nivel_dificuldade"] = dados.get("nivel_dificuldade", configs["nivel_dificuldade"])
                configs["qtd_slides"] = dados.get("qtd_slides", configs["qtd_slides"])
                configs["qtd_questoes"] = dados.get("qtd_questoes", configs["qtd_questoes"])
                configs["formato_questoes"] = dados.get("formato_questoes", configs["formato_questoes"])
                configs["escola_unidade"] = dados.get("escola_unidade", configs["escola_unidade"])
        except Exception as e:
            st.error(f"Erro ao carregar configurações do usuário: {e}")
    return configs

def salvar_configuracoes_usuario(usuario, api_key, nivel_dificuldade, qtd_slides, qtd_questoes, formato_questoes, escola_unidade):
    if db is not None and usuario:
        try:
            db.collection('configuracoes_professores').document(usuario.lower()).set({
                "usuario": usuario,
                "api_key": api_key,
                "nivel_dificuldade": nivel_dificuldade,
                "qtd_slides": qtd_slides,
                "qtd_questoes": qtd_questoes,
                "formato_questoes": formato_questoes,
                "escola_unidade": escola_unidade,
                "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }, merge=True)
        except Exception as e:
            st.error(f"Erro ao salvar configurações no Firestore: {e}")

def avaliar_submissao_aluno(pacote_aula, respostas_usuario, api_key):
    questoes = pacote_aula.get('questoes', {})
    total_questoes = 0
    acertos = 0
    erros = 0
    em_branco = 0
    detalhamento = []

    if questoes.get('multipla_escolha'):
        for idx, q in enumerate(questoes['multipla_escolha']):
            total_questoes += 1
            resp_aluno = respostas_usuario.get(f"mc_{idx}", None)
            correta_idx = q.get('correta', 0)
            opcoes = q.get('opcoes', [])
            texto_correto = opcoes[correta_idx] if correta_idx < len(opcoes) else ""

            if not resp_aluno:
                em_branco += 1
                detalhamento.append({"tipo": "Múltipla Escolha", "pergunta": q.get('pergunta'), "status": "EM_BRANCO", "resposta": "Não respondida", "gabarito": texto_correto, "feedback": f"Você deixou esta questão em branco. A resposta correta era: {texto_correto}. {q.get('feedback', '')}"})
            elif resp_aluno == texto_correto or resp_aluno.startswith(f"{['A','B','C','D','E'][correta_idx]})"):
                acertos += 1
                detalhamento.append({"tipo": "Múltipla Escolha", "pergunta": q.get('pergunta'), "status": "CORRETO", "resposta": resp_aluno, "gabarito": texto_correto, "feedback": f"Parabéns! Resposta correta. {q.get('feedback', '')}"})
            else:
                erros += 1
                detalhamento.append({"tipo": "Múltipla Escolha", "pergunta": q.get('pergunta'), "status": "ERRADO", "resposta": resp_aluno, "gabarito": texto_correto, "feedback": f"Incorreto. Sua escolha foi '{resp_aluno}', mas a alternativa correta é '{texto_correto}'. {q.get('feedback', '')}"})

    if questoes.get('verdadeiro_falso'):
        for idx, q in enumerate(questoes['verdadeiro_falso']):
            total_questoes += 1
            resp_aluno = respostas_usuario.get(f"vf_{idx}", {})
            itens = q.get('itens', [])
            
            if not resp_aluno:
                em_branco += 1
                detalhamento.append({"tipo": "Verdadeiro ou Falso", "pergunta": q.get('enunciado'), "status": "EM_BRANCO", "resposta": "Não respondida", "gabarito": "Avaliação de Itens V/F", "feedback": f"Questão não respondida. {q.get('feedback', '')}"})
            else:
                acertos_item = 0
                total_itens = len(itens) if itens else 1
                if itens:
                    for it_idx, item in enumerate(itens):
                        val_aluno = resp_aluno.get(f"item_{it_idx}") if isinstance(resp_aluno, dict) else None
                        if val_aluno == item.get('gabarito'):
                            acertos_item += 1
                    
                    if acertos_item == total_itens:
                        acertos += 1
                        detalhamento.append({"tipo": "Verdadeiro ou Falso", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": f"Acertou {acertos_item}/{total_itens} itens", "gabarito": "Todas afirmativas corretas", "feedback": f"Excelente! Você analisou todas as afirmativas corretamente. {q.get('feedback', '')}"})
                    elif acertos_item >= (total_itens / 2):
                        acertos += 0.5
                        detalhamento.append({"tipo": "Verdadeiro ou Falso", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": f"Acertou {acertos_item}/{total_itens} itens", "gabarito": "Parcialmente correto", "feedback": f"Você acertou a maioria dos itens ({acertos_item}/{total_itens}). Revise as afirmativas marcadas erroneamente."})
                    else:
                        erros += 1
                        detalhamento.append({"tipo": "Verdadeiro ou Falso", "pergunta": q.get('enunciado'), "status": "ERRADO", "resposta": f"Acertou apenas {acertos_item}/{total_itens} itens", "gabarito": "Ajuste de afirmativas necessário", "feedback": f"Atenção: Você errou a maioria das afirmativas. {q.get('feedback', '')}"})

    if questoes.get('lacunas'):
        for idx, q in enumerate(questoes['lacunas']):
            total_questoes += 1
            resp_aluno = respostas_usuario.get(f"lac_{idx}", "").strip()
            gabarito = q.get('resposta', '').strip()

            if not resp_aluno:
                em_branco += 1
                detalhamento.append({"tipo": "Lacuna", "pergunta": q.get('enunciado'), "status": "EM_BRANCO", "resposta": "Em branco", "gabarito": gabarito, "feedback": f"Deixou em branco. A palavra correta era: '{gabarito}'."})
            elif resp_aluno.lower() == gabarito.lower():
                acertos += 1
                detalhamento.append({"tipo": "Lacuna", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": resp_aluno, "gabarito": gabarito, "feedback": f"Correto! A lacuna foi preenchida perfeitamente com '{gabarito}'."})
            else:
                erros += 1
                detalhamento.append({"tipo": "Lacuna", "pergunta": q.get('enunciado'), "status": "ERRADO", "resposta": resp_aluno, "gabarito": gabarito, "feedback": f"Incorreto. Você preencheu '{resp_aluno}', mas o termo correto era '{gabarito}'."})

    if questoes.get('dissertativas'):
        for idx, q in enumerate(questoes['dissertativas']):
            total_questoes += 1
            resp_aluno = respostas_usuario.get(f"dis_{idx}", "").strip()
            expectativa = q.get('expectativa_resposta', '')

            if not resp_aluno or len(resp_aluno) < 3:
                em_branco += 1
                detalhamento.append({"tipo": "Dissertativa", "pergunta": q.get('enunciado'), "status": "EM_BRANCO", "resposta": "Em branco/Insuficiente", "gabarito": expectativa, "feedback": "Questão não respondida ou resposta muito curta."})
            else:
                if GOOGLE_GENAI_DISPONIVEL and api_key:
                    try:
                        client = genai.Client(api_key=api_key)
                        p_eval = f"""
                        Atue como um professor avaliador.
                        Pergunta: {q.get('enunciado')}
                        Expectativa de Resposta Oficial: {expectativa}
                        Resposta do Aluno: {resp_aluno}
                        
                        Critério: Se a resposta do aluno contiver pelo menos 50% dos conceitos-chave da expectativa, considere CORRETO. Caso contrário, ERRADO.
                        Responda APENAS em formato JSON com:
                        {{"status": "CORRETO" ou "ERRADO", "feedback": "Uma explicação concisa justificando a nota e apontando melhorias."}}
                        """
                        res_eval = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=p_eval,
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        eval_json = json.loads(res_eval.text.strip())
                        if eval_json.get("status") == "CORRETO":
                            acertos += 1
                            detalhamento.append({"tipo": "Dissertativa", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": resp_aluno, "gabarito": expectativa, "feedback": eval_json.get("feedback", "Resposta bem fundamentada!")})
                        else:
                            erros += 1
                            detalhamento.append({"tipo": "Dissertativa", "pergunta": q.get('enunciado'), "status": "ERRADO", "resposta": resp_aluno, "gabarito": expectativa, "feedback": eval_json.get("feedback", "A resposta destoa do gabarito esperado.")})
                    except Exception:
                        acertos += 1
                        detalhamento.append({"tipo": "Dissertativa", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": resp_aluno, "gabarito": expectativa, "feedback": "Resposta entregue com sucesso para análise do professor."})
                else:
                    acertos += 1
                    detalhamento.append({"tipo": "Dissertativa", "pergunta": q.get('enunciado'), "status": "CORRETO", "resposta": resp_aluno, "gabarito": expectativa, "feedback": "Resposta entregue."})

    if total_questoes == 0:
        total_questoes = 1

    nota_final = round((acertos / total_questoes) * 10.0, 1)

    return {
        "nota": nota_final,
        "total_questoes": total_questoes,
        "acertos": acertos,
        "erros": erros,
        "em_branco": em_branco,
        "detalhamento": detalhamento
    }

# Estados globais
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'cursos_db' not in st.session_state:
    st.session_state['cursos_db'] = [
        {
            "id": 1, 
            "nome": "Técnico em Segurança do Trabalho", 
            "alunos": 45, 
            "ucs": [
                {"nome": "Gestão de SST", "temas": ["Análise Preliminar de Risco (APR)", "Investigação de Acidentes"]}
            ]
        },
        {
            "id": 2, 
            "nome": "Técnico em Eletrotécnica", 
            "alunos": 32, 
            "ucs": [
                {"nome": "Instalações Elétricas", "temas": ["NR-10 Básico", "Prontuário de Instalações"]}
            ]
        }
    ]

def buscar_historico_auditoria(usuario_filtro=None):
    if db is not None:
        try:
            docs = db.collection('historico_sessoes').stream()
            lista = [doc.to_dict() for doc in docs]
            if lista:
                df = pd.DataFrame(lista)
                colunas_padrao = ["Data", "Escola/Unidade", "Professor Responsável", "Curso", "Unidade Curricular (UC)", "Código Aula", "Aluno", "Nota (0-10)", "Acertos", "Erros", "Em Branco"]
                
                for col in colunas_padrao:
                    if col not in df.columns:
                        df[col] = "-"
                
                if usuario_filtro and not st.session_state.get('is_admin', False):
                    df = df[df["Professor Responsável"].str.lower() == usuario_filtro.lower()]
                    
                return df[colunas_padrao]
        except Exception as e:
            st.error(f"Erro ao buscar histórico do Firebase: {e}")
    return pd.DataFrame(columns=["Data", "Escola/Unidade", "Professor Responsável", "Curso", "Unidade Curricular (UC)", "Código Aula", "Aluno", "Nota (0-10)", "Acertos", "Erros", "Em Branco"])

# --- VISÃO DO ALUNO ---
def tela_aluno_mobile(codigo_aula):
    renderizar_cabecalho()
    
    if 'flash_msg' in st.session_state:
        st.toast(st.session_state['flash_msg'], icon="🚀")
        del st.session_state['flash_msg']
        
    if f"resultado_aluno_{codigo_aula}" in st.session_state and 'balloons_shown' not in st.session_state:
        st.balloons()
        st.session_state['balloons_shown'] = True
    
    if db is None:
        st.error("Serviço temporariamente indisponível. Conexão com banco de dados ausente.")
        return

    try:
        doc_ref = db.collection('aulas_publicas').document(codigo_aula).get()
        if not doc_ref.exists:
            st.warning(f"⚠️ Aula com o código '{codigo_aula}' não foi encontrada ou expirou.")
            return

        dados = doc_ref.to_dict()
        pacote = dados.get("pacote_aula", {})

        st.success(f"📌 **Aula:** {pacote.get('titulo', 'Conteúdo Didático')}")
        st.caption(f"Professor(a): {dados.get('professor')} | Escola: {dados.get('escola_unidade', 'SENAI')} | Turma: {dados.get('turma')}")

        aba_leitura, aba_avaliacao = st.tabs(["📖 Conteúdo da Aula", "✍️ Avaliação Mobile"])

        with aba_leitura:
            st.markdown(pacote.get("resumo_markdown", "Nenhum resumo disponível."))
            
            st.markdown("### 📊 Material Visual / Slides")
            for s in pacote.get("slides", []):
                with st.expander(f"Slide {s.get('numero')}: {s.get('titulo_slide')}"):
                    st.markdown(s.get("html_visual", ""), unsafe_allow_html=True)
                    st.write("**Pontos Chave:**")
                    for top in s.get("topicos", []):
                        st.write(f"- {top}")

        with aba_avaliacao:
            if f"resultado_aluno_{codigo_aula}" in st.session_state:
                res = st.session_state[f"resultado_aluno_{codigo_aula}"]
                
                st.markdown(f"""
                    <div style="background-color: #0f172a; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; margin-bottom: 20px;">
                        <h2 style="color: #38bdf8; margin: 0;">🏆 Nota Final: {res['nota']} / 10.0</h2>
                        <p style="color: #cbd5e1; font-size: 14px; margin-top: 5px;">
                            Total de Questões: <b>{res['total_questoes']}</b> | 
                            Acertos: <span style="color:#4ade80;">{res['acertos']}</span> | 
                            Erros: <span style="color:#f87171;">{res['erros']}</span> | 
                            Em Branco: <span style="color:#facc15;">{res['em_branco']}</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                st.subheader("💡 Feedback Detalhado das Respostas")
                for item in res['detalhamento']:
                    css_cls = "fb-correto" if item['status'] == "CORRETO" else ("fb-errado" if item['status'] == "ERRADO" else "fb-branco")
                    st.markdown(f"""
                        <div class="{css_cls}">
                            <b>[{item['tipo']}]</b> {item['pergunta']}<br>
                            <b>Sua Resposta:</b> {item['resposta']}<br>
                            <b>Feedback Docente:</b> {item['feedback']}
                        </div>
                    """, unsafe_allow_html=True)

                if st.button("🔄 Refazer Avaliação", use_container_width=True):
                    del st.session_state[f"resultado_aluno_{codigo_aula}"]
                    if 'balloons_shown' in st.session_state:
                        del st.session_state['balloons_shown']
                    st.rerun()

            else:
                st.subheader("📝 Responder Avaliação")
                questoes = pacote.get("questoes", {})
                
                with st.form(key=f"form_aluno_{codigo_aula}"):
                    nome_aluno = st.text_input("Seu Nome Completo:")
                    respostas = {}

                    if questoes.get('multipla_escolha'):
                        st.markdown("#### 🔘 Múltipla Escolha")
                        for idx, q in enumerate(questoes['multipla_escolha']):
                            st.write(f"**{idx+1}. {q.get('pergunta')}**")
                            opcoes = q.get('opcoes', [])
                            respostas[f"mc_{idx}"] = st.radio(f"Selecione a resposta para Q{idx+1}:", opcoes, key=f"q_mc_{idx}", index=None)

                    if questoes.get('verdadeiro_falso'):
                        st.markdown("#### ⚖️ Verdadeiro ou Falso")
                        for idx, q in enumerate(questoes['verdadeiro_falso']):
                            st.write(f"**{idx+1}. {q.get('enunciado')}**")
                            itens = q.get('itens', [])
                            respostas[f"vf_{idx}"] = {}
                            if itens:
                                for it_idx, item in enumerate(itens):
                                    st.write(f"&nbsp;&nbsp;*{item.get('texto_afirmativa', f'Afirmativa {it_idx+1}')}*")
                                    respostas[f"vf_{idx}"][f"item_{it_idx}"] = st.radio(
                                        f"Afirmativa {it_idx+1} de Q{idx+1}:", 
                                        ["V", "F"], 
                                        key=f"q_vf_{idx}_it_{it_idx}",
                                        index=None
                                    )

                    if questoes.get('lacunas'):
                        st.markdown("#### ✍️ Preencha a Lacuna")
                        for idx, q in enumerate(questoes['lacunas']):
                            st.write(f"**{idx+1}. {q.get('enunciado')}**")
                            respostas[f"lac_{idx}"] = st.text_input(f"Sua resposta para a lacuna {idx+1}:", key=f"q_lac_{idx}")

                    if questoes.get('dissertativas'):
                        st.markdown("#### 📝 Questões Dissertativas")
                        for idx, q in enumerate(questoes['dissertativas']):
                            st.write(f"**{idx+1}. {q.get('enunciado')}**")
                            respostas[f"dis_{idx}"] = st.text_area(f"Sua resposta para a questão {idx+1}:", key=f"q_dis_{idx}")

                    btn_enviar = st.form_submit_button("🚀 Enviar Respostas e Calcular Nota", type="primary", use_container_width=True)

                    if btn_enviar:
                        if not nome_aluno:
                            st.warning("Preencha seu nome completo para confirmar o envio.")
                        else:
                            api_k = dados.get("api_key", "AIzaSyBpfGI8Z75Qe6Mtnd5yjmJNGaEUJ6Xg6B8")
                            resultado = avaliar_submissao_aluno(pacote, respostas, api_k)
                            
                            submissao = {
                                "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                "Escola/Unidade": dados.get("escola_unidade", "SENAI"),
                                "Professor Responsável": dados.get("professor", "Stepherson"),
                                "Curso": dados.get("turma", "").split(" > ")[0] if " > " in dados.get("turma", "") else dados.get("turma"),
                                "Unidade Curricular (UC)": dados.get("turma", "").split(" > ")[1] if " > " in dados.get("turma", "") else dados.get("turma"),
                                "Código Aula": codigo_aula,
                                "Aluno": nome_aluno,
                                "Nota (0-10)": resultado["nota"],
                                "Acertos": resultado["acertos"],
                                "Erros": resultado["erros"],
                                "Em Branco": resultado["em_branco"],
                                "Respostas Brutas": respostas
                            }
                            
                            db.collection('historico_sessoes').add(submissao)
                            db.collection('aulas_publicas').document(codigo_aula).collection('respostas_alunos').add(submissao)
                            
                            st.session_state[f"resultado_aluno_{codigo_aula}"] = resultado
                            st.session_state['flash_msg'] = "Avaliação enviada com sucesso!"
                            st.rerun()

    except Exception as e:
        st.error(f"Erro ao carregar a aula no celular: {e}")


# --- TELA DE LOGIN DOCENTE ---
def tela_login():
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        caminho_logo = obter_caminho_logo()
        if caminho_logo:
            try:
                with open(caminho_logo, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                mime_type = "image/jpeg" if caminho_logo.lower().endswith(('.jpg', '.jpeg')) else "image/png"
                st.markdown(f'''
                    <div style="text-align: center; margin-bottom: 30px;">
                        <img src="data:{mime_type};base64,{encoded_string}" style="height: 190px; max-width: 100%; object-fit: contain;">
                    </div>
                ''', unsafe_allow_html=True)
            except:
                st.markdown("<h1 style='text-align: center; color: #38bdf8; font-size: 50px; margin-bottom: 30px;'>🎓 STEP EDUCA</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #38bdf8; font-size: 50px; margin-bottom: 30px;'>🎓 STEP EDUCA</h1>", unsafe_allow_html=True)

        with st.form("form_login_docente", clear_on_submit=False):
            st.markdown("""
                <h2 style='text-align: center; color: #ffffff; letter-spacing: 2px; font-weight: 700; margin-top: 0px; margin-bottom: 25px; font-size: 28px;'>
                    DOCENTE
                </h2>
            """, unsafe_allow_html=True)
            
            usuario = st.text_input("Seu Usuário / Nome (Ex: Stepherson)", placeholder="Digite seu usuário...")
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")

            if btn_entrar:
                if usuario.strip():
                    if usuario.strip() == "Stepherson_adm" and senha == "SXdcfvgb01!":
                        st.session_state['is_admin'] = True
                    else:
                        st.session_state['is_admin'] = False

                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = usuario.strip()
                    
                    user_configs = carregar_configuracoes_usuario(usuario.strip())
                    st.session_state['user_api_key'] = user_configs["api_key"]
                    st.session_state['user_nivel_dificuldade'] = user_configs["nivel_dificuldade"]
                    st.session_state['user_qtd_slides'] = user_configs["qtd_slides"]
                    st.session_state['user_qtd_questoes'] = user_configs["qtd_questoes"]
                    st.session_state['user_formato_questoes'] = user_configs["formato_questoes"]
                    st.session_state['user_escola_unidade'] = user_configs["escola_unidade"]
                    
                    st.session_state['flash_msg'] = f"👋 Bem-vindo(a) ao sistema, {usuario.strip()}!"
                    st.rerun()
                else:
                    st.warning("Por favor, informe seu nome para continuar.")
            
            st.markdown("""
                <div style='text-align: center; margin-top: 25px; color: #ffffff; font-style: italic; font-size: 16px; font-weight: 500; letter-spacing: 0.5px;'>
                    De professor para professor
                </div>
            """, unsafe_allow_html=True)

def tela_dashboard():
    st.header("Gerenciamento Curricular")
    st.write("Cadastre, edite ou exclua Cursos, Unidades Curriculares (UCs) e Temas.")
    st.divider()
    
    aba_cadastrar, aba_editar, aba_excluir = st.tabs(["➕ Novo Cadastro", "✏️ Editar Estrutura", "🗑️ Excluir Estrutura"])

    with aba_cadastrar:
        st.subheader("Cadastrar Novo Elemento")
        tipo_cadastro = st.radio("O que você deseja cadastrar?", ["Nova UC/Tema em Curso Existente", "Novo Curso"], horizontal=True)

        if tipo_cadastro == "Novo Curso":
            with st.container(border=True):
                nome_novo_curso = st.text_input("Nome do Novo Curso", placeholder="Ex: Técnico em Automação Industrial")
                qtd_alunos = st.number_input("Quantidade Inicial de Alunos", min_value=0, value=30)
                btn_salvar_curso = st.button("Salvar Novo Curso", type="primary")

                if btn_salvar_curso:
                    if nome_novo_curso.strip():
                        novo_id = max([c["id"] for c in st.session_state['cursos_db']], default=0) + 1
                        st.session_state['cursos_db'].append({
                            "id": novo_id,
                            "nome": nome_novo_curso.strip(),
                            "alunos": qtd_alunos,
                            "ucs": []
                        })
                        st.session_state['flash_msg'] = f"✅ Curso '{nome_novo_curso}' cadastrado com sucesso!"
                        st.rerun()
                    else:
                        st.warning("Preencha o nome do curso.")

        else:
            if not st.session_state['cursos_db']:
                st.info("Nenhum curso cadastrado. Crie um curso primeiro!")
            else:
                with st.container(border=True):
                    col_c1, col_c2, col_c3 = st.columns(3)
                    with col_c1:
                        curso_escolhido = st.selectbox("Selecione o Curso", [c["nome"] for c in st.session_state['cursos_db']], key="cad_curso_sel")
                    with col_c2:
                        nova_uc = st.text_input("Nome da Nova UC", placeholder="Ex: Higiene Ocupacional", key="cad_nova_uc")
                    with col_c3:
                        novo_tema = st.text_input("Tema Principal", placeholder="Ex: Limites de Tolerância", key="cad_novo_tema")
                    
                    if st.button("Salvar UC / Tema", type="primary"):
                        if nova_uc and novo_tema:
                            for c in st.session_state['cursos_db']:
                                if c["nome"] == curso_escolhido:
                                    uc_existente = next((u for u in c["ucs"] if u["nome"] == nova_uc), None)
                                    if uc_existente:
                                        if novo_tema not in uc_existente["temas"]:
                                            uc_existente["temas"].append(novo_tema)
                                    else:
                                        c["ucs"].append({"nome": nova_uc, "temas": [novo_tema]})
                            st.session_state['flash_msg'] = f"✅ UC '{nova_uc}' e tema '{novo_tema}' salvos com sucesso no curso {curso_escolhido}!"
                            st.rerun()
                        else:
                            st.warning("Preencha a UC e o Tema para salvar.")

    with aba_editar:
        st.subheader("Editar Nomes de Cursos, UCs ou Temas")
        if not st.session_state['cursos_db']:
            st.info("Nenhum curso disponível para edição.")
        else:
            tipo_edicao = st.radio("O que deseja editar?", ["Nome do Curso", "Nome de uma UC", "Nome de um Tema"], horizontal=True)
            
            with st.container(border=True):
                if tipo_edicao == "Nome do Curso":
                    curso_edit = st.selectbox("Selecione o Curso a Editar", [c["nome"] for c in st.session_state['cursos_db']], key="edit_c_sel")
                    novo_nome_c = st.text_input("Novo Nome do Curso", value=curso_edit)
                    if st.button("Atualizar Nome do Curso", type="primary"):
                        for c in st.session_state['cursos_db']:
                            if c["nome"] == curso_edit:
                                c["nome"] = novo_nome_c.strip()
                        st.session_state['flash_msg'] = "✅ Nome do Curso atualizado com sucesso!"
                        st.rerun()

                elif tipo_edicao == "Nome de uma UC":
                    curso_edit = st.selectbox("Selecione o Curso", [c["nome"] for c in st.session_state['cursos_db']], key="edit_uc_c_sel")
                    curso_obj = next((c for c in st.session_state['cursos_db'] if c["nome"] == curso_edit), None)
                    
                    if curso_obj and curso_obj["ucs"]:
                        uc_edit = st.selectbox("Selecione a UC a Editar", [u["nome"] for u in curso_obj["ucs"]], key="edit_uc_sel")
                        novo_nome_uc = st.text_input("Novo Nome da UC", value=uc_edit)
                        if st.button("Atualizar Nome da UC", type="primary"):
                            for u in curso_obj["ucs"]:
                                if u["nome"] == uc_edit:
                                    u["nome"] = novo_nome_uc.strip()
                            st.session_state['flash_msg'] = "✅ Nome da UC atualizado com sucesso!"
                            st.rerun()
                    else:
                        st.warning("Este curso não possui UCs cadastradas.")

                elif tipo_edicao == "Nome de um Tema":
                    curso_edit = st.selectbox("Selecione o Curso", [c["nome"] for c in st.session_state['cursos_db']], key="edit_t_c_sel")
                    curso_obj = next((c for c in st.session_state['cursos_db'] if c["nome"] == curso_edit), None)
                    
                    if curso_obj and curso_obj["ucs"]:
                        uc_edit = st.selectbox("Selecione a UC", [u["nome"] for u in curso_obj["ucs"]], key="edit_t_uc_sel")
                        uc_obj = next((u for u in curso_obj["ucs"] if u["nome"] == uc_edit), None)
                        
                        if uc_obj and uc_obj["temas"]:
                            tema_edit = st.selectbox("Selecione o Tema a Editar", uc_obj["temas"], key="edit_t_sel")
                            novo_nome_tema = st.text_input("Novo Nome do Tema", value=tema_edit)
                            if st.button("Atualizar Nome do Tema", type="primary"):
                                idx_t = uc_obj["temas"].index(tema_edit)
                                uc_obj["temas"][idx_t] = novo_nome_tema.strip()
                                st.session_state['flash_msg'] = "✅ Tema atualizado com sucesso!"
                                st.rerun()
                        else:
                            st.warning("Esta UC não possui temas cadastrados.")

    with aba_excluir:
        st.subheader("Excluir Cursos, UCs ou Temas")
        if not st.session_state['cursos_db']:
            st.info("Nenhum curso disponível para exclusão.")
        else:
            tipo_del = st.radio("O que deseja excluir?", ["Curso Inteiro", "Uma UC específica", "Um Tema específico"], horizontal=True)
            
            with st.container(border=True):
                if tipo_del == "Curso Inteiro":
                    curso_del = st.selectbox("Selecione o Curso para EXCLUIR", [c["nome"] for c in st.session_state['cursos_db']], key="del_c_sel")
                    st.error(f"⚠️ Atenção: Excluir o curso '{curso_del}' removerá todas as suas UCs e temas vinculados.")
                    if st.button("🚨 Confirmar Exclusão do Curso", type="primary"):
                        st.session_state['cursos_db'] = [c for c in st.session_state['cursos_db'] if c["nome"] != curso_del]
                        st.session_state['flash_msg'] = "🗑️ Curso removido com sucesso!"
                        st.rerun()

                elif tipo_del == "Uma UC específica":
                    curso_del = st.selectbox("Selecione o Curso", [c["nome"] for c in st.session_state['cursos_db']], key="del_uc_c_sel")
                    curso_obj = next((c for c in st.session_state['cursos_db'] if c["nome"] == curso_del), None)
                    
                    if curso_obj and curso_obj["ucs"]:
                        uc_del = st.selectbox("Selecione a UC para EXCLUIR", [u["nome"] for u in curso_obj["ucs"]], key="del_uc_sel")
                        if st.button("🚨 Excluir UC Selecionada", type="primary"):
                            curso_obj["ucs"] = [u for u in curso_obj["ucs"] if u["nome"] != uc_del]
                            st.session_state['flash_msg'] = "🗑️ UC removida com sucesso!"
                            st.rerun()
                    else:
                        st.info("Sem UCs neste curso.")

                elif tipo_del == "Um Tema específico":
                    curso_del = st.selectbox("Selecione o Curso", [c["nome"] for c in st.session_state['cursos_db']], key="del_t_c_sel")
                    curso_obj = next((c for c in st.session_state['cursos_db'] if c["nome"] == curso_del), None)
                    
                    if curso_obj and curso_obj["ucs"]:
                        uc_del = st.selectbox("Selecione a UC", [u["nome"] for u in curso_obj["ucs"]], key="del_t_uc_sel")
                        uc_obj = next((u for u in curso_obj["ucs"] if u["nome"] == uc_del), None)
                        
                        if uc_obj and uc_obj["temas"]:
                            tema_del = st.selectbox("Selecione o Tema para EXCLUIR", uc_obj["temas"], key="del_t_sel")
                            if st.button("🚨 Excluir Tema Selecionado", type="primary"):
                                uc_obj["temas"].remove(tema_del)
                                st.session_state['flash_msg'] = "🗑️ Tema removido com sucesso!"
                                st.rerun()
                        else:
                            st.info("Sem temas nesta UC.")

    st.divider()

    st.subheader("📚 Meus Cursos e UCs Estruturadas")
    col1, col2 = st.columns(2)
    
    for idx, curso in enumerate(st.session_state['cursos_db']):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"""
                <div class="card-curso">
                    <h3 style='margin:0; color:#ef4444;'>{curso['nome']}</h3>
                    <p style='color:#94a3b8; margin-top:5px;'>{len(curso['ucs'])} UCs cadastradas | {curso['alunos']} Alunos ativos</p>
                </div>
            """, unsafe_allow_html=True)
            with st.expander(f"Ver grade curricular de {curso['nome']}"):
                if not curso["ucs"]:
                    st.caption("Nenhuma UC cadastrada ainda.")
                for uc in curso["ucs"]:
                    st.markdown(f"📁 **UC: {uc['nome']}**")
                    for t in uc["temas"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;— 📄 *Tema:* {t}")

def tela_fabrica_aulas():
    st.markdown("## 🧠 Fábrica de Aulas (Ensino Técnico / Médio)")
    st.write("Gere teoria, slides prontos e disponibilize o link de acesso direto aos alunos.")
    
    usuario_atual = st.session_state.get('user_name', '')
    is_admin = st.session_state.get('is_admin', False)
    
    api_key_salva = st.session_state.get('user_api_key', "AIzaSyBpfGI8Z75Qe6Mtnd5yjmJNGaEUJ6Xg6B8")
    nivel_salvo = st.session_state.get('user_nivel_dificuldade', "Médio / Intermediário")
    qtd_slides_salva = st.session_state.get('user_qtd_slides', 6)
    qtd_questoes_salva = st.session_state.get('user_qtd_questoes', 8)
    formato_questoes_salvo = st.session_state.get('user_formato_questoes', "Misturar todos os formatos (25% cada)")
    escola_unidade_salva = st.session_state.get('user_escola_unidade', "SENAI Sorriso")
    
    opcoes_niveis = ["Fácil / Introdutório", "Médio / Intermediário", "Difícil / Avançado"]
    index_nivel = opcoes_niveis.index(nivel_salvo) if nivel_salvo in opcoes_niveis else 1

    opcoes_formatos = [
        "Somente Múltipla Escolha (Objetiva - 5 opções, 1 correta)",
        "Somente Verdadeiro ou Falso (5 alternativas por questão)",
        "Somente Preencher Lacunas",
        "Somente Questões Dissertativas",
        "Misturar todos os formatos (25% cada)"
    ]
    index_formato = opcoes_formatos.index(formato_questoes_salvo) if formato_questoes_salvo in opcoes_formatos else 4

    if is_admin:
        api_key = st.text_input("🔑 Chave da API do Gemini (Acesso Restrito ao Administrador):", type="password", value=api_key_salva)
    else:
        api_key = api_key_salva

    lista_ucs_disponiveis = []
    for c in st.session_state['cursos_db']:
        for uc in c["ucs"]:
            for tema in uc["temas"]:
                lista_ucs_disponiveis.append(f"{c['nome']} > {uc['nome']} > {tema}")

    with st.container(border=True):
        col_esc1, col_esc2 = st.columns([2, 1])
        with col_esc1:
            uc_selecionada = st.selectbox("Vincular a qual Unidade Curricular e Tema?", lista_ucs_disponiveis if lista_ucs_disponiveis else ["Gestão de SST > Análise de Riscos"])
        with col_esc2:
            escola_unidade = st.text_input("🏫 Escola / Unidade de Atuação:", value=escola_unidade_salva, placeholder="Ex: SENAI Sorriso / Autoescola Dudu")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            nivel_dificuldade = st.selectbox(
                "🎯 Nível de Dificuldade da Aula:",
                opcoes_niveis,
                index=index_nivel,
                help="Define o rigor técnico e profundidade dos materiais."
            )
        with col_p2:
            qtd_slides = st.number_input(
                "📊 Quantidade de Slides:",
                min_value=3,
                max_value=20,
                value=int(qtd_slides_salva),
                step=1
            )
        with col_p3:
            qtd_questoes = st.number_input(
                "📝 Quantidade de Questões:",
                min_value=1,
                max_value=40,
                value=int(qtd_questoes_salva),
                step=1
            )

        formato_questoes = st.selectbox(
            "✍️ Formato das Questões da Avaliação:",
            opcoes_formatos,
            index=index_formato,
            help="Escolha o tipo de questão desejado ou opte pela distribuição equilibrada (25% para cada formato)."
        )

        tema_livre = st.text_area("Descreva ou ajuste o tema da aula:", value=uc_selecionada.split(" > ")[-1] if uc_selecionada else "Gestão de SST")
        
        gerar = st.button("✨ Gerar Pacote Completo e Link Mobile (IA)", type="primary", use_container_width=True)
        
        if gerar:
            if not api_key:
                st.error("⚠️ Insira a chave da API.")
            elif not tema_livre:
                st.warning("⚠️ Descreva o tema da aula.")
            elif not GOOGLE_GENAI_DISPONIVEL:
                st.error("⚠️ Biblioteca 'google-genai' não instalada.")
            else:
                st.session_state['user_api_key'] = api_key
                st.session_state['user_nivel_dificuldade'] = nivel_dificuldade
                st.session_state['user_qtd_slides'] = qtd_slides
                st.session_state['user_qtd_questoes'] = qtd_questoes
                st.session_state['user_formato_questoes'] = formato_questoes
                st.session_state['user_escola_unidade'] = escola_unidade
                
                salvar_configuracoes_usuario(usuario_atual, api_key, nivel_dificuldade, qtd_slides, qtd_questoes, formato_questoes, escola_unidade)
                st.toast("💾 Preferências do professor salvas!", icon="✅")

                if "Somente Múltipla Escolha" in formato_questoes:
                    regra_questoes = f"Gere exatamente {qtd_questoes} questões do tipo 'multipla_escolha'. Cada questão deve conter exatamente 5 opções ('A)', 'B)', 'C)', 'D)', 'E)'), com apenas 1 correta. As demais listas ('verdadeiro_falso', 'lacunas', 'dissertativas') devem vir VAZIAS []."
                elif "Somente Verdadeiro ou Falso" in formato_questoes:
                    regra_questoes = f"Gere exatamente {qtd_questoes} questões do tipo 'verdadeiro_falso'. Cada questão deve ter um enunciado geral e conter EXATAMENTE 5 itens/afirmativas individuais (cada item com 'texto_afirmativa' e 'gabarito': 'V' ou 'F'). As demais listas de questões devem vir VAZIAS []."
                elif "Somente Preencher Lacunas" in formato_questoes:
                    regra_questoes = f"Gere exatamente {qtd_questoes} questões do tipo 'lacunas'. As demais listas de questões devem vir VAZIAS []."
                elif "Somente Questões Dissertativas" in formato_questoes:
                    regra_questoes = f"Gere exatamente {qtd_questoes} questões do tipo 'dissertativas'. As demais listas de questões devem vir VAZIAS []."
                else:
                    q_cada = max(1, math.floor(qtd_questoes * 0.25))
                    regra_questoes = f"""
                    O professor optou por misturar os formatos com 25% cada.
                    Gere exatamente:
                    - {q_cada} questões de 'multipla_escolha' (cada uma com 5 opções A, B, C, D, E e 1 correta);
                    - {q_cada} questões de 'verdadeiro_falso' (cada uma com 5 itens/afirmativas V ou F);
                    - {q_cada} questões de 'lacunas';
                    - {q_cada} questões de 'dissertativas'.
                    Total aproximado de questões: {q_cada * 4}.
                    """

                with st.spinner(f"🧠 Ativando Gem Docente... Gerando pacote para {escola_unidade} no nível [{nivel_dificuldade}]..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        Atue como um designer educacional sênior. Crie um pacote de aula completo sobre o tema: '{tema_livre}'.
                        
                        NÍVEL DE DIFICULDADE EXIGIDO: {nivel_dificuldade}.
                        QUANTIDADE DE SLIDES: Gere EXATAMENTE {qtd_slides} slides didáticos com HTML visual formatado, objetivo e conciso para apresentação.
                        
                        REGRAS PEDAGÓGICAS PARA AVALIAÇÃO:
                        {regra_questoes}
                        
                        Você DEVE retornar APENAS um objeto JSON válido rigorosamente formatado, sem markdown extra ou explicações fora do JSON.
                        Mantenha o HTML dos slides limpo e enxuto para otimizar o tamanho da resposta.
                        
                        Estrutura JSON Obrigatória:
                        {{
                            "titulo": "Título Profissional da Aula",
                            "resumo_markdown": "Resumo estruturado em markdown adaptado ao nível {nivel_dificuldade} com introdução e conceitos para o aluno estudar.",
                            "slides": [
                                {{
                                    "numero": 1,
                                    "titulo_slide": "Título do Slide",
                                    "topicos": ["Tópico 1", "Tópico 2", "Tópico 3"],
                                    "html_visual": "<div style='background:#003b66; color:white; padding:20px; border-radius:12px; text-align:center;'><h2>Slide 1</h2><p>Conteúdo didático</p></div>"
                                }}
                            ],
                            "questoes": {{
                                "multipla_escolha": [
                                    {{
                                        "pergunta": "Texto da questão?",
                                        "opcoes": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                                        "correta": 0,
                                        "feedback": "Explicação pedagógica."
                                    }}
                                ],
                                "verdadeiro_falso": [
                                    {{
                                        "enunciado": "Enunciado principal do contexto?",
                                        "itens": [
                                            {{"texto_afirmativa": "Afirmativa 1...", "gabarito": "V"}},
                                            {{"texto_afirmativa": "Afirmativa 2...", "gabarito": "F"}},
                                            {{"texto_afirmativa": "Afirmativa 3...", "gabarito": "V"}},
                                            {{"texto_afirmativa": "Afirmativa 4...", "gabarito": "F"}},
                                            {{"texto_afirmativa": "Afirmativa 5...", "gabarito": "V"}}
                                        ],
                                        "feedback": "Justificativa pedagógica."
                                    }}
                                ],
                                "lacunas": [
                                    {{
                                        "enunciado": "Texto com a palavra ________ faltando.",
                                        "resposta": "palavra",
                                        "feedback": "Justificativa."
                                    }}
                                ],
                                "dissertativas": [
                                    {{
                                        "enunciado": "Pergunta dissertativa?",
                                        "expectativa_resposta": "O aluno deve abordar..."
                                    }}
                                ]
                            }}
                        }}
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )
                        
                        texto_resposta = response.text.strip()
                        
                        try:
                            pacote_aula = json.loads(texto_resposta)
                        except json.JSONDecodeError:
                            st.error("⚠️ A quantidade de itens solicitada gerou uma resposta muito longa. Tente reduzir a quantidade de questões ou slides.")
                            return

                        codigo_aula = gerar_codigo_aula()
                        st.session_state['ultimo_pacote_aula'] = pacote_aula
                        st.session_state['ultimo_codigo_aula'] = codigo_aula
                        
                        if db is not None:
                            try:
                                db.collection('aulas_publicas').document(codigo_aula).set({
                                    "codigo": codigo_aula,
                                    "professor": st.session_state['user_name'],
                                    "escola_unidade": escola_unidade,
                                    "turma": uc_selecionada,
                                    "nivel_dificuldade": nivel_dificuldade,
                                    "api_key": api_key,
                                    "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    "pacote_aula": pacote_aula
                                })
                            except Exception as ex:
                                st.error(f"❌ Erro ao sincronizar Firestore: {ex}")
                                
                        st.session_state['flash_msg'] = f"☁️ Aula vinculada ao {escola_unidade} gerada com sucesso!"
                        st.rerun()

                    except Exception as e:
                        st.error(f"Erro na IA: {e}")

        if 'ultimo_pacote_aula' in st.session_state:
            pacote_aula = st.session_state['ultimo_pacote_aula']
            codigo_aula = st.session_state.get('ultimo_codigo_aula', 'STP-DEMO')
            
            st.markdown(f"## 📚 {pacote_aula['titulo']}")
            
            url_aluno = f"https://stepeduca.streamlit.app/?aula={codigo_aula}"
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={url_aluno}"

            st.markdown(f"""
                <div class="link-box">
                    <h3 style="margin:0; color:#ef4444;">📱 Link do Aluno Liberado!</h3>
                    <p style="font-size:14px; color:#cbd5e1; margin:5px 0;">Envie este link para a turma acompanhar pelo smartphone:</p>
                    <code style="font-size:16px; color:#f8fafc; background:#1e293b; padding:6px 12px; border-radius:6px;">{url_aluno}</code>
                    <br><br>
                    <img src="{qr_code_url}" alt="QR Code da Aula" style="border-radius:10px; border:2px solid #334155;"/>
                    <p style="font-size:12px; color:#94a3b8; margin-top:5px;">Código Único: <b>{codigo_aula}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            aba_aluno, aba_slides, aba_questoes, aba_mobile, aba_gabarito = st.tabs([
                "📖 Leitura do Aluno", 
                "📊 Slides Prontos (Apresentação)", 
                "📝 Caderno de Questões (Aluno)",
                "📱 Simulação App do Aluno", 
                "🔑 Gabarito Docente"
            ])
            
            with aba_aluno:
                st.markdown(pacote_aula['resumo_markdown'])
                
            with aba_slides:
                st.info("Apresentação em HTML corporativo para projeção:")
                html_completo_slides = f"""<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><title>{pacote_aula['titulo']}</title><script src='https://cdn.tailwindcss.com'></script></head><body class='bg-slate-900 text-white p-10'><h1 class='text-4xl font-bold mb-8 text-blue-400'>Apresentação: {pacote_aula['titulo']}</h1><div class='space-y-12'>"""
                for s in pacote_aula.get('slides', []):
                    html_completo_slides += f"<div class='bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-700'><h2 class='text-2xl font-bold text-amber-400 mb-4'>Slide {s['numero']}: {s['titulo_slide']}</h2>{s['html_visual']}<ul class='mt-4 list-disc pl-5 space-y-2'>"
                    for t in s['topicos']:
                        html_completo_slides += f"<li class='text-slate-300'>{t}</li>"
                    html_completo_slides += "</ul></div>"
                html_completo_slides += "</div></body></html>"

                st.download_button(
                    label="📥 Baixar Apresentação Completa (HTML)",
                    data=html_completo_slides,
                    file_name=f"apresentacao_{codigo_aula}.html",
                    mime="text/html",
                    type="primary"
                )
                
                for s in pacote_aula.get('slides', []):
                    with st.expander(f"Slide {s['numero']}: {s['titulo_slide']}"):
                        st.markdown(s['html_visual'], unsafe_allow_html=True)

            with aba_questoes:
                st.subheader("📝 Caderno de Questões Enviado aos Celulares")
                questoes = pacote_aula.get('questoes', {})
                for k, v in questoes.items():
                    if v:
                        st.markdown(f"### {k.replace('_', ' ').title()}")
                        for i, q in enumerate(v):
                            st.write(f"**{i+1}.** {q.get('pergunta') or q.get('enunciado')}")
                            if k == 'verdadeiro_falso' and q.get('itens'):
                                for sub_i, item in enumerate(q['itens']):
                                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;({sub_i+1}) {item.get('texto_afirmativa')}")

            with aba_mobile:
                st.info("📱 Demonstração visual completa de como o aluno interage via smartphone:")
                
                st.markdown(f"""
                    <div class="mobile-frame-container">
                        <div style="text-align: center; color: #ef4444; border-bottom: 1px solid #1e293b; padding-bottom: 8px; margin-bottom: 12px;">
                            <h3 style="margin: 0;">📱 StepEduca Mobile Demo</h3>
                            <p style="font-size: 11px; color: #94a3b8; margin: 2px 0;">URL: {url_aluno}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                sim_aba_leitura, sim_aba_questoes = st.tabs(["📖 Conteúdo da Aula (Smartphone)", "✍️ Avaliação Mobile (Smartphone)"])

                with sim_aba_leitura:
                    st.markdown(f"#### 📌 {pacote_aula.get('titulo')}")
                    st.markdown(pacote_aula.get('resumo_markdown', 'Nenhum resumo.'))
                    st.divider()
                    st.markdown("##### 📊 Slides de Apoio Visual")
                    for s in pacote_aula.get('slides', []):
                        with st.expander(f"Slide {s.get('numero')}: {s.get('titulo_slide')}"):
                            st.markdown(s.get('html_visual', ''), unsafe_allow_html=True)

                with sim_aba_questoes:
                    st.subheader("📝 Resposta do Aluno em Tempo Real")
                    q_data = pacote_aula.get('questoes', {})
                    
                    if q_data.get('multipla_escolha'):
                        st.markdown("##### 🔘 Múltipla Escolha")
                        for i, q in enumerate(q_data['multipla_escolha']):
                            st.write(f"**Q{i+1}:** {q.get('pergunta')}")
                            st.radio("Selecione:", q.get('opcoes', []), key=f"sim_mc_{i}")

                    if q_data.get('verdadeiro_falso'):
                        st.markdown("##### ⚖️ Verdadeiro ou Falso")
                        for i, q in enumerate(q_data['verdadeiro_falso']):
                            st.write(f"**Q{i+1}:** {q.get('enunciado')}")
                            if q.get('itens'):
                                for sub_i, item in enumerate(q['itens']):
                                    st.radio(f"Item {sub_i+1}: {item.get('texto_afirmativa')}", ["V", "F"], key=f"sim_vf_{i}_{sub_i}")

                    if q_data.get('lacunas'):
                        st.markdown("##### ✍️ Preencha a Lacuna")
                        for i, q in enumerate(q_data['lacunas']):
                            st.write(f"**Q{i+1}:** {q.get('enunciado')}")
                            st.text_input("Resposta:", key=f"sim_lac_{i}")

                    if q_data.get('dissertativas'):
                        st.markdown("##### 📝 Dissertativas")
                        for i, q in enumerate(q_data['dissertativas']):
                            st.write(f"**Q{i+1}:** {q.get('enunciado')}")
                            st.text_area("Sua resposta:", key=f"sim_dis_{i}")

            with aba_gabarito:
                st.subheader("🔑 Gabarito Oficial e Critérios de Correção (Visão Colorida)")
                questoes = pacote_aula.get('questoes', {})

                if questoes.get('multipla_escolha'):
                    st.markdown("### 🔵 Questões de Múltipla Escolha")
                    for i, q in enumerate(questoes['multipla_escolha']):
                        st.markdown(f"""
                            <div class="gab-mc">
                                <b>Q{i+1}:</b> {q.get('pergunta')}<br>
                                <b>Gabarito Correto:</b> Opção de Índice [{q.get('correta')}] ({q.get('opcoes', [''])[q.get('correta', 0)] if q.get('opcoes') else ''})<br>
                                <i>Feedback:</i> {q.get('feedback', '')}
                            </div>
                        """, unsafe_allow_html=True)

                if questoes.get('verdadeiro_falso'):
                    st.markdown("### 🟢 Questões de Verdadeiro ou Falso")
                    for i, q in enumerate(questoes['verdadeiro_falso']):
                        itens_html = ""
                        if q.get('itens'):
                            for sub_i, item in enumerate(q['itens']):
                                itens_html += f"<br>&nbsp;&nbsp;• Item {sub_i+1}: <i>{item.get('texto_afirmativa')}</i> — <b>Gabarito: {item.get('gabarito')}</b>"
                        st.markdown(f"""
                            <div class="gab-vf">
                                <b>Q{i+1}:</b> {q.get('enunciado')}
                                {itens_html}<br>
                                <i>Feedback:</i> {q.get('feedback', '')}
                            </div>
                        """, unsafe_allow_html=True)

                if questoes.get('lacunas'):
                    st.markdown("### 🟠 Questões de Preencher Lacunas")
                    for i, q in enumerate(questoes['lacunas']):
                        st.markdown(f"""
                            <div class="gab-lac">
                                <b>Q{i+1}:</b> {q.get('enunciado')}<br>
                                <b>Gabarito (Palavra-Chave):</b> {q.get('resposta')}<br>
                                <i>Feedback:</i> {q.get('feedback', '')}
                            </div>
                        """, unsafe_allow_html=True)

                if questoes.get('dissertativas'):
                    st.markdown("### 🟣 Questões Dissertativas")
                    for i, q in enumerate(questoes['dissertativas']):
                        st.markdown(f"""
                            <div class="gab-dis">
                                <b>Q{i+1}:</b> {q.get('enunciado')}<br>
                                <b>Expectativa de Resposta (Critérios):</b> {q.get('expectativa_resposta')}
                            </div>
                        """, unsafe_allow_html=True)

# --- NOVO MÓDULO: FÁBRICA KIDS (LETRAMENTO) ---
def tela_fabrica_kids():
    st.markdown("## 🧸 Fábrica Kids (Letramento & Fundamental I)")
    st.write("Crie contações de histórias com voz, ilustrações geradas por IA e atividades pontilhadas para imprimir!")
    
    api_key = st.session_state.get('user_api_key', "AIzaSyBpfGI8Z75Qe6Mtnd5yjmJNGaEUJ6Xg6B8")
    escola_unidade_salva = st.session_state.get('user_escola_unidade', "Escola Municipal")

    if st.session_state.get('is_admin', False):
        api_key = st.text_input("🔑 Chave da API do Gemini (Admin):", type="password", value=api_key)

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            idade_alvo = st.selectbox("Faixa Etária / Ano:", ["Pré-escola", "1º Ano", "2º Ano", "3º Ano", "4º Ano"])
        with col2:
            foco_aula = st.selectbox("Foco Pedagógico:", ["Consciência Fonológica / Alfabeto", "Letramento e Leitura", "Matemática Básica", "Ciências / Regionalidade MS"])
        with col3:
            escola = st.text_input("Escola:", value=escola_unidade_salva)

        tema_kids = st.text_input("Qual o tema da aula?", placeholder="Ex: Animais do Pantanal, Letra C, Higiene Pessoal...")
        
        btn_gerar_kids = st.button("🌟 Criar Magia (Gerar Aula Kids)", type="primary", use_container_width=True)
        
        # Espaço reservado para o painel de loading animado
        loading_placeholder = st.empty()
        
        if btn_gerar_kids:
            if not api_key:
                st.error("⚠️ Insira a chave da API.")
            elif not tema_kids:
                st.warning("⚠️ Escreva o tema da aula para a IA.")
            elif not GOOGLE_GENAI_DISPONIVEL:
                st.error("⚠️ Biblioteca 'google-genai' não instalada.")
            else:
                # PASSO 1: Loading Pedagógico Lúdico (Tempo Estendido para 12s)
                loading_placeholder.markdown("""
                <div style="text-align: center; padding: 50px; background-color: #030712; border-radius: 20px; border: 4px dashed #38bdf8; margin-top: 20px; min-height: 450px; display: flex; flex-direction: column; justify-content: center;">
                    <h2 style="color: #f8fafc; font-size: 38px; margin-bottom: 40px; text-shadow: 2px 2px 5px rgba(0,0,0,0.5);">✨ Hora da Mágica! Vamos ler as vogais bem alto?</h2>
                    <div style="display: flex; justify-content: space-around; font-size: 160px; font-weight: 900; text-shadow: 5px 5px 15px rgba(0,0,0,0.8);">
                        <span style="color:#ef4444; animation: bounce 1s infinite alternate;">A</span>
                        <span style="color:#3b82f6; animation: bounce 1s infinite alternate; animation-delay: 0.2s;">E</span>
                        <span style="color:#22c55e; animation: bounce 1s infinite alternate; animation-delay: 0.4s;">I</span>
                        <span style="color:#eab308; animation: bounce 1s infinite alternate; animation-delay: 0.6s;">O</span>
                        <span style="color:#a855f7; animation: bounce 1s infinite alternate; animation-delay: 0.8s;">U</span>
                    </div>
                    <style>
                        @keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-40px); } }
                    </style>
                </div>
                """, unsafe_allow_html=True)
                
                # Pausa estratégica para a professora interagir com as crianças
                time.sleep(12)
                
                # PASSO 2: Chamada da IA com Blindagem Absoluta nas Imagens
                with st.spinner("🎩 Escrevendo a história e pintando as imagens mágicas..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt_kids = f"""
                        Atue como um pedagogo especialista em alfabetização, letramento e Base Nacional Comum Curricular (BNCC).
                        Crie um material lúdico e formativo para crianças do {idade_alvo}.
                        Tema: '{tema_kids}'. Foco: '{foco_aula}'.
                        IMPORTANTE: Como o público é da região de Mato Grosso do Sul (MS), inclua elementos regionais (fauna, flora, cultura, ex: Arara, Capivara, Tereré, Pantanal) de forma sutil e atrativa se o tema permitir.
                        
                        Retorne EXATAMENTE no formato JSON, rigoroso:
                        {{
                            "titulo": "Título Divertido da Aula",
                            "bncc": ["Código BNCC - Descrição da habilidade"],
                            "letras_foco": ["Letra Principal 1", "Letra Principal 2"], 
                            "historia": [
                                {{
                                    "texto": "Parágrafo curto e lúdico...",
                                    "imagem_prompt": "simple english description max 3 words without punctuation"
                                }},
                                {{
                                    "texto": "Outro parágrafo curto e lúdico...",
                                    "imagem_prompt": "simple english description max 3 words without punctuation"
                                }}
                            ],
                            "palavras_pontilhadas": ["PALAVRA1", "PALAVRA2", "PALAVRA3", "PALAVRA4"],
                            "texto_cursivo": "Uma pequena frase motivacional ou de leitura fácil para as crianças."
                        }}
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_kids,
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        
                        try:
                            pacote_kids = json.loads(response.text.strip())
                            st.session_state['ultimo_pacote_kids'] = pacote_kids
                            st.session_state['escola_kids'] = escola
                            st.session_state['idade_kids'] = idade_alvo
                            st.session_state['flash_msg'] = "🌟 Aula Kids gerada com sucesso!"
                            st.rerun()
                        except json.JSONDecodeError:
                            st.error("⚠️ A IA não retornou um formato válido. Tente novamente.")
                    except Exception as e:
                        st.error(f"Erro na IA: {e}")
                    finally:
                        loading_placeholder.empty()

    if 'ultimo_pacote_kids' in st.session_state:
        pacote = st.session_state['ultimo_pacote_kids']
        
        st.markdown(f"<h2 style='text-align: center; color: #ef4444; font-size: 45px;'>🎈 {pacote.get('titulo', 'Aventura Mágica')}</h2>", unsafe_allow_html=True)
        
        aba_projetor, aba_folhinha, aba_bncc = st.tabs(["📽️ Projetor (Tela Dividida)", "🖨️ Folhinha para Imprimir", "📋 Tabela BNCC"])
        
        with aba_projetor:
            st.info("Atenção Docente: Projete esta tela. O botão de áudio será liberado assim que as imagens terminarem de carregar na tela.")
            
            historia_completa_texto = " ".join([h.get('texto', '') for h in pacote.get('historia', [])])
            
            # Botão de Áudio com atraso de ativação via JavaScript
            audio_html = f"""
                <div style="text-align: center; margin-bottom: 25px;">
                    <button id="btnAudio" onclick="lerHistoria()" disabled style="padding: 15px 35px; font-size: 24px; font-weight: bold; background-color: #475569; color: #94a3b8; border: none; border-radius: 12px; cursor: not-allowed; box-shadow: 0 4px 6px rgba(0,0,0,0.5); transition: 0.5s;">
                        ⏳ Carregando Magia...
                    </button>
                </div>
                <script>
                setTimeout(function() {{
                    var btn = document.getElementById("btnAudio");
                    if(btn) {{
                        btn.disabled = false;
                        btn.style.backgroundColor = "#3b82f6";
                        btn.style.color = "white";
                        btn.style.cursor = "pointer";
                        btn.innerHTML = "▶️ Contar História";
                    }}
                }}, 6000);

                function lerHistoria() {{
                    let texto = "{historia_completa_texto.replace('"', '')}";
                    let fala = new SpeechSynthesisUtterance(texto);
                    fala.lang = 'pt-BR';
                    fala.rate = 0.85; 
                    window.speechSynthesis.speak(fala);
                }}
                </script>
            """
            components.html(audio_html, height=85)
            
            # Tela Dividida: Contação + Ancoragem Visual
            col_historia, col_letras = st.columns([2, 1], gap="large")
            
            with col_historia:
                for i, h in enumerate(pacote.get('historia', [])):
                    with st.container(border=True):
                        # Ultra Filtro de Blindagem para Imagens
                        texto_bruto = h.get('imagem_prompt', 'cute cartoon')
                        # Remove tudo que não for letra ou espaço
                        texto_limpo = re.sub(r'[^a-zA-Z\s]', '', texto_bruto).strip() 
                        palavras = texto_limpo.split()[:3] # Força no máximo 3 palavras limpas
                        texto_curto = " ".join(palavras) + " 3d cartoon"
                        prompt_img = urllib.parse.quote(texto_curto)
                        
                        seed_randomico = random.randint(1, 999999) 
                        url_imagem = f"https://image.pollinations.ai/prompt/{prompt_img}?width=800&height=400&nologo=true&seed={seed_randomico}"
                        
                        st.markdown(f"<img src='{url_imagem}' style='width:100%; border-radius: 8px; margin-bottom: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.4);' alt='Ilustração'>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: center; color: #facc15; line-height: 1.6; font-size: 28px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);'>{h.get('texto')}</h3>", unsafe_allow_html=True)
            
            with col_letras:
                letras_foco = pacote.get('letras_foco', ['A', 'E'])
                html_letras_grandes = ""
                paleta_cores = ["#ef4444", "#3b82f6", "#22c55e", "#eab308", "#a855f7"]
                
                for idx, letra in enumerate(letras_foco):
                    cor = paleta_cores[idx % len(paleta_cores)]
                    html_letras_grandes += f"<span style='color: {cor}; margin: 0 10px; display: inline-block;'>{letra}</span>"
                
                # O painel renderizado via HTML com a classe para ser pego pelo CSS sticky lá em cima
                st.markdown(f"""
                    <div class="painel-letras-sticky">
                        <h3 style='color: #cbd5e1; margin-bottom: 30px; font-size: 26px;'>Letras em Destaque:</h3>
                        <div style='font-size: 180px; font-weight: 900; line-height: 1.1; text-shadow: 6px 6px 0px rgba(255,255,255,0.1), 10px 10px 20px rgba(0,0,0,0.8); animation: pulse-bounce 3s infinite ease-in-out;'>
                            {html_letras_grandes}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        with aba_folhinha:
            st.success("Otimizado para abrir instantaneamente! Clique no botão abaixo para gerar o PDF ou imprimir direto na impressora da escola.")
            
            escola = st.session_state.get('escola_kids', 'Escola Municipal')
            idade = st.session_state.get('idade_kids', '1º Ano')
            prof = st.session_state.get('user_name', 'Professor')
            data_atual = datetime.now().strftime("%d/%m/%Y")
            hora_atual = datetime.now().strftime("%H:%M")
            
            html_preview = f"""
            <div id="area-imprimivel" style="background: white; color: black; padding: 40px; border-radius: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); max-width: 800px; margin: 0 auto; box-sizing: border-box; font-family: Arial, sans-serif;">
                <div class="cabecalho" style="border: 2px solid #000; padding: 15px; border-radius: 8px; margin-bottom: 25px; line-height: 1.8;">
                    <strong>ESCOLA:</strong> {escola}<br>
                    <strong>ALUNO(A):</strong> __________________________________________________________________<br>
                    <strong>PROFESSOR(A):</strong> {prof} &nbsp;&nbsp;&nbsp;&nbsp; <strong>TURMA:</strong> {idade} &nbsp;&nbsp;&nbsp;&nbsp; <strong>DATA:</strong> {data_atual}
                </div>
                
                <div class="titulo-aula" style="text-align: center; font-size: 24px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px;">{pacote.get('titulo')}</div>
                
                <div class="caixa-leitura" style="border: 1px dashed #666; padding: 20px; background-color: #f9f9f9; margin-bottom: 30px; font-size: 18px; line-height: 1.6;">
                    <strong>LEITURA DO DIA:</strong><br><br>
                    {historia_completa_texto}
                </div>
                
                <div class="titulo-sessao" style="font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #000; padding-bottom: 5px;">1. TREINO DE CALIGRAFIA (CUBRA OS PONTILHADOS)</div>
            """
            
            for palavra in pacote.get('palavras_pontilhadas', []):
                html_preview += f'<div class="linha-pontilhada" style="font-family: \'Codystar\', cursive; font-size: 45px; letter-spacing: 5px; color: #777; margin: 10px 0 25px 0; border-bottom: 1px solid #ccc;">{palavra}</div>'
                
            html_preview += f"""
                <div class="titulo-sessao" style="font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #000; padding-bottom: 5px; margin-top: 30px;">2. LEITURA EM LETRA CURSIVA</div>
                <div class="texto-cursivo" style="font-family: 'Dancing Script', cursive; font-size: 35px; color: #000; margin: 20px 0;">{pacote.get('texto_cursivo', 'A educação transforma o mundo.')}</div>
                
                <div class="titulo-sessao" style="font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #000; padding-bottom: 5px; margin-top: 40px;">3. ESPAÇO PARA DESENHO</div>
                <div style="border: 2px solid #000; height: 300px; width: 100%; border-radius: 8px; box-sizing: border-box;">
                    <p style="text-align: center; color: #999; margin-top: 130px;">Desenhe a parte da história que você mais gostou!</p>
                </div>
            </div>

            <!-- Botão de impressão com lógica de Nova Janela Otimizada (Bypass do travamento) -->
            <script>
            function imprimirNovaJanela() {{
                let conteudo = document.getElementById('area-imprimivel').innerHTML;
                let win = window.open('', '_blank');
                win.document.write(`
                    <html>
                    <head>
                        <title>Impressão da Atividade - StepEduca</title>
                        <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Codystar&display=swap" rel="stylesheet">
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 30px; color: #000; box-sizing: border-box; }}
                            .rodape-impressao {{ margin-top: 50px; font-size: 11px; font-style: italic; text-align: center; color: #555; border-top: 1px solid #ccc; padding-top: 10px; }}
                        </style>
                    </head>
                    <body>
                        ${{conteudo}}
                        <div class="rodape-impressao">
                            Impresso em {data_atual} às {hora_atual}. Desenvolvido pelo StepEduca - de professor para professor.
                        </div>
                    </body>
                    </html>
                `);
                win.document.close();
                
                setTimeout(() => {{
                    win.print();
                }}, 1000);
            }}
            </script>
            
            <div style="background-color: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                <button onclick="imprimirNovaJanela()" style="display: block; width: 100%; padding: 15px; font-size: 18px; font-weight: bold; background-color: #ef4444; color: #fff; text-align: center; border: none; border-radius: 8px; cursor: pointer;">
                    🖨️ Imprimir Folhinha Rápida (A4)
                </button>
            </div>
            """
            
            components.html(f"""
                <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Codystar&display=swap" rel="stylesheet">
                {html_preview}
            """, height=1200, scrolling=True)

        with aba_bncc:
            st.subheader("Base Nacional Comum Curricular (BNCC)")
            st.write("Abaixo estão as habilidades e competências trabalhadas neste material, prontas para anexar no seu plano de aula da Secretaria de Educação.")
            for codigo in pacote.get('bncc', []):
                st.info(f"📌 {codigo}")

def tela_sala_aula():
    st.header("📡 Sala de Aula Ao Vivo & Monitoramento de Respostas")
    st.write("Acompanhe o engajamento dos alunos e visualize as entregas da avaliação em tempo real.")
    
    with st.container(border=True):
        codigo_busca = st.text_input("Código da Aula para Monitorar (Ex: STP-9482):", value=st.session_state.get('ultimo_codigo_aula', ''))
        
        if codigo_busca and db is not None:
            try:
                docs = db.collection('aulas_publicas').document(codigo_busca).collection('respostas_alunos').stream()
                lista_respostas = [d.to_dict() for d in docs]
                
                if lista_respostas:
                    st.success(f"📊 {len(lista_respostas)} aluno(s) enviaram a avaliação!")
                    df_resp = pd.DataFrame(lista_respostas)
                    
                    colunas_exibir = ["Data", "Aluno", "Nota (0-10)", "Acertos", "Erros", "Em Branco"]
                    cols = [c for c in colunas_exibir if c in df_resp.columns]
                    st.dataframe(df_resp[cols], use_container_width=True)
                    
                    with st.expander("🔍 Ver detalhamento por aluno"):
                        for r in lista_respostas:
                            st.markdown(f"**Aluno:** {r.get('Aluno')} | **Nota:** {r.get('Nota (0-10)')} ({r.get('Data')})")
                            st.json(r.get('Respostas Brutas', {}))
                else:
                    st.info(f"Nenhuma resposta enviada ainda para o código {codigo_busca}.")
            except Exception as e:
                st.error(f"Erro ao consultar respostas: {e}")

def tela_auditoria():
    st.header("🗄️ Histórico e Relatórios de Notas (Auditoria BD)")
    st.write("Consulte o grid consolidado de entregas dos alunos por Escola, Curso, UC e Professor.")
    
    prof_atual = st.session_state.get('user_name', '')
    df_historico = buscar_historico_auditoria(usuario_filtro=prof_atual)
    
    if df_historico.empty:
        st.info("Nenhum registro de avaliação de alunos encontrado no banco de dados.")
    else:
        with st.container(border=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                escolas_disp = ["Todas"] + list(df_historico["Escola/Unidade"].dropna().unique())
                f_escola = st.selectbox("Filtrar por Escola/Unidade:", escolas_disp)
            with col_f2:
                cursos_disp = ["Todos"] + list(df_historico["Curso"].dropna().unique())
                f_curso = st.selectbox("Filtrar por Curso:", cursos_disp)
            with col_f3:
                ucs_disp = ["Todas"] + list(df_historico["Unidade Curricular (UC)"].dropna().unique())
                f_uc = st.selectbox("Filtrar por UC:", ucs_disp)

            df_filtrado = df_historico.copy()
            if f_escola != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Escola/Unidade"] == f_escola]
            if f_curso != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Curso"] == f_curso]
            if f_uc != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Unidade Curricular (UC)"] == f_uc]

            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            if not df_filtrado.empty and "Nota (0-10)" in df_filtrado.columns:
                try:
                    media_nota = pd.to_numeric(df_filtrado["Nota (0-10)"], errors='coerce').mean()
                    st.metric(label="📊 Média Geral das Turmas Filtradas", value=f"{round(media_nota, 2)} / 10.0")
                except Exception:
                    pass

# --- ROUTER PRINCIPAL DO STREAMLIT ---
def main():
    params = st.query_params
    codigo_aula_param = params.get("aula", None)

    if isinstance(codigo_aula_param, list):
        codigo_aula_param = codigo_aula_param[0]

    if codigo_aula_param:
        tela_aluno_mobile(codigo_aula_param)
    else:
        if not st.session_state['logged_in']:
            tela_login()
        else:
            renderizar_cabecalho()
            
            if 'flash_msg' in st.session_state:
                st.success(st.session_state['flash_msg'])
                del st.session_state['flash_msg']
            
            with st.sidebar:
                st.caption(f"Logado como: **{st.session_state['user_name']}**")
                if st.session_state.get('is_admin', False):
                    st.caption("🛡️ *Perfil Administrador*")
                st.markdown("---")
                menu = st.radio(
                    "Navegação",
                    [
                        "📚 Meus Cursos & UCs", 
                        "🧠 Fábrica de Aulas (Técnico/Médio)", 
                        "🧸 Fábrica Kids (Letramento)", 
                        "📡 Aula Ao Vivo", 
                        "🗄️ Histórico / Relatórios"
                    ]
                )
                st.markdown("---")
                if st.button("Sair"):
                    st.session_state['logged_in'] = False
                    st.session_state['user_name'] = ""
                    st.session_state['is_admin'] = False
                    st.rerun()
                    
            if menu == "📚 Meus Cursos & UCs":
                tela_dashboard()
            elif menu == "🧠 Fábrica de Aulas (Técnico/Médio)":
                tela_fabrica_aulas()
            elif menu == "🧸 Fábrica Kids (Letramento)":
                tela_fabrica_kids()
            elif menu == "📡 Aula Ao Vivo":
                tela_sala_aula()
            elif menu == "🗄️ Histórico / Relatórios":
                tela_auditoria()

if __name__ == "__main__":
    main()