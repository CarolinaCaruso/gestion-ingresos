from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, TipoTrabajo
from sqlalchemy import func, extract
from app.models import Trabajo, Pago, GastoTrabajo


tipos_trabajo = Blueprint(
    'tipos_trabajo',
    __name__,
    url_prefix='/tipos-trabajo'
)


# ===========================
# LISTADO
# ===========================
@tipos_trabajo.route('/')
@login_required
def index():
    tipos = (
        TipoTrabajo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(TipoTrabajo.nombre)
        .all()
    )

    return render_template(
        'tipos_trabajo.html',
        tipos=tipos
    )


# ===========================
# NUEVO
# ===========================
@tipos_trabajo.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400

    existe = TipoTrabajo.query.filter_by(
        nombre=nombre,
        usuario_id=current_user.id
    ).first()

    if existe:
        return jsonify({'error': 'El tipo ya existe'}), 400

    tipo = TipoTrabajo(
        nombre=nombre,
        usuario_id=current_user.id
    )

    db.session.add(tipo)
    db.session.commit()

    return jsonify({'success': True})


# ===========================
# EDITAR
# ===========================
@tipos_trabajo.route('/editar/<int:tipo_id>', methods=['POST'])
@login_required
def editar(tipo_id):
    tipo = TipoTrabajo.query.filter_by(
        id=tipo_id,
        usuario_id=current_user.id
    ).first_or_404()

    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400

    existe = TipoTrabajo.query.filter(
        TipoTrabajo.nombre == nombre,
        TipoTrabajo.usuario_id == current_user.id,
        TipoTrabajo.id != tipo_id
    ).first()

    if existe:
        return jsonify({'error': 'Ya existe otro tipo con ese nombre'}), 400

    tipo.nombre = nombre
    db.session.commit()

    return jsonify({'success': True})


# ===========================
# ELIMINAR
# ===========================
@tipos_trabajo.route('/eliminar/<int:tipo_id>', methods=['POST'])
@login_required
def eliminar(tipo_id):
    tipo = TipoTrabajo.query.filter_by(
        id=tipo_id,
        usuario_id=current_user.id
    ).first_or_404()

    if tipo.trabajos:
        return jsonify(
            {'error': 'No se puede eliminar: tiene trabajos asociados'},
            400
        )

    db.session.delete(tipo)
    db.session.commit()

    return jsonify({'success': True})





@tipos_trabajo.route('/<int:tipo_id>/resumen')
@login_required
def resumen_por_mes(tipo_id):
    rows = (
        db.session.query(
            func.strftime('%m-%Y', Trabajo.fecha).label('mes'),
            func.sum(Pago.monto).label('bruto'),
            func.sum(GastoTrabajo.monto).label('gasto')
        )
        .join(Pago, Pago.trabajo_id == Trabajo.id)
        .outerjoin(GastoTrabajo, GastoTrabajo.trabajo_id == Trabajo.id)
        .filter(
            Trabajo.tipo_id == tipo_id,
            Trabajo.usuario_id == current_user.id
        )
        .group_by('mes')
        .order_by('mes')
        .all()
    )

    return jsonify([
        {
            "mes": r.mes,
            "bruto": float(r.bruto or 0),
            "gasto": float(r.gasto or 0),
            "neto": float((r.bruto or 0) - (r.gasto or 0))
        }
        for r in rows
    ])




@tipos_trabajo.route('/<int:tipo_id>/detalle/<mes>')
@login_required
def detalle_mes(tipo_id, mes):
    mes_num, anio = mes.split("-")

    trabajos = (
        Trabajo.query
        .filter(
            Trabajo.tipo_id == tipo_id,
            Trabajo.usuario_id == current_user.id,
            extract('month', Trabajo.fecha) == int(mes_num),
            extract('year', Trabajo.fecha) == int(anio)
        )
        .all()
    )

    data = []
    for t in trabajos:
        data.append({
            "fecha": t.fecha.strftime("%d/%m"),
            "tipo": t.tipo.nombre,
            "trabajo": t.nombre,
            "bruto": t.ingreso_total_bruto,
            "gasto": t.gasto_total,
            "neto": t.ingreso_total_neto
        })

    return jsonify(data)
