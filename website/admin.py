from django.contrib import admin
from website.models import (Category, SubCategory, WebsiteRecommendation,
                            WebsiteComment, BookRecommendation, BookComment,
                            VideoRecommendation)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(WebsiteRecommendation)
admin.site.register(WebsiteComment)
admin.site.register(BookRecommendation)
admin.site.register(BookComment)
admin.site.register(VideoRecommendation)
