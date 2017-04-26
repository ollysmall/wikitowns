from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from isbn_field import ISBNField

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
    website_author = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    subcategory = models.ForeignKey(SubCategory)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=300) #this may need changing
    url = models.URLField()
    created_date = models.DateTimeField(
            default=timezone.now)
    upvote = models.ManyToManyField(User, related_name='website_upvote')
    downvote = models.ManyToManyField(User, related_name='website_downvote')
    bookmark = models.ManyToManyField(User, related_name='bookmark')

    @property
    def total_votes(self):
        total_upvotes = self.upvote.count()
        total_downvotes = self.downvote.count()

        return total_upvotes - total_downvotes



    class Meta:
       unique_together = (("category", "subcategory", "url"),)

    def __str__(self):
        return self.title

class WebsiteComment(models.Model):
    website = models.ForeignKey(WebsiteRecommendation, related_name='comments')
    author = models.ForeignKey(User)
    text = models.TextField(max_length=2000) #check this length is ok
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

class BookRecommendation(models.Model):
    isbn = ISBNField()
    title = models.CharField(max_length=128)
    recommended_by = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    subcategory = models.ForeignKey(SubCategory)
    book_author = models.CharField(max_length=128)
    book_description = models.CharField(max_length=10000) #check length is ok
    created_date = models.DateTimeField(default=timezone.now)
    book_url = models.URLField(max_length=2000) #this will be a link to the book on amazon
    book_image_url = models.URLField(max_length=500) #check length is ok
    book_publish_date = models.DateField()

    class Meta:
       unique_together = (("category", "subcategory", "isbn"),)

    def __str__(self):
        return self.title
