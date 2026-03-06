# Crypto News Replicator - Frontend

Interfaz web para el Crypto News Replicator, construida con Next.js 14 y Tailwind CSS.

## Características

- ✨ Interfaz intuitiva para ejecutar cada paso del pipeline
- 📊 Visualización en tiempo real de resultados
- 🎨 Diseño moderno con Tailwind CSS
- ⚡ API routes que ejecutan scripts de Python
- 🚀 Lista para desplegar en Vercel

## Desarrollo Local

### Prerequisitos

- Node.js 18+ y npm
- Python 3.8+ (para los scripts del backend)
- Todas las dependencias de Python instaladas (ver `requirements.txt` en el directorio raíz)

### Instalación

```bash
# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.local.example .env.local

# Editar .env.local y agregar tus API keys
nano .env.local
```

### Ejecutar en desarrollo

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## Estructura del Proyecto

```
frontend/
├── app/
│   ├── api/              # API routes
│   │   ├── scrape-x/     # Endpoint para scraping de X
│   │   ├── analyze/      # Endpoint para análisis
│   │   ├── scrape-cmc/   # Endpoint para CoinMarketCap
│   │   ├── generate/     # Endpoint para generación
│   │   └── run-all/      # Endpoint para pipeline completo
│   ├── layout.tsx        # Layout principal
│   ├── page.tsx          # Página principal
│   └── globals.css       # Estilos globales
├── components/           # Componentes React
│   ├── StepCard.tsx
│   ├── ConfigForm.tsx
│   └── ResultsDisplay.tsx
├── lib/                  # Utilidades
│   └── python-executor.ts
└── public/               # Archivos estáticos
```

## Deploy en Vercel

### Opción 1: Deploy desde GitHub

1. Sube el proyecto a GitHub
2. Conecta tu repositorio en [Vercel](https://vercel.com)
3. Configura las variables de entorno:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
4. Deploy automático

### Opción 2: Deploy con Vercel CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Para producción
vercel --prod
```

### Variables de Entorno en Vercel

En el dashboard de Vercel, agrega:

- `ANTHROPIC_API_KEY`: Tu API key de Anthropic
- `OPENAI_API_KEY`: Tu API key de OpenAI (opcional)

## API Endpoints

### POST /api/scrape-x

Scrapea tweets del perfil de X.

**Body:**
```json
{
  "username": "zuler",
  "max_tweets": 200,
  "scroll_count": 20
}
```

### POST /api/analyze

Analiza la personalidad y estilo.

**Body:** `{}` (sin parámetros)

### POST /api/scrape-cmc

Scrapea noticias de CoinMarketCap.

**Body:**
```json
{
  "max_articles": 15,
  "coins": ["bitcoin", "ethereum", "solana"]
}
```

### POST /api/generate

Genera contenido con el estilo aprendido.

**Body:**
```json
{
  "model_provider": "anthropic",
  "temperature": 0.7
}
```

### POST /api/run-all

Ejecuta el pipeline completo.

**Body:** `{}` (sin parámetros)

## Troubleshooting

### Error: "Python script execution failed"

- Verifica que Python 3 esté instalado
- Asegúrate de que todas las dependencias de Python estén instaladas
- Revisa que los paths relativos sean correctos

### Error: "File not found"

- Los scripts de Python deben estar en el directorio padre (`../`)
- Verifica que la estructura de carpetas sea correcta

### Timeouts en API

- Las API routes tienen un timeout de 5 minutos
- Para operaciones largas, considera usar una queue o background jobs

## Personalización

### Cambiar colores

Edita `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    colors: {
      primary: '#FF6B00',    // Cambia estos
      secondary: '#00D4FF',
    },
  },
}
```

### Agregar nuevos pasos

1. Crea un nuevo endpoint en `app/api/nuevo-paso/route.ts`
2. Agrega el paso en `app/page.tsx` en el array `steps`
3. Actualiza el componente `StepCard.tsx` si necesita configuración especial

## License

MIT
