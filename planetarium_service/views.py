from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter
from planetarium_service.models import ShowSession, PlanetariumDome, AstronomyShow, ShowTheme, Reservation
from planetarium_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium_service.serializers import (ShowSessionListSerializer,
                                             ShowSessionDetailSerializer,
                                             ShowSessionSerializer,
                                             PlanetariumDomeSerializer,
                                             AstronomyShowSerializer,
                                             AstronomyShowListSerializer,
                                             AstronomyShowDetailSerializer,
                                             ShowThemeListSerializer,
                                             ShowThemeDetailSerializer,
                                             ShowThemeSerializer,
                                             ReservationSerializer,
                                             ReservationListSerializer)
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet


class AstronomyShowViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = AstronomyShow.objects.prefetch_related("title")
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return AstronomyShowSerializer


class ShowThemeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = ShowTheme.objects.all()

        show_id = self.request.query_params.get("show_id")
        show_name = self.request.query_params.get("show_name")

        if show_id:
            queryset = queryset.filter(
                astronomy_show_id=show_id
            )
        if show_name:
            queryset = queryset.filter(
                astronomy_show__title__icontains=show_name
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowThemeListSerializer
        if self.action == "retrieve":
            return ShowThemeDetailSerializer
        return ShowThemeSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_id",
                type=int,
                description="Filter by show id (ex. ?show_id=1)",
            ),
            OpenApiParameter(
                "show_name",
                type=str,
                description="Filter by show name (ex. ?show_name=show)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = ShowSession.objects.select_related(
            "astronomy_show",
            "planetarium_dome"
        )

        date = self.request.query_params.get("date")
        show_id = self.request.query_params.get("show_id")
        show_name = self.request.query_params.get("show_name")

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)
        if show_id:
            queryset = queryset.filter(astronomy_show_id=show_id)
        if show_name:
            queryset = queryset.filter(
                astronomy_show__title__icontains=show_name
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_id",
                type=int,
                description="Filter by show id (ex. ?show_id=1)",
            ),
            OpenApiParameter(
                "show_name",
                type=str,
                description="Filter by show name (ex. ?show_name=show)",
            ),
            OpenApiParameter(
                "date",
                type=str,
                description="Filter by date (ex. ?date=2003-04-17)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 30


class ReservationViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         GenericViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets",
        "tickets__show_session",
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome",
    )

    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Reservation.objects.prefetch_related(
            "tickets",
            "tickets__show_session",
            "tickets__show_session__astronomy_show",
            "tickets__show_session__planetarium_dome",
        )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
