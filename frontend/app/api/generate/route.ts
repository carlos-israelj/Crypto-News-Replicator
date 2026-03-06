import { NextRequest, NextResponse } from 'next/server'
import { executePythonScript, findLatestFile, readJSONFile } from '@/lib/python-executor'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { model_provider = 'anthropic', temperature = 0.7 } = body

    console.log('Starting content generation...')

    // Ejecutar generación de contenido
    const result = await executePythonScript('main.py', ['--step', '4'])

    if (!result.success) {
      return NextResponse.json(
        { error: 'Error generando contenido', details: result.error },
        { status: 500 }
      )
    }

    // Buscar el archivo de resultados más reciente
    const latestFile = await findLatestFile('output', 'generated_content_')

    if (!latestFile) {
      return NextResponse.json(
        { error: 'No se encontró contenido generado' },
        { status: 404 }
      )
    }

    // Leer y devolver los datos
    const data = await readJSONFile(latestFile)

    return NextResponse.json({
      success: true,
      message: 'Contenido generado exitosamente',
      article_count: data.article_count || 0,
      content: data.content || [],
      model_used: data.model_used,
      file: latestFile,
    })
  } catch (error: any) {
    console.error('Error in generate API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor', details: error.message },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/generate',
    method: 'POST',
    description: 'Genera contenido replicando el estilo de @zuler',
    parameters: {
      model_provider: 'string (default: anthropic)',
      temperature: 'number (default: 0.7)',
    },
  })
}
