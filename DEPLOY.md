# Guía de Deployment en Vercel

## Paso 1: Preparar el Repositorio en GitHub

### 1.1 Inicializar Git (si no está inicializado)

```bash
cd /mnt/c/Users/CarlosIsraelJiménezJ/Documents/Replit/crypto-news-replicator
git init
```

### 1.2 Configurar Git

```bash
git config user.name "Carlos Israel Jimenez"
git config user.email "tu_email@example.com"
```

### 1.3 Agregar el remote

```bash
git remote add origin https://github.com/carlos-israelj/Crypto-News-Replicator.git
```

### 1.4 Revisar archivos antes de commit

```bash
# Asegúrate de que .env NO esté incluido
cat .gitignore
```

Verifica que `.env` esté en el `.gitignore` (✓ ya está incluido)

### 1.5 Hacer el primer commit

```bash
git add .
git commit -m "Initial commit: Crypto News Replicator with Next.js frontend"
git push -u origin main
```

Si hay conflictos o necesitas forzar:

```bash
git push -f origin main
```

## Paso 2: Deploy en Vercel

### Opción A: Desde el Dashboard de Vercel

1. Ve a [https://vercel.com](https://vercel.com)
2. Inicia sesión con GitHub
3. Click en "New Project"
4. Importa el repositorio `carlos-israelj/Crypto-News-Replicator`
5. Configura:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

6. Agrega las variables de entorno:
   - `GOOGLE_API_KEY`: `AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY`

7. Click en "Deploy"

### Opción B: Desde CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (desde el directorio frontend)
cd frontend
vercel

# Cuando pregunte:
# - "Set up and deploy?"  → Yes
# - "Which scope?"        → Tu usuario
# - "Link to existing project?" → No
# - "What's your project's name?" → crypto-news-replicator
# - "In which directory?" → ./
# - "Override settings?" → No

# Agregar variables de entorno
vercel env add GOOGLE_API_KEY production
# Pega tu API key cuando lo pida

# Deploy a producción
vercel --prod
```

## Paso 3: Configurar Variables de Entorno en Vercel

### Desde el Dashboard

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Agregar:

```
GOOGLE_API_KEY = AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY
```

4. Selecciona los ambientes:
   - ✅ Production
   - ✅ Preview
   - ✅ Development

5. Click "Save"

### Desde CLI

```bash
vercel env add GOOGLE_API_KEY
# Selecciona: Production, Preview, Development
# Pega el valor: AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY
```

## Paso 4: Verificar el Deploy

1. Vercel te dará una URL como: `https://crypto-news-replicator-xxx.vercel.app`
2. Abre la URL
3. Prueba cada funcionalidad:
   - ✅ La página carga correctamente
   - ✅ Los botones responden
   - ✅ Las API routes funcionan (probablemente fallarán porque Python no está en Vercel)

## Paso 5: Limitaciones y Soluciones

### ⚠️ Importante: Python en Vercel

Vercel es principalmente para frontend. Los scripts de Python **NO funcionarán** directamente en Vercel porque:
- Vercel es serverless
- No tiene Python pre-instalado
- No soporta procesos largos como web scraping

### Solución 1: Backend Separado (Recomendado)

Desplegar el backend Python en otro servicio:

#### A. Railway.app (Recomendado - Gratis)

1. Ve a [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Selecciona tu repo
4. Agrega variables de entorno
5. Railway detectará Python automáticamente

#### B. Render.com

1. Ve a [render.com](https://render.com)
2. New → Web Service
3. Conecta GitHub
4. Build Command: `pip install -r requirements.txt && playwright install chromium`
5. Start Command: `python main.py`

#### C. Actualizar el Frontend

En `frontend/lib/python-executor.ts`, cambiar:

```typescript
const API_URL = process.env.BACKEND_URL || 'http://localhost:5000'
// Apuntar a tu backend en Railway/Render
```

### Solución 2: Solo Frontend + API Keys externas

Modificar la app para que:
- El usuario pegue datos de tweets manualmente
- Solo se ejecute el análisis y generación con IA en el frontend
- No haga scraping desde Vercel

### Solución 3: Desarrollo Local + Deploy Solo Frontend

- Usa la app localmente para hacer scraping
- Sube los resultados procesados a Vercel
- El frontend solo muestra resultados pre-generados

## Paso 6: Actualizar el Proyecto

Cada vez que hagas cambios:

```bash
# Commit cambios
git add .
git commit -m "Descripción de los cambios"
git push origin main

# Vercel hará auto-deploy
```

Para forzar re-deploy sin cambios:

```bash
cd frontend
vercel --prod
```

## Troubleshooting

### Error: "Git push rejected"

```bash
git pull origin main --rebase
git push origin main
```

### Error: "Vercel build failed"

- Revisa los logs en el dashboard de Vercel
- Asegúrate de que `package.json` esté correcto
- Verifica que el directorio raíz sea `frontend`

### Error: "API routes timeout"

- Las serverless functions en Vercel tienen límite de 10s (free tier)
- Necesitas mover el backend a otro servicio

## Recursos

- [Documentación de Vercel](https://vercel.com/docs)
- [Next.js en Vercel](https://nextjs.org/docs/deployment)
- [Railway.app Docs](https://docs.railway.app)
- [Render.com Docs](https://render.com/docs)

## Próximos Pasos

1. ✅ Push a GitHub
2. ✅ Deploy frontend en Vercel
3. ⏳ Deploy backend en Railway/Render
4. ⏳ Conectar frontend con backend
5. ⏳ Configurar dominio personalizado (opcional)
