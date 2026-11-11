<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['ir-a-registro', 'ir-a-login'])

const enlaces = [
  { id: 'que-es', texto: 'Qué es MediApp' },
  { id: 'como-funciona', texto: 'Cómo funciona' },
  { id: 'medibot', texto: 'MediBot' },
  { id: 'planes', texto: 'Planes' },
]
const ORDEN = ['que-es', 'como-funciona', 'planes', 'medibot']

const lados = [
  {
    etiqueta: 'Pacientes',
    titulo: ['Encontrá y coordiná', 'con tranquilidad.'],
    texto: 'La información que necesitás para dar el próximo paso.',
    items: ['Buscá por especialidad y conocé al profesional.', 'Elegí un turno y consultá tu calendario.', 'Accedé a las fichas que comparten con vos.'],
    boton: 'Buscar profesional',
    destacado: false,
  },
  {
    etiqueta: 'Profesionales',
    titulo: ['Tu agenda,', 'a tu manera.'],
    texto: 'Más orden para dedicarte a lo que mejor hacés.',
    items: ['Definí horarios, pausas y disponibilidad.', 'Gestioná solicitudes y organizá tus pacientes.', 'Registrá y compartí la información de cada consulta.'],
    boton: 'Conocer las herramientas',
    destacado: true,
  },
]

const pasos = [
  { numero: '01', titulo: ['Encontrá tu', 'profesional'], texto: 'Explorá especialidades y consultá el perfil del profesional antes de elegir.', etiquetas: 'Especialidad · Perfil · Información' },
  { numero: '02', titulo: ['Elegí fecha', 'y horario'], texto: 'Seleccioná el tipo de turno, revisá la disponibilidad y confirmá tus datos.', etiquetas: 'Profesional · Fecha · Revisar · Confirmar' },
  { numero: '03', titulo: ['Seguí tu', 'atención'], texto: 'Consultá el estado de tu turno y accedé a las fichas compartidas después de la consulta.', etiquetas: 'Calendario · Notificaciones · Fichas' },
]

const planes = [
  { etiqueta: 'Para comenzar', nombre: 'MediApp Basic', texto: 'Tu presencia y tu agenda en un mismo lugar.', items: ['Perfil profesional', 'Gestión de turnos', 'Información con límites del plan'], boton: 'Conocer Basic', destacado: false },
  { etiqueta: 'Más herramientas', nombre: 'MediApp+', texto: 'Más capacidad para hacer crecer tu práctica.', items: ['Todo lo incluido en Basic', 'Prioridad en el buscador', 'Información de turnos sin límite de caracteres', 'Conexiones ilimitadas'], boton: 'Conocer MediApp+', destacado: true },
  { etiqueta: 'Para equipos', nombre: 'MediApp Business', texto: 'Organización compartida para tu equipo.', items: ['Todo lo incluido en MediApp+', 'Hasta 50 usuarios', 'Conexiones ilimitadas'], boton: 'Conocer Business', destacado: false },
]

const dias = [
  { nombre: 'LUN', numero: 12 },
  { nombre: 'MAR', numero: 13 },
  { nombre: 'MIÉ', numero: 14 },
  { nombre: 'JUE', numero: 15 },
  { nombre: 'VIE', numero: 16 },
  { nombre: 'SÁB', numero: 17 },
  { nombre: 'DOM', numero: 18 },
]

