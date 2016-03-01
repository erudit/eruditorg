class WorkflowMixin(object):
    """
    Provide status list avalaible from current state.
    Apply the transition and save the new state on valid form submitted.
    """

    def get_available_transitions(self):
        return [t.name for t in self.object.
                get_available_user_status_transitions(self.request.user)]

    def apply_transition(self):
        transition_name = self.request.POST.get('transition')
        if transition_name and \
           transition_name in self.get_available_transitions():
            transition = getattr(self.object, transition_name)
            transition()
            self.object.save()

    def form_valid(self, form):
        response = super().form_valid(form)
        self.apply_transition()
        return response
