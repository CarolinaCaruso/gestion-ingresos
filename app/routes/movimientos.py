from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date, datetime
from app.models import (
    TipoTrabajo,
    db,
    Trabajo,
    Pago,
    GastoTrabajo,
    Insumo
)

movimientos = Blueprint(
    "movimientos",
    __name__,
    url_prefix="/movimientos"
)


# ===========================
# NUEVO MOVIMIENTO (VISTA)
# ===========================
@movimientos.route("/nuevo")
@login_required
def nuevo():
    trabajos = (
        Trabajo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Trabajo.fecha.desc())
        .all()
    )

    insumos = (
        Insumo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Insumo.nombre)
        .all()
    )

    tipos_trabajo = (
        TipoTrabajo.query
        .filter_by(usuario_id=current_user.id)
        .order_by(TipoTrabajo.nombre)
        .all()
    )

    return render_template(
        "nuevo_movimiento.html",
        trabajos=trabajos,
        insumos=insumos,
        tipos_trabajo=tipos_trabajo,
        hoy=date.today().isoformat()
    )


# ===========================
# GUARDAR MOVIMIENTO
# ===========================
@movimientos.route("/guardar", methods=["POST"])
@login_required
def guardar():
    data = request.json

    if not data.get("tipo"):
        return jsonify(error="Tipo de movimiento requerido"), 400

    fecha_mov = datetime.strptime(data["fecha"], "%Y-%m-%d").date()

    # ================= TIPO DE TRABAJO =================
    tipo_trabajo = None

    if data["trabajo_id"] == "nuevo":

        if data.get("tipo_trabajo_id") == "nuevo":
            if not data.get("nuevo_tipo_trabajo"):
                return jsonify(error="Nombre de tipo requerido"), 400

            tipo_trabajo = TipoTrabajo(
                nombre=data["nuevo_tipo_trabajo"],
                usuario_id=current_user.id
            )
            db.session.add(tipo_trabajo)
            db.session.flush()

        else:
            tipo_trabajo = TipoTrabajo.query.filter_by(
                id=int(data["tipo_trabajo_id"]),
                usuario_id=current_user.id
            ).first_or_404()

    # ================= TRABAJO =================
    if data["trabajo_id"] == "nuevo":
        trabajo = Trabajo(
            nombre=data["nuevo_trabajo"],
            fecha=datetime.strptime(
                data["fecha_trabajo"], "%Y-%m-%d"
            ).date(),
            tipo_id=tipo_trabajo.id,
            usuario_id=current_user.id
        )
        db.session.add(trabajo)
        db.session.flush()

    else:
        trabajo = Trabajo.query.filter_by(
            id=int(data["trabajo_id"]),
            usuario_id=current_user.id
        ).first_or_404()

    # ================= INGRESO =================
    if data["tipo"] == "ingreso":
        pago = Pago(
            fecha=fecha_mov,
            monto=float(data["monto"]),
            trabajo_id=trabajo.id,
            usuario_id=current_user.id
        )
        db.session.add(pago)

    # ================= GASTO =================
    else:
        insumo = Insumo.query.filter_by(
            id=int(data["insumo_id"]),
            usuario_id=current_user.id
        ).first_or_404()

        gasto = GastoTrabajo(
            fecha=fecha_mov,
            monto=float(data["monto"]) if data.get("monto") else 0,
            tiempo=float(data["tiempo"]) if data.get("tiempo") else 0,
            trabajo_id=trabajo.id,
            insumo_id=insumo.id,
            usuario_id=current_user.id
        )
        db.session.add(gasto)

    db.session.commit()
    return jsonify(success=True)







# ===========================
# RESUMEN ANUAL
# ===========================
@movimientos.route("/resumen-anual")
@login_required
def resumen_anual():
    # ---------------------------
    # INGRESOS POR AÑO
    # ---------------------------
    ingresos_por_anio = (
        db.session.query(
            db.extract("year", Pago.fecha).label("anio"),
            db.func.sum(Pago.monto).label("ingreso_bruto")
        )
        .filter(Pago.usuario_id == current_user.id)
        .group_by("anio")
        .all()
    )

    ingresos_dict = {
        int(row.anio): row.ingreso_bruto or 0
        for row in ingresos_por_anio
    }

    # ---------------------------
    # GASTOS POR AÑO
    # ---------------------------
    gastos_por_anio = (
        db.session.query(
            db.extract("year", GastoTrabajo.fecha).label("anio"),
            db.func.sum(GastoTrabajo.monto).label("gastos")
        )
        .filter(GastoTrabajo.usuario_id == current_user.id)
        .group_by("anio")
        .all()
    )

    gastos_dict = {
        int(row.anio): row.gastos or 0
        for row in gastos_por_anio
    }

    # ---------------------------
    # UNIR AÑOS
    # ---------------------------
    anios = sorted(set(ingresos_dict.keys()) | set(gastos_dict.keys()))

    resumen_anual = []

    for anio in anios:
        ingreso_bruto = ingresos_dict.get(anio, 0)
        gastos = gastos_dict.get(anio, 0)

        resumen_anual.append({
            "anio": anio,
            "ingreso_bruto": round(ingreso_bruto, 2),
            "gastos": round(gastos, 2),
            "ingreso_neto": round(ingreso_bruto - gastos, 2)
        })

    return render_template(
        "resumen_anual.html",
        resumen_anual=resumen_anual
    )
