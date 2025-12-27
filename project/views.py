from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Series, Movie
from .serializers import SeriesSerializer, MovieSerializer
from .filters import SeriesFilter, MovieFilter
from .utils import get_obj_or_404

# ------------------ SERIES VIEW ------------------ #

class SeriesView(APIView):
    searching_fields = ["name", "genre"]
    ordering_fields = ["release_year"]

    # GET
    def get(self, request, pk=None):
        if pk:
            obj, error = get_obj_or_404(Series, pk)
            if error:
                return error
            serializer = SeriesSerializer(obj)
            return Response(serializer.data)

        queryset = Series.objects.all().distinct()
        filterset = SeriesFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        queryset = filterset.qs.distinct()

        queryset = SearchFilter().filter_queryset(request, queryset, self)
        queryset = OrderingFilter().filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response({"success": False, "message": "No results found."}, status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = SeriesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST
    def post(self, request, pk=None):
        if pk:
            return Response({"error": "POST cannot work with a primary key"}, status=status.HTTP_400_BAD_REQUEST)
        many = isinstance(request.data, list)
        serializer = SeriesSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH
    def patch(self, request, pk=None):
        obj, error = get_obj_or_404(Series, pk)
        if error:
            return error
        serializer = SeriesSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data patched successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT
    def put(self, request, pk=None):
        obj, error = get_obj_or_404(Series, pk)
        if error:
            return error
        serializer = SeriesSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        obj, error = get_obj_or_404(Series, pk)
        if error:
            return error
        obj.delete()
        return Response({"message": "Object deleted successfully"}, status=status.HTTP_200_OK)

# ------------------ MOVIE VIEW ------------------ #
class MovieView(APIView):
    searching_fields = ["movie_name", "genre"]
    ordering_fields = ["release_year"]

    # GET
    def get(self, request, pk=None):
        if pk:
            obj, error = get_obj_or_404(Movie, pk)
            if error:
                return error
            serializer = MovieSerializer(obj)
            return Response(serializer.data)

        queryset = Movie.objects.all()
        filterset = MovieFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        queryset = filterset.qs

        queryset = SearchFilter().filter_queryset(request, queryset, self)
        queryset = OrderingFilter().filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response({"success": False, "message": "No results found."}, status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = MovieSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST
    def post(self, request, pk=None):
        if pk:
            return Response({"error": "POST cannot work with a primary key"}, status=status.HTTP_400_BAD_REQUEST)
        many = isinstance(request.data, list)
        serializer = MovieSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH
    def patch(self, request, pk=None):
        obj, error = get_obj_or_404(Movie, pk)
        if error:
            return error
        serializer = MovieSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data patched successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj, error = get_obj_or_404(Movie, pk)
        if error:
            return error
        serializer = MovieSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        obj, error = get_obj_or_404(Movie, pk)
        if error:
            return error
        obj.delete()
        return Response({"message": "Object deleted successfully"}, status=status.HTTP_200_OK)


# Rendering For Series UI

def series_list_ui(request):
    series_queryset = Series.objects.all().order_by("-release_year")

    paginator = Paginator(series_queryset, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "series_list": page_obj.object_list,
    }
    return render(request, "anime/series_list.html", context)


def series_detail_ui(request, pk):
    series = get_object_or_404(Series, pk=pk)
    return render(request, "anime/series_detail.html", {"series": series})

# Rendering For Movie UI

def movie_list_ui(request):
    movie_queryset = Movie.objects.all().order_by("-release_year")

    paginator = Paginator(movie_queryset, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "movie_list": page_obj.object_list,
    }
    return render(request, "movie/movie_list.html", context)


def movie_detail_ui(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, "movie/movie_detail.html", {"movie": movie})