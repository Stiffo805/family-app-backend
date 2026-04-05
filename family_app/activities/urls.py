from django.urls import path

from activities.views import ActivityTimeView, ActivitiesView, MembersView

urlpatterns = [
  path('members/<int:family_member_id>/summary/', ActivityTimeView.as_view(), name='activities-summary'),
  path('members/', MembersView.as_view(), name='members'),
  path('', ActivitiesView.as_view(), name='activities')
]