import json
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, DeleteView, UpdateView, ListView, CreateView

from ads.models import Ads, Categories, Location, User
from homework_27 import settings


class AdDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdsView(ListView):
    model = Ads
    qs = Ads.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.select_related("author_id").order_by("-price")
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        ads = []
        for ad in page_obj:
            ads.append({"id": ad.id,
                        "name": ad.name,
                        "price": ad.price,
                        "description": ad.description,
                        "is_published": ad.is_published,
                        "image": ad.image.url,
                        "author_id": ad.author_id_id,
                        "author": ad.author_id.first_name,
                        "category_id": ad.category_id_id,
                        })
        response = {
            "items": ads,
            "total": page_obj.paginator.count,
            "num_pages": page_obj.paginator.num_pages,
        }
        return JsonResponse(response, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsCreateView(CreateView):
    model = Ads
    fields = ["name", "author_id", "price", "description", "is_published", "category_id"]

    def post(self, request, *args, **kwargs):
        ads_data = json.loads(request.body)
        ads = Ads.objects.create(
            name=ads_data["name"],
            author_id=get_object_or_404(User, pk=ads_data["author_id"]),
            price=ads_data["price"],
            description=ads_data["description"],
            is_published=ads_data["is_published"],
            category_id=get_object_or_404(Categories, pk=ads_data["category_id"]),
        )

        return JsonResponse({"id": ads.id,
                             "name": ads.name,
                             "author_id": ads.author_id_id,
                             "author": ads.author_id.first_name,
                             "price": ads.price,
                             "description": ads.description,
                             "is_published": ads.is_published,
                             "category_id": ads.category_id_id,
                             "image": ads.image.url,
                             })


class AdsDetailView(DetailView):
    model = Ads

    def get(self, request, *args, **kwargs):
        try:
            ads = self.get_object()
        except Ads.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"id": ads.id,
                             "name": ads.name,
                             "author_id": ads.author_id_id,
                             "author": ads.author_id.first_name,
                             "price": ads.price,
                             "description": ads.description,
                             "is_published": ads.is_published,
                             "category_id": ads.category_id_id,
                             "image": ads.image.url,
                             })


@method_decorator(csrf_exempt, name='dispatch')
class AdsUpdateView(UpdateView):
    model = Ads
    fields = ["name", "author_id", "price", "description", "category_id"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        ad_data = json.loads(request.body)
        self.object.name = ad_data["name"]
        self.object.price = ad_data["price"]
        self.object.author_id = get_object_or_404(User, pk=ad_data["author_id"])
        self.object.category_id = get_object_or_404(Categories, pk=ad_data["category_id"])
        self.object.description = ad_data["description"]

        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id_id,
            "author": self.object.author_id.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id_id,
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
            "author_id": self.object.author_id_id,
            "author": self.object.author_id.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id_id,
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
        cat = Categories.objects.create(
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
                             "name": cat.name,
                             })


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


