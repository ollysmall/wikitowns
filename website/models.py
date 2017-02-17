from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField()
    category_img = models.ImageField(upload_to='category_images', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=128)
    slug = models.SlugField()

    class Meta:
       unique_together = (("category", "name"),)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class WebsiteRecommendation(models.Model):
    category = models.ForeignKey(Category)
    subcategory = models.ForeignKey(SubCategory)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=300) #this may need changing
    url = models.URLField()
    created_date = models.DateTimeField(
            default=timezone.now)

    class Meta:
       unique_together = (("category", "subcategory", "url"),)

    def __str__(self):
        return self.title
