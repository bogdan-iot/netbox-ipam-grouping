from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from netbox.views import generic

from ipam.models import Prefix, IPAddress, IPRange

from .models import Application, Group
from .forms import ApplicationForm, GroupForm, ApplicationFilterForm, GroupFilterForm
from .tables import ApplicationTable, GroupTable
from .filtersets import ApplicationFilterSet, GroupFilterSet


def _user_owns(obj, user):
    if not obj.owner:
        return False
    if obj.owner.users.filter(pk=user.pk).exists():
        return True
    if obj.owner.user_groups.filter(
        pk__in=user.groups.values_list("pk", flat=True)
    ).exists():
        return True
    return False


def _inject_request(form_class, request):
    def form_with_request(*args, **kwargs):
        kwargs.setdefault("request", request)
        return form_class(*args, **kwargs)
    return form_with_request


# ------------------------------------------------------------------
# Application views
# ------------------------------------------------------------------

class ApplicationListView(generic.ObjectListView):
    queryset = Application.objects.prefetch_related("owner", "tags")
    table = ApplicationTable
    filterset = ApplicationFilterSet
    filterset_form = ApplicationFilterForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(owner__users=request.user) |
            Q(owner__user_groups__in=request.user.groups.all())
        ).distinct()


class ApplicationView(generic.ObjectView):
    queryset = Application.objects.prefetch_related("owner", "tags")

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.filter(
            custom_field_data__ipam_application=instance.pk
        ).order_by("prefix")
        ip_addresses = IPAddress.objects.filter(
            custom_field_data__ipam_application=instance.pk
        ).order_by("address")
        ip_ranges = IPRange.objects.filter(
            custom_field_data__ipam_application=instance.pk
        ).order_by("start_address")
        return {
            "ipam_groups": instance.ipam_groups.prefetch_related("owner"),
            "prefixes": prefixes,
            "ip_addresses": ip_addresses,
            "ip_ranges": ip_ranges,
        }


class ApplicationCreateView(generic.ObjectEditView):
    queryset = Application.objects.all()
    form = ApplicationForm

    def dispatch(self, request, *args, **kwargs):
        self.form = _inject_request(ApplicationForm, request)
        return super().dispatch(request, *args, **kwargs)


class ApplicationEditView(generic.ObjectEditView):
    queryset = Application.objects.all()
    form = ApplicationForm

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Application, pk=kwargs["pk"])
        if not request.user.is_superuser and not _user_owns(obj, request.user):
            messages.error(request, "You do not have permission to edit this application.")
            return redirect(obj.get_absolute_url())
        self.form = _inject_request(ApplicationForm, request)
        return super().dispatch(request, *args, **kwargs)


class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = Application.objects.all()
    default_return_url = "plugins:netbox_ipam_grouping:application_list"

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Application, pk=kwargs["pk"])
        if not request.user.is_superuser and not _user_owns(obj, request.user):
            messages.error(request, "You do not have permission to delete this application.")
            return redirect(obj.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)


class ApplicationChangelogView(generic.ObjectChangeLogView):
    queryset = Application.objects.all()


class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = Application.objects.all()
    filterset = ApplicationFilterSet
    table = ApplicationTable
    default_return_url = "plugins:netbox_ipam_grouping:application_list"


# ------------------------------------------------------------------
# Group views
# ------------------------------------------------------------------

class GroupListView(generic.ObjectListView):
    queryset = Group.objects.prefetch_related(
        "owner", "application", "member_groups",
        "prefixes", "ip_addresses", "ip_ranges", "tags",
    )
    table = GroupTable
    filterset = GroupFilterSet
    filterset_form = GroupFilterForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(owner__users=request.user) |
            Q(owner__user_groups__in=request.user.groups.all())
        ).distinct()


class GroupView(generic.ObjectView):
    queryset = Group.objects.prefetch_related(
        "owner", "application", "member_groups",
        "prefixes", "ip_addresses", "ip_ranges", "tags",
    )

    def get_extra_context(self, request, instance):
        return {
            "ip_addresses": instance.ip_addresses.order_by("address"),
            "prefixes": instance.prefixes.order_by("prefix"),
            "ip_ranges": instance.ip_ranges.order_by("start_address"),
            "member_groups": instance.member_groups.prefetch_related("owner").order_by("name"),
            "parent_groups": instance.parent_groups.prefetch_related("owner").order_by("name"),
        }


class GroupCreateView(generic.ObjectEditView):
    queryset = Group.objects.all()
    form = GroupForm
    template_name = "netbox_ipam_grouping/group_edit.html"

    def dispatch(self, request, *args, **kwargs):
        self.form = _inject_request(GroupForm, request)
        return super().dispatch(request, *args, **kwargs)


class GroupEditView(generic.ObjectEditView):
    queryset = Group.objects.all()
    form = GroupForm
    template_name = "netbox_ipam_grouping/group_edit.html"

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Group, pk=kwargs["pk"])
        if not request.user.is_superuser and not _user_owns(obj, request.user):
            messages.error(request, "You do not have permission to edit this group.")
            return redirect(obj.get_absolute_url())
        self.form = _inject_request(GroupForm, request)
        return super().dispatch(request, *args, **kwargs)


class GroupDeleteView(generic.ObjectDeleteView):
    queryset = Group.objects.all()
    default_return_url = "plugins:netbox_ipam_grouping:group_list"

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Group, pk=kwargs["pk"])
        if not request.user.is_superuser and not _user_owns(obj, request.user):
            messages.error(request, "You do not have permission to delete this group.")
            return redirect(obj.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)


class GroupChangelogView(generic.ObjectChangeLogView):
    queryset = Group.objects.all()


class GroupBulkDeleteView(generic.BulkDeleteView):
    queryset = Group.objects.all()
    filterset = GroupFilterSet
    table = GroupTable
    default_return_url = "plugins:netbox_ipam_grouping:group_list"