import { NextRequest, NextResponse } from 'next/server'
import { executePythonScript, findLatestFile, readJSONFile } from '@/lib/python-executor'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { username = 'zuler', max_tweets = 200, scroll_count = 20 } = body

    // Ejecutar scraper de X
    console.log('Starting X scraper...')
    const result = await executePythonScript('scrapers/x_scraper.py')

    if (!result.success) {
      return NextResponse.json(
        { error: 'Error ejecutando scraper', details: result.error },
        { status: 500 }
      )
    }

    // Buscar el archivo de resultados más reciente
    const latestFile = await findLatestFile('data/x_tweets', username)

    if (!latestFile) {
      return NextResponse.json(
        { error: 'No se encontraron resultados del scraping' },
        { status: 404 }
      )
    }

    // Leer y devolver los datos
    const data = await readJSONFile(latestFile)

    return NextResponse.json({
      success: true,
      message: 'Scraping completado exitosamente',
      tweet_count: data.tweet_count || 0,
      tweets: data.tweets || [],
      file: latestFile,
    })
  } catch (error: any) {
    console.error('Error in scrape-x API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor', details: error.message },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/scrape-x',
    method: 'POST',
    description: 'Scrapea tweets del perfil de X especificado',
    parameters: {
      username: 'string (default: zuler)',
      max_tweets: 'number (default: 200)',
      scroll_count: 'number (default: 20)',
    },
  })
}
