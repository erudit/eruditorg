from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)


class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = 'userspace/dashboard.html'
