from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from app.models import db, Pago, GastoTrabajo
from sqlalchemy import extract
from collections import defaultdict

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    pagos = (
        Pago.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Pago.fecha.desc())
        .all()
    )


    gastos = (
        GastoTrabajo.query
        .join(GastoTrabajo.trabajo)
        .filter_by(usuario_id=current_user.id)
        .order_by(GastoTrabajo.id.desc())
        .all()
    )


    resumen = defaultdict(lambda: {
        "pagos": [],
        "gastos": [],
        "total_ingresos": 0,
        "total_gastos": 0
    })

    for p in pagos:
        key = p.fecha.strftime("%Y-%m")
        resumen[key]["pagos"].append(p)
        resumen[key]["total_ingresos"] += p.monto

    for g in gastos:
        key = g.fecha.strftime("%Y-%m")
        resumen[key]["gastos"].append(g)
        resumen[key]["total_gastos"] += g.monto

    resumen_ordenado = dict(
        sorted(resumen.items(), reverse=True)
    )



    resumen_final = []

    for key, data in resumen_ordenado.items():
        year, month = key.split("-")
        fecha = datetime(int(year), int(month), 1)

        resumen_final.append({
            "label": fecha.strftime("%B %Y").capitalize(),  # "Enero 2025"
            "pagos": data["pagos"],
            "gastos": data["gastos"],
            "total_ingresos": data["total_ingresos"],
            "total_gastos": data["total_gastos"],
            "neto": data["total_ingresos"] - data["total_gastos"]
         })


    return render_template(
        "index.html",
        meses=resumen_final
    )



from flask import Blueprint, jsonify
from app.models import db, Pago, GastoTrabajo


@main.route("/eliminar/pago/<int:id>", methods=["DELETE"])
@login_required
def eliminar_pago(id):
    pago = Pago.query.filter_by(
        id=id,
        usuario_id=current_user.id
    ).first_or_404()

    db.session.delete(pago)
    db.session.commit()
    return jsonify(success=True)



@main.route("/eliminar/gasto/<int:id>", methods=["DELETE"])
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
