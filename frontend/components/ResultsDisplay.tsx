'use client'

interface ResultsDisplayProps {
  results: {
    success: boolean
    step?: number
    data?: any
    error?: string
  }
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  if (!results) return null

  return (
    <div className={`card ${results.success ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
      <div className="flex items-start gap-3 mb-4">
        <span className="text-2xl">
          {results.success ? '✅' : '❌'}
        </span>
        <div>
          <h3 className="text-lg font-semibold">
            {results.success ? 'Operación Exitosa' : 'Error en la Operación'}
          </h3>
          {results.step && (
            <p className="text-sm text-slate-600">Paso {results.step} completado</p>
          )}
        </div>
      </div>

      {results.error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
          <p className="text-red-800 text-sm">{results.error}</p>
        </div>
      )}

      {results.success && results.data && (
        <div className="space-y-4">
          {/* Tweets scrapeados */}
          {results.data.tweets && (
            <div>
              <h4 className="font-semibold mb-2">Tweets extraídos: {results.data.tweet_count}</h4>
              <div className="bg-slate-50 rounded p-4 max-h-96 overflow-y-auto">
                {results.data.tweets.slice(0, 5).map((tweet: any, i: number) => (
                  <div key={i} className="mb-4 pb-4 border-b last:border-b-0">
                    <p className="text-sm mb-2">{tweet.text}</p>
                    <div className="flex gap-4 text-xs text-slate-500">
                      <span>❤️ {tweet.like_count}</span>
                      <span>🔄 {tweet.retweet_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Análisis de personalidad */}
          {results.data.analysis && (
            <div>
              <h4 className="font-semibold mb-2">Análisis de Personalidad</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="text-xs text-slate-600">Tweets analizados</p>
                  <p className="text-lg font-bold">{results.data.analysis.total_tweets}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="text-xs text-slate-600">Longitud promedio</p>
                  <p className="text-lg font-bold">
                    {results.data.analysis.style_patterns?.avg_tweet_length?.toFixed(0)} chars
                  </p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="text-xs text-slate-600">Uso de emojis</p>
                  <p className="text-lg font-bold">
                    {results.data.analysis.style_patterns?.emoji_usage?.percentage?.toFixed(0)}%
                  </p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="text-xs text-slate-600">Palabras únicas</p>
                  <p className="text-lg font-bold">
                    {results.data.analysis.vocabulary?.unique_words}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Artículos scrapeados */}
          {results.data.articles && (
            <div>
              <h4 className="font-semibold mb-2">
                Artículos extraídos: {results.data.article_count}
              </h4>
              <div className="bg-slate-50 rounded p-4 max-h-96 overflow-y-auto">
                {results.data.articles.slice(0, 5).map((article: any, i: number) => (
                  <div key={i} className="mb-4 pb-4 border-b last:border-b-0">
                    <h5 className="font-medium mb-1">{article.title}</h5>
                    <p className="text-xs text-slate-500 mb-2">
                      Moneda: {article.coin} | Palabras: {article.word_count}
                    </p>
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary hover:underline"
                    >
                      Ver original →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contenido generado */}
          {results.data.content && (
            <div>
              <h4 className="font-semibold mb-2">
                Contenido generado: {results.data.article_count} piezas
              </h4>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {results.data.content.slice(0, 3).map((item: any, i: number) => (
                  <div key={i} className="bg-gradient-to-r from-orange-50 to-cyan-50 rounded-lg p-4">
                    <h5 className="font-medium mb-2 text-sm">
                      {item.original_article?.title}
                    </h5>
                    <div className="space-y-2">
                      <div className="bg-white rounded p-3">
                        <p className="text-xs text-slate-600 mb-1">Tweet generado:</p>
                        <p className="text-sm">{item.tweet}</p>
                      </div>
                      <div className="bg-white rounded p-3">
                        <p className="text-xs text-slate-600 mb-1">Intro de thread:</p>
                        <p className="text-sm">{item.thread_intro}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Datos genéricos */}
          {!results.data.tweets &&
           !results.data.analysis &&
           !results.data.articles &&
           !results.data.content && (
            <div className="bg-slate-50 rounded p-4">
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(results.data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
