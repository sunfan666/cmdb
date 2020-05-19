from .models import Product


res_list = []

def get_product_object(pk):
    try:
        return Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return None


def get_product_tree(queryset):
    ret = []
    for obj in queryset:
        # print(obj)
        # print(queryset)
        node = _get_product_node(obj)
        node["children"] = _get_product_children(Product.objects.filter(pid__exact=obj.id))

        if node['children'] == []:
            res_dict = {}
            res_dict['service_name'] = obj.service_name
            res_dict['id'] = obj.id
            res_list.append(res_dict)
            ret.append(_get_product_node(obj))
        else:
            # ret.append(node)
            for children in node['children']:
                # print(children)
                ret.append(children)
    # print(ret)
    return ret


def _get_product_children(queryset):
    # print(queryset)
    ret = []
    for obj in queryset:
        # print(obj)
        # print(obj.id)
        node = _get_product_node(obj)
        # print(node)
        node['children'] = _get_product_children(Product.objects.filter(pid__exact=obj.id))
        # print(queryset.filter(pid__exact=obj.id))
        # print(node)
        if node['children'] == []:
            res_dict = {}
            res_dict['service_name'] = obj.service_name
            res_dict['id'] = obj.id
            res_list.append(res_dict)
            # print(res_list)
            ret.append(_get_product_node(obj))
        else:
            # ret.append(node)
            for children in node['children']:
                # print(children)
                ret.append(children)

    return ret

def _get_product_node(product_obj):
    node = {}
    node["id"] = product_obj.id
    node["service_name"] = product_obj.service_name
    node["module_letter"] = product_obj.module_letter
    node["pid"] = _get_product_parent(product_obj)
    return node


def _get_product_parent(product_obj):
    return product_obj.pid