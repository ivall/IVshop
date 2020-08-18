from shop.models import Server, Product
from shop.api.serializers import ServerSerializer, ProductSerializer

from django.shortcuts import get_object_or_404
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
            return Response({'detail': 'Nie jesteś zalogowany.'})

        queryset = get_object_or_404(Product, id=pk, server__owner_id=request.session['user_id'])
        serializer = ProductSerializer(queryset)
        return Response(serializer.data)
