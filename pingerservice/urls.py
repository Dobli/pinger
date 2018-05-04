from django.conf.urls import url

from . import views

app_name = 'pingerservice'
urlpatterns = [
    url(r'^start_ping$', views.start_ping, name='start_ping'),
    # Chart api endpoints
    url(r'^api/chart/poolonline/(?P<pool_id>[0-9]+)/$',
        views.chart_data_pool_online,
        name='api_chart_data_pool_online'),
    url(r'^api/chart/pool/(?P<pool_id>[0-9]+)/$',
        views.chart_data_pool,
        name='api_chart_data_pool'),
    url(r'^api/chart/pool/'
        '(?P<pool_id>[0-9]+)'
        '/(?P<year>[0-9]+)'
        '/(?P<month>[0-9]+)'
        '/(?P<day>[0-9]+)/$',
        views.chart_data_pool_date,
        name='api_chart_data_pool_date'),
    # Export api endpoints
    url(r'^api/csv/pool/', views.generate_csv_data, name='api_csv_data'),
    # Data api endpoints
    url(r'^api/pools/$', views.pools, name='api_pools'),
]
