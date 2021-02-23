from collections import OrderedDict

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from django.contrib.auth.mixins import LoginRequiredMixin
from core.authorization.models import Authorization

from .forms import AuthorizationForm
from .viewmixins import RelatedAuthorizationsMixin


class AuthorizationUserView(LoginRequiredMixin, RelatedAuthorizationsMixin, ListView):
    model = Authorization

    def get_queryset(self):
        qs = super(AuthorizationUserView, self).get_queryset()
        target_instance = self.get_target_instance()
        ct = ContentType.objects.get_for_model(target_instance)
        return qs.filter(content_type=ct, object_id=target_instance.pk)

    def get_authorizations_per_app(self):
        data = OrderedDict()

        for key, label in self.get_related_authorization_choices():
            data[key] = {
                "authorizations": self.object_list.filter(authorization_codename=key),
                "label": label,
            }

        return data

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["authorizations"] = self.get_authorizations_per_app()
        return data

    def get_target_instance(self):
        """ Returns the considered target instance associated with authorizations. """
        raise NotImplementedError


class AuthorizationCreateView(LoginRequiredMixin, RelatedAuthorizationsMixin, CreateView):
    model = Authorization
    form_class = AuthorizationForm

    def form_valid(self, form):
        response = super(AuthorizationCreateView, self).form_valid(form)
        messages.success(self.request, _("L’accès a été créé avec succès."))
        return response

    def get_authorization_definition(self):
        """ Returns a tuple of the form (codename, label) for the considered authorization. """
        authorization_labels_dict = dict(self.get_related_authorization_choices())
        try:
            codename = self.request.GET.get("codename", None)
            assert codename is not None
            assert codename in authorization_labels_dict
        except AssertionError:
            raise Http404
        return codename, authorization_labels_dict[codename]

    def get_context_data(self, **kwargs):
        context = super(AuthorizationCreateView, self).get_context_data(**kwargs)
        (
            context["authorization_codename"],
            context["authorization_label"],
        ) = self.authorization_definition
        return context

    def get_form_kwargs(self):
        kwargs = super(AuthorizationCreateView, self).get_form_kwargs()
        authorization_def = self.authorization_definition

        kwargs.update(
            {
                "codename": authorization_def[0],
                "target": self.get_target_instance(),
            }
        )

        return kwargs

    def get_target_instance(self):
        """ Returns the target instance for which we want to create authorizations. """
        raise NotImplementedError

    authorization_definition = cached_property(get_authorization_definition)


class AuthorizationDeleteView(LoginRequiredMixin, DeleteView):
    model = Authorization

    def delete(self, request, *args, **kwargs):
        response = super(AuthorizationDeleteView, self).delete(request, *args, **kwargs)
        messages.success(self.request, _("L’accès a été supprimé avec succès."))
        return response

    def get_queryset(self):
        qs = super(AuthorizationDeleteView, self).get_queryset()
        target_instance = self.get_target_instance()
        ct = ContentType.objects.get_for_model(target_instance)
        return qs.filter(content_type=ct, object_id=target_instance.pk)

    def get_target_instance(self):
        """ Returns the target instance for which we want to delete authorizations. """
        raise NotImplementedError
