import { NextRequest, NextResponse } from 'next/server'
import { executePythonScript, findLatestFile, readJSONFile } from '@/lib/python-executor'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { max_articles = 15, coins = [] } = body

    console.log('Starting CoinMarketCap scraper...')

    // Ejecutar scraper de CoinMarketCap
    const result = await executePythonScript('scrapers/coinmarketcap_scraper.py')

    if (!result.success) {
      return NextResponse.json(
        { error: 'Error ejecutando scraper', details: result.error },
        { status: 500 }
      )
    }

    // Buscar el archivo de resultados más reciente
    const latestFile = await findLatestFile('data/coinmarketcap', 'articles_')

    if (!latestFile) {
      return NextResponse.json(
        { error: 'No se encontraron artículos scrapeados' },
        { status: 404 }
      )
    }

    // Leer y devolver los datos
    const data = await readJSONFile(latestFile)

    return NextResponse.json({
      success: true,
      message: 'Scraping de CoinMarketCap completado',
      article_count: data.article_count || 0,
      articles: data.articles || [],
      file: latestFile,
    })
  } catch (error: any) {
    console.error('Error in scrape-cmc API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor', details: error.message },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/scrape-cmc',
    method: 'POST',
    description: 'Scrapea noticias de CoinMarketCap para las principales criptomonedas',
    parameters: {
      max_articles: 'number (default: 15)',
      coins: 'string[] (optional)',
    },
  })
}
