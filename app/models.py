from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()


# =========================
# USUARIO
# =========================
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(150), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)

    tipos_trabajo = db.relationship('TipoTrabajo', backref='usuario', lazy=True)
    trabajos = db.relationship('Trabajo', backref='usuario', lazy=True)
    pagos = db.relationship('Pago', backref='usuario', lazy=True)
    insumos = db.relationship('Insumo', backref='usuario', lazy=True)
    gastos = db.relationship('GastoTrabajo', backref='usuario', lazy=True)

    foto_url = db.Column(db.String(300))


# =========================
# TIPO TRABAJO
# =========================
class TipoTrabajo(db.Model):
    __tablename__ = 'tipos_trabajo'

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'nombre', name='uq_tipo_trabajo_usuario'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    trabajos = db.relationship('Trabajo', backref='tipo', lazy=True)


# =========================
# TRABAJO
# =========================
class Trabajo(db.Model):
    __tablename__ = 'trabajos'

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'nombre', name='uq_trabajo_usuario'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha = db.Column(db.Date, default=date.today)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_trabajo.id'), nullable=False)

    pagos = db.relationship(
        'Pago',
        backref='trabajo',
        lazy=True,
        cascade="all, delete-orphan"
    )

    gastos = db.relationship(
        'GastoTrabajo',
        backref='trabajo',
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def ingreso_total_bruto(self):
        return sum(p.monto for p in self.pagos)

    @property
    def gasto_total(self):
        return sum(g.monto for g in self.gastos)

    @property
    def ingreso_total_neto(self):
        return self.ingreso_total_bruto - self.gasto_total

    @property
    def horas_totales(self):
        return sum(g.tiempo or 0 for g in self.gastos)

    @property
    def valor_hora(self):
        if self.horas_totales > 0:
            return round(self.ingreso_total_neto / self.horas_totales, 2)
        return 0


# =========================
# PAGO
# =========================
class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    monto = db.Column(db.Float, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    trabajo_id = db.Column(db.Integer, db.ForeignKey('trabajos.id'), nullable=False)


# =========================
# INSUMO
# =========================
class Insumo(db.Model):
    __tablename__ = 'insumos'

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'nombre', name='uq_insumo_usuario'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    gastos = db.relationship('GastoTrabajo', backref='insumo', lazy=True)


# =========================
# GASTO TRABAJO
# =========================
class GastoTrabajo(db.Model):
    __tablename__ = 'gastos_trabajo'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    monto = db.Column(db.Float, nullable=False, default=0)
    tiempo = db.Column(db.Float, nullable=False, default=0)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    trabajo_id = db.Column(db.Integer, db.ForeignKey('trabajos.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
