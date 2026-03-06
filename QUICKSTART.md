# Inicio Rápido 🚀

Guía para empezar a usar Crypto News Replicator en 5 minutos.

## Opción 1: Solo Frontend (Más Fácil)

### 1. Instalar dependencias del frontend

```bash
cd frontend
npm install
```

### 2. Configurar API key

```bash
# Copiar template
cp .env.local.example .env.local

# Editar y agregar tu API key de Gemini
echo "GOOGLE_API_KEY=AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY" > .env.local
```

### 3. Ejecutar

```bash
npm run dev
```

### 4. Abrir navegador

Ir a [http://localhost:3000](http://localhost:3000)

---

## Opción 2: Frontend + Backend (Completo)

### 1. Instalar Python

```bash
# Verificar Python
python3 --version

# Si no tienes Python, instalarlo
# Windows: Descargar desde python.org
# Linux: sudo apt install python3 python3-pip
# Mac: brew install python3
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configurar variables de entorno

```bash
# Copiar template
cp .env.example .env

# El archivo .env ya tiene tu API key configurada
# Solo verifica que esté así:
cat .env
```

Debería mostrar:
```
GOOGLE_API_KEY=AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY
MODEL_PROVIDER=google
```

### 4. Instalar frontend

```bash
cd frontend
npm install
cd ..
```

### 5. Ejecutar

Opción A - Solo frontend:
```bash
cd frontend
npm run dev
```

Opción B - Frontend + testing del backend:
```bash
# Terminal 1 - Probar backend
python main.py --step 1

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 6. Usar la aplicación

1. Ir a [http://localhost:3000](http://localhost:3000)
2. Click en "Ejecutar Pipeline Completo"
3. Esperar resultados (puede tomar 5-10 minutos)
4. Ver el contenido generado

---

## Primeros Pasos con el Frontend

### Dashboard Principal

La página principal muestra 4 pasos:

1. **🐦 Scrapear Perfil de X**
   - Click para expandir
   - Configurar usuario (default: zuler)
   - Click "Ejecutar"
   - Espera ~2-3 minutos

2. **🧠 Analizar Personalidad**
   - Click "Ejecutar" (sin configuración)
   - Espera ~30 segundos
   - Ver análisis de estilo

3. **📰 Scrapear CoinMarketCap**
   - Configurar monedas (opcional)
   - Click "Ejecutar"
   - Espera ~3-5 minutos

4. **✨ Generar Contenido**
   - Seleccionar modelo (Gemini recomendado)
   - Click "Ejecutar"
   - Espera ~2-3 minutos
   - Ver contenido generado

### O más fácil...

Click en **"🚀 Ejecutar Pipeline Completo"** y deja que todo se ejecute automáticamente.

---

## Testing Rápido

### Probar solo el análisis de IA

```bash
# Instalar Python
pip install google-generativeai python-dotenv

# Crear script de prueba
cat > test_gemini.py << 'EOF'
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content("Escribe un tweet corto sobre Bitcoin")
print(response.text)
EOF

# Ejecutar
python test_gemini.py
```

Si funciona, verás un tweet generado sobre Bitcoin.

---

## Troubleshooting

### Error: "npm: command not found"

Necesitas instalar Node.js:
- Windows/Mac: [https://nodejs.org](https://nodejs.org)
- Linux: `sudo apt install nodejs npm`

### Error: "python3: command not found"

Instalar Python 3:
- Windows: [https://python.org](https://python.org)
- Linux: `sudo apt install python3 python3-pip`
- Mac: `brew install python3`

### Error: "GOOGLE_API_KEY not found"

```bash
# Verificar que el .env existe
ls -la .env

# Verificar el contenido
cat .env

# Si no existe, crearlo
echo "GOOGLE_API_KEY=AIzaSyCJdbnFjQswnDzz8yDcrhytmZ06JI2r-OY" > .env
```

### Frontend carga pero APIs fallan

Esto es normal si no tienes Python instalado. Opciones:

1. **Solo visual**: El frontend mostrará la UI pero las operaciones fallarán
2. **Instalar Python**: Sigue la Opción 2 arriba
3. **Deploy separado**: Frontend en Vercel, backend en Railway (ver DEPLOY.md)

### Puerto 3000 ocupado

```bash
# Usar otro puerto
PORT=3001 npm run dev
```

---

## Próximos Pasos

Una vez que todo funcione:

1. ✅ Experimentar con diferentes configuraciones
2. ✅ Probar diferentes monedas
3. ✅ Ajustar parámetros del modelo
4. 📤 Subir a GitHub (ver DEPLOY.md)
5. 🌐 Desplegar en Vercel (ver DEPLOY.md)
6. 🚀 Compartir tu proyecto

---

## Recursos

- **README.md**: Documentación completa
- **DEPLOY.md**: Guía de deployment
- **frontend/README.md**: Docs del frontend
- **INSTRUCCIONES.md**: Guía detallada de uso

## Ayuda

Si algo no funciona, revisa:
1. Versión de Python: `python3 --version` (debe ser 3.8+)
2. Versión de Node: `node --version` (debe ser 18+)
3. API key en .env: `cat .env`
4. Logs de error en la consola

¿Aún con problemas? Revisa los issues en GitHub o crea uno nuevo.
