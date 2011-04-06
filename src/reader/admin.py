from django.contrib import admin
from reader.models import Category, Feed, FeedEntry, UserCategory, UserEntry, UserFeed

class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category,CategoryAdmin)

class FeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(Feed,FeedAdmin)

class FeedEntryAdmin(admin.ModelAdmin):
    pass

admin.site.register(FeedEntry,FeedEntryAdmin)

class UserCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserCategory,UserCategoryAdmin)

class UserEntryAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserEntry,UserEntryAdmin)

class UserFeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserFeed,UserFeedAdmin)

