import { Injectable } from '@angular/core';

export interface ImageCompressionOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  mimeType?: string;
  maxSizeMB?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ImageCompressionService {

  async compressImage(
    file: File,
    options: ImageCompressionOptions = {}
  ): Promise<File> {

    const {
      maxWidth = 1920,
      maxHeight = 1920,
      quality = 0.80,
      mimeType = 'image/jpeg',
      maxSizeMB = 2
    } = options;

    // Si no es una imagen, no hacemos nada
    if (!file.type.startsWith('image/')) {
      throw new Error('El archivo seleccionado no es una imagen.');
    }

    const image = await this.loadImage(file);

    // Calculamos las nuevas dimensiones manteniendo proporción
    const { width, height } = this.calculateDimensions(
      image.width,
      image.height,
      maxWidth,
      maxHeight
    );

    const canvas = document.createElement('canvas');

    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext('2d');

    if (!context) {
      throw new Error('No se pudo crear el contexto del canvas.');
    }

    // Mejor calidad de escalado
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = 'high';

    context.drawImage(
      image,
      0,
      0,
      width,
      height
    );

    // Convertimos a Blob
    const blob = await this.canvasToBlob(
      canvas,
      mimeType,
      quality
    );

    // Si todavía es demasiado grande,
    // seguimos bajando la calidad.
    let finalBlob = blob;
    let currentQuality = quality;

    while (
      finalBlob.size > maxSizeMB * 1024 * 1024 &&
      currentQuality > 0.40
    ) {

      currentQuality -= 0.05;

      finalBlob = await this.canvasToBlob(
        canvas,
        mimeType,
        currentQuality
      );
    }

    // Generamos un nuevo File
    const newFileName = this.changeExtension(
      file.name,
      mimeType
    );

    return new File(
      [finalBlob],
      newFileName,
      {
        type: mimeType,
        lastModified: Date.now()
      }
    );
  }

  private loadImage(file: File): Promise<HTMLImageElement> {

    return new Promise((resolve, reject) => {

      const image = new Image();

      const url = URL.createObjectURL(file);

      image.onload = () => {
        URL.revokeObjectURL(url);
        resolve(image);
      };

      image.onerror = () => {
        URL.revokeObjectURL(url);
        reject(
          new Error('No se pudo cargar la imagen.')
        );
      };

      image.src = url;
    });
  }

  private calculateDimensions(
    originalWidth: number,
    originalHeight: number,
    maxWidth: number,
    maxHeight: number
  ): { width: number; height: number } {

    let width = originalWidth;
    let height = originalHeight;

    // Si ya cumple los límites
    if (
      width <= maxWidth &&
      height <= maxHeight
    ) {
      return {
        width,
        height
      };
    }

    const ratio = Math.min(
      maxWidth / width,
      maxHeight / height
    );

    width = Math.round(width * ratio);
    height = Math.round(height * ratio);

    return {
      width,
      height
    };
  }

  private canvasToBlob(
    canvas: HTMLCanvasElement,
    mimeType: string,
    quality: number
  ): Promise<Blob> {

    return new Promise((resolve, reject) => {

      canvas.toBlob(
        blob => {

          if (blob) {
            resolve(blob);
          } else {
            reject(
              new Error('No se pudo comprimir la imagen.')
            );
          }

        },
        mimeType,
        quality
      );
    });
  }

  private changeExtension(
    fileName: string,
    mimeType: string
  ): string {

    const extension =
      mimeType === 'image/png'
        ? 'png'
        : 'jpg';

    const name = fileName
      .replace(/\.[^/.]+$/, '');

    return `${name}.${extension}`;
  }
}
