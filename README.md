<a href="https://www.noobhub.io">
    <img src="https://www.noobhub.io/static/website/noobhub-twit.png" alt="Noobhub logo" title="noobhub" align="right" height="70" />
</a>

# noobhub

www.noobhub.io is a website to allow people to find, share, rank and bookmark coding resources.

## Why?

Whilst learning to code I often found myself spending quite a lot of time trying to find the best resources to learn from. 
noobhub aims to help solve this by allowing people to share resources they found useful in order to make it easy for others to find.
The ranking system ensures users see the best content first and the bookmarks let them quickly find their favourite content again.

## Features

* Websites, books and videos can be recommended by registered users
* Content can be ranked up or down to highlight the best resources.
* Bookmarks allow users to easily find their favourite content.
* To recommend a book you only need to enter the ISBN and the Amazon API is used to fetch the books details.
* To recommend a video you only need to enter a youtube URL and the YouTube API fetches the videos details.
* Users have profile pages which details the content they have bookmarked and recommended. 
* A simple search feature allows users to narrow down their search within categories.
* Users can filter recommendations by all time best, best of year, best of month or by newest.
* Users can leave comments on recommended resources. 
* Inappropriate recommendations can be reported by users.


## Built with

* [Django](https://www.djangoproject.com/) - Back end framework 
* [Bootstrap](https://getbootstrap.com/) - Front end framework
* [Heroku](https://www.heroku.com/home) - Platform as a Service
* [Amazon S3](https://aws.amazon.com/s3) - Storage and serving of Media files 
* [PostgreSQL](https://www.postgresql.org/) - Database

## API Reference

* [Amazon Product Advertising API](https://docs.aws.amazon.com/AWSECommerceService/latest/DG/Welcome.html) - To fetch book data
* [Google API Python Client](https://developers.google.com/api-client-library/python/) - To fetch youtube data

## Author

Oliver Small - You can reach me at oliver@rotherfields.co.uk

## Acknowledgments

* [Bottlenose](https://github.com/lionheart/bottlenose) - Python wrapper over the Amazon Product Advertising API
* [Django isbn field](https://github.com/secnot/django-isbn-field) - Provides django model field to store and validate ISBN numbers.
* [Flaticon](https://www.flaticon.com) - Website icons
* [Font Awesome](https://fontawesome.com/) - Website icons
* [Django registration redux](https://django-registration-redux.readthedocs.io/en/latest/) - User registration
* [Django el pagination](https://github.com/shtalinberg/django-el-pagination) - Endless pagination
* [Beautiful soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Pull data out of XML files
* [Boto 3](https://boto3.readthedocs.io/en/latest/) - Amazon S3 integration
* [Robert Wheel](http://robertwheal.co.uk/) - Logo design and icon editing

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
