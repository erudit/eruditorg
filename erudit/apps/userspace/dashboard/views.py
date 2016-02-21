from django.views.generic import TemplateView

from apps.userspace.viewmixins import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'userspace/dashboard/home.html'
