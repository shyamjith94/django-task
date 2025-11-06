import csv
from io import TextIOWrapper
from re import A
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FileData
from .serializer import FileDataSerializer
from django.db.models import Count, Avg, Max, Min

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


# Create your views here.


class UploadFile(APIView):
    def post(self, request, format=None):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_wrapper = TextIOWrapper(file.file, encoding='utf-8')
        reader = csv.DictReader(file_wrapper)

        file_obj = []
        batch_size = 5000  # adjust for your system

        for i, row in enumerate(reader):
            # Create model instances without saving them immediately
            file_obj.append(
                FileData(
                    name=row.get('name'),
                    category=row.get('category'),
                    price=row.get('price'),
                    stock=row.get('stock'),
                    created_at=row.get('created_at')
                )
            )

            # When we reach a full batch, persist and clear the list
            if (i + 1) % batch_size == 0:
                FileData.objects.bulk_create(file_obj)
                file_obj = []

        # Persist any remaining objects after the loop
        if file_obj:
            FileData.objects.bulk_create(file_obj)
        return Response({"message": "File uploaded successfully"})
    
    @method_decorator(cache_page(60*2))  # Cache for 2 minutes
    def get(self, request, format=None):
        allowed_filters = ['name', 'category', 'stock', 'price', 'created_at']

        filter_dict = {}
        for field in allowed_filters:
            value = request.query_params.get(field, None)
            if value:
                if field in ['name', 'category',]:
                    filter_dict[f"{field}__icontains"] = value
                else:
                    filter_dict[field] = value
        queryset = FileData.objects.filter(**filter_dict)

        agg_type = request.query_params.get('agg')   # e.g., count, avg, max, min
        agg_field = request.query_params.get('field') # e.g., age

        aggregation_result = None
        if agg_type and agg_field:
            if agg_type.lower() == 'count':
                aggregation_result = queryset.aggregate(count=Count(agg_field))
            elif agg_type.lower() == 'avg':
                aggregation_result = queryset.aggregate(avg=Avg(agg_field))
            elif agg_type.lower() == 'max':
                aggregation_result = queryset.aggregate(max=Max(agg_field))
            elif agg_type.lower() == 'min':
                aggregation_result = queryset.aggregate(min=Min(agg_field))

        # Serialize data
        serializer = FileDataSerializer(queryset, many=True)

        response_data = {
            "data": serializer.data,
            "aggregation": aggregation_result
        }

        # serializer = FileDataSerializer(queryset, many=True)
        return Response(response_data, status=200)