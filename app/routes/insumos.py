from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import GastoTrabajo, TipoTrabajo, Trabajo, db, Insumo

insumos = Blueprint(
    'insumos',
    __name__,
    url_prefix='/insumos'
)


@insumos.route('/')
@login_required
def index():
    insumos = (
        Insumo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Insumo.nombre)
        .all()
    )
    return render_template('insumos.html', insumos=insumos)


@insumos.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400

    existe = Insumo.query.filter_by(
        nombre=nombre,
        usuario_id=current_user.id
    ).first()

    if existe:
        return jsonify({'error': 'El insumo ya existe'}), 400

    insumo = Insumo(
        nombre=nombre,
        usuario_id=current_user.id
    )

    db.session.add(insumo)
    db.session.commit()

    return jsonify({'success': True})


@insumos.route('/editar/<int:insumo_id>', methods=['POST'])
@login_required
def editar(insumo_id):
    insumo = Insumo.query.filter_by(
        id=insumo_id,
        usuario_id=current_user.id
    ).first_or_404()

    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400

    existe = Insumo.query.filter(
        Insumo.nombre == nombre,
        Insumo.usuario_id == current_user.id,
        Insumo.id != insumo_id
    ).first()

    if existe:
        return jsonify({'error': 'Ya existe otro insumo con ese nombre'}), 400

    insumo.nombre = nombre
    db.session.commit()

    return jsonify({'success': True})


@insumos.route('/eliminar/<int:insumo_id>', methods=['POST'])
@login_required
def eliminar(insumo_id):
    insumo = Insumo.query.filter_by(
        id=insumo_id,
        usuario_id=current_user.id
    ).first_or_404()

    if insumo.gastos:
        return jsonify(
            {'error': 'No se puede eliminar: tiene gastos asociados'},
            400
        )

    db.session.delete(insumo)
    db.session.commit()

    return jsonify({'success': True})






from sqlalchemy import func, extract
from datetime import datetime

@insumos.route('/<int:insumo_id>/resumen')
@login_required
def resumen_por_mes(insumo_id):
    rows = (
        db.session.query(
            func.strftime('%m-%Y', GastoTrabajo.fecha).label('mes'),
            func.sum(GastoTrabajo.monto).label('total'),
            func.sum(GastoTrabajo.tiempo).label('tiempo')
        )
        .filter(
            GastoTrabajo.insumo_id == insumo_id,
            GastoTrabajo.usuario_id == current_user.id
        )
        .group_by('mes')
        .order_by('mes')
        .all()
    )

    return jsonify([
        {
            "mes": r.mes,
            "total": int(r.total or 0),
            "tiempo": float(r.tiempo or 0)
        }
        for r in rows
    ])



@insumos.route('/<int:insumo_id>/detalle/<mes>')
@login_required
def detalle_mes(insumo_id, mes):
    mes_num, anio = mes.split("-")

    gastos = (
        GastoTrabajo.query
        .join(Trabajo)
        .filter(
            GastoTrabajo.insumo_id == insumo_id,
            GastoTrabajo.usuario_id == current_user.id,
            extract('month', GastoTrabajo.fecha) == int(mes_num),
            extract('year', GastoTrabajo.fecha) == int(anio)
        )
        .all()
    )

    return jsonify([
        {
            "fecha": g.fecha.strftime("%d/%m"),
            "trabajo": g.trabajo.nombre,
            "tiempo": float(g.tiempo),
            "monto": int(g.monto)
        }
        for g in gastos
    ])
