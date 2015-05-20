from django.conf.urls import patterns, include, url
from mccme import views

urlpatterns = patterns(
    '',

    url(r'^$', views.test),
    url(r'^action/', views.action),
    url(r'^show_me/', views.show_me),
    url(r'^user/(?P<uid>\d+)/$', views.user_stats),
    url(r'^uid/(?P<uid>\d+)/$', views.show_user)

)
