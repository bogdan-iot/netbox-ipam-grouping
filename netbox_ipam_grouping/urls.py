from django.urls import path

app_name = "netbox_ipam_grouping"


def _views():
    from . import views
    return views


def _models():
    from . import models
    return models


def _changelog():
    from netbox.views.generic import ObjectChangeLogView
    return ObjectChangeLogView


urlpatterns = [
    # Applications
    path(
        "applications/",
        lambda request: _views().ApplicationListView.as_view()(request),
        name="application_list",
    ),
    path(
        "applications/add/",
        lambda request: _views().ApplicationCreateView.as_view()(request),
        name="application_add",
    ),
    path(
        "applications/edit/",
        lambda request: _views().ApplicationBulkEditView.as_view()(request),
        name="application_bulk_edit",
    ),
    path(
        "applications/delete/",
        lambda request: _views().ApplicationBulkDeleteView.as_view()(request),
        name="application_bulk_delete",
    ),
    path(
        "applications/<int:pk>/",
        lambda request, pk: _views().ApplicationView.as_view()(request, pk=pk),
        name="application",
    ),
    path(
        "applications/<int:pk>/edit/",
        lambda request, pk: _views().ApplicationEditView.as_view()(request, pk=pk),
        name="application_edit",
    ),
    path(
        "applications/<int:pk>/delete/",
        lambda request, pk: _views().ApplicationDeleteView.as_view()(request, pk=pk),
        name="application_delete",
    ),
    path(
        "applications/<int:pk>/changelog/",
        lambda request, pk: _changelog().as_view()(
            request, pk=pk, model=_models().Application
        ),
        name="application_changelog",
    ),

    # Groups
    path(
        "",
        lambda request: _views().GroupListView.as_view()(request),
        name="group_list",
    ),
    path(
        "add/",
        lambda request: _views().GroupCreateView.as_view()(request),
        name="group_add",
    ),
    path(
        "edit/",
        lambda request: _views().GroupBulkEditView.as_view()(request),
        name="group_bulk_edit",
    ),
    path(
        "delete/",
        lambda request: _views().GroupBulkDeleteView.as_view()(request),
        name="group_bulk_delete",
    ),
    path(
        "import/",
        lambda request: _views().GroupBulkImportView.as_view()(request),
        name="group_bulk_import",
    ),
    path(
        "import/",
        lambda request: _views().GroupBulkImportView.as_view()(request),
        name="group_import",
    ),
    path(
        "<int:pk>/",
        lambda request, pk: _views().GroupView.as_view()(request, pk=pk),
        name="group",
    ),
    path(
        "<int:pk>/edit/",
        lambda request, pk: _views().GroupEditView.as_view()(request, pk=pk),
        name="group_edit",
    ),
    path(
        "<int:pk>/delete/",
        lambda request, pk: _views().GroupDeleteView.as_view()(request, pk=pk),
        name="group_delete",
    ),
    path(
        "<int:pk>/changelog/",
        lambda request, pk: _changelog().as_view()(
            request, pk=pk, model=_models().Group
        ),
        name="group_changelog",
    ),
]
