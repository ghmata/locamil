"""
Aplicação Flask para gestão de locadora de veículos.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, date, timedelta
from models import db, Carro, Cliente, Locacao, Gasto
import os
import csv
import io
import json as json_lib
import re
from urllib.parse import quote
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
 
app = Flask(__name__)

# Configurações da aplicação usando variáveis de ambiente
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///locadora.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Validar SECRET_KEY em produção
if not os.getenv('FLASK_DEBUG', 'True') == 'True' and app.config['SECRET_KEY'] == 'dev-key-change-in-production':
    raise ValueError(
        "⚠️ ERRO DE SEGURANÇA: SECRET_KEY não foi configurada! "
        "Por favor, defina a variável de ambiente SECRET_KEY antes de executar em produção."
    )

# Inicializar banco de dados
db.init_app(app)


def seed_database():
    """
    Popula o banco de dados com frota realista e gastos de exemplo.
    Executado automaticamente na primeira inicialização.
    """
    # Verificar se já existem carros cadastrados
    if Carro.query.count() > 0:
        return
    
    # ========== CATEGORIA: ECONÔMICO ==========
    frota_economico = [
        {'modelo': 'Renault Kwid', 'placa': 'KWD-1010', 'cor': 'Branco', 'diaria': 80.00, 'km': 45000},
        {'modelo': 'Fiat Mobi', 'placa': 'MOB-2020', 'cor': 'Prata', 'diaria': 75.00, 'km': 38000},
    ]
    
    for carro_data in frota_economico:
        carro = Carro(
            modelo=carro_data['modelo'],
            placa=carro_data['placa'],
            cor=carro_data['cor'],
            categoria='Econômico',
            quilometragem=carro_data['km'],
            valor_diaria=carro_data['diaria']
        )
        db.session.add(carro)
    
    # ========== CATEGORIA: CONFORTO ==========
    frota_conforto = [
        {'modelo': 'Hyundai HB20', 'placa': 'HB-3030', 'cor': 'Branco', 'diaria': 120.00, 'km': 52000},
        {'modelo': 'Chevrolet Onix', 'placa': 'ONX-4040', 'cor': 'Preto', 'diaria': 115.00, 'km': 48000},
        {'modelo': 'VW Polo', 'placa': 'POL-5050', 'cor': 'Prata', 'diaria': 130.00, 'km': 35000},
    ]
    
    for carro_data in frota_conforto:
        carro = Carro(
            modelo=carro_data['modelo'],
            placa=carro_data['placa'],
            cor=carro_data['cor'],
            categoria='Conforto',
            quilometragem=carro_data['km'],
            valor_diaria=carro_data['diaria']
        )
        db.session.add(carro)
    
    # ========== CATEGORIA: SUV ==========
    frota_suv = [
        {'modelo': 'VW T-Cross', 'placa': 'TCR-6060', 'cor': 'Cinza', 'diaria': 180.00, 'km': 28000},
        {'modelo': 'Chevrolet Tracker', 'placa': 'TRK-7070', 'cor': 'Branco', 'diaria': 175.00, 'km': 31000},
    ]
    
    for carro_data in frota_suv:
        carro = Carro(
            modelo=carro_data['modelo'],
            placa=carro_data['placa'],
            cor=carro_data['cor'],
            categoria='SUV',
            quilometragem=carro_data['km'],
            valor_diaria=carro_data['diaria']
        )
        db.session.add(carro)
    
    # ========== CATEGORIA: PREMIUM ==========
    frota_premium = [
        {'modelo': 'BMW 320i', 'placa': 'BMW-8080', 'cor': 'Preto', 'diaria': 350.00, 'km': 18000},
        {'modelo': 'Mercedes C180', 'placa': 'MER-9090', 'cor': 'Prata', 'diaria': 380.00, 'km': 15000},
    ]
    
    for carro_data in frota_premium:
        carro = Carro(
            modelo=carro_data['modelo'],
            placa=carro_data['placa'],
            cor=carro_data['cor'],
            categoria='Premium',
            quilometragem=carro_data['km'],
            valor_diaria=carro_data['diaria']
        )
        db.session.add(carro)
    
    db.session.commit()
    
    # ========== ADICIONAR GASTOS DE EXEMPLO (últimos 6 meses) ==========
    carros = Carro.query.all()
    hoje = date.today()
    
    # Gastos distribuídos nos últimos 6 meses
    gastos_exemplo = [
        # Mês 1 (6 meses atrás)
        {'carro_idx': 0, 'tipo': 'Manutenção', 'descricao': 'Troca de óleo e filtros', 'valor': 280.00, 'dias_atras': 180},
        {'carro_idx': 2, 'tipo': 'Seguro', 'descricao': 'Seguro anual', 'valor': 1200.00, 'dias_atras': 175},
        
        # Mês 2 (5 meses atrás)
        {'carro_idx': 1, 'tipo': 'Lavagem', 'descricao': 'Lavagem completa', 'valor': 80.00, 'dias_atras': 150},
        {'carro_idx': 5, 'tipo': 'Manutenção', 'descricao': 'Alinhamento e balanceamento', 'valor': 150.00, 'dias_atras': 145},
        
        # Mês 3 (4 meses atrás)
        {'carro_idx': 3, 'tipo': 'Manutenção', 'descricao': 'Revisão dos 50.000 km', 'valor': 650.00, 'dias_atras': 120},
        {'carro_idx': 7, 'tipo': 'Seguro', 'descricao': 'Seguro premium anual', 'valor': 2800.00, 'dias_atras': 115},
        
        # Mês 4 (3 meses atrás)
        {'carro_idx': 4, 'tipo': 'Lavagem', 'descricao': 'Lavagem e polimento', 'valor': 120.00, 'dias_atras': 90},
        {'carro_idx': 6, 'tipo': 'Manutenção', 'descricao': 'Troca de pneus', 'valor': 1400.00, 'dias_atras': 85},
        
        # Mês 5 (2 meses atrás)
        {'carro_idx': 0, 'tipo': 'Lavagem', 'descricao': 'Lavagem simples', 'valor': 50.00, 'dias_atras': 60},
        {'carro_idx': 8, 'tipo': 'Manutenção', 'descricao': 'Troca de óleo sintético', 'valor': 450.00, 'dias_atras': 55},
        
        # Mês 6 (mês passado)
        {'carro_idx': 2, 'tipo': 'Lavagem', 'descricao': 'Lavagem completa', 'valor': 80.00, 'dias_atras': 30},
        {'carro_idx': 5, 'tipo': 'Manutenção', 'descricao': 'Troca de pastilhas de freio', 'valor': 380.00, 'dias_atras': 25},
        {'carro_idx': 1, 'tipo': 'IPVA', 'descricao': 'IPVA 2025', 'valor': 520.00, 'dias_atras': 20},
    ]
    
    for gasto_data in gastos_exemplo:
        if gasto_data['carro_idx'] < len(carros):
            gasto = Gasto(
                carro_id=carros[gasto_data['carro_idx']].id,
                tipo=gasto_data['tipo'],
                descricao=gasto_data['descricao'],
                valor=gasto_data['valor'],
                data_gasto=hoje - timedelta(days=gasto_data['dias_atras'])
            )
            db.session.add(gasto)
    
    db.session.commit()
    print("✅ Frota Premium e gastos cadastrados com sucesso!")


def verificar_disponibilidade(carro_id, data_retirada, data_devolucao, locacao_id=None):
    """
    Verifica se um carro está disponível no período especificado.
    
    Args:
        carro_id: ID do carro
        data_retirada: Data de retirada
        data_devolucao: Data de devolução
        locacao_id: ID da locação atual (para edição, excluir da verificação)
    
    Returns:
        (bool, str): (disponivel, mensagem_erro)
    """
    # Verificar se o carro está em manutenção
    carro = Carro.query.get(carro_id)
    if carro and carro.em_manutencao:
        return False, f"O carro {carro.modelo} - {carro.placa} está em manutenção e não pode ser alugado."
    
    # Validar datas
    if data_devolucao < data_retirada:
        return False, "A data de devolução não pode ser anterior à data de retirada."
    
    # Buscar locações ativas do carro no período
    locacoes_conflito = Locacao.query.filter(
        Locacao.carro_id == carro_id,
        Locacao.status == 'ativa',
        Locacao.id != locacao_id if locacao_id else True
    ).filter(
        # Verificar sobreposição de datas
        db.or_(
            # Caso 1: Nova locação começa durante uma locação existente
            db.and_(
                Locacao.data_retirada <= data_retirada,
                Locacao.data_devolucao >= data_retirada
            ),
            # Caso 2: Nova locação termina durante uma locação existente
            db.and_(
                Locacao.data_retirada <= data_devolucao,
                Locacao.data_devolucao >= data_devolucao
            ),
            # Caso 3: Nova locação engloba uma locação existente
            db.and_(
                Locacao.data_retirada >= data_retirada,
                Locacao.data_devolucao <= data_devolucao
            )
        )
    ).first()
    
    if locacoes_conflito:
        return False, f"O carro {carro.modelo} - {carro.placa} já está alugado neste período."
    
    return True, ""


def formatar_telefone(whatsapp):
    """
    Formata o número de telefone adicionando o prefixo +55 se necessário.
    Remove caracteres não numéricos e adiciona +55 no início.
    
    Args:
        whatsapp: String com o número de telefone
    
    Returns:
        str: Número formatado com +55 ou string vazia se inválido
    """
    if not whatsapp or not whatsapp.strip():
        return ""
    
    # Se já começar com +55, retornar como está (após limpar)
    if whatsapp.strip().startswith('+55'):
        numeros = re.sub(r'\D', '', whatsapp)
        return f"+{numeros}" if numeros.startswith('55') else f"+55{numeros[2:]}" if len(numeros) > 2 else ""
    
    # Remover todos os caracteres não numéricos
    numeros = re.sub(r'\D', '', whatsapp)
    
    # Se já começar com 55 (sem +), adicionar +
    if numeros.startswith('55'):
        return f"+{numeros}"
    
    # Se começar com 0, remover o 0 e adicionar 55
    if numeros.startswith('0'):
        numeros = numeros[1:]
    
    # Adicionar +55 no início
    if len(numeros) >= 10:  # Validar que tem pelo menos 10 dígitos (DDD + número)
        return f"+55{numeros}"
    
    return ""


def calcular_valor_total(carro_id, data_retirada, data_devolucao):
    """
    Calcula o valor total da locação.
    
    Args:
        carro_id: ID do carro
        data_retirada: Data de retirada
        data_devolucao: Data de devolução
    
    Returns:
        float: Valor total calculado
    """
    carro = Carro.query.get(carro_id)
    if not carro:
        return 0.0
    
    dias = (data_devolucao - data_retirada).days + 1
    return dias * carro.valor_diaria


def get_status_carro_hoje(carro_id):
    """
    Retorna o status de um carro hoje (Disponível ou Alugado).
    
    Args:
        carro_id: ID do carro
    
    Returns:
        dict: {'status': 'disponivel'|'alugado', 'locacao': Locacao ou None}
    """
    hoje = date.today()
    
    locacao_ativa = Locacao.query.filter(
        Locacao.carro_id == carro_id,
        Locacao.status == 'ativa',
        Locacao.data_retirada <= hoje,
        Locacao.data_devolucao >= hoje
    ).first()
    
    if locacao_ativa:
        return {
            'status': 'alugado',
            'locacao': locacao_ativa
        }
    
    return {
        'status': 'disponivel',
        'locacao': None
    }


# ============================================================================
# ROTAS
# ============================================================================

@app.route('/')
def index():
    """Dashboard principal com KPIs financeiros e gráficos interativos."""
    # Garantir que o banco está inicializado
    with app.app_context():
        if Carro.query.count() == 0:
            seed_database()
    
    # Buscar todos os carros
    carros = Carro.query.filter_by(ativo=True).order_by(Carro.categoria, Carro.modelo).all()
    
    # Status de cada carro hoje
    status_carros = []
    for carro in carros:
        status = get_status_carro_hoje(carro.id)
        status_carros.append({
            'carro': carro,
            'status': status['status'],
            'locacao': status['locacao']
        })
    
    # Próximas devoluções (hoje e próximos 7 dias)
    hoje = date.today()
    proxima_semana = hoje + timedelta(days=7)
    
    proximas_devolucoes = Locacao.query.filter(
        Locacao.status == 'ativa',
        Locacao.data_devolucao >= hoje,
        Locacao.data_devolucao <= proxima_semana
    ).order_by(Locacao.data_devolucao).limit(10).all()
    
    # Próximas retiradas (hoje e próximos 7 dias)
    proximas_retiradas = Locacao.query.filter(
        Locacao.status == 'ativa',
        Locacao.data_retirada >= hoje,
        Locacao.data_retirada <= proxima_semana
    ).order_by(Locacao.data_retirada).limit(10).all()
    
    # ========== DADOS FINANCEIROS ==========
    
    # Calcular faturamento dos últimos 6 meses (para gráfico)
    faturamento_mensal = []
    labels_meses = []
    
    for i in range(5, -1, -1):  # 6 meses (do mais antigo ao mais recente)
        mes_ref = hoje - timedelta(days=30 * i)
        inicio_mes = mes_ref.replace(day=1)
        
        # Calcular fim do mês
        if mes_ref.month == 12:
            fim_mes = mes_ref.replace(day=31)
        else:
            proximo_mes = mes_ref.replace(month=mes_ref.month + 1, day=1)
            fim_mes = proximo_mes - timedelta(days=1)
        
        # Somar locações finalizadas no mês
        locacoes_mes = Locacao.query.filter(
            Locacao.status.in_(['ativa', 'finalizada']),
            Locacao.data_retirada >= inicio_mes,
            Locacao.data_retirada <= fim_mes
        ).all()
        
        faturamento = sum(loc.valor_total for loc in locacoes_mes)
        faturamento_mensal.append(round(faturamento, 2))
        
        # Nome do mês em português
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        labels_meses.append(meses_pt[mes_ref.month - 1])
    
    # Faturamento total (últimos 6 meses)
    faturamento_total = sum(faturamento_mensal)
    
    # Despesas totais (últimos 6 meses)
    inicio_periodo = hoje - timedelta(days=180)
    gastos_periodo = Gasto.query.filter(Gasto.data_gasto >= inicio_periodo).all()
    despesas_total = sum(gasto.valor for gasto in gastos_periodo)
    
    # Lucro líquido
    lucro_liquido = faturamento_total - despesas_total
    
    # ========== STATUS DA FROTA (para gráfico de rosca) ==========
    total_carros = len(carros)
    carros_alugados = sum(1 for item in status_carros if item['status'] == 'alugado')
    carros_disponiveis = sum(1 for item in status_carros if item['status'] == 'disponivel')
    carros_manutencao = Carro.query.filter_by(ativo=True, em_manutencao=True).count()
    
    return render_template(
        'dashboard.html',
        status_carros=status_carros,
        proximas_devolucoes=proximas_devolucoes,
        proximas_retiradas=proximas_retiradas,
        # KPIs Financeiros
        faturamento_total=faturamento_total,
        despesas_total=despesas_total,
        lucro_liquido=lucro_liquido,
        # Dados para gráficos
        faturamento_mensal=faturamento_mensal,
        labels_meses=labels_meses,
        carros_alugados=carros_alugados,
        carros_disponiveis=carros_disponiveis,
        carros_manutencao=carros_manutencao,
        total_carros=total_carros
    )


@app.route('/nova_locacao', methods=['GET', 'POST'])
def nova_locacao():
    """Formulário para criar uma nova locação."""
    if request.method == 'POST':
        # Obter dados do formulário
        nome_cliente = request.form.get('nome_cliente', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        carro_id = request.form.get('carro_id', type=int)
        data_retirada_str = request.form.get('data_retirada')
        data_devolucao_str = request.form.get('data_devolucao')
        
        # Validações básicas
        if not nome_cliente:
            flash('⚠️ Por favor, preencha o nome do cliente.', 'danger')
            return redirect(url_for('nova_locacao'))
        
        if not carro_id:
            flash('⚠️ Por favor, selecione um carro.', 'danger')
            return redirect(url_for('nova_locacao'))
        
        if not data_retirada_str or not data_devolucao_str:
            flash('⚠️ Por favor, preencha as datas de retirada e devolução.', 'danger')
            return redirect(url_for('nova_locacao'))
        
        try:
            data_retirada = datetime.strptime(data_retirada_str, '%Y-%m-%d').date()
            data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('⚠️ Datas inválidas. Por favor, verifique.', 'danger')
            return redirect(url_for('nova_locacao'))
        
        # Verificar disponibilidade
        disponivel, mensagem = verificar_disponibilidade(carro_id, data_retirada, data_devolucao)
        if not disponivel:
            flash(f'❌ {mensagem}', 'danger')
            return redirect(url_for('nova_locacao'))
        
        # Buscar ou criar cliente
        cliente = Cliente.query.filter_by(nome=nome_cliente).first()
        if not cliente:
            # Formatar WhatsApp com +55
            whatsapp_formatado = formatar_telefone(whatsapp) if whatsapp else ""
            cliente = Cliente(nome=nome_cliente, whatsapp=whatsapp_formatado)
            db.session.add(cliente)
            db.session.flush()
        else:
            # Atualizar WhatsApp se fornecido e ainda não tiver +55 ou estiver vazio
            if whatsapp:
                whatsapp_formatado = formatar_telefone(whatsapp)
                if whatsapp_formatado and (not cliente.whatsapp or not cliente.whatsapp.startswith('+55')):
                    cliente.whatsapp = whatsapp_formatado
        
        # Calcular valor total
        valor_total = calcular_valor_total(carro_id, data_retirada, data_devolucao)
        
        # Criar locação
        locacao = Locacao(
            carro_id=carro_id,
            cliente_id=cliente.id,
            data_retirada=data_retirada,
            data_devolucao=data_devolucao,
            valor_total=valor_total,
            status='ativa'
        )
        
        db.session.add(locacao)
        db.session.commit()
        
        flash(f'✅ Locação criada com sucesso! Total: R$ {valor_total:.2f}', 'success')
        return redirect(url_for('index'))
    
    # GET: Exibir formulário
    # Garantir que o banco está inicializado
    with app.app_context():
        if Carro.query.count() == 0:
            seed_database()
    
    carros = Carro.query.filter_by(ativo=True).order_by(Carro.modelo, Carro.placa).all()
    hoje = date.today().strftime('%Y-%m-%d')
    return render_template('nova_locacao.html', carros=carros, hoje=hoje)


@app.route('/calcular_valor', methods=['POST'])
def calcular_valor():
    """Endpoint AJAX para calcular valor em tempo real."""
    data = request.get_json()
    carro_id = data.get('carro_id', type=int)
    data_retirada_str = data.get('data_retirada')
    data_devolucao_str = data.get('data_devolucao')
    
    if not carro_id or not data_retirada_str or not data_devolucao_str:
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    try:
        data_retirada = datetime.strptime(data_retirada_str, '%Y-%m-%d').date()
        data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erro': 'Datas inválidas'}), 400
    
    valor_total = calcular_valor_total(carro_id, data_retirada, data_devolucao)
    dias = (data_devolucao - data_retirada).days + 1
    
    return jsonify({
        'valor_total': valor_total,
        'dias': dias
    })


@app.route('/historico')
def historico():
    """Página com histórico de todas as locações."""
    # Buscar todas as locações ordenadas por data de retirada (mais recentes primeiro)
    locacoes = Locacao.query.order_by(Locacao.data_retirada.desc(), Locacao.created_at.desc()).all()
    
    return render_template('historico.html', locacoes=locacoes)


@app.route('/finalizar_locacao/<int:locacao_id>', methods=['POST'])
def finalizar_locacao(locacao_id):
    """Finaliza uma locação (marca como finalizada)."""
    locacao = Locacao.query.get_or_404(locacao_id)
    locacao.status = 'finalizada'
    db.session.commit()
    
    flash('✅ Locação finalizada com sucesso!', 'success')
    return redirect(url_for('historico'))


@app.route('/cancelar_locacao/<int:locacao_id>', methods=['POST'])
def cancelar_locacao(locacao_id):
    """Cancela uma locação."""
    locacao = Locacao.query.get_or_404(locacao_id)
    locacao.status = 'cancelada'
    db.session.commit()
    
    flash('✅ Locação cancelada com sucesso!', 'success')
    return redirect(url_for('historico'))


@app.route('/whatsapp/<int:locacao_id>')
def enviar_comprovante_whatsapp(locacao_id):
    """
    Gera link do WhatsApp Web com mensagem pré-formatada do comprovante.
    Redireciona para o WhatsApp Web.
    """
    locacao = Locacao.query.get_or_404(locacao_id)
    
    if not locacao.cliente.whatsapp:
        flash('⚠️ Cliente não possui WhatsApp cadastrado.', 'warning')
        return redirect(url_for('historico'))
    
    # Formatar dados da locação
    dias = (locacao.data_devolucao - locacao.data_retirada).days + 1
    data_retirada_formatada = locacao.data_retirada.strftime('%d/%m/%Y')
    data_devolucao_formatada = locacao.data_devolucao.strftime('%d/%m/%Y')
    
    # Criar mensagem do comprovante
    mensagem = f"""*COMPROVANTE DE LOCAÇÃO*

