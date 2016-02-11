from django.views.generic import TemplateView

from core.userspace.viewmixins import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'userspace/dashboard.html'
