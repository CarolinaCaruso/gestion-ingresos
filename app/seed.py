from datetime import date
from app.models import (
    db,
    Usuario,
    TipoTrabajo,
    Trabajo,
    Pago,
    Insumo,
    GastoTrabajo
)

def run_seed():

    # ================= USUARIO =================
    usuario = Usuario(
        email="carolinabcaruso@gmail.com",
        nombre="Carolina"
    )
    db.session.add(usuario)
    db.session.commit()  # 🔴 importante para tener usuario.id

    # ================= TIPOS DE TRABAJO =================
    tipos = ["mural", "cuadro", "evento", "contenido", "edicion"]
    tipos_trabajo = {}

    for nombre in tipos:
        tipo = TipoTrabajo(
            nombre=nombre,
            usuario_id=usuario.id
        )
        db.session.add(tipo)
        tipos_trabajo[nombre] = tipo

    # ================= INSUMOS =================
    nombres_insumos = ["uber", "colectivo", "comida", "pinturas", "bastidores"]
    insumos = {}

    for nombre in nombres_insumos:
        insumo = Insumo(
            nombre=nombre,
            usuario_id=usuario.id
        )
        db.session.add(insumo)
        insumos[nombre] = insumo

    db.session.commit()

    # ================= TRABAJO 1 =================
    trabajo1 = Trabajo(
        nombre="Mural Coco",
        fecha=date(2024, 1, 1),
        tipo=tipos_trabajo["mural"],
        usuario_id=usuario.id
    )
    db.session.add(trabajo1)

    db.session.add_all([
        Pago(fecha=date(2024, 1, 1), monto=30000, trabajo=trabajo1, usuario_id=usuario.id),
        Pago(fecha=date(2024, 1, 3), monto=50000, trabajo=trabajo1, usuario_id=usuario.id),
        Pago(fecha=date(2024, 1, 10), monto=20000, trabajo=trabajo1, usuario_id=usuario.id)
    ])

    db.session.add_all([
        GastoTrabajo(
            fecha=date(2024, 1, 2),
            trabajo=trabajo1,
            insumo=insumos["pinturas"],
            monto=5000,
            usuario_id=usuario.id
        ),
        GastoTrabajo(
            fecha=date(2024, 1, 5),
            trabajo=trabajo1,
            insumo=insumos["colectivo"],
            monto=350,
            tiempo=2,
            usuario_id=usuario.id
        )
    ])

    # ================= TRABAJO 2 =================
    trabajo2 = Trabajo(
        nombre="Cuadro Abstracto Azul",
        fecha=date(2024, 2, 10),
        tipo=tipos_trabajo["cuadro"],
        usuario_id=usuario.id
    )
    db.session.add(trabajo2)

    db.session.add_all([
        Pago(fecha=date(2024, 2, 10), monto=20000, trabajo=trabajo2, usuario_id=usuario.id),
        Pago(fecha=date(2024, 2, 15), monto=15000, trabajo=trabajo2, usuario_id=usuario.id)
    ])

    db.session.add_all([
        GastoTrabajo(
            fecha=date(2024, 2, 11),
            trabajo=trabajo2,
            insumo=insumos["bastidores"],
            monto=4000,
            usuario_id=usuario.id
        ),
        GastoTrabajo(
            fecha=date(2024, 2, 12),
            trabajo=trabajo2,
            insumo=insumos["comida"],
            monto=2500,
            tiempo=1.5,
            usuario_id=usuario.id
        )
    ])

    # ================= TRABAJO 3 =================
    trabajo3 = Trabajo(
        nombre="Contenido Instagram Febrero",
        fecha=date(2024, 2, 1),
        tipo=tipos_trabajo["contenido"],
        usuario_id=usuario.id
    )
    db.session.add(trabajo3)

    db.session.add_all([
        Pago(fecha=date(2024, 2, 5), monto=18000, trabajo=trabajo3, usuario_id=usuario.id),
        Pago(fecha=date(2024, 2, 20), monto=12000, trabajo=trabajo3, usuario_id=usuario.id)
    ])

    db.session.add_all([
        GastoTrabajo(
            fecha=date(2024, 2, 3),
            trabajo=trabajo3,
            insumo=insumos["uber"],
            monto=1200,
            tiempo=0.5,
            usuario_id=usuario.id
        ),
        GastoTrabajo(
            fecha=date(2024, 2, 18),
            trabajo=trabajo3,
            insumo=insumos["comida"],
            monto=3000,
            tiempo=2,
            usuario_id=usuario.id
        )
    ])

    # ================= TRABAJO 4 =================
    trabajo4 = Trabajo(
        nombre="Evento Feria de Arte",
        fecha=date(2024, 3, 5),
        tipo=tipos_trabajo["evento"],
        usuario_id=usuario.id
    )
    db.session.add(trabajo4)

    db.session.add_all([
        Pago(fecha=date(2024, 3, 5), monto=60000, trabajo=trabajo4, usuario_id=usuario.id),
        Pago(fecha=date(2024, 3, 7), monto=25000, trabajo=trabajo4, usuario_id=usuario.id)
    ])

    db.session.add_all([
        GastoTrabajo(
            fecha=date(2024, 3, 5),
            trabajo=trabajo4,
            insumo=insumos["uber"],
            monto=3000,
            tiempo=1,
            usuario_id=usuario.id
        ),
        GastoTrabajo(
            fecha=date(2024, 3, 6),
            trabajo=trabajo4,
            insumo=insumos["comida"],
            monto=4500,
            tiempo=3,
            usuario_id=usuario.id
        )
    ])

    # ================= TRABAJO 5 =================
    trabajo5 = Trabajo(
        nombre="Edición Video YouTube",
        fecha=date(2024, 3, 20),
        tipo=tipos_trabajo["edicion"],
        usuario_id=usuario.id
    )
    db.session.add(trabajo5)

    db.session.add_all([
        Pago(fecha=date(2024, 3, 22), monto=35000, trabajo=trabajo5, usuario_id=usuario.id)
    ])

    db.session.add_all([
        GastoTrabajo(
            fecha=date(2024, 3, 21),
            trabajo=trabajo5,
            insumo=insumos["comida"],
            monto=1800,
            tiempo=2.5,
            usuario_id=usuario.id
        )
    ])

    db.session.commit()
