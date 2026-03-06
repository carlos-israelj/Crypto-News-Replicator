'use client'

import { useState } from 'react'
import StepCard from '@/components/StepCard'
import ConfigForm from '@/components/ConfigForm'
import ResultsDisplay from '@/components/ResultsDisplay'

export default function Home() {
  const [activeStep, setActiveStep] = useState<number | null>(null)
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const steps = [
    {
      id: 1,
      title: 'Scrapear Perfil de X',
      description: 'Extrae tweets de @zuler para analizar su estilo de escritura',
      icon: '🐦',
      endpoint: '/api/scrape-x',
      color: 'bg-blue-500'
    },
    {
      id: 2,
      title: 'Analizar Personalidad',
      description: 'Analiza patrones de escritura, vocabulario y tono',
      icon: '🧠',
      endpoint: '/api/analyze',
      color: 'bg-purple-500'
    },
    {
      id: 3,
      title: 'Scrapear CoinMarketCap',
      description: 'Extrae noticias TOP de las principales criptomonedas',
      icon: '📰',
      endpoint: '/api/scrape-cmc',
      color: 'bg-green-500'
    },
    {
      id: 4,
      title: 'Generar Contenido',
      description: 'Replica las noticias con el estilo de @zuler',
      icon: '✨',
      endpoint: '/api/generate',
      color: 'bg-orange-500'
    }
  ]

  const handleRunStep = async (step: any, config: any) => {
    setLoading(true)
    setResults(null)

    try {
      const response = await fetch(step.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })

      const data = await response.json()

      if (response.ok) {
        setResults({
          success: true,
          step: step.id,
          data: data
        })
      } else {
        setResults({
          success: false,
          error: data.error || 'Error desconocido'
        })
      }
    } catch (error: any) {
      setResults({
        success: false,
        error: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRunAll = async () => {
    setLoading(true)
    setResults(null)

    try {
      const response = await fetch('/api/run-all', {
        method: 'POST',
      })

      const data = await response.json()
      setResults({
        success: response.ok,
        data: data
      })
    } catch (error: any) {
      setResults({
        success: false,
        error: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4">
          Bienvenido al Replicador de Noticias Crypto
        </h2>
        <p className="text-lg text-slate-600 max-w-3xl mx-auto">
          Extrae noticias de CoinMarketCap y replícalas con el estilo único de @zuler.
          Ejecuta cada paso individualmente o corre el pipeline completo.
        </p>
      </div>

      {/* Run All Button */}
      <div className="mb-8 text-center">
        <button
          onClick={handleRunAll}
          disabled={loading}
          className="btn-primary px-8 py-4 text-lg"
        >
          {loading ? '⏳ Procesando...' : '🚀 Ejecutar Pipeline Completo'}
        </button>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        {steps.map((step) => (
          <StepCard
            key={step.id}
            step={step}
            isActive={activeStep === step.id}
            onClick={() => setActiveStep(activeStep === step.id ? null : step.id)}
            onRun={handleRunStep}
            loading={loading}
          />
        ))}
      </div>

      {/* Config Form */}
      {activeStep && (
        <div className="mb-12">
          <ConfigForm
            step={steps.find(s => s.id === activeStep)!}
            onClose={() => setActiveStep(null)}
          />
        </div>
      )}

      {/* Results Display */}
      {results && (
        <ResultsDisplay results={results} />
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <span>⚡</span> Rápido
          </h3>
          <p className="text-slate-600 text-sm">
            Procesa cientos de tweets y artículos en minutos
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <span>🎯</span> Preciso
          </h3>
          <p className="text-slate-600 text-sm">
            Replica el estilo con alta fidelidad usando IA avanzada
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <span>🔧</span> Personalizable
          </h3>
          <p className="text-slate-600 text-sm">
            Ajusta cada parámetro según tus necesidades
          </p>
        </div>
      </div>
    </div>
  )
}
