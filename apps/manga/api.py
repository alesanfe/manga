import os

from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.manga.downloader import download_all_chapters, download_selected_chapters, download_range_of_chapters, \
    create_zip
from apps.manga.serializer import MangaDownloadSerializer


class MangaDownloadView(APIView):
    def post(self, request):
        serializer = MangaDownloadSerializer(data=request.data)
        print('Hola')
        if serializer.is_valid():
            manga_name = serializer.validated_data['manga_name']
            chapters = serializer.validated_data['chapters']
            print(chapters)
            if not chapters:  # Si la lista de capítulos está vacía, descargar todo el manga
                pdfs_data = download_all_chapters(manga_name)
            elif len(chapters) == 1:  # Si hay un solo capítulo, descargar ese capítulo
                print("Descargando todo el manga")
                print("================================")
                pdfs_data = download_selected_chapters(manga_name, chapters)
                print("================================")
                print(pdfs_data)
            elif len(chapters) == 2:  # Si hay dos capítulos, descargar el rango especificado
                start_chapter, end_chapter = chapters
                pdfs_data = download_range_of_chapters(manga_name, start_chapter, end_chapter)
            else:
                return Response({'error': 'Formato de solicitud no válido'}, status=status.HTTP_400_BAD_REQUEST)

            if pdfs_data:
                combined_zip_data = create_zip(pdfs_data)

                with open('manga_download.zip', 'wb') as f:
                    f.write(combined_zip_data.getvalue())

                with open('manga_download.zip', 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="manga_download.zip"'
                    response['Content-Length'] = os.path.getsize('manga_download.zip')

                return response
            else:
                return Response({'error': 'Error al generar el ZIP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

