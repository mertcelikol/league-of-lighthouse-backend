import os
from fastapi_amis_admin import i18n
i18n.set_language(language='en_US')

from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from .models import User, StudentData
from .utils import add_documentation_panel

# Setup AdminSite with DB URL
site = AdminSite(settings=Settings(database_url=os.getenv("DATABASE_URL")))

# Optional: Add a custom help panel for students/admins
site = add_documentation_panel(site)

""" 🔥 ⬇️ Add all your models below this line ⬇️ 🔥 """

# Register User model
@site.register_admin
class UserAdmin(admin.ModelAdmin):
    page_schema = 'User'
    model = User
    search_fields = ['email', 'role']
    list_display = ['id', 'email', 'role', 'is_active']
    readonly_fields = ['id']

# Register StudentData model
@site.register_admin
class StudentDataAdmin(admin.ModelAdmin):
    page_schema = 'StudentData'
    model = StudentData
    list_display = ['id', 'student_id', 'data']
    search_fields = ['data']
