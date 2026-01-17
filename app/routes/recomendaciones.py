from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date
from calendar import monthrange
from app.models import db
import locale

recomendaciones = Blueprint(
    'recomendaciones',
    __name__,
    url_prefix='/recomendaciones'
)

from app.models import Pago, GastoTrabajo
from sqlalchemy import func

def total_neto_mes(usuario_id, year, month):
    inicio = date(year, month, 1)
    fin = date(year, month, monthrange(year, month)[1])

    total_ingresos = db.session.query(
        func.coalesce(func.sum(Pago.monto), 0)
    ).filter(
        Pago.usuario_id == usuario_id,
        Pago.fecha.between(inicio, fin)
    ).scalar()

    total_gastos = db.session.query(
        func.coalesce(func.sum(GastoTrabajo.monto), 0)
    ).filter(
        GastoTrabajo.usuario_id == usuario_id,
        GastoTrabajo.fecha.between(inicio, fin)
    ).scalar()

    return total_ingresos - total_gastos



@recomendaciones.route('/')
@login_required
def index():
    hoy = date.today()

    # locale en español
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

    # mes actual y anterior
    meses = []

    meses.append((hoy.year, hoy.month))

    if hoy.month == 1:
        meses.append((hoy.year - 1, 12))
    else:
        meses.append((hoy.year, hoy.month - 1))

    datos = []

    for year, month in meses:
        total = total_neto_mes(current_user.id, year, month)

        total_ahorrable = max(total, 0)

        fecha = date(year, month, 1)

        datos.append({
            "year": year,
            "month": month,
            "mes_formateado": fecha.strftime("%B de %Y").capitalize(),
            "total": total,
            "ahorros": {
                "Conservador": {
                    "porcentaje": 10,
                    "monto": round(total_ahorrable * 0.10, 2)
                },
                "Equilibrado": {
                    "porcentaje": 20,
                    "monto": round(total_ahorrable * 0.20, 2)
                },
                "Ambicioso": {
                    "porcentaje": 30,
                    "monto": round(total_ahorrable * 0.30, 2)
                }
            }
        })


    return render_template(
        "recomendaciones.html",
        datos=datos
    )
