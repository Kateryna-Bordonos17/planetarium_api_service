from rest_framework import serializers
from django.db import transaction

from planetarium_service.models import (AstronomyShow,
                                        PlanetariumDome,
                                        Reservation,
                                        Ticket,
                                        ShowSession,
                                        ShowTheme)


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id",
                  "title",
                  "description",
                  "show_theme")


class AstronomyShowListSerializer(AstronomyShowSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id",
                  "title",
                  "show_theme")


class AstronomyShowDetailSerializer(AstronomyShowListSerializer):
    show_themes = serializers.StringRelatedField(many=True)

    class Meta:
        model = AstronomyShow
        fields = ("id",
                  "title",
                  "description",
                  "show_theme")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id",
                  "name",
                  "rows",
                  "seats_in_row",
                  "capacity")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("show_session",
                  "row",
                  "seat")

    def validate(self, attrs):
        row = attrs.get("row")
        seat = attrs.get("seat")
        show_session = attrs.get("show_session")

        if row < 0 or row > show_session.planetarium_dome.rows:
            raise serializers.ValidationError(
                f"Row must be in available range: "
                f"(1, {show_session.planetarium_dome.rows})"
            )
        if seat < 0 or seat > show_session.planetarium_dome.seats_in_row:
            raise serializers.ValidationError(
                "Seat must be in available range: "
                f"(1, {show_session.planetarium_dome.seats_in_row})"
            )

        is_available = (
            Ticket.objects.filter(show_session=show_session,
                                  row=row,
                                  seat=seat).count() == 0
        )
        if not is_available:
            raise serializers.ValidationError("Ticket is already taken")

        return attrs


class TicketListSerializer(TicketSerializer):
    show_session = serializers.StringRelatedField(many=False,
                                                  read_only=True)
    reservation = serializers.StringRelatedField(many=False,
                                                 read_only=True)

    class Meta:
        model = Ticket
        fields = ("id",
                  "reservation",
                  "show_session",
                  "row",
                  "seat")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row",
                  "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True,
                               read_only=False,
                               allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id",
                  "tickets",
                  "created_at")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Reservation.objects.create(**validated_data)

        for ticket_data in tickets_data:
            ticket_data["reservation"] = order
            Ticket.objects.create(**ticket_data)

        return order


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True,
                                   read_only=True)


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = "__all__"


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer(many=False,
                                             read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False,
                                                 read_only=True)

    taken_places = TicketSeatsSerializer(source="tickets",
                                         many=True,
                                         read_only=True)

    class Meta:
        model = ShowSession
        fields = ("id",
                  "astronomy_show",
                  "planetarium_dome",
                  "show_time",
                  "taken_places")


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.StringRelatedField(
        many=False,
        read_only=True
    )
    planetarium_dome = serializers.StringRelatedField(
        many=False,
        read_only=True
    )
    tickets_available = serializers.SerializerMethodField(
        method_name="get_tickets_available"
    )

    @staticmethod
    def get_tickets_available(obj):
        return obj.planetarium_dome.capacity - obj.tickets.count()

    class Meta:
        model = ShowSession
        fields = ("id",
                  "astronomy_show",
                  "planetarium_dome",
                  "show_time",
                  "tickets_available")


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = "__all__"


class ShowThemeListSerializer(ShowThemeSerializer):
    class Meta:
        model = ShowTheme
        fields = "__all__"


class ShowThemeDetailSerializer(ShowThemeSerializer):
    shows = serializers.SerializerMethodField(method_name="get_show")

    class Meta:
        model = ShowTheme
        fields = ("id",
                  "name",
                  "shows")

    @staticmethod
    def get_show(obj):
        return obj.astronomy_show.all().values_list("title",
                                                    flat=True)