Olá, {locacao.cliente.nome}!

Segue o comprovante da sua locação:

🚗 *Veículo:* {locacao.carro.modelo} - {locacao.carro.placa}
📅 *Data de Retirada:* {data_retirada_formatada}
📅 *Data de Devolução:* {data_devolucao_formatada}
⏱️ *Período:* {dias} dia(s)
💰 *Valor Total:* R$ {locacao.valor_total:.2f}

Obrigado pela preferência! 🚗✨"""
    
    # Codificar mensagem para URL
    mensagem_encoded = quote(mensagem)
    
    # Limpar o número (remover + e caracteres especiais para o link)
    numero_limpo = re.sub(r'\D', '', locacao.cliente.whatsapp)
    
    # Criar link do WhatsApp Web
    whatsapp_url = f"https://wa.me/{numero_limpo}?text={mensagem_encoded}"
    
    return redirect(whatsapp_url)


@app.route('/exportar')
def exportar():
    """Página de exportação de dados."""
    return render_template('exportar.html')


@app.route('/exportar/sql')
def exportar_sql():
    """Exporta todos os dados em formato SQL (INSERT statements)."""
    carros = Carro.query.all()
    clientes = Cliente.query.all()
    locacoes = Locacao.query.all()
    
    sql_content = []
    sql_content.append("-- Exportação de dados da Locadora")
    sql_content.append(f"-- Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append("-- Formato: SQL INSERT statements")
    sql_content.append("")
    sql_content.append("-- ============================================")
    sql_content.append("-- TABELA: CARROS")
    sql_content.append("-- ============================================")
    sql_content.append("")
    
    for carro in carros:
        modelo_escaped = carro.modelo.replace("'", "''") if carro.modelo else ""
        placa_escaped = carro.placa.replace("'", "''") if carro.placa else ""
        cor_escaped = (carro.cor or "").replace("'", "''")
        sql_content.append(
            f"INSERT INTO carros (id, modelo, placa, cor, valor_diaria, ativo, created_at) "
            f"VALUES ({carro.id}, '{modelo_escaped}', '{placa_escaped}', "
            f"'{cor_escaped}', {carro.valor_diaria}, {1 if carro.ativo else 0}, "
            f"'{carro.created_at.strftime('%Y-%m-%d %H:%M:%S')}');"
        )
    
    sql_content.append("")
    sql_content.append("-- ============================================")
    sql_content.append("-- TABELA: CLIENTES")
    sql_content.append("-- ============================================")
    sql_content.append("")
    
    for cliente in clientes:
        nome_escaped = cliente.nome.replace("'", "''") if cliente.nome else ""
        whatsapp_escaped = cliente.whatsapp.replace("'", "''") if cliente.whatsapp else ""
        sql_content.append(
            f"INSERT INTO clientes (id, nome, whatsapp, created_at) "
            f"VALUES ({cliente.id}, '{nome_escaped}', "
            f"'{whatsapp_escaped}', '{cliente.created_at.strftime('%Y-%m-%d %H:%M:%S')}');"
        )
    
    sql_content.append("")
    sql_content.append("-- ============================================")
    sql_content.append("-- TABELA: LOCACOES")
    sql_content.append("-- ============================================")
    sql_content.append("")
    
    for locacao in locacoes:
        observacoes_escaped = (locacao.observacoes or "").replace("'", "''")
        status_escaped = locacao.status.replace("'", "''") if locacao.status else ""
        sql_content.append(
            f"INSERT INTO locacoes (id, carro_id, cliente_id, data_retirada, data_devolucao, "
            f"valor_total, status, observacoes, created_at) "
            f"VALUES ({locacao.id}, {locacao.carro_id}, {locacao.cliente_id}, "
            f"'{locacao.data_retirada}', '{locacao.data_devolucao}', {locacao.valor_total}, "
            f"'{status_escaped}', '{observacoes_escaped}', "
            f"'{locacao.created_at.strftime('%Y-%m-%d %H:%M:%S')}');"
        )
    
    sql_text = "\n".join(sql_content)
    
    # Criar arquivo em memória
    output = io.BytesIO()
    output.write(sql_text.encode('utf-8'))
    output.seek(0)
    
    filename = f"locadora_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    return send_file(
        output,
        mimetype='text/sql',
        as_attachment=True,
        download_name=filename
    )


@app.route('/exportar/csv')
def exportar_csv():
    """Exporta locações em formato CSV para análise."""
    locacoes = Locacao.query.all()
    
    # Criar CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Carro', 'Placa', 'Cliente', 'WhatsApp', 
        'Data Retirada', 'Data Devolução', 'Dias', 
        'Valor Diária', 'Valor Total', 'Status', 'Data Criação'
    ])
    
    # Dados
    for locacao in locacoes:
        dias = (locacao.data_devolucao - locacao.data_retirada).days + 1
        writer.writerow([
            locacao.id,
            locacao.carro.modelo,
            locacao.carro.placa,
            locacao.cliente.nome,
            locacao.cliente.whatsapp or '',
            locacao.data_retirada.strftime('%d/%m/%Y'),
            locacao.data_devolucao.strftime('%d/%m/%Y'),
            dias,
            locacao.carro.valor_diaria,
            locacao.valor_total,
            locacao.status,
            locacao.created_at.strftime('%d/%m/%Y %H:%M:%S')
        ])
    
    # Converter para bytes
    output_bytes = io.BytesIO()
    output_bytes.write(output.getvalue().encode('utf-8-sig'))  # BOM para Excel
    output_bytes.seek(0)
    
    filename = f"locacoes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/exportar/json')
def exportar_json():
    """Exporta todos os dados em formato JSON para análise."""
    carros = [carro.to_dict() for carro in Carro.query.all()]
    clientes = [cliente.to_dict() for cliente in Cliente.query.all()]
    locacoes = []
    
    for locacao in Locacao.query.all():
        loc_dict = locacao.to_dict()
        loc_dict['data_retirada'] = locacao.data_retirada.isoformat()
        loc_dict['data_devolucao'] = locacao.data_devolucao.isoformat()
        loc_dict['created_at'] = locacao.created_at.isoformat()
        locacoes.append(loc_dict)
    
    dados_export = {
        'exportacao': {
            'data': datetime.now().isoformat(),
            'versao': '1.0'
        },
        'carros': carros,
        'clientes': clientes,
        'locacoes': locacoes
    }
    
    json_text = json_lib.dumps(dados_export, ensure_ascii=False, indent=2)
    
    # Criar arquivo em memória
    output = io.BytesIO()
    output.write(json_text.encode('utf-8'))
    output.seek(0)
    
    filename = f"locadora_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

def init_db():
    """Cria as tabelas e popula o banco na primeira execução."""
    with app.app_context():
        db.create_all()
        seed_database()


if __name__ == '__main__':
    # Garantir que as tabelas existam
    init_db()
    
    # Configurações do servidor a partir de variáveis de ambiente
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    app.run(debug=debug_mode, host=host, port=port)

