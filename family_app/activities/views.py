from datetime import timedelta
from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.request import Request

# Swagger UI decorators and types (drf-spectacular)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from activities.models import ActivitiesLog, FamilyMember, Activity
from activities.serializers import ActivitySerializer, FamilyMemberSerializer


class ActivityTimeView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Get total time spent on specific activities",
        description="Calculates the total time a family member spent on given activities within an optional date range.",
        parameters=[
            OpenApiParameter(
                name="activities_ids",
                description="Comma-separated list of activity IDs (e.g., 1,2,3)",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="start_date",
                description="Start date for filtering in YYYY-MM-DD format",
                required=False,
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date for filtering in YYYY-MM-DD format",
                required=False,
                type=OpenApiTypes.DATE,
            ),
        ]
    )
    def get(self, request: Request, family_member_id: int):
        # Safely fetch the user or return 404
        family_member = get_object_or_404(FamilyMember, id=family_member_id)
        
        # Extract query parameters
        raw_ids = request.query_params.get('activities_ids', '')
        activity_ids_list = [int(id_str) for id_str in raw_ids.split(',') if id_str.isdigit()]
        
        # Use .get() without a default empty string, so it returns None if not provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        considered_activities = Activity.objects.all()
        
        if activity_ids_list:
            considered_activities = Activity.objects.filter(id__in=activity_ids_list)
        
        # Build the base queryset
        queryset = ActivitiesLog.objects.filter(
            family_member=family_member,
            activity__in=considered_activities
        )
        
        # Apply date filters dynamically to prevent crashing on empty strings
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # IMPORTANT: Initialize with an empty timedelta, not an int
        time_per_activity = defaultdict(timedelta)
        
        activity_names_map = {activity.id: ({"name": activity.name, "is_good": activity.is_good}) for activity in considered_activities}
        
        for log_entry in queryset:
            # Adding timedelta to timedelta
            time_per_activity[log_entry.activity.id] += (log_entry.end_date - log_entry.start_date)
        
        result = []
        for activity_id, activity_time_delta in time_per_activity.items():
            activity_data = activity_names_map.get(activity_id, {})
            
            activity_name = activity_data.get('name')
            is_good = activity_data.get('is_good')
            
            # Calculate hours by dividing total seconds
            hours_spent = activity_time_delta.total_seconds() / 3600.0
            
            result.append({
                "activity_id": activity_id,
                "activity_name": activity_name,
                "is_good": is_good,
                # Round to 2 decimal places for a cleaner JSON response
                "time_spent_hours": round(hours_spent, 2)
            })
        
        return JsonResponse({"items": result})
    
class ActivitiesView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        activities = Activity.objects.all()
        result = ActivitySerializer(activities, many=True).data
        return JsonResponse({"items": result})
    
class MembersView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        members = FamilyMember.objects.all()
        result = FamilyMemberSerializer(members, many=True).data
        return JsonResponse({"items": result})