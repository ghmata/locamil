"""
Sistema de Controle de Aluguel de Carros
Aplicação web interativa para gerenciar locações de veículos com visualização em timeline.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO E CONSTANTES
# ============================================================================

# Definição da frota de veículos
FROTA = {
    "HB20 (Único)": "HB-001",
    "Celta #01": "CEL-100",
    "Celta #02": "CEL-200",
    "Celta #03": "CEL-300"
}

# Arquivo para persistência de dados
DATA_FILE = "alugueis.json"

# ============================================================================
# FUNÇÕES DE PERSISTÊNCIA DE DADOS
# ============================================================================

def carregar_alugueis():
    """
    Carrega os aluguéis salvos do arquivo JSON.
    Retorna uma lista vazia se o arquivo não existir.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Converter strings de data de volta para objetos date
                for aluguel in dados:
                    aluguel['data_inicio'] = datetime.strptime(
                        aluguel['data_inicio'], '%Y-%m-%d'
                    ).date()
                    aluguel['data_fim'] = datetime.strptime(
                        aluguel['data_fim'], '%Y-%m-%d'
                    ).date()
                return dados
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            st.error(f"Erro ao carregar dados: {e}")
            return []
    return []


def salvar_alugueis(alugueis):
    """
    Salva a lista de aluguéis no arquivo JSON.
    Converte objetos date para strings antes de salvar.
    """
    try:
        # Converter objetos date para strings
        dados_para_salvar = []
        for aluguel in alugueis:
            aluguel_copy = aluguel.copy()
            aluguel_copy['data_inicio'] = aluguel['data_inicio'].strftime('%Y-%m-%d')
            aluguel_copy['data_fim'] = aluguel['data_fim'].strftime('%Y-%m-%d')
            dados_para_salvar.append(aluguel_copy)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_para_salvar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False


# ============================================================================
# FUNÇÕES DE VALIDAÇÃO E LÓGICA DE NEGÓCIO
# ============================================================================

def verificar_sobreposicao(data_inicio, data_fim, carro, alugueis_existentes, id_excluir=None):
    """
    Verifica se há sobreposição de datas para um carro específico.
    
    Args:
        data_inicio: Data de início do novo aluguel
        data_fim: Data de fim do novo aluguel
        carro: Nome do carro
        alugueis_existentes: Lista de aluguéis existentes
        id_excluir: ID do aluguel a ser excluído da verificação (útil para edição)
    
    Returns:
        True se houver sobreposição, False caso contrário
    """
    # Criar range de datas do novo aluguel
    range_novo = pd.date_range(start=data_inicio, end=data_fim, freq='D')
    
    for aluguel in alugueis_existentes:
        # Pular o aluguel que está sendo editado/excluído
        if id_excluir is not None and aluguel.get('id') == id_excluir:
            continue
        
        # Verificar apenas aluguéis do mesmo carro
        if aluguel['carro'] == carro:
            range_existente = pd.date_range(
                start=aluguel['data_inicio'],
                end=aluguel['data_fim'],
                freq='D'
            )
            
            # Verificar se há interseção entre os ranges
            if len(range_novo.intersection(range_existente)) > 0:
                return True
    
    return False


def validar_datas(data_inicio, data_fim):
    """
    Valida se a data de fim é maior ou igual à data de início.
    
    Returns:
        (bool, str): Tupla com (é_válido, mensagem_erro)
    """
    if data_fim < data_inicio:
        return False, "A data de fim não pode ser menor que a data de início."
    return True, ""


