from django.contrib import admin
from .models import ProfileSkill, Skill, Profile

class SkillAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    readonly_fields = ('id',)
    list_per_page = 10
    
class ProfileSkillAdmin(admin.ModelAdmin):
    search_fields = ('skill__name',)
    readonly_fields = ('id',)
    list_per_page = 10

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_intro', 'location')
    search_fields = ('user__username', 'short_intro', 'location') 
    readonly_fields = ('id', 'updated', 'created', 'user') 
    # raw_id_fields = ('user',)
    list_filter = ('created',) 
    list_per_page = 10
    
    
admin.site.register(Skill, SkillAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileSkill, ProfileSkillAdmin)

