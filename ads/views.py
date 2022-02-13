import json
import pandas as pd
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

from ads.models import Ads, Categories


class AdDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"}, status=200)


class DataAds(View):  # заполнение БД данными из csv
    def get(self, request):
        data_ads = pd.read_csv("ads.csv", sep=",").to_dict()
        i = 0
        while max(data_ads["Id"].keys()) >= i:
            Ads.objects.create(name=data_ads["name"][i], author=data_ads["author"][i], price=data_ads["price"][i],
                               description=data_ads["description"][i], address=data_ads["address"][i],
                               is_published=data_ads["is_published"][i])
            i += 1

        data_cat = pd.read_csv("categories.csv", sep=",").to_dict()
        i = 0
        while max(data_cat["id"].keys()) >= i:
            Categories.objects.create(name=data_cat["name"][i])
            i += 1

        return JsonResponse("База заполнена", safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdsView(View):
    def get(self, request):
        try:
            ads = Ads.objects.all()
            response = []
            for ad in ads:
                response.append({"id": ad.id,
                                 "name": ad.name,
                                 "author": ad.author,
                                 "price": ad.price,
                                 "description": ad.description,
                                 "address": ad.address,
                                 "is_published": ad.is_published})
        except Ads.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse(response, safe=False)

    def post(self, request):
        ads_data = json.loads(request.body)
        ads = Ads.objects.create(
            name=ads_data["name"],
            author=ads_data["author"],
            price=ads_data["price"],
            description=ads_data["description"],
            address=ads_data["address"],
            is_published=ads_data["is_published"],
        )

        return JsonResponse({"name": ads.name,
                             "author": ads.author,
                             "price": ads.price,
                             "description": ads.description,
                             "address": ads.address,
                             "is_published": ads.is_published})


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
                             "is_published": ads.is_published})


@method_decorator(csrf_exempt, name='dispatch')
class CatView(View):
    def get(self, request):
        try:
            categories = Categories.objects.all()
            response = []
            for cat in categories:
                response.append({"id": cat.id,
                                 "name": cat.name,
                                 })

        except Categories.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)

        return JsonResponse(response, safe=False)

    def post(self, request):
        cat_data = json.loads(request.body)
        cat = Categories.objects.create(name=cat_data["name"])

        return JsonResponse({"name": cat.name,
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
