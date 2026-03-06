'use client'

interface ConfigFormProps {
  step: {
    id: number
    title: string
  }
  onClose: () => void
}

export default function ConfigForm({ step, onClose }: ConfigFormProps) {
  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold">Configurando: {step.title}</h3>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600"
        >
          ✕
        </button>
      </div>
      <p className="text-sm text-slate-600">
        Ajusta la configuración usando los controles arriba y haz clic en "Ejecutar" cuando estés listo.
      </p>
    </div>
  )
}
