from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from .serializers import UserSerializer, UserInfoSerializer, UserRegSerializer

from .filters import UserFilter

from menu.common import get_menu_tree
from django.contrib.auth.models import Group


User = get_user_model()


class UserRegViewset(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    create:
    创建用户
    
    update:
    修改密码
    """
    queryset = User.objects.all()
    serializer_class = UserRegSerializer

# from rest_framework import viewsets,
class UserInfoViewset(viewsets.ViewSet):
# class UserInfoViewset(viewsets.ModelViewSet):
    """
    获取当前登陆的用户信息
    """
#     queryset = User.objects.all()
#     serializer_class = UserInfoSerializer
#     filter_class = UserFilter
#     filter_fields = ("username",)
#     extra_perms_map = {
#         "GET": ["users.show_user_list"]
#     }
#
#     def get_queryset(self):
#         queryset = super(UserInfoViewset, self).get_queryset()
#         queryset = queryset.order_by("id")
#         queryset = queryset.exclude(is_superuser=True)
#         return queryset

    permission_classes = (permissions.IsAuthenticated,)
    def list(self, request, *args, **kwargs):
        # 获取登陆用户的用户组信息
        user = self.request.user
        user_groups_obj = user.groups.values()
        user_groups_info = {}
        user_groups_infos = []
        from copy import deepcopy
        for group_obj in user_groups_obj:
            user_groups_info["gid"] = group_obj["id"]
            user_groups_info["gname"] = group_obj["name"]

            user_groups_infos.append(user_groups_info)
            # 需要深度复制 否则下次更改时会连之前的列表中的值一起更改
            user_groups_info = deepcopy(user_groups_info)

        # 如果登录用户是超级用户则返回所有的组ID
        if self.request.user.is_superuser:
            user_groups_infos = Group.objects.values()
            # print(user_groups_infos)
            data = {
                "username": self.request.user.username,
                "name": self.request.user.name,
                "is_superuser": self.request.user.is_superuser,
                "groupsinfo": user_groups_infos,
                "menus": get_menu_tree(self.request.user.get_view_permissions())
            }
        else:
            data = {
                "username": self.request.user.username,
                "name": self.request.user.name,
                "is_superuser": self.request.user.is_superuser,
                "groupsinfo": user_groups_infos,
                "menus": get_menu_tree(self.request.user.get_view_permissions())
            }

        return Response(data)


class UsersViewset(viewsets.ModelViewSet):
    """
    retrieve:
    获取用户信息

    list:
    获取用户列表

    update:
    更新用户信息

    delete:
    删除用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = UserFilter
    filter_fields = ("username",)
    extra_perms_map = {
        "GET": ["users.show_user_list"]
    }

    def get_queryset(self):
        queryset = super(UsersViewset, self).get_queryset()
        queryset = queryset.order_by("id")
        queryset = queryset.exclude(is_superuser=True)
        return queryset
