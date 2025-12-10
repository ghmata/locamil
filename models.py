"""
Modelos do banco de dados para o Locamil Pro - SaaS de Gestão de Frota Premium.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Carro(db.Model):
    """Modelo para representar um veículo da frota."""
    __tablename__ = 'carros'
    
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(50), nullable=False)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    cor = db.Column(db.String(20), nullable=True)
    categoria = db.Column(db.String(30), nullable=False, default='Econômico')  # Econômico, Conforto, SUV, Premium
    quilometragem = db.Column(db.Integer, default=0)
    valor_diaria = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    em_manutencao = db.Column(db.Boolean, default=False)  # Carros em manutenção não podem ser alugados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    locacoes = db.relationship('Locacao', backref='carro', lazy=True, cascade='all, delete-orphan')
    gastos = db.relationship('Gasto', backref='carro', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Carro {self.modelo} - {self.placa}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'modelo': self.modelo,
            'placa': self.placa,
            'cor': self.cor,
            'categoria': self.categoria,
            'quilometragem': self.quilometragem,
            'valor_diaria': self.valor_diaria,
            'ativo': self.ativo,
            'em_manutencao': self.em_manutencao
        }


class Cliente(db.Model):
    """Modelo para representar um cliente."""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com locações
    locacoes = db.relationship('Locacao', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'whatsapp': self.whatsapp
        }


class Locacao(db.Model):
    """Modelo para representar uma locação."""
    __tablename__ = 'locacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    carro_id = db.Column(db.Integer, db.ForeignKey('carros.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_retirada = db.Column(db.Date, nullable=False)
    data_devolucao = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ativa')  # ativa, finalizada, cancelada
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Locacao {self.id} - {self.carro.modelo}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'carro': self.carro.modelo if self.carro else None,
            'placa': self.carro.placa if self.carro else None,
            'cliente': self.cliente.nome if self.cliente else None,
            'whatsapp': self.cliente.whatsapp if self.cliente else None,
            'data_retirada': self.data_retirada.strftime('%d/%m/%Y') if self.data_retirada else None,
            'data_devolucao': self.data_devolucao.strftime('%d/%m/%Y') if self.data_devolucao else None,
            'valor_total': self.valor_total,
            'status': self.status
        }
    
    def calcular_dias(self):
        """Calcula o número de dias da locação."""
        if self.data_retirada and self.data_devolucao:
            return (self.data_devolucao - self.data_retirada).days + 1
        return 0


class Gasto(db.Model):
    """Modelo para representar gastos operacionais com veículos."""
    __tablename__ = 'gastos'
    
    id = db.Column(db.Integer, primary_key=True)
    carro_id = db.Column(db.Integer, db.ForeignKey('carros.id'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # Manutenção, Seguro, Lavagem, Combustível, IPVA, Outros
    descricao = db.Column(db.String(200), nullable=True)
    valor = db.Column(db.Float, nullable=False)
    data_gasto = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Gasto {self.tipo} - R$ {self.valor}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'carro': self.carro.modelo if self.carro else None,
            'placa': self.carro.placa if self.carro else None,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': self.valor,
            'data_gasto': self.data_gasto.strftime('%d/%m/%Y') if self.data_gasto else None
        }