def gerar_id():
    """
    Gera um ID único para um novo aluguel baseado no timestamp.
    """
    return int(datetime.now().timestamp() * 1000)


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def main():
    """
    Função principal da aplicação Streamlit.
    """
    # Configuração da página
    st.set_page_config(
        page_title="Sistema de Controle de Aluguel de Carros",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("🚗 Sistema de Controle de Aluguel de Carros")
    st.markdown("---")
    
    # Carregar dados salvos
    if 'alugueis' not in st.session_state:
        st.session_state.alugueis = carregar_alugueis()
    
    # ========================================================================
    # BARRA LATERAL - Formulário de Nova Reserva
    # ========================================================================
    with st.sidebar:
        st.header("📅 Nova Reserva")
        
        # Formulário de novo aluguel
        with st.form("form_novo_aluguel", clear_on_submit=True):
            nome_locatario = st.text_input(
                "Nome do Locatário:",
                placeholder="Digite o nome do cliente"
            )
            
            carro = st.selectbox(
                "Carro:",
                options=list(FROTA.keys()),
                format_func=lambda x: f"{x} - Placa: {FROTA[x]}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input(
                    "Data Início:",
                    value=date.today(),
                    min_value=date.today()
                )
            
            with col2:
                data_fim = st.date_input(
                    "Data Fim:",
                    value=date.today(),
                    min_value=date.today()
                )
            
            botao_agendar = st.form_submit_button(
                "✅ Agendar",
                use_container_width=True
            )
            
            if botao_agendar:
                # Validações
                if not nome_locatario.strip():
                    st.error("⚠️ Por favor, preencha o nome do locatário.")
                else:
                    # Validar datas
                    valido, msg_erro = validar_datas(data_inicio, data_fim)
                    if not valido:
                        st.error(f"⚠️ {msg_erro}")
                    else:
                        # Verificar sobreposição
                        if verificar_sobreposicao(
                            data_inicio,
                            data_fim,
                            carro,
                            st.session_state.alugueis
                        ):
                            st.error(
                                f"⚠️ O carro {carro} já está ocupado neste período. "
                                "Por favor, escolha outra data ou outro veículo."
                            )
                        else:
                            # Criar novo aluguel
                            novo_aluguel = {
                                'id': gerar_id(),
                                'locatario': nome_locatario.strip(),
                                'carro': carro,
                                'placa': FROTA[carro],
                                'data_inicio': data_inicio,
                                'data_fim': data_fim
                            }
                            
                            st.session_state.alugueis.append(novo_aluguel)
                            
                            if salvar_alugueis(st.session_state.alugueis):
                                st.success(
                                    f"✅ Aluguel agendado com sucesso! "
                                    f"{carro} reservado para {nome_locatario}."
                                )
                                st.rerun()
                            else:
                                st.error("❌ Erro ao salvar o aluguel.")
    
    # ========================================================================
    # ÁREA PRINCIPAL - Visualização de Timeline
    # ========================================================================
    
    if len(st.session_state.alugueis) == 0:
        st.info("📋 Nenhum agendamento cadastrado ainda. Use o formulário na barra lateral para criar uma nova reserva.")
    else:
        # Preparar dados para o gráfico de timeline
        df_timeline = pd.DataFrame(st.session_state.alugueis)
        
        # Criar coluna de texto para tooltip
        df_timeline['tooltip'] = (
            df_timeline['locatario'] + '<br>' +
            'Início: ' + df_timeline['data_inicio'].astype(str) + '<br>' +
            'Fim: ' + df_timeline['data_fim'].astype(str)
        )
        
        # Criar gráfico de timeline (Gantt Chart)
        fig = px.timeline(
            df_timeline,
            x_start='data_inicio',
            x_end='data_fim',
            y='carro',
            color='locatario',
            hover_name='locatario',
            hover_data={
                'data_inicio': '|%d/%m/%Y',
                'data_fim': '|%d/%m/%Y',
                'placa': True,
                'carro': False,
                'locatario': False
            },
            title="📅 Timeline de Aluguéis",
            labels={
                'carro': 'Veículo',
                'locatario': 'Locatário'
            },
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Personalizar layout do gráfico
        fig.update_layout(
            height=400,
            xaxis_title="Período",
            yaxis_title="Veículos",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            hovermode='closest'
        )
        
        # Atualizar barras para melhor visualização
        fig.update_traces(marker_line_width=1, marker_line_color='black')
        
        # Exibir gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # ====================================================================
        # TABELA DE DADOS - Listagem e Exclusão
        # ====================================================================
        st.markdown("---")
        st.subheader("📊 Tabela de Agendamentos")
        
        # Preparar DataFrame para exibição
        df_tabela = pd.DataFrame(st.session_state.alugueis)
        
        # Ordenar por data de início (mais recentes primeiro)
        df_tabela = df_tabela.sort_values('data_inicio', ascending=False)
        
        # Formatar datas para exibição
        df_tabela['data_inicio'] = pd.to_datetime(df_tabela['data_inicio']).dt.strftime('%d/%m/%Y')
        df_tabela['data_fim'] = pd.to_datetime(df_tabela['data_fim']).dt.strftime('%d/%m/%Y')
        
        # Selecionar colunas para exibição
        colunas_exibir = ['id', 'locatario', 'carro', 'placa', 'data_inicio', 'data_fim']
        df_tabela_exibir = df_tabela[colunas_exibir].copy()
        
        # Renomear colunas para português
        df_tabela_exibir.columns = ['ID', 'Locatário', 'Carro', 'Placa', 'Data Início', 'Data Fim']
        
        # Adicionar coluna de seleção para exclusão
        df_tabela_exibir['Excluir'] = False
        
        # Usar st.data_editor para permitir seleção
        df_editado = st.data_editor(
            df_tabela_exibir,
            use_container_width=True,
            hide_index=True,
            column_config={
                'ID': st.column_config.NumberColumn('ID', disabled=True),
                'Locatário': st.column_config.TextColumn('Locatário', disabled=True),
                'Carro': st.column_config.TextColumn('Carro', disabled=True),
                'Placa': st.column_config.TextColumn('Placa', disabled=True),
                'Data Início': st.column_config.TextColumn('Data Início', disabled=True),
                'Data Fim': st.column_config.TextColumn('Data Fim', disabled=True),
                'Excluir': st.column_config.CheckboxColumn('Excluir')
            }
        )
        
        # Botão para excluir agendamentos selecionados
        if st.button("🗑️ Excluir Agendamentos Selecionados", type="primary"):
            # Encontrar IDs dos agendamentos marcados para exclusão
            indices_para_excluir = df_editado[df_editado['Excluir'] == True].index
            
            if len(indices_para_excluir) > 0:
                # Obter IDs dos agendamentos a serem excluídos
                ids_para_excluir = df_tabela.iloc[indices_para_excluir]['id'].tolist()
                
                # Remover da lista de aluguéis
                st.session_state.alugueis = [
                    aluguel for aluguel in st.session_state.alugueis
                    if aluguel['id'] not in ids_para_excluir
                ]
                
                # Salvar alterações
                if salvar_alugueis(st.session_state.alugueis):
                    st.success(f"✅ {len(ids_para_excluir)} agendamento(s) excluído(s) com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar as alterações.")
            else:
                st.warning("⚠️ Nenhum agendamento selecionado para exclusão.")
        
        # Estatísticas rápidas
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Agendamentos", len(st.session_state.alugueis))
        with col2:
            hoje = date.today()
            agendamentos_ativos = sum(
                1 for a in st.session_state.alugueis
                if a['data_inicio'] <= hoje <= a['data_fim']
            )
            st.metric("Agendamentos Ativos Hoje", agendamentos_ativos)
        with col3:
            agendamentos_futuros = sum(
                1 for a in st.session_state.alugueis
                if a['data_inicio'] > hoje
            )
            st.metric("Agendamentos Futuros", agendamentos_futuros)


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()


 