const documentos = {
  terminos: {
    titulo: 'Términos y condiciones',
    secciones: [
      { titulo: '1. Uso de MediApp', texto: 'MediApp es una plataforma que conecta pacientes con profesionales de la salud para buscar profesionales, reservar turnos y compartir información de las consultas. Al crear una cuenta aceptás estos términos.' },
      { titulo: '2. Cuentas', texto: 'Sos responsable de que tus datos sean correctos y de cuidar tu contraseña. Cada cuenta es personal y no se puede compartir.' },
      { titulo: '3. Turnos', texto: 'Los turnos quedan sujetos a la confirmación del profesional. Si no podés asistir, cancelalo con anticipación desde la plataforma.' },
      { titulo: '4. Profesionales', texto: 'Cada profesional es responsable de la atención que brinda, de la información que comparte y de mantener sus horarios actualizados.' },
      { titulo: '5. MediBot', texto: 'MediBot orienta sobre el uso de la plataforma. No da diagnósticos ni reemplaza la consulta con un profesional.' },
      { titulo: '6. Cambios', texto: 'Podemos actualizar estos términos. Si hay cambios importantes, te vamos a avisar dentro de la plataforma.' },
    ],
  },
  privacidad: {
    titulo: 'Política de privacidad',
    secciones: [
      { titulo: '1. Datos que guardamos', texto: 'Guardamos los datos de tu cuenta (nombre, correo, teléfono y los que completes en tu perfil), tus turnos y las fichas que comparten los profesionales.' },
      { titulo: '2. Para qué los usamos', texto: 'Los usamos solo para que la plataforma funcione: mostrar profesionales, gestionar turnos y enviarte notificaciones.' },
      { titulo: '3. Quién los ve', texto: 'Tus fichas solo las ven vos y el profesional que las compartió. No vendemos ni compartimos tus datos con terceros.' },
      { titulo: '4. Tus derechos', texto: 'Podés ver y modificar tus datos desde la configuración de tu cuenta, o pedirnos que los eliminemos.' },
    ],
  },
}
const documentoAbierto = ref<keyof typeof documentos | null>(null)

const hero = ref<HTMLElement | null>(null)
const navBlanca = ref(false)
const activa = ref('')

function revisarScroll() {
  navBlanca.value = window.scrollY > (hero.value?.offsetHeight ?? 0) - 80
  activa.value = ORDEN.filter((id) => (document.getElementById(id)?.offsetTop ?? Infinity) - 120 <= window.scrollY).pop() ?? ''
}

function irA(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', revisarScroll)
  revisarScroll()
})
onBeforeUnmount(() => window.removeEventListener('scroll', revisarScroll))
</script>

