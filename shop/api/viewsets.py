from shop.models import Server, Product
from shop.api.serializers import ServerSerializer, ProductSerializer

from rest_framework import viewsets
from rest_framework.response import Response


class ServersViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving servers.
    """

    def list(self, request):
        queryset = Server.objects.all()
        serializer = ServerSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductsViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving products.
    """

    def list(self, request):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving product.
    """

    def retrieve(self, request, pk=None):
        if not 'user_id' in request.session:
            return Response({'detail': 'Nie jesteś zalogowany.'}, status=401)

        queryset = Product.objects.filter(id=pk).values('server__id')
        if not queryset:
            return Response({'detail': 'Nie znaleziono takiego produktu.'}, status=404)

        server_id = queryset[0]['server__id']
        server = Server.objects.filter(id=server_id).values('owner_id')
        admins = Server.get_admins(server_id)

        if request.session['user_id'] in admins or request.session['user_id'] == str(server[0]['owner_id']):
            serializer = ProductSerializer(Product.objects.get(id=pk))
            return Response(serializer.data)

        return Response({'detail': 'Nie posiadasz dostępu do tego produktu.'}, status=401)


