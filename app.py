"""
Aplicação Flask para gestão de locadora de veículos.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, date, timedelta
from models import db, Carro, Cliente, Locacao
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
    Popula o banco de dados com a frota inicial do cliente.
    Executado automaticamente na primeira inicialização.
    """
    # Verificar se já existem carros cadastrados
    if Carro.query.count() > 0:
        return
    
    # 1 HB20 - Diária R$ 120,00
    hb20 = Carro(
        modelo='HB20',
        placa='HB-001',
        cor='Branco',
        valor_diaria=120.00
    )
    db.session.add(hb20)
    
    # 4 Celtas - Diária R$ 90,00 cada
    celtas = [
        {'placa': 'CEL-100', 'cor': 'Prata'},
        {'placa': 'CEL-200', 'cor': 'Branco'},
        {'placa': 'CEL-300', 'cor': 'Preto'},
        {'placa': 'CEL-400', 'cor': 'Prata'}
    ]
    
    for celta in celtas:
        carro = Carro(
            modelo='Celta',
            placa=celta['placa'],
            cor=celta['cor'],
            valor_diaria=90.00
        )
        db.session.add(carro)
    
    db.session.commit()
    print("✅ Frota inicial cadastrada com sucesso!")


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
        carro = Carro.query.get(carro_id)
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
    """Dashboard principal com visão geral da frota."""
    # Garantir que o banco está inicializado
    with app.app_context():
        if Carro.query.count() == 0:
            seed_database()
    
    # Buscar todos os carros
    carros = Carro.query.filter_by(ativo=True).order_by(Carro.modelo, Carro.placa).all()
    
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
    
    return render_template(
        'dashboard.html',
        status_carros=status_carros,
        proximas_devolucoes=proximas_devolucoes,
        proximas_retiradas=proximas_retiradas
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

