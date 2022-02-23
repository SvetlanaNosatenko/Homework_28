import json
import pandas as pd
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, DeleteView, UpdateView, ListView, CreateView

from ads.models import Ads, Categories, Location, User
from homework_27 import settings


class AdDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"}, status=200)


class DataAds(View):  # заполнение БД данными из csv
    def get(self, request):

        data_location = pd.read_csv("location.csv", sep=",")
        i = 0
        while max(data_location["id"].keys()) >= i:
            Location.objects.create(name=data_location["name"][i],
                                    lat=data_location["lat"][i],
                                    lng=data_location["lng"][i])
            i += 1

        data_user = pd.read_csv("user.csv", sep=",")
        i = 0
        while max(data_user["id"].keys()) >= i:
            User.objects.create(first_name=data_user["first_name"][i], last_name=data_user["last_name"][i],
                                username=data_user["username"][i], password=data_user["password"][i],
                                role=data_user["role"][i], age=data_user["age"][i],
                                location=data_location["location"][i])
            i += 1

        data_cat = pd.read_csv("categories.csv", sep=",")
        i = 0
        while max(data_cat["id"].keys()) >= i:
            Categories.objects.create(name=data_cat["name"][i])
            i += 1

        data_ads = pd.read_csv("ads.csv", sep=",")

        i = 0
        while max(data_ads["Id"].keys()) >= i:
            Ads.objects.create(name=data_ads["name"][i], author_id=data_user["id"][i], price=data_ads["price"][i],
                               description=data_ads["description"][i], address=data_ads["address"][i],
                               is_published=data_ads["is_published"][i], category_id=data_cat["id"])
            i += 1
        return JsonResponse("База заполнена", safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdsView(ListView):
    model = Ads
    qs = Ads.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.select_related("author").order_by("-price")
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        ads = []
        for ad in page_obj:
            ads.append({"id": ad.id,
                        "name": ad.name,
                        "author": ad.author,
                        "price": ad.price,
                        "description": ad.description,
                        "address": ad.address,
                        "is_published": ad.is_published,
                        "category_id": get_object_or_404(Categories, ad["category_id"]),
                        "image": ad.image.url,
                        })
        response = {
            "items": ads,
            "total": page_obj.paginator.count,
            "num_pages": page_obj.paginator.num_pages
        }
        return JsonResponse(response)


@method_decorator(csrf_exempt, name='dispatch')
class AdsCreateView(CreateView):
    model = Ads
    fields = ["name", "author", "price", "description", "is_published", "category_id"]

    def post(self, request, *args, **kwargs):
        ads_data = json.loads(request.body)
        ads = Ads.objects.create(
            name=ads_data["name"],
            author=get_object_or_404(User, ads_data["author_id"]),
            price=ads_data["price"],
            description=ads_data["description"],
            is_published=ads_data["is_published"],
            category=get_object_or_404(Categories, ads_data["category_id"]),
        )

        return JsonResponse({"id": ads.id,
                             "name": ads.name,
                             "author_id": ads.author_id,
                             "author": ads.author.first_name,
                             "price": ads.price,
                             "description": ads.description,
                             "is_published": ads.is_published,
                             "category_id": ads.category_id,
                             "image": ads.image.url,
                             })


class AdsDetailView(DetailView):
    model = Ads

    def get(self, request, *args, **kwargs):
        try:
            ads = self.get_object()
        except Ads.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"name": ads.name,
                             "author": ads.author,
                             "price": ads.price,
                             "description": ads.description,
                             "address": ads.address,
                             "is_published": ads.is_published,
                             "image": ads.image.url,
                             })


@method_decorator(csrf_exempt, name='dispatch')
class AdsUpdateView(UpdateView):
    model = Ads
    fields = ["name", "author", "price", "description", "category"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        ad_data = json.loads(request.body)
        self.object.name = ad_data["name"]
        self.object.price = ad_data["price"]
        self.object.author = get_object_or_404(User, ad_data["author_id"])
        self.object.category = get_object_or_404(Categories, ad_data["category_id"])
        self.object.description = ad_data["description"]

        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": self.object.author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "image": self.object.image.url,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdsImageView(UpdateView):
    model = Ads
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = request.FILES['image']
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": self.object.author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "image": self.object.image.url,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdsDeleteView(DeleteView):
    model = Ads
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CatView(ListView):
    model = Categories
    qs = Categories.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.order_by("name")
        response = []
        for cat in self.object_list:
            response.append({"id": cat.id,
                             "name": cat.name,
                             })

        return JsonResponse(response, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CatCreateView(CreateView):
    model = Categories
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        cat_data = json.loads(request.body)
        cat = Ads.objects.create(
            name=cat_data["name"],
        )

        return JsonResponse({"id": cat.id,
                             "name": cat.name,
                             })


class CatDetailView(DetailView):
    model = Categories

    def get(self, request, *args, **kwargs):
        try:
            cat = self.get_object()
        except Categories.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"id": cat.id,
                             "name": cat.name})


@method_decorator(csrf_exempt, name='dispatch')
class CatDeleteView(DeleteView):
    model = Categories
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CatUpdateView(UpdateView):
    model = Categories
    fields = ["name"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        cat_data = json.loads(request.body)
        self.object.name = cat_data["name"]

        try:
            self.object.full_clean()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=422)

        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
        })


