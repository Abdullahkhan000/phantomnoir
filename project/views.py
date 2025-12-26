from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Series , Movie
from .serializers import SeriesSerializer , MovieSerializer
from .filters import SeriesFilter , MovieFilter


class SeriesView(APIView):
    searching_fields = ["name", "genre"]
    ordering_fields = ["release_year"]

    def get_object(self, pk=None):
        try:
            return Series.objects.get(pk=pk)
        except Series.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response(
                    {"error": "Object Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = SeriesSerializer(obj)
            return Response(serializer.data)

        queryset = Series.objects.all().distinct()

        filterset = SeriesFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        queryset = filterset.qs.distinct()

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        order_filter = OrderingFilter()
        queryset = order_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = SeriesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if pk is not None:
            return Response(
                {"error": "POST Cannot Work In Primary Key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        many = isinstance(request.data, list)
        serializer = SeriesSerializer(data=request.data, many=many)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if not pk:
            return Response(
                {"error": "Primary key is required for PATCH"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)

        serializer = SeriesSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieView(APIView):
    searching_fields = ["movie_name","genre"]
    ordering_fields = ["release_year"]
    def get_object(self,pk=None):
        try:
            return Movie.objects.get(pk)
        except Movie.DoesNotExist:
            return None

    def get(self,request,pk=None):
        if pk:
            obj = self.get_object(pk=pk)
            if not obj:
                return Response({"error":"Object Data Not Found"},status=status.HTTP_404_NOT_FOUND)
            serializer = MovieSerializer(obj)
            return Response(serializer.data)

        queryset = Movie.objects.all()
        filterset = MovieFilter(request.GET,queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors,status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        order_filter = OrderingFilter()
        queryset = order_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset,request)
        serializer = MovieSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self,request,pk=None):
        if pk:
            return Response({"error":"POST Cannot Work In Primary Key"},status=status.HTTP_404_NOT_FOUND)

        many = isinstance(request.data, list)
        serializer = MovieSerializer(data=request.data, many=many)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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