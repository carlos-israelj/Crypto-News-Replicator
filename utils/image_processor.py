"""
Procesador de imágenes
Modifica imágenes extraídas de CoinMarketCap para darles un estilo único
"""

import os
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import random


class ImageProcessor:
    def __init__(self, output_dir='images/processed'):
        """
        Inicializa el procesador de imágenes

        Args:
            output_dir: Directorio donde guardar imágenes procesadas
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def resize_image(self, image_path, max_width=1200, max_height=800):
        """
        Redimensiona una imagen manteniendo aspecto

        Args:
            image_path: Path a la imagen original
            max_width: Ancho máximo
            max_height: Alto máximo

        Returns:
            PIL Image redimensionada
        """
        img = Image.open(image_path)

        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Calcular nuevo tamaño manteniendo aspecto
        ratio = min(max_width / img.width, max_height / img.height)
        if ratio < 1:
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        return img

    def apply_filter(self, img, filter_type='enhance'):
        """
        Aplica filtros a la imagen

        Args:
            img: PIL Image
            filter_type: Tipo de filtro ('enhance', 'vibrant', 'cool', 'warm', 'dramatic')

        Returns:
            PIL Image con filtro aplicado
        """
        if filter_type == 'enhance':
            # Mejorar contraste y nitidez
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)

        elif filter_type == 'vibrant':
            # Colores más vibrantes
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)

        elif filter_type == 'cool':
            # Tono frío (más azul)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.9)
            # Aplicar tinte azul ligero
            blue_tint = Image.new('RGB', img.size, (0, 50, 100))
            img = Image.blend(img, blue_tint, 0.1)

        elif filter_type == 'warm':
            # Tono cálido (más naranja/amarillo)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            warm_tint = Image.new('RGB', img.size, (255, 150, 0))
            img = Image.blend(img, warm_tint, 0.08)

        elif filter_type == 'dramatic':
            # Alto contraste y saturación
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.95)

        return img

    def add_border(self, img, border_width=5, border_color='#FF6B00'):
        """
        Añade un borde a la imagen

        Args:
            img: PIL Image
            border_width: Ancho del borde en píxeles
            border_color: Color del borde (hex o nombre)

        Returns:
            PIL Image con borde
        """
        # Crear nueva imagen con borde
        new_size = (img.width + border_width * 2, img.height + border_width * 2)
        bordered_img = Image.new('RGB', new_size, border_color)
        bordered_img.paste(img, (border_width, border_width))

        return bordered_img

    def add_watermark(self, img, text='@zuler', position='bottom-right', opacity=0.3):
        """
        Añade marca de agua a la imagen

        Args:
            img: PIL Image
            text: Texto de la marca de agua
            position: Posición ('bottom-right', 'bottom-left', 'top-right', 'top-left')
            opacity: Opacidad de la marca de agua (0-1)

        Returns:
            PIL Image con marca de agua
        """
        # Crear capa para marca de agua
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)

        # Intentar usar una fuente, si no está disponible usar la default
        try:
            # Tamaño de fuente relativo al tamaño de imagen
            font_size = max(20, min(img.width, img.height) // 25)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                # Si todo falla, no añadir marca de agua
                return img

        # Calcular posición
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        margin = 20

        positions = {
            'bottom-right': (img.width - text_width - margin, img.height - text_height - margin),
            'bottom-left': (margin, img.height - text_height - margin),
            'top-right': (img.width - text_width - margin, margin),
            'top-left': (margin, margin)
        }

        pos = positions.get(position, positions['bottom-right'])

        # Dibujar marca de agua con sombra
        shadow_offset = 2
        draw.text((pos[0] + shadow_offset, pos[1] + shadow_offset), text,
                 fill=(0, 0, 0, int(255 * opacity * 0.5)), font=font)
        draw.text(pos, text, fill=(255, 255, 255, int(255 * opacity)), font=font)

        # Combinar con imagen original
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        img = Image.alpha_composite(img, watermark)
        return img.convert('RGB')

    def process_image(self, image_path, filter_type='enhance', add_border=True,
                     add_watermark=True, watermark_text='@zuler'):
        """
        Procesa una imagen con todas las transformaciones

        Args:
            image_path: Path a la imagen original
            filter_type: Tipo de filtro a aplicar
            add_border: Si se añade borde
            add_watermark: Si se añade marca de agua
            watermark_text: Texto de la marca de agua

        Returns:
            Path de la imagen procesada
        """
        try:
            print(f"Procesando imagen: {Path(image_path).name}")

            # Cargar y redimensionar
            img = self.resize_image(image_path)

            # Aplicar filtro
            img = self.apply_filter(img, filter_type)

            # Añadir borde
            if add_border:
                border_colors = ['#FF6B00', '#00D4FF', '#FFD700', '#FF1493', '#00FF00']
                img = self.add_border(img, border_width=3,
                                    border_color=random.choice(border_colors))

            # Añadir marca de agua
            if add_watermark:
                img = self.add_watermark(img, text=watermark_text,
                                       position='bottom-right', opacity=0.4)

            # Guardar imagen procesada
            original_name = Path(image_path).stem
            output_path = self.output_dir / f"{original_name}_processed.jpg"

            img.save(output_path, 'JPEG', quality=90, optimize=True)
            print(f"  ✓ Imagen guardada: {output_path}")

            return str(output_path)

        except Exception as e:
            print(f"  ✗ Error procesando imagen {image_path}: {e}")
            return None

    def process_batch(self, image_paths, filter_type='enhance', **kwargs):
        """
        Procesa un lote de imágenes

        Args:
            image_paths: Lista de paths de imágenes
            filter_type: Tipo de filtro (puede ser 'random' para aleatorio)
            **kwargs: Argumentos adicionales para process_image

        Returns:
            Diccionario mapeando paths originales a procesados
        """
        results = {}
        filter_types = ['enhance', 'vibrant', 'cool', 'warm', 'dramatic']

        for i, img_path in enumerate(image_paths, 1):
            print(f"\nProcesando imagen {i}/{len(image_paths)}")

            # Elegir filtro
            current_filter = random.choice(filter_types) if filter_type == 'random' else filter_type

            # Procesar
            processed_path = self.process_image(img_path, filter_type=current_filter, **kwargs)

            if processed_path:
                results[img_path] = processed_path

        print(f"\n✓ Procesamiento completado: {len(results)}/{len(image_paths)} imágenes")
        return results


def main():
    """Función de prueba"""
    import sys

    # Buscar imágenes en directorio
    images_dir = Path("images/original")
    if not images_dir.exists():
        print("No se encontró el directorio images/original")
        return

    # Obtener todas las imágenes
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(images_dir.glob(f"*{ext}"))

    if not image_files:
        print("No se encontraron imágenes para procesar")
        return

    print(f"Encontradas {len(image_files)} imágenes")

    # Crear procesador
    processor = ImageProcessor()

    # Procesar todas las imágenes
    results = processor.process_batch(
        [str(f) for f in image_files],
        filter_type='random',
        add_border=True,
        add_watermark=True,
        watermark_text='@zuler'
    )

    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE PROCESAMIENTO:")
    print("="*60)
    for original, processed in list(results.items())[:5]:
        print(f"\n{Path(original).name}")
        print(f"  → {Path(processed).name}")


if __name__ == "__main__":
    main()
