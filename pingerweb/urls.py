from django.conf.urls import url

from . import views

app_name = 'pingerweb'
urlpatterns = [
    # example: /pingerweb/
    url(r'^$', views.index, name='home'),
    # example: /pingerweb/pools
    url(r'^pools/$', views.pools, name='pools'),
    # example: /pingerweb/online
    url(r'^online/$', views.online, name='online'),
    # example: /pingerweb/consumption
    url(r'^consumption/$', views.consumption, name='consumption'),
    # example: /pingerweb/export
    url(r'^export/$', views.export, name='export'),
]
