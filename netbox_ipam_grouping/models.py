from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from ipam.models import Prefix, IPAddress, IPRange


class Application(NetBoxModel):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name=_("slug"),
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
    )
    owner = models.ForeignKey(
        to="users.Owner",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="applications",
        verbose_name=_("owner"),
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("application")
        verbose_name_plural = _("applications")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_ipam_grouping:application", args=[self.pk])

    def user_can_view(self, user):
        if user.is_superuser:
            return True
        if not self.owner:
            return False
        if self.owner.users.filter(pk=user.pk).exists():
            return True
        if self.owner.user_groups.filter(
            pk__in=user.groups.values_list("pk", flat=True)
        ).exists():
            return True
        return False


class Group(NetBoxModel):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
    )
    owner = models.ForeignKey(
        to="users.Owner",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ipam_groups",
        verbose_name=_("owner"),
    )
    application = models.ForeignKey(
        to="Application",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ipam_groups",
        verbose_name=_("application"),
    )
    # Self-referential M2M:
    #   group.member_groups.all()  → groups that belong to this group
    #   group.parent_groups.all()  → groups this group belongs to
    member_groups = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
        related_name="parent_groups",
        verbose_name=_("member groups"),
    )
    prefixes = models.ManyToManyField(
        Prefix,
        blank=True,
        related_name="ipam_groups",
        verbose_name=_("prefixes"),
    )
    ip_addresses = models.ManyToManyField(
        IPAddress,
        blank=True,
        related_name="ipam_groups",
        verbose_name=_("IP addresses"),
    )
    ip_ranges = models.ManyToManyField(
        IPRange,
        blank=True,
        related_name="ipam_groups",
        verbose_name=_("IP ranges"),
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_ipam_grouping:group", args=[self.pk])

    def user_can_view(self, user):
        if user.is_superuser:
            return True
        if not self.owner:
            return False
        if self.owner.users.filter(pk=user.pk).exists():
            return True
        if self.owner.user_groups.filter(
            pk__in=user.groups.values_list("pk", flat=True)
        ).exists():
            return True
        return False
