"""bvt_apk URL Configuration
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
import xadmin
from django.views.static import serve
from django.views.generic import  TemplateView
from users.views import  RegisterView
from users import  views

urlpatterns = [
	path('admin/', admin.site.urls),
	url(r'^xadmin/', xadmin.site.urls),
	url(r'^captcha/', include('captcha.urls')),
	# """用户管理"""
	# http://127.0.0.1:8000/test/?name=alvin
	path('test/', views.qatest),
	path('index/', views.index, name="index"),
	path('', views.index),
	path('logout/', views.logout),
	path('accounts/login/', views.index),
	# path( 'register/', views.register ),
	url( r'^register/', RegisterView.as_view(), name='register' ),
	# """项目管理"""
	path('project/', include('project.urls')),
	# """模块管理"""
	path('module/', include('module.urls')),
	# """apk管理"""
	path( 'apk/', include( 'apk.urls' ) ),
]
