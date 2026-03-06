import { NextRequest, NextResponse } from 'next/server'
import { executePythonScript, findLatestFile, readJSONFile } from '@/lib/python-executor'

export async function POST(request: NextRequest) {
  try {
    console.log('Starting personality analysis...')

    // Ejecutar analizador de personalidad
    const result = await executePythonScript('utils/personality_analyzer.py')

    if (!result.success) {
      return NextResponse.json(
        { error: 'Error ejecutando análisis', details: result.error },
        { status: 500 }
      )
    }

    // Buscar el archivo de análisis más reciente
    const latestFile = await findLatestFile('models/training_data', '_analysis.json')

    if (!latestFile) {
      return NextResponse.json(
        { error: 'No se encontró archivo de análisis' },
        { status: 404 }
      )
    }

    // Leer y devolver los datos
    const data = await readJSONFile(latestFile)

    return NextResponse.json({
      success: true,
      message: 'Análisis completado exitosamente',
      analysis: data,
      file: latestFile,
    })
  } catch (error: any) {
    console.error('Error in analyze API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor', details: error.message },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/analyze',
    method: 'POST',
    description: 'Analiza la personalidad y estilo de escritura de los tweets',
  })
}
