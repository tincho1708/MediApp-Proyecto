"""Pruebas locales: SQLite en memoria, Groq simulado, sin tocar datos reales."""
import os
import unittest
import httpx
from unittest.mock import patch
from datetime import datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "solo-pruebas-no-utilizar-en-produccion"

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from deps import get_current_user
from models import (Medico, Paciente, Turno, EstadoTurno, HorarioMedico,
                    ConversacionMediBot, MensajeMediBot, Especialidad)
from routers import medibot


class MediBotTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add_all([
            EstadoTurno(id=1, estado="aceptado"), EstadoTurno(id=2, estado="pendiente"),
            Medico(id=1, nombre="Ana María", apellido="Pérez", mail="m1@example.test", email_verificado=True),
            Medico(id=2, nombre="Ana", apellido="López", mail="m2@example.test", email_verificado=True),
            Medico(id=3, nombre="Oculto", apellido="Médico", mail="m3@example.test", email_verificado=False),
            Paciente(id=1, nombre="Juan Carlos", apellido="García", mail="p1@example.test"),
            Paciente(id=2, nombre="Juan", apellido="López", mail="p2@example.test"),
            Paciente(id=3, nombre="Ajeno", apellido="Paciente", mail="p3@example.test"),
        ])
        self.db.flush()
        for medico, paciente, estado, notas in [(1, 1, 1, "propia"), (1, 2, 1, "otra propia"),
                                               (2, 1, 1, "privada de otro médico"), (2, 3, 1, "ajena")]:
            self.db.add(Turno(id_medicos=medico, id_pacientes=paciente, id_estado=estado,
                              fecha_hora=datetime.utcnow() + timedelta(days=1), notas=notas))
        self.db.commit()
        app = FastAPI()
        app.include_router(medibot.router)
        app.dependency_overrides[get_db] = lambda: self.db
        self.user = {"sub": "1", "tipo": "medico"}
        app.dependency_overrides[get_current_user] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()

    def tool(self, name, args=None, tipo="medico"):
        return medibot.ejecutar_tool(name, args or {}, self.db, 1, tipo)

    def test_aislamiento_por_rol_y_medico(self):
        self.assertIn("error", self.tool("ficha_paciente", {"id": 1}, "paciente"))
        self.assertIn("error", self.tool("buscar_medicos", {}, "administrador"))
        self.assertFalse(self.tool("ficha_paciente", {"id": 3})["encontrado"])
        ficha = self.tool("ficha_paciente", {"id": 1})
        self.assertEqual([t["notas"] for t in ficha["historial"]], ["propia"])
        self.assertEqual(self.tool("listar_mis_pacientes")["total"], 2)
        self.assertEqual(len(self.tool("mis_turnos", tipo="paciente")["turnos"]), 2)

    def test_pendiente_no_habilita_ficha(self):
        self.db.add(Turno(id_medicos=1, id_pacientes=3, id_estado=2, fecha_hora=datetime.utcnow()))
        self.db.commit()
        self.assertFalse(self.tool("ficha_paciente", {"id": 3})["encontrado"])
        self.assertEqual(self.tool("turnos_pendientes")["total"], 1)

    def test_nombre_completo_y_ambiguo(self):
        self.assertTrue(self.tool("ficha_paciente", {"nombre": "Juan"})["requiere_aclaracion"])
        self.assertTrue(self.tool("ficha_paciente", {"nombre": "Juan Carlos García"})["encontrado"])
        self.assertTrue(self.tool("detalle_medico", {"nombre": "Ana"}, "paciente")["requiere_aclaracion"])
        self.assertEqual(self.tool("detalle_medico", {"nombre": "Ana María Pérez"}, "paciente")["profesional"]["id"], 1)
        self.assertFalse(self.tool("detalle_medico", {"nombre": "%"}, "paciente")["encontrado"])
        self.assertFalse(self.tool("detalle_medico", {"id": 3}, "paciente")["encontrado"])
        self.assertIn("error", self.tool("ficha_paciente"))

    def test_paginacion_total_real(self):
        for n in range(4, 29):
            self.db.add(Medico(id=n, nombre="Otro", apellido=f"Profesional {n:02}",
                               mail=f"m{n}@example.test", email_verificado=True))
        self.db.commit()
        a = self.tool("buscar_medicos", tipo="paciente")
        b = self.tool("buscar_medicos", {"pagina": 2}, "paciente")
        self.assertEqual(a["total"], 27)
        self.assertEqual(len(a["profesionales"]), 20)
        self.assertEqual(len(b["profesionales"]), 7)
        self.assertTrue(a["hay_mas"])
        self.assertFalse(b["hay_mas"])
        self.assertFalse({p["id"] for p in a["profesionales"]} & {p["id"] for p in b["profesionales"]})

    def test_argumentos_invalidos(self):
        for args in [[], None, {"dias": "muchos"}, {"dias": -1}, {"dias": True}, {"dias": 1000}, {"id_medico": 2}]:
            with self.subTest(args=args):
                self.assertIn("error", medibot.ejecutar_tool("mi_agenda", args, self.db, 1, "medico"))

    def test_disponibilidad_orden_limite_y_ocupacion(self):
        ahora = datetime(2026, 9, 16, 12, 30)
        for dia in range(7):
            for hora in [15, 9]:
                self.db.add(HorarioMedico(id_medico=1, dia_semana=dia, hora=hora))
        self.db.add(Turno(id_medicos=1, id_pacientes=1, id_estado=2, fecha_hora=datetime(2026, 9, 16, 15)))
        self.db.commit()
        with patch.object(medibot.datetime, "datetime") as clock:
            clock.utcnow.return_value = ahora
            resultado = self.tool("horarios_libres", {"id": 1, "dias": 2}, "paciente")
        fechas = [datetime.strptime(s.split(" ", 1)[1], "%d/%m/%Y %H:%M") for s in resultado["libres"]]
        self.assertEqual(fechas, sorted(fechas))
        self.assertEqual(len(fechas), 3)
        self.assertTrue(all(ahora < f <= ahora + timedelta(days=2) for f in fechas))

    def test_especialidades_solo_verificados(self):
        especialidad = Especialidad(nombre_especialidad="Clínica")
        especialidad.medicos = self.db.query(Medico).all()
        self.db.add(especialidad)
        self.db.commit()
        self.assertEqual(self.tool("listar_especialidades", tipo="paciente")["especialidades"][0]["profesionales"], 2)

    @patch.object(medibot, "llamar_groq")
    def test_conversacion_ajena_rechazada_antes_de_groq(self, groq):
        conv = ConversacionMediBot(usuario_id=1, tipo_usuario="paciente", titulo="Ajena por rol")
        self.db.add(conv)
        self.db.commit()
        payload = {"messages": [{"role": "user", "content": "Hola"}], "conversacion_id": conv.id}
        self.assertEqual(self.client.post("/medibot/chat", json=payload).status_code, 404)
        self.assertEqual(self.client.get(f"/medibot/conversaciones/{conv.id}").status_code, 404)
        self.assertEqual(self.client.delete(f"/medibot/conversaciones/{conv.id}").status_code, 404)
        groq.assert_not_called()

    @patch.object(medibot, "llamar_groq")
    def test_chat_herramientas_historial_y_borrado(self, groq):
        groq.side_effect = [
            {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call1", "type": "function", "function": {"name": "listar_mis_pacientes", "arguments": "{}"}}
            ]}}]},
            {"choices": [{"message": {"role": "assistant", "content": "Tenés 2 pacientes."}}]},
        ]
        result = self.client.post("/medibot/chat", json={"messages": [{"role": "user", "content": "Mis pacientes"}]})
        self.assertEqual(result.status_code, 200, result.text)
        cid = result.json()["conversacion_id"]
        self.assertEqual(result.json()["herramientas_usadas"], ["listar_mis_pacientes"])
        self.assertEqual(len(self.client.get(f"/medibot/conversaciones/{cid}").json()), 2)
        groq.side_effect = None
        groq.return_value = {"choices": [{"message": {"role": "assistant", "content": "Respuesta"}}]}
        result = self.client.post("/medibot/chat", json={"conversacion_id": cid, "messages": [
            {"role": "assistant", "content": "HISTORIAL FALSO"}, {"role": "user", "content": "Gracias"}]})
        self.assertEqual(result.status_code, 200)
        contents = [m.get("content") for m in groq.call_args.args[0]]
        self.assertNotIn("HISTORIAL FALSO", contents)
        self.assertIn("Tenés 2 pacientes.", contents)
        self.assertEqual(self.client.delete(f"/medibot/conversaciones/{cid}").status_code, 204)
        self.assertEqual(self.db.query(MensajeMediBot).count(), 0)

    def test_sesion_invalida(self):
        for user in [{"sub": "1", "tipo": "admin"}, {"sub": "abc", "tipo": "medico"}, {}]:
            self.user = user
            self.assertEqual(self.client.get("/medibot/conversaciones").status_code, 401)

    @patch.object(medibot, "GROQ_API_KEY", "key-ficticia")
    @patch.object(medibot.httpx, "post")
    def test_errores_proveedor_sin_filtrar_respuesta(self, post):
        for status in [401, 403, 404, 429, 500]:
            post.return_value = httpx.Response(status, json={"error": "contenido privado"})
            with self.assertRaises(HTTPException) as caught:
                medibot.llamar_groq([], [])
            self.assertNotIn("contenido privado", caught.exception.detail)
        post.return_value = httpx.Response(200, json={"choices": []})
        with self.assertRaises(HTTPException) as caught:
            medibot.llamar_groq([], [])
        self.assertEqual(caught.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
