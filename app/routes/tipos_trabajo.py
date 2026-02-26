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

    # Verificación robusta usando join
    existe_trabajo = (
        db.session.query(Trabajo.id)
        .filter(
            Trabajo.tipo_id == tipo.id,
            Trabajo.usuario_id == current_user.id
        )
        .first()
    )
    
    print("Trabajos asociados:", tipo.trabajos)

    if tipo.trabajos:
        return jsonify(
            {'error': 'No se puede eliminar: tiene trabajos asociados'},
        ), 400
        

    db.session.delete(tipo)
    db.session.commit()

    return jsonify({'success': True})





@tipos_trabajo.route('/<int:tipo_id>/resumen')
@login_required
def resumen_por_mes(tipo_id):

    # -------- FILTRO DINÁMICO --------
    if tipo_id == 0:
        filtro_tipo = Trabajo.tipo_id.is_(None)
    else:
        filtro_tipo = Trabajo.tipo_id == tipo_id

    # -------- INGRESOS (por fecha del PAGO) --------
    ingresos = (
        db.session.query(
            func.strftime('%m-%Y', Pago.fecha).label('mes'),
            func.sum(Pago.monto).label('bruto')
        )
        .join(Trabajo, Pago.trabajo_id == Trabajo.id)
        .filter(
            filtro_tipo,
            Trabajo.usuario_id == current_user.id
        )
        .group_by('mes')
        .all()
    )

    # -------- GASTOS (por fecha del GASTO) --------
    gastos = (
        db.session.query(
            func.strftime('%m-%Y', GastoTrabajo.fecha).label('mes'),
            func.sum(GastoTrabajo.monto).label('gasto')
        )
        .join(Trabajo, GastoTrabajo.trabajo_id == Trabajo.id)
        .filter(
            filtro_tipo,
            Trabajo.usuario_id == current_user.id
        )
        .group_by('mes')
        .all()
    )

    # -------- UNIR RESULTADOS --------
    resumen = {}

    for r in ingresos:
        resumen[r.mes] = {
            "mes": r.mes,
            "bruto": float(r.bruto or 0),
            "gasto": 0.0
        }

    for g in gastos:
        if g.mes not in resumen:
            resumen[g.mes] = {
                "mes": g.mes,
                "bruto": 0.0,
                "gasto": float(g.gasto or 0)
            }
        else:
            resumen[g.mes]["gasto"] = float(g.gasto or 0)

    # Calcular neto y ordenar por mes
    resultado = []
    for mes in sorted(resumen.keys()):
        bruto = resumen[mes]["bruto"]
        gasto = resumen[mes]["gasto"]

        resultado.append({
            "mes": mes,
            "bruto": bruto,
            "gasto": gasto,
            "neto": bruto - gasto
        })

    return jsonify(resultado)


@tipos_trabajo.route('/<int:tipo_id>/detalle/<mes>')
@login_required
def detalle_mes(tipo_id, mes):

    mes_num, anio = mes.split("-")

    # -------- FILTRO DINÁMICO --------
    if tipo_id == 0:
        filtro_tipo = Trabajo.tipo_id.is_(None)
    else:
        filtro_tipo = Trabajo.tipo_id == tipo_id

    # -------- PAGOS DEL MES --------
    pagos = (
        db.session.query(Pago, Trabajo)
        .join(Trabajo, Pago.trabajo_id == Trabajo.id)
        .filter(
            filtro_tipo,
            Trabajo.usuario_id == current_user.id,
            extract('month', Pago.fecha) == int(mes_num),
            extract('year', Pago.fecha) == int(anio)
        )
        .all()
    )

    # -------- GASTOS DEL MES --------
    gastos = (
        db.session.query(GastoTrabajo, Trabajo)
        .join(Trabajo, GastoTrabajo.trabajo_id == Trabajo.id)
        .filter(
            filtro_tipo,
            Trabajo.usuario_id == current_user.id,
            extract('month', GastoTrabajo.fecha) == int(mes_num),
            extract('year', GastoTrabajo.fecha) == int(anio)
        )
        .all()
    )

    data = []

    # Agregar pagos
    for pago, trabajo in pagos:
        data.append({
            "fecha": pago.fecha.strftime("%d/%m"),
            "tipo": trabajo.tipo.nombre if trabajo.tipo else "Sin tipo",
            "trabajo": trabajo.nombre,
            "bruto": float(pago.monto),
            "gasto": 0.0,
            "neto": float(pago.monto)
        })

    # Agregar gastos
    for gasto, trabajo in gastos:
        data.append({
            "fecha": gasto.fecha.strftime("%d/%m"),
            "tipo": trabajo.tipo.nombre if trabajo.tipo else "Sin tipo",
            "trabajo": trabajo.nombre,
            "bruto": 0.0,
            "gasto": float(gasto.monto),
            "neto": -float(gasto.monto)
        })

    # Ordenar por fecha
    data.sort(key=lambda x: x["fecha"])

    return jsonify(data)