<template>
  <div class="font-['Inter'] text-[#182234] bg-white">
    <nav class="fixed inset-x-0 top-0 z-50 h-16 lg:h-18 px-4 lg:px-26 flex items-center justify-between gap-4 transition-colors duration-300" :class="navBlanca ? 'bg-white border-b border-[#D7E2F0] shadow-[0_0.1875rem_0.625rem_0_rgba(24,34,52,0.04)]' : 'bg-[#0A1424]/30 backdrop-blur-sm'">
      <button class="flex items-center gap-1 cursor-pointer" @click="irA('inicio')">
        <img src="@/assets/imagenes/imagen-logo.png" alt="Logo MediApp" class="size-10 lg:size-12" />
        <span class="text-[22px] lg:text-[1.75rem] font-semibold" :class="navBlanca ? 'text-[#1F6FC9]' : 'text-white'">App</span>
      </button>

      <div class="hidden lg:flex items-center gap-8 text-sm font-medium">
        <button v-for="e in enlaces" :key="e.id" class="cursor-pointer transition-colors" :class="navBlanca ? (activa === e.id ? 'text-[#1F6FC9]' : 'text-[#182234] hover:text-[#1F6FC9]') : 'text-white hover:text-white/70'" @click="irA(e.id)">{{ e.texto }}</button>
      </div>

      <div class="flex items-center gap-3 lg:gap-6">
        <button class="text-[15px] lg:text-sm font-medium cursor-pointer hover:opacity-80" :class="navBlanca ? 'text-[#1F6FC9]' : 'text-white'" @click="emit('ir-a-login')">Iniciar sesión</button>
        <button class="h-10 lg:h-11 px-4 lg:px-6 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-sm font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-registro')">Crear cuenta →</button>
      </div>
    </nav>

    <section id="inicio" ref="hero" class="relative min-h-screen bg-[#0A1424] overflow-hidden flex flex-col">
      <img src="@/assets/imagenes/landing-hero.jpg" alt="Profesional atendiendo a una paciente" class="absolute inset-y-0 right-0 h-full w-full lg:w-[62%] object-cover object-[60%_center] brightness-125" />
      <div class="absolute inset-0 bg-[#0A1424]/40 lg:bg-[linear-gradient(90deg,#0A1424_38%,rgba(10,20,36,0.35)_46%,rgba(10,20,36,0)_54%)]"></div>

      <div class="relative flex-1 px-4 lg:px-26 pt-28 pb-10 flex flex-col justify-between gap-12">
        <div class="flex-1 flex flex-col justify-center gap-5 lg:gap-6 max-w-2xl">
          <span class="text-[12px] lg:text-[0.7rem] font-medium tracking-wide text-white/80">TU SALUD. TU TIEMPO. TU ESPACIO.</span>
          <h1 class="text-[36px] lg:text-[3.6rem] font-semibold leading-[1.1] text-white">Más cerca de<br />una mejor atención.</h1>
          <p class="text-[17px] lg:text-[1.2rem] leading-relaxed text-white/85">Conectá con profesionales y organizá tus consultas.<br class="hidden lg:block" /> MediApp reúne todo en un mismo lugar.</p>
          <div class="flex flex-col sm:flex-row gap-3 lg:gap-4 pt-2">
            <button class="h-12 lg:h-[2.6rem] sm:w-56 lg:w-52 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-[0.8rem] font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-registro', 'Paciente')">Encontrar profesional</button>
            <button class="h-12 lg:h-[2.6rem] sm:w-56 lg:w-45 rounded-lg bg-white text-[15px] lg:text-[0.8rem] font-medium text-[#1F6FC9] cursor-pointer hover:bg-[#EDF5FF] transition-colors" @click="emit('ir-a-registro', 'Medico')">Soy profesional</button>
          </div>
        </div>

        <button class="self-start text-[15px] lg:text-[0.8rem] font-medium text-white cursor-pointer hover:text-white/70" @click="irA('que-es')">Conocé MediApp ↓</button>
      </div>
    </section>

    <section id="que-es" class="scroll-mt-16 lg:scroll-mt-18 bg-[#F4F7FB] px-4 lg:px-26 py-16 lg:py-19 flex flex-col gap-10 lg:gap-11">
      <div class="flex flex-col gap-3 lg:gap-2.5">
        <span class="text-[12px] lg:text-[0.65rem] font-semibold text-[#1F6FC9]">UNA PLATAFORMA, DOS LADOS</span>
        <h2 class="text-[28px] lg:text-[2.4rem] font-semibold leading-tight">La misma conexión. Distintas necesidades.</h2>
        <p class="text-[16px] lg:text-[0.95rem] text-[#61718B]">Herramientas para quienes buscan atención y para quienes la brindan.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 lg:gap-[1.4rem]">
        <article v-for="lado in lados" :key="lado.etiqueta" class="p-6 lg:p-[1.8rem] lg:min-h-104 rounded-2xl border border-[#D7E2F0] flex flex-col gap-4 lg:gap-[1.1rem]" :class="lado.destacado ? 'bg-[#EDF5FF]' : 'bg-white'">
          <span class="text-[12px] lg:text-[0.65rem] font-semibold uppercase text-[#1F6FC9]">{{ lado.etiqueta }}</span>
          <h3 class="text-[22px] lg:text-[1.75rem] font-semibold leading-tight">{{ lado.titulo[0] }}<br />{{ lado.titulo[1] }}</h3>
          <p class="text-[15px] lg:text-[0.85rem] text-[#61718B]">{{ lado.texto }}</p>
          <ul class="flex flex-col gap-3 lg:gap-[0.9rem] text-[15px] lg:text-[0.8rem]">
            <li v-for="item in lado.items" :key="item" class="flex items-start gap-3"><span class="text-[#1F6FC9]">✓</span>{{ item }}</li>
          </ul>
          <button class="self-start mt-2 h-11 lg:h-[2.6rem] px-6 lg:w-54 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-xs font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="lado.destacado ? irA('planes') : emit('ir-a-registro', 'Paciente')">{{ lado.boton }}</button>
        </article>
      </div>
    </section>

    <section id="como-funciona" class="scroll-mt-16 lg:scroll-mt-18 bg-white px-4 lg:px-26 py-16 lg:py-19 flex flex-col gap-10 lg:gap-11">
      <div class="flex flex-col gap-3 lg:gap-2.5">
        <span class="text-[12px] lg:text-[0.65rem] font-semibold text-[#1F6FC9]">CÓMO FUNCIONA</span>
        <h2 class="text-[28px] lg:text-[2.4rem] font-semibold leading-tight">De encontrar un profesional a tener tu turno.</h2>
        <p class="text-[16px] lg:text-[0.95rem] text-[#61718B]">Un recorrido claro, paso a paso.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 lg:gap-[1.1rem]">
        <article v-for="(paso, i) in pasos" :key="paso.numero" class="p-6 lg:p-[1.8rem] lg:min-h-86 rounded-2xl border border-[#D7E2F0] flex flex-col gap-4 lg:gap-[1.1rem]" :class="i === 0 ? 'bg-[#F8FAFD]' : 'bg-[#EDF5FF]'">
          <span class="text-[34px] lg:text-[2.4rem] font-semibold leading-none text-[#1F6FC9]">{{ paso.numero }}</span>
          <h3 class="pt-2 text-[20px] lg:text-[1.4rem] font-semibold leading-tight">{{ paso.titulo[0] }}<br />{{ paso.titulo[1] }}</h3>
          <p class="text-[15px] lg:text-[0.85rem] text-[#61718B]">{{ paso.texto }}</p>
          <span class="text-[12px] lg:text-[0.6rem] font-medium text-[#1F6FC9]">{{ paso.etiquetas }}</span>
        </article>
      </div>

      <button class="self-center h-11 lg:h-[2.6rem] px-8 lg:w-52 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-xs font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-registro', 'Paciente')">Empezar mi búsqueda</button>
    </section>

    <section id="planes" class="scroll-mt-16 lg:scroll-mt-18 bg-[#F4F7FB] px-4 lg:px-26 py-16 lg:py-19 flex flex-col gap-10 lg:gap-11">
      <div class="flex flex-col gap-3 lg:gap-2.5">
        <span class="text-[12px] lg:text-[0.65rem] font-semibold text-[#1F6FC9]">PLANES PARA PROFESIONALES</span>
        <h2 class="text-[28px] lg:text-[2.4rem] font-semibold leading-tight">Un espacio para cada etapa de tu práctica.</h2>
        <p class="text-[16px] lg:text-[0.95rem] text-[#61718B]">Conocé las opciones de MediApp para organizar tu atención.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 lg:gap-[1.1rem]">
        <article v-for="plan in planes" :key="plan.nombre" class="p-6 lg:p-[1.8rem] lg:min-h-104 rounded-2xl border border-[#D7E2F0] flex flex-col gap-4 lg:gap-[1.1rem]" :class="plan.destacado ? 'bg-[#EDF5FF]' : 'bg-white'">
          <span class="text-[12px] lg:text-[0.6rem] font-semibold uppercase text-[#1F6FC9]">{{ plan.etiqueta }}</span>
          <h3 class="text-[22px] lg:text-2xl font-semibold">{{ plan.nombre }}</h3>
          <p class="text-[15px] lg:text-[0.85rem] text-[#61718B]">{{ plan.texto }}</p>
          <ul class="flex flex-col gap-3 lg:gap-[0.9rem] text-[15px] lg:text-[0.8rem]">
            <li v-for="item in plan.items" :key="item" class="flex items-start gap-3"><span class="text-[#1F6FC9]">✓</span>{{ item }}</li>
          </ul>
          <button class="self-start mt-2 h-11 lg:h-[2.6rem] px-6 lg:w-52 rounded-lg text-[15px] lg:text-xs font-medium cursor-pointer transition-colors" :class="plan.destacado ? 'bg-[#1F6FC9] text-white hover:bg-[#185BA6]' : 'bg-[#EDF5FF] text-[#1F6FC9] hover:bg-[#DCEBFE]'" @click="emit('ir-a-registro', 'Medico')">{{ plan.boton }}</button>
        </article>
      </div>
    </section>

    <section id="medibot" class="scroll-mt-16 lg:scroll-mt-18 bg-white px-4 lg:px-26 py-16 lg:py-14 grid grid-cols-1 lg:grid-cols-[1fr_33.5rem] items-center gap-10 lg:gap-20">
      <div class="flex flex-col gap-4 lg:gap-[1.1rem]">
        <span class="text-[12px] lg:text-[0.65rem] font-semibold text-[#1F6FC9]">ASISTENTE DE MEDIAPP</span>
        <h2 class="text-[28px] lg:text-[2.6rem] font-semibold leading-tight">Una ayuda más.<br />Cuando la necesitás.</h2>
        <p class="text-[16px] lg:text-[0.95rem] text-[#61718B] max-w-120">MediBot te orienta dentro de la plataforma y te ayuda a encontrar información y herramientas.</p>
        <span class="text-[15px] lg:text-[0.85rem] font-semibold text-[#1F6FC9]">Para pacientes</span>
        <p class="text-[15px] lg:text-[0.85rem]">Ayuda para buscar profesionales y ubicar tus turnos y fichas.</p>
        <span class="text-[15px] lg:text-[0.85rem] font-semibold text-[#1F6FC9]">Para profesionales</span>
        <p class="text-[15px] lg:text-[0.85rem]">Apoyo en la redacción de informes y tareas administrativas.</p>
        <button class="self-start mt-1 h-11 lg:h-[2.6rem] px-6 lg:w-46 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-xs font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-registro')">Conocer MediBot</button>
      </div>

      <div class="p-6 lg:p-[1.8rem] bg-[#EDF5FF] rounded-2xl border border-[#D7E2F0] flex flex-col gap-4 lg:gap-[1.1rem]">
        <div class="flex flex-col gap-1">
          <span class="text-[20px] lg:text-[1.4rem] font-semibold text-[#1F6FC9]">MediBot</span>
          <span class="text-[13px] lg:text-[0.7rem] text-[#61718B]">Tu asistente en MediApp</span>
        </div>
        <div class="px-4 lg:px-[1.1rem] py-4 lg:py-[1.4rem] bg-white rounded-xl text-[15px] lg:text-[0.8rem]">¿Dónde puedo ver mis fichas médicas?</div>
        <div class="px-4 lg:px-[1.1rem] py-4 lg:py-[1.4rem] bg-white rounded-xl flex flex-col gap-3 lg:gap-[0.9rem]">
          <span class="text-[15px] lg:text-[0.85rem] font-semibold">Podés encontrarlas en Mis médicos.</span>
          <p class="text-[14px] lg:text-xs text-[#61718B]">Abrí el perfil de tu profesional y entrá a Mis fichas médicas.<br />Allí vas a ver las fichas que compartió con vos.</p>
        </div>
        <button class="self-start h-11 lg:h-[2.6rem] px-6 lg:w-45 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-[0.7rem] font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-login')">Ir a mis médicos</button>
        <span class="text-[12px] lg:text-[0.55rem] text-[#61718B]">MediBot orienta sobre la plataforma. No reemplaza la consulta profesional.</span>
      </div>
    </section>

    <section class="bg-[#F4F7FB] px-4 lg:px-26 pt-16 lg:pt-19 pb-8 lg:pb-10 flex flex-col gap-10 lg:gap-12">
      <div class="flex flex-col gap-3 lg:gap-2.5">
        <span class="text-[12px] lg:text-[0.65rem] font-semibold text-[#1F6FC9]">CONOCÉ MEDIAPP</span>
        <h2 class="text-[28px] lg:text-[2.4rem] font-semibold leading-tight">Un diseño claro. Todo conectado.</h2>
        <p class="text-[16px] lg:text-[0.95rem] text-[#61718B]">Una experiencia para pacientes y otra para profesionales, con la misma forma simple de organizarse.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[44rem_1fr] items-center gap-10 lg:gap-20">
        <div class="p-5 lg:p-[1.1rem] bg-white rounded-2xl border border-[#D7E2F0] shadow-[0_1rem_2.5rem_-0.5rem_rgba(26,58,96,0.18)] flex flex-col gap-4 lg:gap-[1.1rem]">
          <div class="flex items-center justify-between gap-4">
            <span class="text-[18px] lg:text-[1.1rem] font-semibold text-[#1F6FC9]">MediApp</span>
            <span class="text-[12px] lg:text-[0.6rem] text-[#61718B]">Tu espacio de salud</span>
          </div>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <span class="text-[18px] lg:text-[1.2rem] font-semibold">Todo listo para tu próxima consulta</span>
            <span class="px-3 py-1 rounded-full bg-[#E7F7EE] text-[12px] lg:text-[0.65rem] font-medium text-[#1E8E4F]">✓ Confirmado</span>
          </div>

          <div class="p-3 lg:p-[0.8rem] bg-[#F4F7FB] rounded-xl border border-[#D7E2F0] flex items-center gap-4 lg:gap-[1.4rem]">
            <div class="shrink-0 w-14 lg:w-14 py-2 bg-white rounded-lg flex flex-col items-center">
              <span class="text-[18px] lg:text-[1.2rem] font-semibold text-[#1F6FC9] leading-none">16</span>
              <span class="text-[11px] lg:text-[0.55rem] text-[#61718B]">OCT</span>
            </div>
            <div class="flex-1 min-w-0 grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div class="flex flex-col gap-1 min-w-0">
                <span class="text-[11px] lg:text-[0.55rem] text-[#61718B]">Tipo de turno</span>
                <span class="text-[15px] lg:text-[0.95rem] font-semibold truncate">Psicólogo</span>
              </div>
              <div class="flex flex-col gap-1 min-w-0">
                <span class="text-[11px] lg:text-[0.55rem] text-[#61718B]">Profesional</span>
                <span class="text-[15px] lg:text-[0.95rem] font-semibold truncate">Lic. Lucía Fernández</span>
              </div>
              <div class="flex flex-col gap-1 min-w-0">
                <span class="text-[11px] lg:text-[0.55rem] text-[#61718B]">Horario</span>
                <span class="text-[15px] lg:text-[0.95rem] font-semibold">◷ 12:45</span>
              </div>
            </div>
            <span class="shrink-0 text-[20px] text-[#61718B]">›</span>
          </div>

          <div class="grid grid-cols-7 gap-1.5 lg:gap-[0.7rem]">
            <div v-for="dia in dias" :key="dia.nombre" class="py-2 lg:py-[0.6rem] rounded-lg flex flex-col items-center gap-0.5" :class="dia.numero === 16 ? 'bg-[#1F6FC9] text-white' : 'bg-[#F4F7FB] text-[#61718B]'">
              <span class="text-[10px] lg:text-[0.55rem]">{{ dia.nombre }}</span>
              <span class="text-[13px] lg:text-[0.65rem]">{{ dia.numero }}</span>
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-3">
            <span class="text-[13px] lg:text-[0.65rem] text-[#61718B]">Tus turnos y fichas, siempre a mano.</span>
            <button class="h-10 lg:h-[2.1rem] px-5 lg:w-40 rounded-lg bg-[#1F6FC9] text-[14px] lg:text-xs font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-login')">Ver mi calendario →</button>
          </div>
        </div>

        <div class="flex flex-col gap-4 lg:gap-[1.1rem]">
          <h2 class="text-[28px] lg:text-[2.1rem] font-semibold leading-tight">Tu próximo paso,<br />más simple.</h2>
          <p class="text-[16px] lg:text-[0.85rem] text-[#61718B] max-w-100">Reservá tu próxima consulta o empezá a organizar tu consultorio con MediApp.</p>
          <div class="flex flex-col items-start gap-1 lg:w-56 pt-2">
            <button class="w-full sm:w-64 lg:w-full h-11 lg:h-[2.6rem] rounded-lg bg-[#1F6FC9] text-[15px] lg:text-[0.7rem] font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="emit('ir-a-registro')">Crear mi cuenta</button>
            <button class="w-full sm:w-64 lg:w-full h-11 lg:h-[2.6rem] text-[15px] lg:text-[0.7rem] font-medium text-[#1F6FC9] cursor-pointer hover:underline" @click="emit('ir-a-registro', 'Medico')">Soy profesional</button>
          </div>
          <button class="self-start text-[14px] lg:text-[0.7rem] font-medium text-[#1F6FC9] cursor-pointer hover:underline" @click="emit('ir-a-login')">¿Ya tenés una cuenta? Iniciar sesión</button>
        </div>
      </div>

      <div class="pt-6 lg:pt-6 border-t border-[#D7E2F0] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <span class="text-[13px] lg:text-[0.65rem] font-medium text-[#1F6FC9]">MediApp · Conectamos personas, simplificamos el cuidado.</span>
        <div class="flex gap-5 text-[13px] lg:text-[0.65rem] text-[#61718B]">
          <button v-for="(doc, clave) in documentos" :key="clave" class="cursor-pointer hover:text-[#1F6FC9] hover:underline" @click="documentoAbierto = clave">{{ doc.titulo }}</button>
        </div>
      </div>
    </section>

    <!-- pop up -->
    <div v-if="documentoAbierto" class="fixed inset-0 z-60 px-4 bg-[#0A1424]/50 flex items-center justify-center" @click.self="documentoAbierto = null">
      <div class="w-full max-w-160 max-h-[85vh] p-6 lg:p-[1.8rem] bg-white rounded-2xl shadow-xl flex flex-col gap-4">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-[20px] lg:text-2xl font-semibold">{{ documentos[documentoAbierto].titulo }}</h2>
            <p class="text-[13px] lg:text-[0.7rem] text-[#61718B]">Última actualización: noviembre de 2026</p>
          </div>
          <button class="text-[22px] leading-none text-[#61718B] cursor-pointer hover:text-[#182234]" @click="documentoAbierto = null">×</button>
        </div>
        <div class="h-px bg-[#D7E2F0]"></div>

        <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-4 pr-1">
          <div v-for="seccion in documentos[documentoAbierto].secciones" :key="seccion.titulo" class="flex flex-col gap-1">
            <h3 class="text-[15px] lg:text-[0.85rem] font-semibold">{{ seccion.titulo }}</h3>
            <p class="text-[14px] lg:text-[0.8rem] text-[#61718B]">{{ seccion.texto }}</p>
          </div>
        </div>

        <button class="self-end h-11 lg:h-[2.6rem] px-8 rounded-lg bg-[#1F6FC9] text-[15px] lg:text-xs font-medium text-white cursor-pointer hover:bg-[#185BA6] transition-colors" @click="documentoAbierto = null">Entendido</button>
      </div>
    </div>
  </div>
</template>
