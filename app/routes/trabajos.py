from flask import Blueprint, render_template, jsonify, request
from app.models import GastoTrabajo, Pago, TipoTrabajo, db, Trabajo
from flask_login import login_required, current_user


trabajos = Blueprint(
    'trabajos',
    __name__,
    url_prefix='/trabajos'
)


@trabajos.route('/')
@login_required
def index():
    trabajos = (
        Trabajo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Trabajo.fecha.desc())
        .all()
    )

    tipos = TipoTrabajo.query.all()

    tipos_serializados = [
        {"id": t.id, "nombre": t.nombre}
        for t in tipos
    ]

    return render_template(
        'trabajos.html',
        trabajos=trabajos,
        tipos=tipos_serializados
    )




@trabajos.route('/detalle/<int:trabajo_id>')
@login_required
def detalle(trabajo_id):
    trabajo = (
        Trabajo.query
        .filter_by(id=trabajo_id, usuario_id=current_user.id)
        .first_or_404()
    )

    return jsonify({
        "pagos": [
            {
                "id": p.id,
                "fecha": p.fecha.strftime("%d/%m/%Y"),
                "monto": p.monto
            } for p in trabajo.pagos
        ],
        "gastos": [
            {
                "id": g.id,
                "insumo": g.insumo.nombre,
                "monto": g.monto,
                "tiempo": g.tiempo
            } for g in trabajo.gastos
        ],
        "bruto": trabajo.ingreso_total_bruto,
        "gastos_total": trabajo.gasto_total,
        "neto": trabajo.ingreso_total_neto,
        "horas_totales": trabajo.horas_totales
    })



@trabajos.route('/eliminar/<int:trabajo_id>', methods=['POST'])
@login_required
def eliminar(trabajo_id):
    trabajo = (
        Trabajo.query
        .filter_by(id=trabajo_id, usuario_id=current_user.id)
        .first_or_404()
    )

    db.session.delete(trabajo)
    db.session.commit()
    return jsonify({"success": True})








@trabajos.route("/eliminar/pago/<int:id>", methods=["DELETE"])
@login_required
def eliminar_pago(id):
    pago = (
        Pago.query
        .join(Pago.trabajo)
        .filter(
            Pago.id == id,
            Pago.trabajo.has(usuario_id=current_user.id)
        )
        .first_or_404()
    )

    db.session.delete(pago)
    db.session.commit()
    return jsonify(success=True)



@trabajos.route("/eliminar/gasto/<int:id>", methods=["DELETE"])
@login_required
def eliminar_gasto(id):
    gasto = (
        GastoTrabajo.query
        .join(GastoTrabajo.trabajo)
        .filter(
            GastoTrabajo.id == id,
            GastoTrabajo.trabajo.has(usuario_id=current_user.id)
        )
        .first_or_404()
    )

    db.session.delete(gasto)
    db.session.commit()
    return jsonify(success=True)






from datetime import datetime

@trabajos.route("/editar/<int:trabajo_id>", methods=["PUT"])
@login_required
def editar_trabajo(trabajo_id):
    trabajo = (
        Trabajo.query
        .filter_by(id=trabajo_id, usuario_id=current_user.id)
        .first_or_404()
    )

    data = request.get_json()

    trabajo.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d")
    trabajo.nombre = data["nombre"]
    trabajo.tipo_id = int(data["tipo_id"])

    db.session.commit()
    return jsonify(success=True)




@trabajos.route("/nuevo", methods=["POST"])
@login_required
def nuevo_trabajo():
    data = request.get_json()

    trabajo = Trabajo(
        nombre=data["nombre"],
        fecha=datetime.strptime(data["fecha"], "%Y-%m-%d"),
        tipo_id=int(data["tipo_id"]),
        usuario_id=current_user.id
    )

    db.session.add(trabajo)
    db.session.commit()

    return jsonify(success=True)




@trabajos.route("/tipos/nuevo", methods=["POST"])
@login_required
def nuevo_tipo():
    data = request.get_json()

    tipo = TipoTrabajo(
        nombre=data["nombre"],
        usuario_id=current_user.id
    )

    db.session.add(tipo)
    db.session.commit()

    return jsonify({
        "id": tipo.id,
        "nombre": tipo.nombre
    })
