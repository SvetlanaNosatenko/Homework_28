from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, ListView, DetailView, CreateView, UpdateView
import json

from ads.models import Location, User, Ads
from homework_27 import settings


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except User.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "age": user.age,
            "locations": list(map(str, user.locations.all())),
        }
        )


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ["username", "password", "first_name", "last_name", "role", "age", "locations"]

    def post(self, request, *args, **kwargs):
        user_data = json.loads(request.body)
        user = User.objects.create(
            username=user_data["username"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            age=user_data["age"],
        )

        for location in user_data["locations"]:
            locations, _ = Location.objects.get_or_create(name=location)
            user.locations.add(locations)

        return JsonResponse({"id": user.id,
                             "username": user.username,
                             "first_name": user.first_name,
                             "last_name": user.last_name,
                             "role": user.role,
                             "age": user.age,
                             "locations": list(map(str, user.locations.all())),
                             })


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ["username", "password", "first_name", "last_name", "age", "locations"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        user_data = json.loads(request.body)

        self.object.username = user_data["username"],
        self.object.password = user_data["password"],
        self.object.first_name = user_data["first_name"],
        self.object.last_name = user_data["last_name"],
        self.object.age = user_data["age"]

        for location in user_data["locations"]:
            locations, _ = Location.objects.get_or_create(name=location)
            self.object.locations.add(locations)

        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "username": self.object.username,
            "first_name": self.object.first_name,
            "last_name": self.object.last_name,
            "age": self.object.age,
            "locations": list(map(str, self.object.locations.all())),
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(ListView):
    model = User
    qs = User.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.annotate(total_ads=Count("ads"))

        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        users = []
        for user in page_obj:
            users.append({"id": user.id,
                          "username": user.username,
                          "first_name": user.first_name,
                          "last_name": user.last_name,
                          "role": user.role,
                          "age": user.age,
                          "total_ads": user.total_ads,
                          "locations": list(map(str, user.locations.all())),
                          })
        response = {
            "items": users,
            "total": page_obj.paginator.count,
            "num_pages": page_obj.paginator.num_pages,
        }
        return JsonResponse(response)
