'use client'

import { useState } from 'react'

interface StepCardProps {
  step: {
    id: number
    title: string
    description: string
    icon: string
    endpoint: string
    color: string
  }
  isActive: boolean
  onClick: () => void
  onRun: (step: any, config: any) => void
  loading: boolean
}

export default function StepCard({ step, isActive, onClick, onRun, loading }: StepCardProps) {
  const [config, setConfig] = useState<any>({})

  const getDefaultConfig = () => {
    switch (step.id) {
      case 1:
        return {
          username: 'zuler',
          max_tweets: 200,
          scroll_count: 20
        }
      case 2:
        return {}
      case 3:
        return {
          max_articles: 15,
          coins: ['bitcoin', 'ethereum', 'tether', 'bnb', 'solana']
        }
      case 4:
        return {
          model_provider: 'anthropic',
          temperature: 0.7
        }
      default:
        return {}
    }
  }

  const handleRun = () => {
    const finalConfig = Object.keys(config).length > 0 ? config : getDefaultConfig()
    onRun(step, finalConfig)
  }

  return (
    <div className={`card ${isActive ? 'ring-2 ring-primary' : ''} cursor-pointer`}>
      <div onClick={onClick}>
        <div className="flex items-start gap-4">
          <div className={`${step.color} w-12 h-12 rounded-lg flex items-center justify-center text-2xl`}>
            {step.icon}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-1">{step.title}</h3>
            <p className="text-sm text-slate-600">{step.description}</p>
          </div>
        </div>
      </div>

      {isActive && (
        <div className="mt-4 pt-4 border-t">
          {step.id === 1 && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Usuario de X</label>
                <input
                  type="text"
                  className="input-field"
                  defaultValue="zuler"
                  onChange={(e) => setConfig({ ...config, username: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Máximo de tweets</label>
                <input
                  type="number"
                  className="input-field"
                  defaultValue={200}
                  onChange={(e) => setConfig({ ...config, max_tweets: parseInt(e.target.value) })}
                />
              </div>
            </div>
          )}

          {step.id === 3 && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Máximo de artículos</label>
                <input
                  type="number"
                  className="input-field"
                  defaultValue={15}
                  onChange={(e) => setConfig({ ...config, max_articles: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Monedas (separadas por coma)</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="bitcoin,ethereum,solana"
                  onChange={(e) => setConfig({ ...config, coins: e.target.value.split(',').map(c => c.trim()) })}
                />
              </div>
            </div>
          )}

          {step.id === 4 && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Proveedor de IA</label>
                <select
                  className="input-field"
                  defaultValue="google"
                  onChange={(e) => setConfig({ ...config, model_provider: e.target.value })}
                >
                  <option value="google">Google (Gemini) - Gratis ⭐</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="openai">OpenAI (GPT-4)</option>
                </select>
              </div>
              <p className="text-xs text-slate-500">
                💡 Gemini es gratis y rápido, perfecto para pruebas
              </p>
            </div>
          )}

          <button
            onClick={handleRun}
            disabled={loading}
            className="btn-primary w-full mt-4"
          >
            {loading ? 'Procesando...' : `Ejecutar Paso ${step.id}`}
          </button>
        </div>
      )}
    </div>
  )
}
