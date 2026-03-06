import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'

const execAsync = promisify(exec)

export interface PythonResult {
  success: boolean
  data?: any
  error?: string
  stdout?: string
  stderr?: string
}

export async function executePythonScript(
  scriptPath: string,
  args: string[] = []
): Promise<PythonResult> {
  try {
    // Ruta al directorio raíz del proyecto (un nivel arriba de frontend)
    const projectRoot = path.join(process.cwd(), '..')
    const fullScriptPath = path.join(projectRoot, scriptPath)

    // Construir comando
    const argsString = args.join(' ')
    const command = `cd ${projectRoot} && python3 ${fullScriptPath} ${argsString}`

    console.log('Executing:', command)

    const { stdout, stderr } = await execAsync(command, {
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      timeout: 300000, // 5 minutos timeout
    })

    return {
      success: true,
      stdout: stdout,
      stderr: stderr,
    }
  } catch (error: any) {
    console.error('Python execution error:', error)
    return {
      success: false,
      error: error.message,
      stdout: error.stdout,
      stderr: error.stderr,
    }
  }
}

export async function readJSONFile(filePath: string): Promise<any> {
  try {
    const projectRoot = path.join(process.cwd(), '..')
    const fullPath = path.join(projectRoot, filePath)

    const fs = require('fs').promises
    const content = await fs.readFile(fullPath, 'utf-8')
    return JSON.parse(content)
  } catch (error: any) {
    console.error('Error reading JSON file:', error)
    throw new Error(`Failed to read ${filePath}: ${error.message}`)
  }
}

export async function findLatestFile(directory: string, pattern: string): Promise<string | null> {
  try {
    const projectRoot = path.join(process.cwd(), '..')
    const fullPath = path.join(projectRoot, directory)

    const fs = require('fs').promises
    const files = await fs.readdir(fullPath)

    const matchingFiles = files
      .filter((f: string) => f.includes(pattern))
      .map((f: string) => ({
        name: f,
        path: path.join(directory, f),
      }))

    if (matchingFiles.length === 0) return null

    // Por simplicidad, devolver el último alfabéticamente (que suele ser el más reciente con timestamps)
    matchingFiles.sort((a: any, b: any) => b.name.localeCompare(a.name))

    return matchingFiles[0].path
  } catch (error) {
    console.error('Error finding latest file:', error)
    return null
  }
}
