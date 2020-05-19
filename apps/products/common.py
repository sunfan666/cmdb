from .models import Product


def get_product_object(pk):
    try:
        return Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return None


def get_product_tree(queryset, group_queryset=None):
    ret = []
    first_products = _get_first_product(queryset)
    for obj in first_products:
        print(first_products)
        node = _get_product_node(obj, group_queryset)
        node["children"] = _get_product_children(queryset.filter(pid__exact=obj.id), group_queryset)
        ret.append(node)
    return ret


def _get_first_product(queryset):
    ret = []
    def check_exists(obj):
        if obj in ret:
            return True
        return False
    for obj in queryset:
        if obj.pid == 0:
            # 当前节点为一级
            if not check_exists(obj):
                ret.append(obj)
        else:
            pass
    return ret

def _get_product_children(queryset, group_queryset=None):
    # print(queryset)
    ret = []
    for obj in queryset:
        # print(obj)
        # print(obj.id)
        node = _get_product_node(obj, group_queryset)
        # print(node)
        # print(group_queryset)
        node['children'] = _get_product_children(Product.objects.filter(pid__exact=obj.id), group_queryset)
        # print(queryset.filter(pid__exact=obj.id))
        # print(node)
        if node['children'] == []:
            ret.append(_get_product_node(obj, group_queryset))
        else:
            ret.append(node)


        # ret.append(_get_product_node(obj, group_queryset))
    return ret

def _get_product_node(product_obj, group_queryset=None):
    node = {}
    node["id"] = product_obj.id
    node["label"] = product_obj.service_name
    # node["module_letter"] = product_obj.module_letter
    # node['show'] = product_obj.show
    node["pid"] = _get_product_parent(product_obj)
    if group_queryset is not None:
        node["permission"] = _get_product_permission(product_obj, group_queryset)
    return node


def _get_product_parent(product_obj):
    # try:
    #     return product_obj.pid
    # except:
    #     return 0
    return product_obj.pid


def _get_product_permission(product_obj, group_queryset=None):
    if group_queryset is None:
        return True
    try:
        group_queryset.get(pk=product_obj.id)
        return True
    except:
        return False