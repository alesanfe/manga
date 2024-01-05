from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.manga.downloader import download_all_chapters, download_selected_chapters, download_range_of_chapters, \
    combine_pdfs
from apps.manga.serializer import MangaDownloadSerializer


class MangaDownloadView(APIView):
    def post(self, request):
        serializer = MangaDownloadSerializer(data=request.data)
        if serializer.is_valid():
            manga_name = serializer.validated_data['manga_name']
            chapters = serializer.validated_data['chapters']

            if not chapters:  # Si la lista de capítulos está vacía, descargar todo el manga
                pdfs_data = download_all_chapters(manga_name)
            elif len(chapters) == 1:  # Si hay un solo capítulo, descargar ese capítulo
                pdfs_data = download_selected_chapters(manga_name, chapters)
            elif len(chapters) == 2:  # Si hay dos capítulos, descargar el rango especificado
                start_chapter, end_chapter = chapters
                pdfs_data = download_range_of_chapters(manga_name, start_chapter, end_chapter)
            else:
                return Response({'error': 'Formato de solicitud no válido'}, status=status.HTTP_400_BAD_REQUEST)

            if pdfs_data:
                if isinstance(pdfs_data, list):
                    # Si es una lista de PDFs, combínalos en un solo PDF
                    combined_pdf_data = combine_pdfs(pdfs_data)  # Implementa la función combine_pdfs según tus necesidades
                    response = Response(combined_pdf_data.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="manga_download.pdf"'
                    return response
                else:
                    # Si es un solo PDF, devuelve ese PDF
                    response = Response(pdfs_data.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="manga_download.pdf"'
                    return response
            else:
                return Response({'error': 'Error al generar el PDF'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


