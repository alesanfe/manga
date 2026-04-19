import os

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.manga.serializer import MangaDownloadSerializer
# Import centralized logger configuration
from utils.logger_config import logger
from utils.manga_services import download_all_chapters, download_selected_chapters, download_range_of_chapters, \
    create_zip


class MangaDownloadView(APIView):
    """
    API View para descargar capítulos de manga y generar archivos ZIP con PDFs.
    
    Acepta requests POST con:
    - manga_name: Nombre del manga en my.ninemanga.com
    - chapters: Lista de capítulos (vacío para todos, [1] para uno, [1,10] para rango)
    
    Retorna un archivo ZIP con los PDFs de los capítulos solicitados.
    """
    def post(self, request):
        serializer = MangaDownloadSerializer(data=request.data)
        logger.info('Manga download request received')
        
        if not serializer.is_valid():
            logger.warning(f'Invalid request data: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            manga_name = serializer.validated_data['manga_name']
            chapters = serializer.validated_data['chapters']
            logger.info(f'Downloading manga: {manga_name}, chapters: {chapters}')
            
            if not chapters:  # Si la lista de capítulos está vacía, descargar todo el manga
                pdfs_data = download_all_chapters(manga_name)
            elif len(chapters) == 1:  # Si hay un solo capítulo, descargar ese capítulo
                logger.info(f"Downloading single chapter: {chapters[0]}")
                pdfs_data = download_selected_chapters(manga_name, chapters)
                logger.info(f"Downloaded {len(pdfs_data)} PDFs")
            elif len(chapters) == 2:  # Si hay dos capítulos, descargar el rango especificado
                start_chapter, end_chapter = chapters
                pdfs_data = download_range_of_chapters(manga_name, start_chapter, end_chapter)
            else:
                return Response({'error': 'Formato de solicitud no válido'}, status=status.HTTP_400_BAD_REQUEST)

            if not pdfs_data:
                logger.error('No PDF data generated')
                return Response({'error': 'Error al generar el ZIP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            combined_zip_data = create_zip(pdfs_data)
            
            with open(settings.DOWNLOAD_OUTPUT_PATH, 'wb') as f:
                f.write(combined_zip_data.getvalue())

            with open(settings.DOWNLOAD_OUTPUT_PATH, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="manga_download.zip"'
                response['Content-Length'] = os.path.getsize(settings.DOWNLOAD_OUTPUT_PATH)

            logger.info('Manga download completed successfully')
            return response
            
        except Exception as e:
            logger.error(f'Error processing manga download: {e}', exc_info=True)
            return Response({'error': f'Error interno del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

