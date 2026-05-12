import sys
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

    member_groups = DynamicModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Member groups",
        query_params={"application": "$application"},
    )

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
            "member_groups",
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

            member_qs = Group.objects.filter(
                Q(owner__users=user) |
                Q(owner__user_groups__in=user.groups.all())
            ).distinct()
            if self.instance and self.instance.pk:
                member_qs = member_qs.exclude(pk=self.instance.pk)
            self.fields["member_groups"].queryset = member_qs

            for field_name in ("prefixes", "ip_addresses", "ip_ranges"):
                self.fields[field_name].widget.add_query_param("owned_by_user", user.pk)

        else:
            if self.instance and self.instance.pk:
                self.fields["member_groups"].queryset = Group.objects.exclude(
                    pk=self.instance.pk
                )

    def clean_owner(self):
        return _clean_owner(self.cleaned_data.get("owner"))

    def clean(self):
        # Read raw POST data to check for members — we cannot rely on
        # cleaned_data here because super().clean() returns None/empty
        # when field-level errors exist (e.g. M2M fields absent from POST).
        # self.data always contains the raw submitted values regardless.
        has_members = any([
            self.data.getlist("prefixes"),
            self.data.getlist("ip_addresses"),
            self.data.getlist("ip_ranges"),
            self.data.getlist("member_groups"),
        ])
        if not has_members:
            raise forms.ValidationError(
                "A group must contain at least one Prefix, IP Address, "
                "IP Range, or Member group."
            )

        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        # Prevent circular membership
        member_groups = cleaned_data.get("member_groups") or []
        if self.instance and self.instance.pk and member_groups:
            for candidate in member_groups:
                seen = set()
                queue = list(candidate.parent_groups.all())
                while queue:
                    g = queue.pop()
                    if g.pk in seen:
                        continue
                    seen.add(g.pk)
                    if g.pk == self.instance.pk:
                        raise forms.ValidationError(
                            {"member_groups": f"Adding '{candidate}' would create a circular group membership."}
                        )
                    queue.extend(g.parent_groups.all())

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
