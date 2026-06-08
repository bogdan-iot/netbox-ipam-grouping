import sys
from django import forms
from django.db.models import Q
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms.rendering import FieldSet
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    DynamicModelChoiceField,
    SlugField,
    TagFilterField,
)

from ipam.models import Prefix, IPAddress, IPRange
from users.models import Owner
from .models import Application, Group
from .utils import has_unrestricted_permission

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


# ------------------------------------------------------------------
# Create / Edit forms
# ------------------------------------------------------------------

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
            if not has_unrestricted_permission(self.request, 'view', 'users', 'owner'):
                self.fields["owner"] = _scoped_owner_field(user)

    def clean_owner(self):
        return _clean_owner(self.cleaned_data.get("owner"))


class GroupForm(NetBoxModelForm):

    name = forms.CharField(
        max_length=200,
        help_text="Don't include G_ , e.g. 'App1-Servers-Prod'",
    )

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

        # Hide AppViz custom fields that can't be modified.
        for field in ('cf_appviz_diff', 'cf_appviz_sync'):
            self.fields.pop(field, None)
            # self.custom_fields.pop(field, None)

        if user and not user.is_superuser:
            self.fields.pop('cf_appviz_object_id', None)

            owner_pks = list(
                Owner._default_manager.filter(
                    Q(users=user) | Q(user_groups__in=user.groups.all())
                ).distinct().values_list("pk", flat=True)
            )

            if not has_unrestricted_permission(self.request, 'view', 'users', 'owner'):
                self.fields["owner"] = _scoped_owner_field(user)
                if self.instance and self.instance.pk and self.instance.owner_id:
                    existing = Owner._default_manager.filter(pk=self.instance.owner_id).first()
                    if existing:
                        current_choices = list(self.fields["owner"].choices)
                        pks = [str(pk) for pk, _ in current_choices]
                        if str(existing.pk) not in pks:
                            self.fields["owner"].choices = current_choices + [
                                (str(existing.pk), existing.name)
                            ]
            else:
                # Explicitly set the initial value for users with unrestricted access
                if self.instance and self.instance.pk and self.instance.owner_id:
                    self.fields["owner"].initial = self.instance.owner_id

            if not has_unrestricted_permission(self.request, 'view', 'netbox_ipam_grouping', 'application'):
                app_qs = Application.objects.filter(owner__pk__in=owner_pks)
                if self.instance and self.instance.pk and self.instance.application_id:
                    app_qs = app_qs | Application.objects.filter(pk=self.instance.application_id)
                self.fields["application"].queryset = app_qs.distinct()

            if not has_unrestricted_permission(self.request, 'view', 'netbox_ipam_grouping', 'group'):
                member_qs = Group.objects.filter(
                    Q(owner__users=user) |
                    Q(owner__user_groups__in=user.groups.all())
                ).distinct()
            else:
                member_qs = Group.objects.all()
            if self.instance and self.instance.pk:
                member_qs = member_qs.exclude(pk=self.instance.pk)
            self.fields["member_groups"].queryset = member_qs

            if not has_unrestricted_permission(self.request, 'view', 'ipam', 'prefix'):
                self.fields["prefixes"].widget.add_query_param("owned_by_user", user.pk)

            if not has_unrestricted_permission(self.request, 'view', 'ipam', 'ipaddress'):
                self.fields["ip_addresses"].widget.add_query_param("owned_by_user", user.pk)

            if not has_unrestricted_permission(self.request, 'view', 'ipam', 'iprange'):
                self.fields["ip_ranges"].widget.add_query_param("owned_by_user", user.pk)

        else:
            if self.instance and self.instance.pk:
                self.fields["member_groups"].queryset = Group.objects.exclude(
                    pk=self.instance.pk
                )

    def clean_owner(self):
        return _clean_owner(self.cleaned_data.get("owner"))

    def clean(self):
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


class ApplicationBulkEditForm(NetBoxModelBulkEditForm):
    model = Application

    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label='Owner',
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label='Description',
    )

    nullable_fields = ('description', 'owner')


class GroupBulkEditForm(NetBoxModelBulkEditForm):
    model = Group

    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label='Owner',
    )
    application = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label='Application',
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label='Description',
    )

    nullable_fields = ('description', 'owner', 'application')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('cf_appviz_diff', 'cf_appviz_object_id', 'cf_appviz_sync'):
            self.custom_fields.pop(field, None)
            self.fields.pop(field, None)
        self.custom_field_groups.pop('AppViz', None)


# ------------------------------------------------------------------
# Filter forms (used by the list views' filter panel)
# ------------------------------------------------------------------

class ApplicationFilterForm(NetBoxModelFilterSetForm):
    model = Application
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('owner_id', name='Ownership'),
    )

    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label='Owner',
    )
    tag = TagFilterField(Application)


class GroupFilterForm(NetBoxModelFilterSetForm):
    model = Group
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('owner_id', 'application_id', name='Assignment'),
    )

    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label='Owner',
    )
    application_id = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label='Application',
    )
    tag = TagFilterField(Group)
