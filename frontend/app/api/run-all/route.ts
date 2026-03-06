import { NextRequest, NextResponse } from 'next/server'
import { executePythonScript, findLatestFile, readJSONFile } from '@/lib/python-executor'

export async function POST(request: NextRequest) {
  try {
    console.log('Starting full pipeline...')

    // Ejecutar pipeline completo
    const result = await executePythonScript('main.py')

    if (!result.success) {
      return NextResponse.json(
        { error: 'Error ejecutando pipeline', details: result.error, stderr: result.stderr },
        { status: 500 }
      )
    }

    // Recopilar resultados de cada paso
    const results: any = {
      success: true,
      message: 'Pipeline completado exitosamente',
      steps: {},
    }

    // Paso 1: Tweets
    try {
      const tweetsFile = await findLatestFile('data/x_tweets', 'zuler')
      if (tweetsFile) {
        const tweetsData = await readJSONFile(tweetsFile)
        results.steps.scrape_x = {
          success: true,
          tweet_count: tweetsData.tweet_count,
          file: tweetsFile,
        }
      }
    } catch (e) {
      console.error('Error loading tweets:', e)
    }

    // Paso 2: Análisis
    try {
      const analysisFile = await findLatestFile('models/training_data', '_analysis.json')
      if (analysisFile) {
        const analysisData = await readJSONFile(analysisFile)
        results.steps.analysis = {
          success: true,
          total_tweets: analysisData.total_tweets,
          file: analysisFile,
        }
      }
    } catch (e) {
      console.error('Error loading analysis:', e)
    }

    // Paso 3: Artículos
    try {
      const articlesFile = await findLatestFile('data/coinmarketcap', 'articles_')
      if (articlesFile) {
        const articlesData = await readJSONFile(articlesFile)
        results.steps.scrape_cmc = {
          success: true,
          article_count: articlesData.article_count,
          file: articlesFile,
        }
      }
    } catch (e) {
      console.error('Error loading articles:', e)
    }

    // Paso 4: Contenido generado
    try {
      const contentFile = await findLatestFile('output', 'generated_content_')
      if (contentFile) {
        const contentData = await readJSONFile(contentFile)
        results.steps.generate = {
          success: true,
          article_count: contentData.article_count,
          file: contentFile,
        }
        // Incluir algunos ejemplos
        results.content_preview = contentData.content?.slice(0, 3) || []
      }
    } catch (e) {
      console.error('Error loading generated content:', e)
    }

    results.stdout = result.stdout
    results.execution_log = result.stdout?.split('\n').filter((line: string) =>
      line.includes('✓') || line.includes('✗') || line.includes('PASO')
    )

    return NextResponse.json(results)
  } catch (error: any) {
    console.error('Error in run-all API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor', details: error.message },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/run-all',
    method: 'POST',
    description: 'Ejecuta el pipeline completo (todos los pasos)',
    note: 'Puede tomar varios minutos dependiendo de la configuración',
  })
}
