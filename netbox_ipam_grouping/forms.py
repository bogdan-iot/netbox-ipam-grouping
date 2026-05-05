from django import forms
from django.db.models import Q
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField, DynamicModelChoiceField, SlugField

from ipam.models import Prefix, IPAddress, IPRange
from users.models import Owner
from .models import Application, Group


def _scoped_owner_field(user):
    owner_objects = list(
        Owner._default_manager.filter(
            Q(users=user) | Q(user_groups__in=user.groups.all())
        ).distinct().order_by("name")
    )
    return forms.ChoiceField(
        choices=[("", "---------")] + [(str(o.pk), o.name) for o in owner_objects],
        required=True,
        label="Owner",
    )


def _clean_owner(val):
    if not val:
        return None
    if isinstance(val, Owner):
        return val
    try:
        return Owner._default_manager.get(pk=int(val))
    except (Owner.DoesNotExist, ValueError, TypeError):
        raise forms.ValidationError("Select a valid owner.")


class ApplicationForm(NetBoxModelForm):

    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label="Owner",
        selector=True,
    )
    slug = SlugField()

    class Meta:
        model = Application
        fields = ["name", "slug", "description", "owner", "tags"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        user = self.request.user if self.request else None
        if user and not user.is_superuser:
            self.fields["owner"] = _scoped_owner_field(user)

    def clean_owner(self):
        return _clean_owner(self.cleaned_data.get("owner"))


class GroupForm(NetBoxModelForm):

    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=True,
        label="Owner",
        selector=True,
    )

    application = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        required=True,
        label="Application",
        selector=True,
    )

    # $application causes the widget to append cf_ipam_application=<pk> to every
    # AJAX call whenever the application field changes.
    # When no application is selected, $application resolves to "" which makes
    # the API call ?cf_ipam_application= (empty). The ScopedXxxFilterSet
    # intercepts this and returns queryset.none() — so no options appear.
    # Visual locking is handled by JavaScript in group_edit.html.
    prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Prefixes",
        query_params={"cf_ipam_application": "$application"},
    )

    ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="IP Addresses",
        query_params={"cf_ipam_application": "$application"},
    )

    ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="IP Ranges",
        query_params={"cf_ipam_application": "$application"},
    )

    class Meta:
        model = Group
        fields = [
            "name",
            "description",
            "owner",
            "application",
            "prefixes",
            "ip_addresses",
            "ip_ranges",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        user = self.request.user if self.request else None

        if user and not user.is_superuser:
            self.fields["owner"] = _scoped_owner_field(user)

            owner_pks = list(
                Owner._default_manager.filter(
                    Q(users=user) | Q(user_groups__in=user.groups.all())
                ).distinct().values_list("pk", flat=True)
            )
            self.fields["application"].queryset = Application.objects.filter(
                owner__pk__in=owner_pks
            )

            for field_name in ("prefixes", "ip_addresses", "ip_ranges"):
                self.fields[field_name].widget.add_query_param("owned_by_user", user.pk)

    def clean_owner(self):
        return _clean_owner(self.cleaned_data.get("owner"))

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        application = cleaned_data.get("application")
        if not application:
            return cleaned_data

        mismatched = []
        for field_name, label in (
            ("prefixes", "Prefix"),
            ("ip_addresses", "IP address"),
            ("ip_ranges", "IP range"),
        ):
            objects = cleaned_data.get(field_name) or []
            for obj in objects:
                obj_app = obj.custom_field_data.get("ipam_application")
                if obj_app is not None and obj_app != application.pk:
                    mismatched.append(
                        f"{label} '{obj}' is assigned to a different application."
                    )

        if mismatched:
            raise forms.ValidationError(
                "The following objects belong to a different application than "
                "the one selected for this group:\n" + "\n".join(mismatched)
            )

        return cleaned_data
