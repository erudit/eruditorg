# -*- coding: utf-8 -*-


class RelatedAuthorizationsMixin:
    # This attribute should be overridden on any subclass
    related_authorizations = []

    def get_related_authorizations(self):
        """ Returns the AuthorizationDef instances of authorizations that can be assigned. """
        return self.related_authorizations

    def get_related_authorization_choices(self):
        """ Returns a list of tuples of the form (codename, label) using the authorizations. """
        return [(a.codename, a.label) for a in self.get_related_authorizations()]
